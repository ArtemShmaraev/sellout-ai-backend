from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductUnitSerializer
from wishlist.models import Wishlist, WishlistUnit
from products.models import Product
from products.serializers import ProductMainPageSerializer, ProductSerializer
import json


class ProductUnitProductView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductUnitSerializer(product.product_units, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductUnitProductSlugView(APIView):
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductUnitSerializer(product.product_units, many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


def product_unit_product_main(product_id, user_id):
    try:
        product = Product.objects.get(id=product_id)
        ans = ProductSerializer(product).data
        if user_id > 0:
            try:
                wishlist = Wishlist.objects.get(user_id=user_id)
                data = WishlistUnit.objects.filter(wishlist=wishlist, product_id=product_id)
                ans['in_wishlist'] = len(data) > 0
            except Wishlist.DoesNotExist:
                ans['in_wishlist'] = False
        return ans
    except Product.DoesNotExist:
        return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductUnitProductMainView(APIView):
    def get(self, request, product_id, user_id):
        try:
            if Product.objects.filter(id=product_id).exists():
                if request.user.id == user_id or request.user.is_staff:
                    return Response(product_unit_product_main(product_id, user_id))
                else:
                    return Response(product_unit_product_main(product_id, 0))
            else:
                return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)
