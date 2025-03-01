import datetime

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PromoCode
from .serializers import PromoCodeSerializer
# Create your views here.


def check_promo(text, user_id):
    try:
        promo = PromoCode.objects.get(string_representation=text)
        if promo.activation_count >= promo.max_activation_count:
            return 0, Response("Промокод закончился")
        if promo.active_status and promo.active_until_date >= datetime.date.today():
            promo.activation_count += 1
            promo.save()
            return 1, Response(PromoCodeSerializer(promo).data)
        else:
            return 0, Response("Промокод неактивен")
    except:
        return 0, Response("Промокод не найден")

class PromocodeView(APIView):
    def post(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            data = request.data
            text = data['promo_code']

            return check_promo(text, user_id)[1]

        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)