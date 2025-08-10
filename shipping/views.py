from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

from products.tools import update_price
from users.models import User, UserStatus
from .models import ProductUnit
from .serializers import ProductUnitSerializer, DeliveryTypeSerializer
from wishlist.models import Wishlist
from products.models import Product
from products.serializers import ProductMainPageSerializer, ProductSerializer
import json
from products.formula_price import formula_price


class DeliveryForSizeView(APIView):
    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            user_status = User.objects.get(id=request.user.id).user_status if request.user.id else UserStatus.objects.get(name="Amethyst")
            update_price(product)
            view_size = json.loads(request.body)['view_size']
            product_units = product.product_units.filter(view_size_platform=view_size, availability=True)
            s = []
            for product_unit in product_units:
                d = dict()
                if user_status.base:
                    price = {"start_price": product_unit.start_price, "final_price": product_unit.final_price}
                else:
                    price = formula_price(product_unit.product, product_unit, user_status)
                d['id'] = product_unit.id
                d['final_price'] = price['final_price']
                d['start_price'] = price['start_price']
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
            update_price(product)
            user_status = User.objects.get(id=request.user.id).user_status if self.request.user.id else UserStatus.objects.get(
                name="Amethyst")

            prices_by_size = {}

            # Проход по каждому элементу списка
            for item in product_units:
                size = item.view_size_platform
                available = item.availability

                # Проверка наличия размера в словаре
                if size not in prices_by_size:
                    prices_by_size[size] = {"final_price": [], "start_price": [], "available": False,
                                            "is_fast_shipping": False, "is_sale": False, "is_return": False,
                                            "size_sellout": []}
                prices_by_size[size]["size_sellout"].extend(item.size.all().values_list("id"))

                if available:
                    prices_by_size[size]["available"] = True
                    if user_status.base:
                        price = {"start_price": item.start_price, "final_price": item.final_price}
                    else:
                        price = formula_price(item.product, item, user_status)

                    prices_by_size[size]['final_price'].append(price['final_price'])
                    prices_by_size[size]['start_price'].append(price['start_price'])

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

                min_price = prices['final_price'][0]
                min_price_without_sale = prices['start_price'][0]
                for i in range(len(prices['final_price'])):
                    if prices['final_price'][i] <= min_price:
                        min_price = prices['final_price'][i]
                        min_price_without_sale = prices['start_price'][i]
                d = dict()
                if len(prices) > 0:
                    d['min_price'] = min_price
                    d['min_price_without_sale'] = min_price_without_sale
                    d['available'] = prices['available']
                    d['is_fast_shipping'] = prices['is_fast_shipping']
                    d['is_sale'] = prices['is_sale']
                    d['is_return'] = prices['is_return']
                    d['size'] = list(set(prices["size_sellout"]))
                    d['size_for_api'] = size
                    d['view_size'] = size.replace("INT", "")

                min_prices_by_size[size] = d
                s.append(d)

            def custom_sort_key(s):
                s = str(s["view_size"]).lower()
                size_order = {
                    "xxxxxxs": "00", "6xs": "00",
                    "xxxxxs": "01", "5xs": "01",
                    "xxxxs": "02", "4xs": "02",
                    "xxxs": "03", "3xs": "03",
                    "xxs": "04", "2xs": "04",
                    "xs": "05",
                    "s": "06",
                    "m": "07",
                    "l": "08",
                    "xl": "09",
                    "xxl": "10", "2xl": "10",
                    "xxxl": "11", "3xl": "11",
                    "xxxxl": "12", "4xl": "12",
                    "xxxxxl": "13", "5xl": "13",
                    "xxxxxxl": "14", "6xl": "12",
                    "xxxxxxxl": "15", "7xl": "15",
                    "xxxxxxxxl": "16", "8xl": "16",
                    "xxxxxxxxxl": "17", "9xl": "17",
                    "xxxxxxxxxxl": "18", "10xl": "18",
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
            s_id = [s.strip() for s in s_product_unit if s.strip()]
            product_units = ProductUnit.objects.filter(id__in=s_id)

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
            user_status = User.objects.get(id=request.user.id).user_status if request.user.id else UserStatus.objects.get(
                name="Amethyst")

            sum = 0
            sale = 0
            for product_unit in product_units:
                update_price(product_unit.product)
                if user_status.base:
                    update_price(product_unit.product)
                    price = {"start_price": product_unit.start_price, "final_price": product_unit.final_price}
                else:
                    price = formula_price(product_unit.product, product_unit, user_status)
                sum += price['start_price']
                sale += price['start_price'] - price['final_price']

            return Response({"total_amount": sum, "sale": sale, "final_amount": sum-sale})
        except json.JSONDecodeError:
            return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
        except ProductUnit.DoesNotExist:
            return Response("One or more product units do not exist", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
