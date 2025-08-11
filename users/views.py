import base64
import hashlib
from datetime import datetime, timedelta

from django.core import signing
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.hashers import check_password, make_password
from .serializers import UserSerializer, UserSizeSerializer
from products.serializers import ProductSerializer, ProductMainPageSerializer, SizeTableSerializer, BrandSerializer
from .models import User, Gender, EmailConfirmation, UserStatus
from rest_framework import exceptions
from products.models import Product, Brand, SizeTable, SizeTranslationRows
from django.db import models
from shipping.views import product_unit_product_main
import json
from shipping.models import AddressInfo, ProductUnit, ConfigurationUnit
from shipping.serializers import AddressInfoSerializer
from wishlist.models import Wishlist
from orders.models import ShoppingCart
from django.utils.module_loading import import_string
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import AUTH_HEADER_TYPES, JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from .tools import check_adress, register_user

from shipping.views import ProductUnitProductMainView
from sellout.settings import HOST, FRONTEND_HOST, CACHE_TIME
import requests
from rest_framework.views import APIView
from rest_framework.response import Response

from users.tools import secret_password
from django.shortcuts import redirect
from sellout.settings import GOOGLE_OAUTH2_KEY, GOOGLE_OAUTH2_SECRET



class LoyaltyProgram(APIView):
    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            res = {"bonuses": user.bonuses.total_amount, "status_name": user.user_status.name, "total": user.total_amount_order()}

            statuses = UserStatus.objects.filter(base=True).order_by("total_orders_amount")
            user_total = res['total']
            new_level = 0
            if user.user_status.base:
                for status in statuses:
                    if status.total_orders_amount > user_total:
                        new_level = status.total_orders_amount - user_total
                        break

            res["until_next_status"] = new_level
            res["number_card"] = str(user.id).zfill(4)[-4:]
            return Response(res)
        except ObjectDoesNotExist as e:
            # Обработка исключения ObjectDoesNotExist (например, если объект не существует)
            return Response({"error": str(e)}, status=404)
        except Exception as e:
            # Общая обработка других исключений
            return Response({"error": str(e)}, status=500)




class WaitList(APIView):
    def get(self, request):
        try:

            user = User.objects.get(id=request.user.id)
            wait_list = user.wait_list.values_list("id", flat=True)
            return Response(wait_list)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, product_id):
        try:
            data = json.loads(request.body)
            size = data.get("size", [])
            user = User.objects.get(id=request.user.id)
            product = Product.objects.get(id=product_id)
            sizes = SizeTranslationRows.objects.filter(id__in=size)
            for size in sizes:
                config = ConfigurationUnit.objects.get_or_create(product=product, size=size)[0]
                user.wait_list.add(config)
            user.save()
            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except ProductUnit.DoesNotExist:
            return Response({"error": "ProductUnit not found."}, status=status.HTTP_404_NOT_FOUND)


class SendVerifyEmail(APIView):
    def get(self, request, user_id):
        url = request.GET.get("url")
        user = User.objects.get(id=user_id)
        email_confirmation = EmailConfirmation.objects.get(user=user)
        check = f"https://{FRONTEND_HOST}/email_confirmed/{email_confirmation.token}?url={url}"
        url = "https://sellout.su/mail/send_customer_service_mail/"
        recipient_email = user.email
        body = check

        params = {
            "recipient_email": recipient_email,
            "body": body
        }
        requests.get(url, params=params)
        return Response("ok")


def confirm_email(request, token):
    try:
        url = request.GET.get("url")
        email = signing.loads(token)
        user = User.objects.filter(email=email).first()
        user.verify_email = True
        user.save()
        # Опционально: Удаляйте запись о подтверждении из базы данных
        # if url != None:
        #     return redirect(url)  # Перенаправление на страницу с подтверждением
        return redirect(f"https://{FRONTEND_HOST}/email_success")
    except signing.BadSignature:
        return redirect(f'https://{FRONTEND_HOST}/email_invalid')  # Перенаправление на страницу с ошибкой


class SendSetPassword(APIView):
    def get(self, request, email):
        try:
            user = User.objects.get(email=email)
            # Генерируйте токен и преобразуйте его в строку
            token = default_token_generator.make_token(user)
            # Преобразуйте идентификатор пользователя в строку и закодируйте его
            uid_str = str(user.pk)
            uidb64 = urlsafe_base64_encode(force_bytes(uid_str))

            # Создайте ссылку с токеном и идентификатором пользователя
            reset_password_link = f"https://{FRONTEND_HOST}/reset-password/{uidb64}/{token}"
            url = "https://sellout.su/mail/send_customer_service_mail/"
            recipient_email = user.email
            body = reset_password_link

            params = {
                "recipient_email": recipient_email,
                "body": body
            }

            requests.get(url, params=params)
            return Response("ok")

        except User.DoesNotExist:
            return Response("Пользователь не найден.", status=status.HTTP_404_NOT_FOUND)


class UserChangePasswordLK(APIView):

    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            data = json.loads(request.body)

            old_password = data.get('old_password', '').strip()
            new_password = data.get('new_password', '').strip()

            if not old_password or not new_password:
                return Response("Не указаны старый или новый пароль.", status=status.HTTP_400_BAD_REQUEST)

            if not check_password(old_password, user.password):
                return Response("Старый пароль указан неверно.", status=status.HTTP_400_BAD_REQUEST)

            user.set_password(new_password)
            user.save()

            return Response("Пароль успешно изменен.")
        except User.DoesNotExist:
            return Response("Пользователь не найден.", status=status.HTTP_404_NOT_FOUND)
        except json.JSONDecodeError:
            return Response("Неверный формат JSON.", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserChangePassword(generics.GenericAPIView):
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

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError):
            return Response("Ошибка", status=status.HTTP_400_BAD_REQUEST)

        try:
            if default_token_generator.check_token(user, token.strip()):
                data = json.loads(request.body)
                user.set_password(data.get('password', '').strip())
                user.save()
                log_data = {'username': user.username, 'password': data['password']}
                serializer = self.get_serializer(data=log_data)
                serializer.is_valid(raise_exception=True)
                return Response(serializer.validated_data, status=status.HTTP_200_OK)
            else:
                return Response("Ошибка", status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response("Ошибка", status=status.HTTP_400_BAD_REQUEST)
        except json.JSONDecodeError:
            return Response("Ошибка", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # В этом месте можно обработать другие исключения, если необходимо
            return Response("Ошибка", status=status.HTTP_400_BAD_REQUEST)


def initiate_google_auth(request):
    # Формирование URL для авторизации
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    client_id = GOOGLE_OAUTH2_KEY  # Замените на ваш реальный клиентский ID
    # redirect_uri = "http://localhost:3000"
    redirect_uri = f"https://{FRONTEND_HOST}"
    scope = "email profile"
    response_type = "id_token"
    nonce = "1213"

    auth_url = f"{google_auth_url}?client_id={client_id}&redirect_uri={redirect_uri}&response_type={response_type}&scope={scope}&nonce={nonce}"

    # Перенаправление пользователя на URL авторизации
    return redirect(auth_url)


class GoogleAuth(generics.GenericAPIView):
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

    def get(self, request, *args, **kwargs):
        try:
            id_token = request.query_params.get('id_token')

            header_b64, payload_b64, signature_b64 = id_token.split('.')

            header = json.loads(base64.urlsafe_b64decode(header_b64 + '==').decode('utf-8'))
            payload = json.loads(base64.urlsafe_b64decode(payload_b64 + '==').decode('utf-8'))

            if payload:
                data = {}
                data['first_name'] = payload.get('given_name')
                data['last_name'] = payload.get('family_name')
                data['username'] = payload.get('email')
                data['is_mailing_list'] = False

                data['password'] = secret_password(payload.get('email'))
                if not User.objects.filter(username=data['username']).exists():
                    register_user(data)
                else:
                    user = User.objects.get(username=data['username'])
                    user.set_password(data['password'])
                    user.save()

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


class SizeTableInLK(APIView):
    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
            res = {"user_shoes_size": None,
                   "user_clothes_size": None}
            if user.shoes_size is not None:
                res["user_shoes_size"] = user.shoes_size.id
            if user.clothes_size is not None:
                res["user_clothes_size"] = user.clothes_size.id

            if user.gender:
                if user.gender.name == "M":
                    size_tables = SizeTableSerializer(
                        SizeTable.objects.filter(name__in=["Shoes_Adults", "Clothes_Men"]), many=True, context={"user": user}).data
                else:
                    size_tables = SizeTableSerializer(
                        SizeTable.objects.filter(name__in=["Shoes_Adults", "Clothes_Women"]), many=True, context={"user": user}).data
            else:
                size_tables = SizeTableSerializer(
                    SizeTable.objects.filter(name__in=["Shoes_Adults", "Clothes_Men"]), many=True, context={"user": user}).data
            res['size_tables'] = size_tables
            return Response(res)
        except User.DoesNotExist:
            return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)


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
        preferred_shoes_size_row_id = data.get('preferred_shoes_size_row')
        preferred_clothes_size_row_id = data.get('preferred_clothes_size_row')
        shoes_size_id = data.get('shoes_size')
        clothes_size_id = data.get('clothes_size')
        height = data.get('height')
        weight = data.get('weight')

        if preferred_shoes_size_row_id is not None:
            user.preferred_shoes_size_row_id = preferred_shoes_size_row_id
        if preferred_clothes_size_row_id is not None:
            user.preferred_clothes_size_row_id = preferred_clothes_size_row_id
        if shoes_size_id is not None:
            user.shoes_size_id = shoes_size_id
        if clothes_size_id is not None:
            user.clothes_size_id = clothes_size_id
        if height is not None and height != "":
            user.height = height
        if weight is not None and weight != "":
            user.weight = weight
        user.save(size_info=True)

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
                if "date" in data:
                    date_format = "%d.%m.%Y"
                    parsed_date = datetime.strptime(data['date'], date_format)
                    user.happy_birthday = parsed_date
                user.save()
                serializer = UserSerializer(user)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserForSpamEmail(APIView):
    def get(self, request):
        if request.query_params.get("pwd") == "hjk,tju89eio[plaCVWRKDSlkj" or request.user.is_staff:
            emails = User.objects.filter(is_mailing_list=True).values("email")
            return Response(emails)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


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
            if User.objects.filter(username=data['username']).exists():
                return Response("Пользователь уже существует", status=status.HTTP_400_BAD_REQUEST)
            register_user(data)

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

                s_products = user.last_viewed_products
                product_list_string = json.dumps(s_products, sort_keys=True)  # Преобразуем список в строку
                product_list_hash = hashlib.sha256(
                    product_list_string.encode('utf-8')).hexdigest()  # Получаем хеш-сумму
                # Используем хеш-сумму в качестве ключа кэша
                cache_product_key = f"last_{product_list_hash}"

                cached_data = cache.get(cache_product_key)

                if cached_data is not None:
                    products = cached_data
                else:
                    products = Product.objects.filter(id__in=user.last_viewed_products).order_by(
                        models.Case(
                            *[models.When(id=id, then=index) for index, id in enumerate(user.last_viewed_products)])
                    )
                    cache.set(cache_product_key, products, CACHE_TIME)


                return Response(ProductMainPageSerializer(products, many=True, context={
                    "wishlist": Wishlist.objects.get(
                        user=User(id=self.request.user.id)) if request.user.id else None}).data)
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
                address = AddressInfo(name=data['name'], address=address_info['value'], other_info=address_info, post_index=address_info['data']['postal_code'])
            else:
                address = AddressInfo(name=data['name'], address=data['address'])

            address.save()
            request.user.address.add(address)

            if data['is_main']:
                address.is_main = True
                address.save()

            if address.is_main:
                for ad in User.objects.get(id=user_id).address.all():
                    if ad.is_main and ad != address:
                        ad.is_main = False
                        ad.save()
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
                    address.post_index = address_info['data']['postal_code']
                else:
                    address.address = data['address']

            address.is_main = data.get('is_main', address.is_main)
            if address.is_main:
                for ad in User.objects.get(id=user_id).address.all():
                    if ad.is_main and ad != address:
                        ad.is_main = False
                        ad.save()
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

class FavoriteBrands(APIView):
    def get(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            try:
                user = User.objects.get(id=user_id)
                return Response(BrandSerializer(user.favorite_brands.all(), many=True, context={'user_id': user_id}).data)

            except User.DoesNotExist:
                return Response("бренд не существует", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("Доступ запрещен", status=status.HTTP_403_FORBIDDEN)


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
