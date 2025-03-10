from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductUnitSerializer
from wishlist.models import Wishlist, WishlistUnit
from products.models import Product
from products.serializers import ProductMainPageSerializer, ProductSerializer
import json


class ProductUnitProductView(APIView):
    def get(self, request, product_id):
        if Product.objects.filter(id=product_id).exists():
            product = Product.objects.get(id=product_id)
            return Response(ProductUnitSerializer(product.product_units, many=True).data)
        return Response("Товар не найден")


class ProductUnitProductSlugView(APIView):
    def get(self, request, slug):
        if Product.objects.filter(slug=slug).exists():
            product = Product.objects.get(slug=slug)
            return Response(ProductUnitSerializer(product.product_units, many=True).data)
        return Response("Товар не найден")


def product_unit_product_main(product_id, user_id):
    if Product.objects.filter(id=product_id).exists():
        product = Product.objects.get(id=product_id)
        ans = ProductSerializer(product).data
        if user_id > 0:
            wishlist = Wishlist.objects.get(user_id=user_id)
            data = WishlistUnit.objects.filter(wishlist=wishlist, product_id=product_id)
            ans['in_wishlist'] = len(data) > 0
        return ans
    return Response("Товар не найден")


class ProductUnitProductMainView(APIView):
    def get(self, request, product_id, user_id):
        if Product.objects.filter(id=product_id).exists():
            if request.user.id == user_id or request.user.is_staff:
                return Response(product_unit_product_main(product_id, user_id))
            else:
                return Response(product_unit_product_main(product_id, 0))
        return Response("Товар не найден")


# Create your views here.

