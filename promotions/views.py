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
                cart.promo_code = None
                cart.total()
                return Response({
                    "final_amount": cart.final_amount,
                    "message": "Промокод не найден", "status": False,
                    "promo_sale": 0,
                    "promo_code": "",
                    "promo_bonus": 0,
                    "bonus": cart.bonus})


            check = promo.check_promo(cart)

            if check["status"]:
                cart.promo_code = promo
                cart.total()
                print({
                    "final_amount": cart.final_amount,
                    "message": check["message"], "status": True,
                    "promo_sale": check["promo_sale"],
                    "promo_code": promo.string_representation,
                    "promo_bonus": check['promo_bonus'],
                    "bonus": cart.bonus})
            return Response({
                    "final_amount": cart.final_amount,
                    "message": check["message"], "status": True,
                    "promo_sale": check["promo_sale"],
                    "promo_code": promo.string_representation,
                    "promo_bonus": check['promo_bonus'],
                    "bonus": cart.bonus})

        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            data = json.loads(request.body)
            cart = ShoppingCart.objects.get(user_id=user_id)
            cart.promo_code = None
            cart.save()
            return Response(
                {"final_amount": cart.final_amount, "message": "", "status": False, "total_sale": cart.total_sale,
                 'promo_bonus': 0})
        return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


class PromocodeAnonView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        data = json.loads(request.body)
        text = data['promo']
        list_unit = data["product_unit_list"]
        if "" in list_unit:
            list_unit.remove("")
        s_product_unit = list_unit
        s_id = [s.strip() for s in s_product_unit if s.strip()]

        product_units = ProductUnit.objects.filter(id__in=s_id)
        sum = 0
        sale = 0
        bonus = 0
        max_bonus = 0
        for product_unit in product_units:
            update_price(product_unit.product)
            price = {"start_price": product_unit.start_price, "final_price": product_unit.final_price,
                     "bonus": product_unit.bonus}
            sum += price['start_price']
            sale += price['start_price'] - price['final_price']
            bonus += price['bonus']
            max_bonus = max(max_bonus, bonus)

        try:
            promo = PromoCode.objects.get(string_representation=text.upper())
        except:
            return Response(
                {"final_amount": sum - sale, "message": "Промокод не найден", "status": False, "sale": sale,
                 "promo_sale": 0, 'promo_bonus': 0, "bonus": bonus})
        check = promo.check_anon_promo(sum - sale)

        if check['status']:
            final_amount = sum - sale - check['promo_sale']
            if check["promo_bonus"] > 0:
                bonus -= max_bonus

            return Response({
                "final_amount": final_amount,
                "message": check["message"], "status": True,
                "promo_sale": check["promo_sale"],
                "promo_code": promo.string_representation,
                "promo_bonus": check['promo_bonus'],
                "bonus": bonus})
        else:
            return Response({"final_amount": sum, "message": check[1], "status": False, "sale": sale,
                             "promo_sale": 0, 'promo_bonus': 0, "bonus": bonus})
