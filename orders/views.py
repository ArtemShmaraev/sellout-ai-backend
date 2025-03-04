from django.shortcuts import render
from .models import ShoppingCart, Order
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ShoppingCartSerializer, OrderSerializer
from shipping.models import ProductUnit
from shipping.serializers import ProductUnitSerializer
from rest_framework import status
from promotions.models import PromoCode
from promotions.views import check_promo
from users.models import User


class ShoppingCartUser(APIView):
    def get(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            return Response(ShoppingCartSerializer(ShoppingCart.objects.get(user_id=user_id)).data)
        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


class ShoppingCartAddProductUnit(APIView):
    def post(self, request, user_id, product_unit_id):
        if request.user.id == user_id or request.user.is_staff:
            product_unit = ProductUnit.objects.get(id=product_unit_id)
            ShoppingCart.objects.get(user_id=user_id).product_units.add(product_unit)
            return Response(ProductUnitSerializer(product_unit).data)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
''

class ShoppingCartDelProductUnit(APIView):
    def delete(self, request, user_id, product_unit_id):
        if request.user.id == user_id or request.user.is_staff:
            product_unit = ProductUnit.objects.get(id=product_unit_id)
            ShoppingCart.objects.get(user_id=user_id).product_units.remove(product_unit)
            return Response(ProductUnitSerializer(product_unit).data)
        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


class CheckOutView(APIView):
    def post(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            data = request.data
            order = Order(user=User.objects.get(id=user_id),
                          # product_unit=pr_unit,
                          total_amount=data['total_amount'],
                          email=data['email'],
                          tel=data['tel'],
                          name=data['first_name'],
                          surname=data['last_name'],
                          address_id=data['address_id'],
                          status_id=1,
                          fact_of_payment=False)
            check, promo = check_promo(data["promo_code"], user_id)
            if check:
                order.promo_code = PromoCode.objects.get(string_representation=data["promo_code"])
            order.save()
            units = data['product_unit']
            for unit in units:
                order.product_unit.add(ProductUnit.objects.get(id=unit))
            order.save()
            return Response(OrderSerializer(order).data)
        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


class AllOrdersView(APIView):
    def get(self, request):
        if request.user.is_staff:
            return Response(OrderSerializer(Order.objects.all(), many=True).data)
        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


class UserOrdersView(APIView):
    def get(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            return Response(OrderSerializer(Order.objects.filter(user_id=user_id), many=True).data)
        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


class OrderView(APIView):
    def get(self, request, order_id):
        id = Order.objects.get(id=order_id).user.id
        if request.user.id == id or request.user.is_staff:
            return Response(OrderSerializer(Order.objects.filter(id=order_id), many=True).data)
        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)



