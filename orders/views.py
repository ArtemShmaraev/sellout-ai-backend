import json

from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import ShoppingCart, Order, OrderUnit, Status
# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ShoppingCartSerializer, OrderSerializer
from shipping.models import ProductUnit, AddressInfo
from shipping.serializers import ProductUnitSerializer
from rest_framework import status
from promotions.models import PromoCode
from promotions.views import check_promo
from users.models import User
from .tools import get_delivery_costs, get_delivery_price, round_to_nearest


class DeliveryInfo(APIView):
    def get(self, request):

        try:
            user = User.objects.get(id=request.user.id)
            cart = ShoppingCart.objects.get(user=user)
            data = json.loads(request.body)
            if data['delivery_info'] == 0:
                return {
                    "sum_part": 0,
                    "sum_all": 0,
                    "block": False
                }

            zip = "0"
            if "address_id" in data:
                try:
                    zip = AddressInfo.objects.get(id=data['address_id']).post_index
                except AddressInfo.DoesNotExist:
                    return JsonResponse({"error": "Адрес не найден"}, status=400)

            target = data.get("target", "0")

            product_units = cart.product_units.annotate(
                delivery_days=F('delivery_type__days_max')
            )

            sorted_product_units = product_units.order_by('delivery_days')
            tec = [sorted_product_units[0]]
            sum_part = 0
            for unit in sorted_product_units[1:]:
                if abs(tec[0].delivery_days - unit.delivery_days) <= 3:
                    tec.append(unit)
                else:
                    sum_part += get_delivery_price(tec, "02743", target, zip)
                    tec = [unit]

            sum_part += get_delivery_price(tec, "02743", target, zip)
            sum_all = get_delivery_price(cart.product_units.all(), "02743", target, zip)
            res = {"sum_part": round_to_nearest(sum_part), "sum_all": round_to_nearest(sum_all), "block": False}
            if ((int(data["delivery_type"]) == 1 or int(
                    data["delivery_type"]) == 2) and product_units.count() != 1) and (sum_part != sum_all):
                res["block"] = True

            # Возвращаем успешный ответ
            return Response(res)

        except User.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=404)
        except ShoppingCart.DoesNotExist:
            return Response({"error": "Корзина пользователя не найдена"}, status=404)
        except json.JSONDecodeError:
            return Response({"error": "Ошибка разбора JSON"}, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class ChangeStatusUnit(APIView):
    def get(self, request, order_unit_id):
        if request.query_params.get("pwd") == "hjk,tju89eio[plaCVWRKDSlkj" or request.user.is_staff:
            try:
                order_unit = OrderUnit.objects.get(id=order_unit_id)
                return Response(order_unit.status.name, status=status.HTTP_200_OK)
            except OrderUnit.DoesNotExist:
                return Response("Order unit not found", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)

    def post(self, request, order_unit_id):
        if request.query_params.get("pwd") == "hjk,tju89eio[plaCVWRKDSlkj" or request.user.is_staff:
            new_status_name = json.loads(request.body).get(
                "status_name")  # Здесь предполагается, что вы передаете имя нового статуса в запросе POST
            try:
                order_unit = OrderUnit.objects.get(id=order_unit_id)
                try:
                    new_status = Status.objects.get(
                        name=new_status_name)  # Предполагается, что у вас есть модель Status для статусов
                    order_unit.status = new_status
                    order_unit.save()
                    order = order_unit.orders.first()
                    order.change_status()
                    return Response("Status changed successfully", status=status.HTTP_200_OK)
                except Status.DoesNotExist:
                    return Response("New status not found", status=status.HTTP_404_NOT_FOUND)
            except OrderUnit.DoesNotExist:
                return Response("Order unit not found", status=status.HTTP_404_NOT_FOUND)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


class ShoppingCartUser(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, user_id):
        try:
            if request.user.id == user_id or request.user.is_staff:

                shopping_cart = ShoppingCart.objects.get(user_id=user_id)
                shopping_cart.total()
                serializer = ShoppingCartSerializer(shopping_cart, context={"user_id": user_id})
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except ShoppingCart.DoesNotExist:
            return Response("Корзина не найдена", status=status.HTTP_404_NOT_FOUND)

    def post(self, request, user_id, product_unit_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                product_unit = get_object_or_404(ProductUnit, id=product_unit_id)
                shopping_cart = get_object_or_404(ShoppingCart, user_id=user_id)
                shopping_cart.product_units.add(product_unit)
                shopping_cart.unit_order.append(product_unit_id)
                shopping_cart.total()
                serializer = ProductUnitSerializer(product_unit)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except ProductUnit.DoesNotExist:
            return Response("ProductUnit не найден", status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, user_id, product_unit_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                product_unit = get_object_or_404(ProductUnit, id=product_unit_id)
                shopping_cart = get_object_or_404(ShoppingCart, user_id=user_id)
                shopping_cart.product_units.remove(product_unit)
                shopping_cart.unit_order.remove(product_unit_id)
                shopping_cart.total()
                serializer = ProductUnitSerializer(product_unit)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except ProductUnit.DoesNotExist:
            return Response("ProductUnit не найден", status=status.HTTP_404_NOT_FOUND)

    def put(self, request, user_id, product_unit_id, new_product_unit_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                product_unit = get_object_or_404(ProductUnit, id=product_unit_id)
                shopping_cart = get_object_or_404(ShoppingCart, user_id=user_id)
                shopping_cart.product_units.remove(product_unit)
                s = shopping_cart.unit_order
                shopping_cart.unit_order = [new_product_unit_id if x == product_unit_id else x for x in s]
                shopping_cart.total()
                serializer = ProductUnitSerializer(product_unit)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except ProductUnit.DoesNotExist:
            return Response("ProductUnit не найден", status=status.HTTP_404_NOT_FOUND)


class UseBonus(APIView):

    def post(self, request, user_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                bonus = int(json.loads(request.body)["bonus"])
                cart = ShoppingCart.objects.get(user_id=user_id)
                if bonus <= cart.user.bonuses.total_amount:
                    cart.bonus_sale = bonus
                    cart.save()
                    return Response("Бонусы списаны")
                else:
                    return Response("Недостаточно бонусов", status=status.HTTP_403_FORBIDDEN)
        except ShoppingCart.DoesNotExist:
            return Response("Пользователь не найден", status=status.HTTP_404_NOT_FOUND)


class CheckOutView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request, user_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                cart = ShoppingCart.objects.get(user_id=user_id)
                data = json.loads(request.body)
                # print(data)
                user = get_object_or_404(User, id=user_id)

                order = Order(user=user, total_amount=cart.total_amount, final_amount=cart.final_amount,
                              promo_code=cart.promo_code,
                              email=data['email'], phone=data['phone'],
                              name=data['name'], surname=data['surname'], patronymic=data['patronymic'],
                              status=Status.objects.get(name="Ожидает подтверждения"), fact_of_payment=False,
                              promo_sale=cart.promo_sale,
                              bonus_sale=cart.bonus_sale, total_sale=cart.total_sale, comment=data['comment'])
                if "address_id" in data:
                    order.address = get_object_or_404(AddressInfo, id=data['address_id'])
                else:
                    order.pvz = data.get('target', 0)
                order.save()

                for unit in cart.product_units.all():
                    order.add_order_unit(unit)
                order.promo_sale = cart.promo_sale
                order.bonus_sale = cart.bonus_sale
                if order.bonus_sale > 0:
                    cart.user.bonuses.deduct_bonus(order.bonus_sale)
                order.get_delivery(data)
                order.final_amount += round_to_nearest(order.delivery_price)
                order.save()

                serializer = OrderSerializer(order)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response("Пользователь не найден", status=status.HTTP_404_NOT_FOUND)
        except AddressInfo.DoesNotExist:
            return Response("Адрес не найден", status=status.HTTP_404_NOT_FOUND)


class AllOrdersView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        if request.query_params.get("pwd") == "hjk,tju89eio[plaCVWRKDSlkj":
            order_status = request.query_params.get("status")
            orders = Order.objects.all()
            if order_status:
                orders = Order.objects.filter(status__name=order_status)
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)


class UserOrdersView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, user_id):
        try:
            if request.user.id == user_id or request.user.is_staff:
                orders = Order.objects.filter(user_id=user_id)
                serializer = OrderSerializer(orders, many=True)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except User.DoesNotExist:
            return Response("Пользователь не найден", status=status.HTTP_404_NOT_FOUND)


class OrderView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if request.user.id == order.user.id or request.user.is_staff:
                serializer = OrderSerializer(order)
                return Response(serializer.data)
            else:
                return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
        except Order.DoesNotExist:
            return Response("Заказ не найден", status=status.HTTP_404_NOT_FOUND)


class ListProductUnitOrderView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request, user_id):
        if request.user.id == user_id or request.user.is_staff:
            try:
                s_product_unit = json.loads(request.body)["product_unit_list"]
                product_units = ProductUnit.objects.filter(id__in=s_product_unit)
                cart = ShoppingCart.objects.get(user_id=user_id)
                for product_unit in product_units:
                    cart.product_units.add(product_unit)
                    if product_unit.id not in cart.unit_order:
                        cart.unit_order.append(product_unit.id)
                cart.total()
                return Response(cart.product_units.values_list('id', flat=True))
            except json.JSONDecodeError:
                return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
            except ProductUnit.DoesNotExist:
                return Response("One or more product units do not exist", status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("Доступ запрещён", status=status.HTTP_403_FORBIDDEN)
