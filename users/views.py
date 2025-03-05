from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer
from products.serializers import ProductSerializer, SizeSerializer
from .models import User, Gender
from products.models import Product
from sellout.settings import url
from shipping.views import product_unit_product_main
import json
from shipping.models import AddressInfo
from shipping.serializers import AddressInfoSerializer
from wishlist.models import Wishlist
from orders.models import ShoppingCart

from shipping.views import ProductUnitProductMainView

import requests


class UserInfoView(APIView):
    def get(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            return Response(UserSerializer(User.objects.get(id=user_id)).data)
        return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


class RegisterUser(APIView):
    def post(self, request):
        data = request.data
        genders = {'male': 1, "female": 2}
        new_user = User(username=data['username'], password=data['password'], first_name=data['first_name'],
                        last_name=data['last_name'], gender_id=genders[data['gender']])
        new_user.set_password(data['password'])
        new_user.save()
        # создание корзины и вл для пользователя
        cart = ShoppingCart(user_id=new_user.id)
        wl = Wishlist(user_id=new_user.id)
        cart.save()
        wl.save()
        return Response(requests.post(f"{url}/api/token/", data={'username': new_user.username,
                                                                 'password': data['password']}).json())


class LoginUser(APIView):
    def post(self, request):
        data = request.data
        return Response(requests.post(f"{url}/api/token/", data={'username': data['username'],
                                                                 'password': data['password']}).json())


# последние 7 просмотренных товаров пользователя
class UserLastSeenView(APIView):
    def get(self, request, user_id):
        def s_id(product):
            return product_unit_product_main(product['id'], user_id)

        if request.user.id == user_id or request.user.is_staff:
            s = list(map(s_id, list(ProductSerializer(User.objects.filter(id=user_id)[0].last_viewed_products, many=True).data[-7:])))
            return Response(s)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


class AddressUserView(APIView):
    def get(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            return Response(AddressInfoSerializer(User.objects.get(id=user_id).address.all(), many=True).data)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)



