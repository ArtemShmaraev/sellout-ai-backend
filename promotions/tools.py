import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PromoCodeSerializer



def check_promo(promo, user_id, cart):
    try:
        if promo.activation_count >= promo.max_activation_count:
            return 0, Response("Промокод закончился")
        if promo.active_status and promo.active_until_date >= datetime.date.today():
            return 1, Response(PromoCodeSerializer(promo).data), promo
        else:
            return 0, Response("Промокод неактивен")
    except:
        return 0, Response("Промокод не найден")