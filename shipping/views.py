from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import ProductUnitSerializer, DeliveryTypeSerializer
from wishlist.models import Wishlist
from products.models import Product, SizeTranslationRows
from products.serializers import ProductMainPageSerializer, ProductSerializer, SizeTranslationRowsSerializer
import json

class DeliveryForSizeView(APIView):
    def get(self, request, product_id, size_id):
        try:
            product = Product.objects.get(id=product_id)
            product_units = product.product_units.filter(size_id=size_id)
            s = []
            for product_unit in product_units:
                d = dict()
                d['id'] = product_unit.id
                d['final_price'] = product_unit.final_price
                d['start_price'] = product_unit.start_price
                d['delivery'] = DeliveryTypeSerializer(product_unit.delivery_type).data
                s.append(d)
            return Response(s)


        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)
        except SizeTranslationRows.DoesNotExist:
            return Response("Размер не найден", status=status.HTTP_404_NOT_FOUND)


class MinPriceForSizeView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            product_units = product.product_units.all()

            prices_by_size = {}

            # Проход по каждому элементу списка
            for item in product_units:
                size_id = item.size_id
                price = item.final_price
                available = item.availability

                # Проверка наличия размера в словаре
                if size_id not in prices_by_size:
                    prices_by_size[size_id] = []
                prices_by_size[size_id].append(price)

            min_prices_by_size = {}
            s = []

            # Вычисление минимальной цены для каждого размера
            for size_id, prices in prices_by_size.items():

                min_price = min(prices)
                d = dict()
                d['min_price'] = 0
                if len(prices) > 0:
                    d['min_price'] = min_price
                    d['size'] = SizeTranslationRowsSerializer(SizeTranslationRows.objects.get(id=size_id)).data
                    d['view_size'] = SizeTranslationRows.objects.get(id=size_id).EU
                    d['available'] = True
                else:
                    d['available'] = False
                min_prices_by_size[size_id] = d
                s.append(d)
            return Response(s)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)

class ProductUnitProductView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductUnitSerializer(product.product_units.order_by('size_id'), many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductUnitProductSlugView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductUnitSerializer(product.product_units.order_by('size_id'), many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


def product_unit_product_main(product_id, user_id):
    # authentication_classes = [JWTAuthentication]
    try:
        product = Product.objects.get(id=product_id)
        ans = ProductSerializer(product).data
        if user_id > 0:
            try:
                wishlist = Wishlist.objects.get(user_id=user_id)
                ans['in_wishlist'] = wishlist.products.filter(product_id=product_id)
            except Wishlist.DoesNotExist:
                ans['in_wishlist'] = False
        return ans
    except Product.DoesNotExist:
        return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductUnitProductMainView(APIView):
    # authentication_classes = [JWTAuthentication]

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
