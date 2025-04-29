from django.utils.functional import cached_property
from django.db import models
import rest_framework.generics
from django.db.models import Q
from rest_framework.decorators import api_view, action
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
from time import time
from django.http import JsonResponse, FileResponse
from .models import Product, Category, Line, DewuInfo
from rest_framework import status
from .serializers import ProductMainPageSerializer, CategorySerializer, LineSerializer, ProductSerializer, DewuInfoSerializer
from .tools import build_line_tree, build_category_tree, category_no_child, line_no_child, add_product


# Create your views here.
class DewuInfoListView(APIView):
    def get(self, request):
        dewu_infos = DewuInfo.objects.all()
        count = dewu_infos.count()
        page_number = request.query_params.get("page")
        page_number = int(page_number if page_number else 1)
        start_index = (page_number - 1) * 60
        queryset = dewu_infos[start_index:start_index + 60]
        serializer = DewuInfoSerializer(queryset, many=True)
        res = {'count': count, "results": serializer.data}  # Замените на вашу сериализацию
        return Response(res, status=status.HTTP_200_OK)


class DewuInfoView(APIView):
    def get(self, request, spu_id):
        dewu_info = DewuInfo.objects.filter(spu_id=spu_id)
        serializer = DewuInfoSerializer(dewu_info, many=True)
        # Замените на вашу сериализацию
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, spu_id):
        data = json.loads(request.body)
        if DewuInfo.objects.filter(spu_id=spu_id).exists():
            dewu_info = DewuInfo.objects.get(spu_id=spu_id)
            if "api_data" in data:
                dewu_info.api_data = data['api_data']
            if "preprocessed_data" in data:
                dewu_info.preprocessed_data = data['preprocessed_data']
            if "web_data" in data:
                dewu_info.web_data = data['web_data']
            dewu_info.save()
        else:
            dewu_info = DewuInfo(spu_id=spu_id)
            if "api_data" in data:
                dewu_info.api_data = data['api_data']
            if "preprocessed_data" in data:
                dewu_info.preprocessed_data = data['preprocessed_data']
            if "web_data" in data:
                dewu_info.web_data = data['web_data']
            dewu_info.save()
        return Response(DewuInfoSerializer(dewu_info).data)




class ProductSearchView(APIView):
    def get(self, request):
        query = json.loads(request.body)  # Получение параметра запроса
        search_fields = query

        q_objects = Q()
        for k, v in search_fields.items():
            q_objects &= Q(**{f'{k}__icontains': v})

        products = Product.objects.filter(q_objects)
        count = products.count()
        page_number = self.request.query_params.get("page")
        page_number = int(page_number if page_number else 1)
        start_index = (page_number - 1) * 60
        queryset = products[start_index:start_index + 60]
        serializer = ProductMainPageSerializer(queryset, many=True)
        res = {'count': count, "results": serializer.data}# Замените на вашу сериализацию

        return Response(res, status=status.HTTP_200_OK)


# class CustomPagination(PageNumberPagination):
#     # default_limit = 60
#     page_size = 60
#     # page_size_query_param = 'page_size'  # Дополнительно можно разрешить клиенту указывать желаемое количество товаров на странице
#     # max_page_size = 120  # Опционально, чтобы ограничить максимальное количество товаров на странице
#     count = False
#
#     #


class ProductView(APIView):

    # @method_decorator(cache_page(60 * 5))
    def get(self, request):

        t1 = time()
        queryset = Product.objects.all()
        t2 = time()
        print("t1", t2 - t1)
        context = {'user_id': self.request.user.id}

        size = self.request.query_params.getlist('size')
        price_max = self.request.query_params.get('price_max')
        price_min = self.request.query_params.get('price_min')
        ordering = self.request.query_params.get('ordering')

        # Передайте значения фильтров в контекст сериализатора
        context['size'] = context['size_us'] = size if size else None
        context['price_max'] = price_max if price_max else None
        context['price_min'] = price_min if price_min else None
        context['ordering'] = ordering if ordering else None
        # Создаем объект пагинации
        line = self.request.query_params.getlist('line')
        color = self.request.query_params.getlist('color')
        is_fast_shipping = self.request.query_params.get("is_fast_shipping")
        is_sale = self.request.query_params.get("is_sale")
        is_return = self.request.query_params.get("is_return")
        category = self.request.query_params.getlist("category")
        gender = self.request.query_params.getlist("gender")
        brand = self.request.query_params.getlist("brand")
        collab = self.request.query_params.getlist("collab")
        available = self.request.query_params.get("available")
        custom = self.request.query_params.get("custom")

        if not available:
            queryset = queryset.filter(available_flag=True)
        if not custom:
            queryset = queryset.filter(is_custom=False)
        if collab:
            if collab == "all":
                queryset = queryset.filter(is_collab=True)
            else:
                queryset = queryset.filter(collab__query_name__in=collab)
        if brand:
            for brand_name in brand:
                queryset = queryset.filter(brands__query_name=brand_name)
        if line:
            queryset = queryset.filter(lines__full_eng_name__in=line)

            def find_common_ancestor(lines):
                # Создаем множество для хранения всех родительских линеек
                ancestors = set()

                # Добавляем все родительские линейки в множество
                for line in lines:
                    current_line = line
                    while current_line.parent_line:
                        ancestors.add(current_line.parent_line)
                        current_line = current_line.parent_line

                # Проходим по списку линеек и находим первую общую родительскую линейку
                for line in lines:
                    current_line = line
                    while current_line.parent_line:
                        if current_line.parent_line in ancestors:
                            return current_line.parent_line
                        current_line = current_line.parent_line

                return None  # Если общей родительской линейки не найдено
            # Пример использования
            selected_lines = Line.objects.filter(full_eng_name__in=line)  # Ваши выбранные линейки
            oldest_line = find_common_ancestor(selected_lines)


        if color:
            queryset = queryset.filter(Q(main_color__name__in=color))
        if category:
            queryset = queryset.filter(categories__eng_name__in=category)

            def find_common_ancestor(categories):
                # Создаем множество для хранения всех родительских линеек
                ancestors = set()

                # Добавляем все родительские линейки в множество
                for category in categories:
                    current_category = category
                    while current_category.parent_category:
                        ancestors.add(current_category.parent_category)
                        current_category = current_category.parent_category

                # Проходим по списку линеек и находим первую общую родительскую линейку
                for category in categories:
                    current_category = category
                    while current_category.parent_category:
                        if current_category.parent_category in ancestors:
                            return current_category.parent_category
                        current_category = current_category.parent_category
                return None  # Если общей родительской линейки не найдено
            selected_cat = Category.objects.filter(eng_name__in=category)  # Ваши выбранные линейки
            oldest_cat = find_common_ancestor(selected_cat)
            print(oldest_cat)

        if gender:
            queryset = queryset.filter(Q(gender__name__in=gender))


        filters = Q()
        # Фильтр по цене
        if price_min:
            filters &= Q(product_units__final_price__gte=price_min)

            # Фильтр по максимальной цене
        if price_max:
            filters &= Q(product_units__final_price__lte=price_max)

        # Фильтр по размеру
        if size:
            filters &= Q(product_units__size__in=size)

        # Фильтр по наличию скидки
        if is_sale:
            filters &= Q(product_units__is_sale=is_sale)
        if is_return:
            filters &= Q(product_units__is_return=is_return)
        if is_fast_shipping:
            filters &= Q(product_units__fast_shipping=is_fast_shipping)
        if filters != Q():
        # Выполняем фильтрацию
            queryset = queryset.filter(filters)
        queryset = queryset.distinct()

        t3 = time()
        print("t2", t3 - t2)

        # paginator = CustomPagination()
        # Применяем пагинацию к списку объектов Product
        # paginated_products = paginator.paginate_queryset(queryset, request)
        # serializer = ProductMainPageSerializer(queryset, many=True, context=context).data
        # res = paginator.get_paginated_response(serializer)

        res = {"count": queryset.count()}
        t4 = time()
        print("t3", t4 - t3)

        page_number = self.request.query_params.get("page")
        page_number = int(page_number if page_number else 1)
        start_index = (page_number - 1) * 60
        queryset = queryset[start_index:start_index + 60]
        t41 = time()
        print("t41", t41 - t3)

        # Сериализуем объекты и возвращаем ответ с пагинированными данными
        serializer = ProductMainPageSerializer(queryset, many=True, context=context).data
        t5 = time()
        print("t4", t5 - t41)

        res['results'] = serializer
        t6 = time()
        print("t5", t6 - t5)




        # line = ""
        # cat = ""
        # if lines:
        #     tree = build_line_tree(LineSerializer(Line.objects.all(), many=True).data)
        #     line = find_oldest_name(tree, lines, cat=False)
        # if categories:
        #     tree = build_category_tree(CategorySerializer(Category.objects.all(), many=True).data)
        #     cat = find_oldest_name(tree, categories)
        # response.data["products_page_header"] = str(line) + " " + str(cat)






        return Response(res)


class ProductSlugView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductMainPageSerializer(product, context={'user_id': request.user.id, "list_lines": True})
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductIdView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
            serializer = ProductMainPageSerializer(product, context={"list_lines": True, 'user_id': request.user.id})
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class CategoryTreeView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        cats = CategorySerializer(Category.objects.all(), many=True).data
        return Response(build_category_tree(cats))


class CategoryNoChildView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        cats = CategorySerializer(Category.objects.all(), many=True).data
        return Response(category_no_child(build_category_tree(cats)))


class LineTreeView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        lines = LineSerializer(Line.objects.all(), many=True).data
        return Response(build_line_tree(lines))


class LineNoChildView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        lines = LineSerializer(Line.objects.all(), many=True).data
        return Response(line_no_child(lines))


class ProductUpdateView(APIView):
    # authentication_classes = [JWTAuthentication]

    def delete(self, request, product_id):
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response("Товар успешно удален")

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        data = json.loads(request.body)
        if 'categories' in data:
            categories = data.get('categories', [])
            product.categories.clear()
            product.categories.add(*categories)

        if 'lines' in data:
            lines = data.get('lines', [])
            product.lines.clear()
            product.lines.add(*lines)

        if 'colors' in data:
            colors = data.get('colors', [])
            product.lines.add(*colors)

        if 'brands' in data:
            brands = data.get('brands', [])
            product.brands.clear()
            product.brands.add(*brands)

        if 'tags' in data:
            tags = data.get('tags', [])
            product.tags.clear()
            product.tags.add(*tags)

        # Обработайте остальные поля по аналогии
        if 'model' in data:
            product.model = data.get('model', product.model)
        if 'colorway' in data:
            product.colorway = data.get('colorway', product.colorway)
        if 'russian_name' in data:
            product.russian_name = data.get('russian_name', product.russian_name)
        if 'manufacturer_sku' in data:
            product.manufacturer_sku = data.get('manufacturer_sku', product.manufacturer_sku)
        if 'description' in data:
            product.description = data.get('description', product.description)
        if 'bucket_link' in data:
            product.bucket_link = data.get('bucket_link', product.bucket_link)
        if 'main_color' in data:
            product.main_color_id = data.get('main_color', product.main_color_id)
        product.slug = ""
        product.save()

        return Response(ProductMainPageSerializer(product).data, status=status.HTTP_200_OK)


class ProductSizeView(APIView):
    def get(self, request):
        # Откройте JSON-файл и загрузите его содержимое
        with open('size_table_2.json', 'r', encoding='utf-8') as file:
            product_sizes_data = json.load(file)

        # Верните JSON-данные в ответе
        return Response(product_sizes_data)


class AddProductView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        product = add_product(data)
        return Response(product.manufacturer_sku)


class ListProductView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            s_products = json.loads(request.body)["products"]
            products = Product.objects.filter(id__in=s_products).order_by(
                models.Case(*[models.When(id=id, then=index) for index, id in enumerate(s_products)])
            )
            return Response(ProductMainPageSerializer(products, many=True).data)
        except json.JSONDecodeError:
            return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response("One or more product do not exist", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class ProductMainPageView(rest_framework.generics.ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     # pagination_class = PageNumberPagination
#     # permission_classes = [AllowAny,]
#     # filter_backends = [ProductFilter]
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['user_id'] = self.request.user.id
#         return context


# возвращает список продуктов для главной странички всех товаров
# class ProductsView(APIView):
#
#     def get(self, request, page_number):
#         products = Product.objects.get_queryset().order_by('id')
#         page_number = self.request.query_params.get('page_number ', page_number)
#         page_size = self.request.query_params.get('page_size ', 5)
#         try:
#             products = Paginator(products, page_size).page(page_number)
#         except Exception as e:
#             print(e)
#             return Response("Ошибка")
#         list_products = []
#         if request.user.id:
#             for product in products:
#                 list_products.append(product_unit_product_main(product.id, request.user.id))
#         else:
#             for product in products:
#                 list_products.append(product_unit_product_main(product.id, 0))
#
#         ans = {"page number": page_number,
#                'items': list_products}
#         return Response(ans, status=status.HTTP_200_OK)
