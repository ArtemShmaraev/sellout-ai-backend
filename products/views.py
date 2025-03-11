import rest_framework.generics
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from wishlist.models import Wishlist, WishlistUnit
from products.models import Product
from rest_framework import status
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from .serializers import ProductSerializer, ProductMainPageSerializer
from shipping.views import product_unit_product_main
from products.service import ProductFilter
from rest_framework.permissions import AllowAny

# Create your views here.



class ProductSlugView(APIView):
    def get(self, request, slug):
        if Product.objects.filter(slug=slug).exists():
            product = Product.objects.get(slug=slug)
            return Response(ProductMainPageSerializer(product).data)
        return Response("Товар не найден")


class ProductIdView(APIView):
    def get(self, request, id):
        if Product.objects.filter(id=id).exists():
            product = Product.objects.get(id=id)
            return Response(ProductSerializer(product).data)
        return Response("Товар не найден")



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

