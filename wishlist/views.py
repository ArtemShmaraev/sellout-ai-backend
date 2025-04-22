from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Wishlist
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import WishlistSerializer
from products.models import Product
from sellout.settings import URL
from rest_framework import status
from users.models import User
from products.serializers import ProductSerializer, ProductMainPageSerializer

import requests


# информация о вишлисте пользователя
# информация о вишлисте пользователя
class UserWishlist(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)

            # Проверяем, имеет ли пользователь право просматривать список желаний
            if not (request.user.id == user_id or request.user.is_staff):
                return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)

            wishlist_products = Wishlist.objects.get(user=user).products
            return Response(ProductMainPageSerializer(wishlist_products, many=True, context={'user_id': user_id}).data)
        except User.DoesNotExist:
            return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id, product_id):
        if request.user.id == user_id or request.user.is_staff:
            if product_id is not None:
                try:
                    user = User.objects.get(id=user_id)
                    product = Product.objects.get(id=product_id)
                    wishlist = Wishlist.objects.get(user=user)
                    wishlist.products.add(product)

                    return Response(
                        ProductMainPageSerializer(wishlist.products, many=True, context={'user_id': user_id}).data)
                except User.DoesNotExist:
                    return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)
                except Product.DoesNotExist:
                    return Response("Продукт не существует", status=status.HTTP_404_NOT_FOUND)
            else:
                return Response("Не указан идентификатор продукта", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, user_id, product_id):
        try:
            # Проверяем, имеет ли пользователь право удалять элемент из списка желаний
            if not (request.user.id == user_id or request.user.is_staff):
                return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)

            # Проверяем, существует ли элемент списка желаний
            wishlist = Wishlist.objects.get(user_id=user_id)
            product = Product.objects.get(id=product_id)
            if product not in wishlist.products.all():
                raise Product.DoesNotExist
            wishlist.products.remove(product)

            return Response("Элемент успешно удален из списка желаний")
        except User.DoesNotExist:
            return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response("Элемент списка желаний не существует", status=status.HTTP_404_NOT_FOUND)

# добавить товар в вишлист с размером
# class UserAddWishlist(APIView):
#     def post(self, request, user_id, product_id, size_id):
#         if user_id == request.user.id or request.user.is_staff:
#             wishlist_id = WishlistSerializer(Wishlist.objects.get(user=user_id)).data['id']
#             wishlist = Wishlist.objects.get(id=wishlist_id)
#             product = Product.objects.get(id=product_id)
#             size = SizeTranslationRows.objects.get(id=size_id)
#             wl = WishlistUnit(product=product, size=size, wishlist=wishlist)
#             wl.save()
#             return Response(WishlistUnitSerializer(wl).data)
#         else:
#             return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
#
#
# # удалить товар из вишлиста по id
# class UserDeleteWishlist(APIView):
#     def delete(self, request, wishlist_unit_id):
#         wishlist_unit = WishlistUnit.objects.get(id=wishlist_unit_id)
#         user = wishlist_unit.wishlist.user
#         if user.id == request.user.id or request.user.is_staff:
#             data = WishlistUnitSerializer(wishlist_unit).data
#             wishlist_unit.delete()
#             return Response(data)
#         else:
#             return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


# # добавить в вишлист товар без размера
# class UserAddWishlistNoSize(APIView):
#     def post(self, request, user_id, product_id):
#         if request.user.id == user_id or request.user.is_staff:
#             wishlist_id = WishlistSerializer(Wishlist.objects.get(user=user_id)).data['id']
#             wishlist = Wishlist.objects.get(id=wishlist_id)
#             product = Product.objects.get(id=product_id)
#             wl = WishlistUnit(product=product, wishlist=wishlist)
#             wl.save()
#             return Response(WishlistUnitSerializer(wl).data)
#         else:
#             return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


# Изменить размер товара, который уже в вишлитсе
# class UserChangeSizeWishlist(APIView):
#     def post(self, request, user_id, wishlist_unit_id, size_id):
#         if user_id == request.user.id or request.user.is_staff:
#             wishlist_unit = WishlistUnit.objects.get(id=wishlist_unit_id)
#             wishlist_unit.size = SizeTranslationRows.objects.get(id=size_id)
#             return Response(WishlistUnitSerializer(wishlist_unit).data)
#         else:
#             return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
