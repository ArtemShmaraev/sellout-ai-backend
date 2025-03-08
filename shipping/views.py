from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductUnitSerializer
from .models import ProductUnit
from wishlist.models import Wishlist, WishlistUnit
from products.models import Product
from products.serializers import ProductMainPageSerializer, ProductSerializer
import json


class ProductUnitProductView(APIView):
    def get(self, request, product_id):
        s = ProductUnit.objects.filter(product_id=product_id)
        return Response(ProductUnitSerializer(s, many=True).data)


class ProductUnitProductSlugView(APIView):
    def get(self, request, slug):
        print(slug)
        s = ProductUnit.objects.filter(product__slug=slug)
        return Response(ProductUnitSerializer(s, many=True).data)


def product_unit_product_main(product_id, user_id):
    if Product.objects.filter(id=product_id).exists():
        product = Product.objects.get(id=product_id)
        ans = ProductSerializer(product).data
        ans['min_price'] = product.min_price
        if user_id > 0:
            wishlist = Wishlist.objects.get(user_id=user_id)
            data = WishlistUnit.objects.filter(wishlist=wishlist, product_id=product_id)
            ans['in_wishlist'] = len(data) > 0
        return ans
    return "Товар не найден"


class ProductUnitProductMainView(APIView):
    def get(self, request, product_id, user_id):
        if request.user.id == user_id or request.user.is_staff:
            return Response(product_unit_product_main(product_id, user_id))
        else:
            return Response(product_unit_product_main(product_id, 0))


# Create your views here.

