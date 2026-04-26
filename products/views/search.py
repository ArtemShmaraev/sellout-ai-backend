import json

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import DewuInfo, Product, SGInfo
from products.search_tools import add_filter_search, suggest_search
from products.serializers import (
    DewuInfoSerializer,
    ProductMainPageSerializer,
    ProductSerializer,
    SGInfoSerializer,
)


class SearchBySkuView(APIView):
    def get(self, request):
        params = request.query_params
        search_type = params.get("type", "product")
        formatted_manufacturer_sku = params.get("formatted_manufacturer_sku")
        if search_type == "product":
            products = Product.objects.filter(formatted_manufacturer_sku=formatted_manufacturer_sku)
            return Response(ProductSerializer(products, many=True).data)
        elif search_type == "dewu_info":
            dewu_infos = DewuInfo.objects.filter(formatted_manufacturer_sku=formatted_manufacturer_sku)
            return Response(DewuInfoSerializer(dewu_infos, many=True).data)
        else:
            print(formatted_manufacturer_sku)
            sg_infos = SGInfo.objects.filter(formatted_manufacturer_sku=formatted_manufacturer_sku)
            return Response(SGInfoSerializer(sg_infos, many=True).data)


class AddFilterSearch(APIView):
    def get(self, request):
        return Response(add_filter_search(request))


class ProductSearchView(APIView):
    def get(self, request):
        query = json.loads(request.body)
        search_fields = query

        from django.db.models import Q
        q_objects = Q()
        for k, v in search_fields.items():
            q_objects &= Q(**{f'{k}__icontains': v})

        products = Product.objects.filter(q_objects)
        count = products.count()
        page_number = self.request.query_params.get("page")
        page_number = int(page_number if page_number else 1)
        start_index = (page_number - 1) * 96
        queryset = products[start_index:start_index + 96]
        serializer = ProductMainPageSerializer(queryset, many=True)
        res = {'count': count, "results": serializer.data}
        return Response(res, status=status.HTTP_200_OK)


class SuggestSearch(APIView):
    def get(self, request):
        return Response(suggest_search(request))


class _AiSearchRequestSerializer(serializers.Serializer):
    query = serializers.CharField(help_text="Запрос пользователя в свободной форме")
    session_id = serializers.CharField(required=False, allow_blank=True,
                                       help_text="ID сессии для продолжения диалога (необязательно)")


class AiSearchView(APIView):
    SESSION_TTL = 30 * 60  # 30 минут
    MAX_HISTORY = 10       # последние 10 сообщений (5 диалоговых пар)

    @extend_schema(request=_AiSearchRequestSerializer, summary="AI-ассистент по подбору товаров")
    def post(self, request):
        import json as _json
        import uuid

        from django.core.cache import cache

        from products.ai_search import filter_products_from_dict, query_to_filters

        user_query = request.data.get("query", "").strip()
        if not user_query:
            return Response({"error": "query is required"}, status=status.HTTP_400_BAD_REQUEST)

        session_id = request.data.get("session_id") or str(uuid.uuid4())
        cache_key = f"ai_search:{session_id}"
        history = cache.get(cache_key) or []

        try:
            llm_result = query_to_filters(user_query, history)
        except Exception as e:
            return Response({"error": f"LLM error: {str(e)}"}, status=status.HTTP_502_BAD_GATEWAY)

        history.append({"role": "user", "content": user_query})
        history.append({"role": "assistant", "content": _json.dumps(llm_result, ensure_ascii=False)})
        cache.set(cache_key, history[-self.MAX_HISTORY:], self.SESSION_TTL)

        filters = llm_result.get("filters", {})
        explanation = llm_result.get("explanation", "")
        suggestions = llm_result.get("suggestions", [])

        products = filter_products_from_dict(filters)

        context = {"wishlist": None}
        serializer = ProductMainPageSerializer(products, many=True, context=context)

        return Response({
            "session_id": session_id,
            "explanation": explanation,
            "suggestions": suggestions,
            "filters_used": filters,
            "count": len(serializer.data),
            "products": serializer.data,
        }, status=status.HTTP_200_OK)
