from django.shortcuts import render
from rest_framework.views import APIView
from promotions.models import Bonuses
from .serializers import UserSerializer, UserSizeSerializer
from products.serializers import ProductSerializer, ProductMainPageSerializer
from .models import User, Gender
from rest_framework import exceptions
from products.models import Product, Brand
from django.db import models
from sellout.settings import URL
from shipping.views import product_unit_product_main
import json
from shipping.models import AddressInfo
from shipping.serializers import AddressInfoSerializer
from wishlist.models import Wishlist
from orders.models import ShoppingCart
from django.utils.module_loading import import_string
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES, JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from .tools import check_adress

from shipping.views import ProductUnitProductMainView

import requests


class UserSizeInfo(APIView):
    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            return Response(UserSizeSerializer(user).data)
        except User.DoesNotExist:
            return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        data = json.loads(request.body)
        user = User.objects.get(id=request.user.id)

        # Assuming the data dictionary contains the necessary fields for sizes, height, and weight
        preferred_shoes_size_row_id = data.get('preferred_shoes_size_table')
        preferred_clothes_size_row_id = data.get('preferred_clothes_size_table')
        shoes_size_id = data.get('shoes_size')
        clothes_size_id = data.get('clothes_size')
        height = data.get('height')
        weight = data.get('weight')

        if preferred_shoes_size_row_id is not None:
            user.preferred_shoes_size_row_id = preferred_shoes_size_row_id
        if preferred_clothes_size_row_id is not None:
            user.preferred_clothes_size_table_id = preferred_clothes_size_row_id
        if shoes_size_id is not None:
            user.shoes_size_id = shoes_size_id
        if clothes_size_id is not None:
            user.clothes_size_id = clothes_size_id
        if height is not None:
            user.height = height
        if weight is not None:
            user.weight = weight

        user.save()

        return Response(UserSizeSerializer(user).data, status=status.HTTP_201_CREATED)




class UserInfoView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, user_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                user = User.objects.get(id=user_id)
                return Response(UserSerializer(user).data)
            else:
                return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, user_id):
        try:
            genders = {'male': 1, "female": 2}
            user = User.objects.get(id=user_id)
            if user is None:
                return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)
            if request.user.id == user_id or request.user.is_staff:
                data = json.loads(request.body)
                user.username = data.get('username', user.username)
                user.first_name = data.get('first_name', user.first_name)
                user.last_name = data.get('last_name', user.last_name)
                user.email = data.get('email', user.email)
                user.phone_number = data.get("phone", user.phone_number)
                if "gender" in data:
                    user.gender_id = genders['gender']
                user.save()
                serializer = UserSerializer(user)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        try:
            data = json.loads(request.body)
            genders = {'male': 1, "female": 2}
            if User.objects.filter(username=data['username']).exists():
                return Response("Пользователь уже существует", status=status.HTTP_400_BAD_REQUEST)

            new_user = User(username=data['username'], password=data['password'], first_name=data['first_name'],
                            last_name=data['last_name'], gender_id=genders[data['gender']],
                            is_mailing_list=data['is_mailing_list'], email=data['username'], phone_number=data['phone'])
            new_user.set_password(data['password'])
            new_user.save()
            cart = ShoppingCart(user_id=new_user.id)
            wl = Wishlist(user_id=new_user.id)
            bonus = Bonuses()
            bonus.save()
            new_user.bonuses = bonus
            new_user.save()
            cart.save()
            wl.save()

            log_data = {'username': data["username"], 'password': data['password']}
            serializer = self.get_serializer(data=log_data)
            serializer.is_valid(raise_exception=True)

            return Response(serializer.validated_data, status=status.HTTP_200_OK)

        except exceptions.ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        except TokenError as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # except Exception as e:
        #     print(e)
        #     return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# последние 7 просмотренных товаров пользователя
class UserLastSeenView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if request.user.id == user_id or request.user.is_staff:
                products = Product.objects.filter(id__in=user.last_viewed_products).order_by(
                models.Case(*[models.When(id=id, then=index) for index, id in enumerate(user.last_viewed_products)])
            )
                return Response(ProductMainPageSerializer(products, many=True).data)
            else:
                return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            if product_id is not None:
                try:
                    user = User.objects.get(id=user_id)
                    product = Product.objects.get(id=product_id)
                    if product.id in user.last_viewed_products:
                        user.last_viewed_products.remove(product.id)
                    user.last_viewed_products.insert(0, product.id)
                    if len(user.last_viewed_products) > 20:
                        user.last_viewed_products = user.last_viewed_products[:20]
                    user.save()
                    return Response("Продукт успешно добавлен в список последних просмотров")
                except User.DoesNotExist:
                    return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)
                except Product.DoesNotExist:
                    return Response("Продукт не существует", status=status.HTTP_404_NOT_FOUND)
            else:
                return Response("Не указан идентификатор продукта", status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


class UserAddressView(APIView):
    authentication_classes = [JWTAuthentication]



    def get(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            return Response(AddressInfoSerializer(User.objects.get(id=user_id).address.all(), many=True).data)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)

    def post(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            data = json.loads(request.body)
            address_info = check_adress(data['address'])
            if address_info:
                address = AddressInfo(name=data['name'], address=address_info['value'], post_index=data['post_index'], other_info=address_info)
            else:
                address = AddressInfo(name=data['name'], address=data['address'], post_index=data['post_index'])

            address.save()
            request.user.address.add(address)


            if data['is_main']:
                address.is_main = True
                address.save()
            return Response(AddressInfoSerializer(address).data)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)

    def put(self, request, user_id, address_id):
        if request.user.id == user_id or request.user.is_staff:
            try:
                address = AddressInfo.objects.get(id=address_id)
            except AddressInfo.DoesNotExist:
                return Response("Адрес не существует", status=status.HTTP_404_NOT_FOUND)

            data = json.loads(request.body)
            address.name = data.get('name', address.name)
            if 'address' in data:
                address_info = check_adress(data['address'])
                if address_info:
                    address.address = address_info['value']
                    address.other_info = address_info
                else:
                    address.address = data['address']
            address.post_index = data.get('post_index', address.post_index)
            address.is_main = data.get('is_main', address.is_main)
            address.save()

            return Response(AddressInfoSerializer(address).data)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, user_id, address_id):
        if request.user.id == user_id or request.user.is_staff:
            try:
                address = AddressInfo.objects.get(id=address_id)
            except AddressInfo.DoesNotExist:
                return Response("Адрес не существует", status=status.HTTP_404_NOT_FOUND)

            address.delete()

            return Response("Адрес успешно удален")
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


class UserChangePassword(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            data = json.loads(request.body)
            user = User.objects.get(id=request.user.id)

            user.set_password(data['password'])
            user.save()

            return Response("Пароль успешно изменен")
        except KeyError as e:
            return Response(f"Отсутствует обязательное поле: {str(e)}", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# класс из джанго
class TokenViewBase(generics.GenericAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = None
    _serializer_class = ""

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
        serializer = self.get_serializer(data=json.loads(request.body))

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class UserLoginView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """

    _serializer_class = api_settings.TOKEN_OBTAIN_SERIALIZER


class TokenVerifyView(TokenViewBase):
    """
    Takes a token and indicates if it is valid.  This view provides no
    information about a token's fitness for a particular use.
    """

    _serializer_class = api_settings.TOKEN_VERIFY_SERIALIZER


class TokenRefreshView(TokenViewBase):
    """
    Takes a refresh type JSON web token and returns an access type JSON web
    token if the refresh token is valid.
    """

    _serializer_class = api_settings.TOKEN_REFRESH_SERIALIZER


class AddFavoriteBrands(APIView):
    def get(self, request, user_id, brand_id):
        if request.user.id == user_id or request.user.is_staff:
            try:
                user = User.objects.get(id=user_id)
                brand = Brand.objects.get(id=brand_id)
                user.favorite_brands.add(brand)
                return Response("бренд добавлен")

            except Brand.DoesNotExist:
                return Response("бренд не существует", status=status.HTTP_404_NOT_FOUND)

            except User.DoesNotExist:
                return Response("бренд не существует", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, user_id, brand_id):
        if request.user.id == user_id or request.user.is_staff:
            try:
                user = User.objects.get(id=user_id)
                brand = Brand.objects.get(id=brand_id)
                user.favorite_brands.remove(brand)
                return Response("бренд удален")

            except Brand.DoesNotExist:
                return Response("бренд не существует", status=status.HTTP_404_NOT_FOUND)

            except User.DoesNotExist:
                return Response("бренд не существует", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)
