from django.shortcuts import render
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
from django.utils.module_loading import import_string
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings

from shipping.views import ProductUnitProductMainView

import requests


class UserInfoView(APIView):
    def get(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            return Response(UserSerializer(User.objects.get(id=user_id)).data)
        return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


class UserRegister(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = None
    _serializer_class = api_settings.TOKEN_OBTAIN_SERIALIZER

    www_authenticate_realm = "api"

    def get_serializer_class(self):
        """
        If serializer_class is set, use it directly. Otherwise get the class from settings.
        """

        if self.serializer_class:
            return self.serializer_class
        try:
            return import_string(self._serializer_class)
        except ImportError:
            msg = "Could not import serializer '%s'" % self._serializer_class
            raise ImportError(msg)

    def get_authenticate_header(self, request):
        return '{} realm="{}"'.format(
            AUTH_HEADER_TYPES[0],
            self.www_authenticate_realm,
        )

    def post(self, request, *args, **kwargs):
        # _serializer_class = api_settings.TOKEN_OBTAIN_SERIALIZER
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
        log_data = {'username': data["username"],
                    'password': data['password']}

        serializer = self.get_serializer(data=log_data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# последние 7 просмотренных товаров пользователя
class UserLastSeenView(APIView):
    def get(self, request, user_id):
        def s_id(product):
            return product_unit_product_main(product['id'], user_id)

        if request.user.id == user_id or request.user.is_staff:
            s = list(map(s_id, list(
                ProductSerializer(User.objects.filter(id=user_id)[0].last_viewed_products, many=True).data[-7:])))
            return Response(s)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


class UserAddressView(APIView):
    def get(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            return Response(AddressInfoSerializer(User.objects.get(id=user_id).address.all(), many=True).data)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)
