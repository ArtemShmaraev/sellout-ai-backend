import datetime
import json

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.models import ShoppingCart
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import PromoCode
from .tools import check_promo
from .serializers import PromoCodeSerializer


# Create your views here.





class PromocodeView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            data = json.loads(request.body)
            text = data['promo']
            cart = ShoppingCart.objects.get(user_id=user_id)
            try:
                promo = PromoCode.objects.get(string_representation=text.upper())
            except:
                return Response("Промокод не найден")
            check = check_promo(promo, user_id, cart)
            print(check)

            if check[0]:
                promo = check[2]
                cart.promo_code = promo
                cart.save()
                return Response("Промокод применен")
            return Response(check[1])


        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
