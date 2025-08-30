import json

from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication

from products.tools import platform_update_price
from .models import ShoppingCart, Order, OrderUnit, Status
# Create your views here.
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ShoppingCartSerializer, OrderSerializer
from shipping.models import ProductUnit, AddressInfo
from shipping.serializers import ProductUnitSerializer
from rest_framework import status
from promotions.models import PromoCode, AccrualBonus
from users.models import User, EmailConfirmation
from .tools import get_delivery_costs, get_delivery_price, round_to_nearest, send_email_confirmation_order, get_delivery
from .tools_for_user import update_user_status


class DeliveryInfo(APIView):
    def post(self, request):

        try:
            user = User.objects.get(id=request.user.id)
            cart = ShoppingCart.objects.get(user=user)
            data = json.loads(request.body)
            if str(data['delivery_type']) == "0" or (cart.final_amount > user.user_status.free_ship_amount > 0):
                print(user.user_status.name)
                return Response({
                    "sum_part": 0,
                    "sum_all": 0,
                    "block": False
                })
            zip = "0"
            if "address_id" in data:
                try:
                    zip = AddressInfo.objects.get(id=data['address_id']).post_index
                except AddressInfo.DoesNotExist:
                    return Response({"error": "Адрес не найден"}, status=400)

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
            if ((str(data["delivery_type"]) == "1" or str((data["delivery_type"])) == "2") and product_units.count() != 1) and (sum_part != sum_all):
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
                units = ProductUnit.objects.filter(id__in=shopping_cart.unit_order)
                for unit in units.all():
                    platform_update_price(unit.product)
                shopping_cart.product_units.set(units)
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
                if product_unit_id in shopping_cart.unit_order:
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

            product_unit = get_object_or_404(ProductUnit, id=product_unit_id)
            shopping_cart = get_object_or_404(ShoppingCart, user_id=user_id)
            shopping_cart.product_units.remove(product_unit)
            s = shopping_cart.unit_order
            shopping_cart.unit_order = [new_product_unit_id if x == product_unit_id else x for x in s]
            new_product_unit_id = get_object_or_404(ProductUnit, id=new_product_unit_id)
            shopping_cart.product_units.add(new_product_unit_id)
            shopping_cart.total()
            serializer = ProductUnitSerializer(product_unit)
            return Response(serializer.data)

        except ProductUnit.DoesNotExist:
            return Response("ProductUnit не найден", status=status.HTTP_404_NOT_FOUND)


class UseBonus(APIView):

    def post(self, request):
        try:
            user = request.user
            bonus = int(json.loads(request.body)["bonus"])
            cart = ShoppingCart.objects.get(user=user)
            if bonus <= cart.user.bonuses.total_amount:
                cart.bonus_sale = bonus
                cart.total()
                serializer = ShoppingCartSerializer(cart, context={"user_id": user.id})
                return Response(serializer.data)
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
                if not user.verify_email:
                    return Response("Подтвердите почту", status=status.HTTP_401_UNAUTHORIZED)

                order = Order(user=user, total_amount=cart.total_amount, final_amount=cart.final_amount,
                              promo_code=cart.promo_code,
                              email=data['email'], phone=data['phone'],
                              name=data['name'], surname=data['surname'], patronymic=data['patronymic'],
                              status=Status.objects.get(name="Заказ принят"), fact_of_payment=False,
                              promo_sale=cart.promo_sale,
                              bonus_sale=cart.bonus_sale, total_sale=cart.total_sale, comment=data.get('comment', ""), final_amount_without_shipping=cart.final_amount)
                if "address_id" in data:
                    order.address = get_object_or_404(AddressInfo, id=data['address_id'])
                else:
                    order.pvz_address = str(data.get('pvz_address', ""))
                    order.pvz = str(data.get('target', 0))
                order.save()

                if user.patronymic == "":
                    user.patronymic = data['patronymic']
                if user.phone_number == "":
                    user.phone_number = data['phone']

                for unit in cart.product_units.all():
                    order.add_order_unit(unit, user.user_status)
                if order.bonus_sale > 0:
                    cart.user.bonuses.deduct_bonus(order.bonus_sale)
                get_delivery(order, data)
                if order.final_amount <= user.user_status.free_ship_amount or not order.user.user_status.base:
                    order.final_amount += order.delivery_price

                else:
                    order.delivery_view_price = 0
                order.save()

                if user.user_status.base:
                    orders_count = Order.objects.filter(user=user).count()
                    units = order.order_units.order_by("-bonus")
                    k = 0
                    sum_bonus = 0
                    for unit in units:
                        if orders_count == 1 and k == 0:
                            sum_bonus += 1000
                        else:
                            sum_bonus += unit.bonus
                        k += 1
                    accrual_bonus = AccrualBonus(amount=sum_bonus)
                    accrual_bonus.save()
                    user.bonuses.accrual.add(accrual_bonus)
                    user.bonuses.update_total_amount()
                    user.update_user_status()

                if cart.promo_code is not None:
                    cart.promo_code.activation_count += 1
                    cart.promo_code.save()

                    if cart.promo_code.ref_promo:
                        ref_user = cart.promo_code.owner
                        ref_accrual_bonus = AccrualBonus(amount=cart.promo_sale, type="Приглашение")
                        ref_accrual_bonus.save()
                        ref_user.total_ref_bonus += cart.promo_sale
                        ref_user.bonuses.accrual.add(ref_accrual_bonus)
                        cart.user.ref_user = ref_user
                        cart.user.save()
                        ref_user.save()

                serializer = OrderSerializer(order).data
                send_email_confirmation_order(serializer, order.email)
                cart.clear()
                return Response(serializer)
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
                orders = Order.objects.filter(user_id=user_id).order_by("-id")
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
                s_id = [s.strip() for s in s_product_unit if s.strip()]
                product_units = ProductUnit.objects.filter(id__in=s_id)
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
