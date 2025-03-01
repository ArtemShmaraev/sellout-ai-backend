from django.shortcuts import render
from .models import Wishlist, WishlistUnit
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from products.serializers import ProductSerializer, SizeSerializer
from users.models import User
from .serializers import WishlistSerializer, WishlistUnitSerializer
from products.models import Product
from products.models import Size
from sellout.settings import url
from rest_framework import status
from shipping.views import product_unit_product_main

import requests


# информация о вишлисте пользователя
class UserWishlist(APIView):
    def get(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            wishlist = Wishlist.objects.get(user_id=user_id)
            data = WishlistUnit.objects.filter(wishlist=wishlist)
            ans = []
            for el in data:
                main = product_unit_product_main(el.product.id, user_id)
                ans.append({'id': el.id, 'product': main,
                            "size": SizeSerializer(Size.objects.get(id=el.size.id)).data,
                            'product_unit': requests.get(f"{url}/api/v1/product_unit/product/{el.product.id}").json()[0]})
            return Response(ans)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


# добавить товар в вишлист с размером
class UserAddWishlist(APIView):
    def post(self, request, user_id, product_id, size_id):
        if user_id == request.user.id or request.user.is_staff:
            wishlist_id = WishlistSerializer(Wishlist.objects.get(user=user_id)).data['id']
            wishlist = Wishlist.objects.get(id=wishlist_id)
            product = Product.objects.get(id=product_id)
            size = Size.objects.get(id=size_id)
            wl = WishlistUnit(product=product, size=size, wishlist=wishlist)
            wl.save()
            return Response(WishlistUnitSerializer(wl).data)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


# удалить товар из вишлиста по id
class UserDeleteWishlist(APIView):
    def delete(self, request, wishlist_unit_id):
        wishlist_unit = WishlistUnit.objects.get(id=wishlist_unit_id)
        user = wishlist_unit.wishlist.user
        if user.id == request.user.id or request.user.is_staff:
            data = WishlistUnitSerializer(wishlist_unit).data
            wishlist_unit.delete()
            return Response(data)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


# добавить в вишлист товар без размера
class UserAddWishlistNoSize(APIView):
    def post(self, request, user_id, product_id):
        if request.user.id == user_id or request.user.is_staff:
            wishlist_id = WishlistSerializer(Wishlist.objects.get(user=user_id)).data['id']
            wishlist = Wishlist.objects.get(id=wishlist_id)
            product = Product.objects.get(id=product_id)
            size = Size.objects.get(product_id=product_id, INT=0)
            wl = WishlistUnit(product=product, size=size, wishlist=wishlist)
            wl.save()
            return Response(WishlistUnitSerializer(wl).data)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


# Изменить размер товара, который уже в вишлитсе
class UserChangeSizeWishlist(APIView):
    def post(self, request, user_id, wishlist_unit_id, size_id):
        if user_id == request.user.id or request.user.is_staff:
            wishlist_unit = WishlistUnit.objects.get(id=wishlist_unit_id)
            wishlist_unit.size = Size.objects.get(id=size_id)
            return Response(WishlistUnitSerializer(wishlist_unit).data)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
