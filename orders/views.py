from django.shortcuts import render
from .models import ShoppingCart
# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ShoppingCartSerializer
from shipping.models import ProductUnit
from shipping.serializers import ProductUnitSerializer
from rest_framework import status
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