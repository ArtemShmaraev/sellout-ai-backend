import datetime
import json

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.models import ShoppingCart
from rest_framework_simplejwt.authentication import JWTAuthentication

from products.formula_price import formula_price
from products.tools import update_price
from shipping.models import ProductUnit
from users.models import UserStatus
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
                return Response({"final_amount": cart.final_amount, "message": "Промокод не найден", "status": False})
            check = check_promo(promo, user_id)

            if check[0]:
                promo = check[2]
                cart.promo_code = promo
                cart.total()
                return Response({"final_amount": cart.final_amount, "message": "Промокод применен", "status": True})
            return Response({"final_amount": cart.final_amount, "message": check[1], "status": False})
        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            data = json.loads(request.body)
            cart = ShoppingCart.objects.get(user_id=user_id)
            cart.promo_code = None
            cart.save()
            return Response({"final_amount": cart.final_amount, "message": "", "status": False})
        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


class PromocodeAnonView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = json.loads(request.body)
        text = data['promo']
        s_product_unit = data["product_unit_list"]
        product_units = ProductUnit.objects.filter(id__in=s_product_unit)
        sum = 0
        sale = 0
        for product_unit in product_units:
            update_price(product_unit.product)
            price = {"start_price": product_unit.start_price, "final_price": product_unit.final_price}
            sum += price['start_price']
            sale += price['start_price'] - price['final_price']

        try:
            promo = PromoCode.objects.get(string_representation=text.upper())
        except:
            return Response({"final_amount": sum, "message": "Промокод не найден", "status": False, "total_sale": 0, "sale": sale, "promo_sale": 0})
        check = check_promo(promo)

        if check[0]:
            promo = check[2]
            if promo.discount_percentage > 0:

                final_amount = round((sum - sale) * (100 - promo.discount_percentage) // 100)
            elif promo.discount_absolute > 0:
                final_amount = round((sum - sale) - promo.discount_absolute)
            else:
                return Response({"final_amount": sum, "message": "Промокод не активен", "status": False, "sale": sale})
            return Response({"final_amount": final_amount, "message": "Промокод применен", "status": True,
                             "total_sale": sum - final_amount, "sale": sale, "promo_sale": sum - final_amount - sale})
        else:
            return Response({"final_amount": sum, "message": check[1], "status": False, "total_sale": 0, "sale": sale, "promo_sale": 0})
