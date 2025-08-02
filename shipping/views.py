from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import ProductUnit
from .serializers import ProductUnitSerializer, DeliveryTypeSerializer
from wishlist.models import Wishlist
from products.models import Product
from products.serializers import ProductMainPageSerializer, ProductSerializer
import json


class DeliveryForSizeView(APIView):
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            view_size = json.loads(request.body)['view_size']
            product_units = product.product_units.filter(view_size_platform=view_size, availability=True)
            s = []
            for product_unit in product_units:
                d = dict()
                d['id'] = product_unit.id
                d['final_price'] = product_unit.final_price
                d['start_price'] = product_unit.start_price
                d['available'] = product_unit.availability
                d['is_fast_shipping'] = product_unit.is_fast_shipping
                d['is_sale'] = product_unit.is_sale
                d['is_return'] = product_unit.is_return
                d['delivery'] = DeliveryTypeSerializer(product_unit.delivery_type).data
                s.append(d)
            return Response(s)


        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class MinPriceForSizeView(APIView):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            product_units = product.product_units.all()

            prices_by_size = {}

            # Проход по каждому элементу списка
            for item in product_units:
                size = item.view_size_platform
                price = item.final_price
                available = item.availability

                # Проверка наличия размера в словаре
                if size not in prices_by_size:
                    prices_by_size[size] = {"price": [], "price_without_sale": [], "available": False,
                                            "is_fast_shipping": False, "is_sale": False, "is_return": False,
                                            "size_sellout": []}
                prices_by_size[size]["size_sellout"].extend(item.size.all().values_list("id"))

                if available:
                    prices_by_size[size]["available"] = True
                    prices_by_size[size]['price'].append(price)
                    prices_by_size[size]['price_without_sale'].append(item.start_price)
                    if item.is_fast_shipping:
                        prices_by_size[size]["is_fast_shipping"] = True
                    if item.is_sale:
                        prices_by_size[size]["is_sale"] = True
                    if item.is_return:
                        prices_by_size[size]["is_return"] = True

                else:
                    prices_by_size[size]['price'].append(999_999_999)
            min_prices_by_size = {}
            s = []

            # Вычисление минимальной цены для каждого размера
            for size, prices in prices_by_size.items():

                min_price = prices['price'][0]
                min_price_without_sale = prices['price_without_sale'][0]
                for i in range(len(prices['price'])):
                    if prices['price'][i] <= min_price:
                        min_price = prices['price'][i]
                        min_price_without_sale = max(min_price_without_sale, prices['price_without_sale'][i])
                d = dict()
                if len(prices) > 0:
                    d['min_price'] = min_price
                    d['min_price_without_sale'] = min_price_without_sale
                    d['available'] = prices['available']
                    d['is_fast_shipping'] = prices['is_fast_shipping']
                    d['is_sale'] = prices['is_sale']
                    d['is_return'] = prices['is_return']
                    d['size'] = list(set(prices["size_sellout"]))
                    d['view_size'] = size.replace("INT", "")
                min_prices_by_size[size] = d
                s.append(d)

            def custom_sort_key(s):
                s = s["view_size"].lower()
                size_order = {
                    "xxxxxxs": 0, "6xs": 0,
                    "xxxxxs": 1, "5xs": 1,
                    "xxxxs": 2, "4xs": 2,
                    "xxxs": 3, "3xs": 3,
                    "xxs": 4, "2xs": 4,
                    "xs": 5,
                    "s": 6,
                    "m": 7,
                    "l": 8,
                    "xl": 9,
                    "xxl": 10, "2xl": 10,
                    "xxxl": 11, "3xl": 11,
                    "xxxxl": 12, "4xl": 12,
                    "xxxxxl": 13, "5xl": 13,
                    "xxxxxxl": 14, "6xl": 12,
                    "xxxxxxxl": 15, "7xl": 15,
                    "xxxxxxxxl": 16, "8xl": 16,
                    "xxxxxxxxxl": 17, "9xl": 17,
                    "xxxxxxxxxxl": 18, "10xl": 18,
                }
                parts = []
                current_part = ''

                for char in s:
                    if char.isalpha():  # Проверяем, является ли символ буквой (размером)
                        current_part += char
                    else:
                        if current_part:
                            parts.append(size_order.get(current_part.lower(), current_part.lower()))
                            current_part = ''
                        parts.append(char)

                if current_part:
                    parts.append(size_order.get(current_part.lower(), current_part.lower()))

                return parts

            return Response(sorted(s, key=custom_sort_key))
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductUnitProductView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductUnitSerializer(product.product_units.order_by('size'), many=True)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductUnitProductSlugView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductUnitSerializer(product.product_units.order_by('size'), many=True)
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


class ListProductUnitView(APIView):
    # authentication_classes = [JWTAuthentication]
    def post(self, request):
        try:
            s_product_unit = json.loads(request.body)["product_unit_list"]
            product_units = ProductUnit.objects.filter(id__in=s_product_unit)

            serializer = ProductUnitSerializer(product_units, many=True)
            return Response(serializer.data)
        except json.JSONDecodeError:
            return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
        except ProductUnit.DoesNotExist:
            return Response("One or more product units do not exist", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TotalPriceForListProductUnitView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            s_product_unit = json.loads(request.body)["product_unit_list"]
            product_units = ProductUnit.objects.filter(id__in=s_product_unit)
            sum = 0
            for product_unit in product_units:
                sum += product_unit.final_price

            return Response({"total_amount": sum})
        except json.JSONDecodeError:
            return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
        except ProductUnit.DoesNotExist:
            return Response("One or more product units do not exist", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
