from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from wishlist.models import Wishlist, WishlistUnit
from products.models import Product
from rest_framework import status
from django.core.paginator import Paginator
from sellout.settings import url
from shipping.views import product_unit_product_main


# Create your views here.


# возвращает список продуктов для главной странички всех товаров
class ProductsView(APIView):
    def get(self, request, page_number):
        products = Product.objects.get_queryset().order_by('id')
        page_number = self.request.query_params.get('page_number ', page_number)
        page_size = self.request.query_params.get('page_size ', 5)
        try:
            products = Paginator(products, page_size).page(page_number)
        except Exception as e:
            print(e)
            return Response("Ошибка")
        list_products = []
        if request.user.id:
            for product in products:
                list_products.append(product_unit_product_main(product.id, request.user.id))
        else:
            for product in products:
                list_products.append(product_unit_product_main(product.id, 0))

        ans = {"page number": page_number,
               'items': list_products}
        return Response(ans, status=status.HTTP_200_OK)

