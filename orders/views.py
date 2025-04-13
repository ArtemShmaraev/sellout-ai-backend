import json

from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import ShoppingCart, Order
# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ShoppingCartSerializer, OrderSerializer
from shipping.models import ProductUnit, AddressInfo
from shipping.serializers import ProductUnitSerializer
from rest_framework import status
from promotions.models import PromoCode
from promotions.views import check_promo
from users.models import User





class ShoppingCartUser(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, user_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                shopping_cart = ShoppingCart.objects.get(user_id=user_id)
                serializer = ShoppingCartSerializer(shopping_cart)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except ShoppingCart.DoesNotExist:
            return Response("Корзина не найдена", status=status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id, product_unit_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                product_unit = get_object_or_404(ProductUnit, id=product_unit_id)
                shopping_cart = get_object_or_404(ShoppingCart, user_id=user_id)
                shopping_cart.product_units.add(product_unit)
                serializer = ProductUnitSerializer(product_unit)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except ProductUnit.DoesNotExist:
            return Response("ProductUnit не найден", status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id, product_unit_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                product_unit = get_object_or_404(ProductUnit, id=product_unit_id)
                shopping_cart = get_object_or_404(ShoppingCart, user_id=user_id)
                shopping_cart.product_units.remove(product_unit)
                serializer = ProductUnitSerializer(product_unit)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except ProductUnit.DoesNotExist:
            return Response("ProductUnit не найден", status=status.HTTP_404_NOT_FOUND)


class CheckOutView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request, user_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                data = json.loads(request.body)
                user = get_object_or_404(User, id=user_id)
                address = get_object_or_404(AddressInfo, id=data['address_id'])

                order = Order(user=user, total_amount=data['total_amount'],
                              email=data['email'], tel=data['tel'],
                              name=data['first_name'], surname=data['last_name'],
                              address=address, status_id=1, fact_of_payment=False)

                check, promo = check_promo(data["promo_code"], user_id)
                if check:
                    promo_code = get_object_or_404(PromoCode, string_representation=data["promo_code"])
                    order.promo_code = promo_code

                order.save()

                units = data['product_unit']
                for unit in units:
                    product_unit = get_object_or_404(ProductUnit, id=unit)
                    order.product_unit.add(product_unit)

                serializer = OrderSerializer(order)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response("Пользователь не найден", status=status.HTTP_404_NOT_FOUND)
        except AddressInfo.DoesNotExist:
            return Response("Адрес не найден", status=status.HTTP_404_NOT_FOUND)


class AllOrdersView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        if request.user.is_staff:
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


class UserOrdersView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, user_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                orders = Order.objects.filter(user_id=user_id)
                serializer = OrderSerializer(orders, many=True)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response("Пользователь не найден", status=status.HTTP_404_NOT_FOUND)


class OrderView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if request.user.id == order.user.id or request.user.is_staff:
                serializer = OrderSerializer(order)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except Order.DoesNotExist:
            return Response("Заказ не найден", status=status.HTTP_404_NOT_FOUND)


class ListProductUnitOrderView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            try:
                s_product_unit = json.loads(request.body)["product_unit_list"]
                product_units = ProductUnit.objects.filter(id__in=s_product_unit)
                cart = ShoppingCart.objects.get(user_id=user_id)
                for product_unit in product_units:
                    cart.product_units.add(product_unit)
                return Response("Корзина обновлена")
            except json.JSONDecodeError:
                return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
            except ProductUnit.DoesNotExist:
                return Response("One or more product units do not exist", status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
