from django.db import models
from django.conf import settings
from django.db.models import F

from promotions.tools import check_promo
from django.utils import timezone

from shipping.models import AddressInfo
from .tools import get_delivery_costs, get_delivery_price, round_to_nearest
from products.formula_price import formula_price

class Status(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False)

    def __str__(self):
        return self.name


def get_default_status():
    default_object = Status.objects.get_or_create(name="Ожидает подтверждения")[0]
    return default_object.pk


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False, blank=False,
                             related_name="orders")
    order_units = models.ManyToManyField("OrderUnit", blank=True, related_name="orders")
    total_amount = models.IntegerField(default=0)
    final_amount = models.IntegerField(default=0)
    final_amount_without_shipping = models.IntegerField(default=0)
    email = models.EmailField(null=False, blank=False)
    phone = models.CharField(max_length=20, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    surname = models.CharField(max_length=100, null=False, blank=False)
    patronymic = models.CharField(max_length=100, default="")
    delivery = models.CharField(max_length=100, default="")
    delivery_price = models.IntegerField(default=0)
    delivery_view_price = models.IntegerField(default=0)
    groups_delivery = models.JSONField(default=list)
    address = models.ForeignKey("shipping.AddressInfo", on_delete=models.PROTECT, related_name="orders", null=True,
                                blank=True)
    pvz = models.CharField(default="", max_length=100)
    promo_code = models.ForeignKey("promotions.PromoCode", on_delete=models.PROTECT, blank=True, null=True,
                                   related_name="orders")
    sale = models.IntegerField(default=0)
    bonus_sale = models.IntegerField(default=0)
    promo_sale = models.IntegerField(default=0)
    total_sale = models.IntegerField(default=0)
    status = models.ForeignKey("Status", on_delete=models.SET_DEFAULT, null=False, blank=False,
                               related_name="orders", default=get_default_status())
    payment = models.CharField(max_length=100, default="")
    fact_of_payment = models.BooleanField(default=False)
    comment = models.CharField(default="", max_length=4048)
    date = models.DateTimeField(default=timezone.now)
    cancel = models.BooleanField(default=False)
    cancel_reason = models.CharField(default="", max_length=1024)

    def get_delivery(self, data):
        zip = "0"
        if "address_id" in data:
            zip = AddressInfo.objects.get(id=data['address_id']).post_index

        target = data.get("target", "0")

        if int(data['delivery_type']) == 0:
            self.delivery_price = 0
            self.delivery = "по Москве без консолидации"
            self.groups_delivery.append([unit.id for unit in self.order_units.all()])
        else:
            if int(data['delivery_type']) == 1:
                zip = "0"
                name_delivery = "Пункт выдачи"
            else:
                target = "0"
                name_delivery = "Курьер"

            if data['consolidation']:
                self.groups_delivery.append([unit.id for unit in self.order_units.all()])
                self.delivery_price = get_delivery_price(self.order_units.all(), "02743", target, zip)
                self.delivery = f"{name_delivery}"

            else:
                product_units = self.order_units.annotate(
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
                        self.groups_delivery.append([unit.id for unit in tec])
                        tec = [unit]

                sum_part += get_delivery_price(tec, "02743", target, zip)
                self.groups_delivery.append([unit.id for unit in tec])
                self.delivery_price = sum_part
                self.delivery = f"{name_delivery} + консолидация"

        self.delivery_price = round_to_nearest(self.delivery_price)
        self.delivery_view_price = self.delivery_price
        self.save()

    def change_status(self):
        min_status_id = self.order_units.aggregate(min_status_id=models.Min('status__id'))['min_status_id']
        if min_status_id is not None:
            self.status = Status.objects.get(id=min_status_id)
            self.save()

    def add_order_unit(self, product_unit, user_status):
        price = formula_price(product_unit.product, product_unit, user_status)
        order_unit = OrderUnit(
            product=product_unit.product,
            view_size_platform=product_unit.view_size_platform,
            weight=product_unit.weight,
            # size_table_platform=product_unit.size_table_platform,
            start_price=price['start_price'],
            final_price=price['final_price'],
            delivery_type=product_unit.delivery_type,
            platform=product_unit.platform,
            url=product_unit.url,
            warehouse=product_unit.warehouse,
            is_return=product_unit.is_return,
            is_fast_shipping=product_unit.is_fast_shipping,
            is_sale=product_unit.is_sale
        )
        order_unit.save()
        self.order_units.add(order_unit)


class ShoppingCart(models.Model):
    user = models.ForeignKey("users.User", related_name="shopping_cart", on_delete=models.CASCADE,
                             blank=False)
    product_units = models.ManyToManyField("shipping.ProductUnit", blank=True,
                                           related_name="shopping_carts")
    unit_order = models.JSONField(default=list)
    promo_code = models.ForeignKey("promotions.PromoCode", on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name="carts")
    total_amount = models.IntegerField(default=0)
    sale = models.IntegerField(default=0)
    bonus_sale = models.IntegerField(default=0)
    promo_sale = models.IntegerField(default=0)
    total_sale = models.IntegerField(default=0)
    final_amount = models.IntegerField(default=0)

    def total(self):

        # Пересчитать total_amount на основе product_units и их цен
        total_amount = 0
        sale = 0
        for product_unit in self.product_units.all():
            price = formula_price(product_unit.product, product_unit, self.user.user_status)
            total_amount += price['start_price']
            sale += price['start_price'] - price['final_price']

        # Обновить поле total_amount для текущей корзины
        self.total_amount = total_amount
        self.sale = sale

        # Выполнить проверку активности промокода и его применимости
        # Ваш код для проверки промокода здесь
        # Если промокод активен и применим, обновить поле promo_code для текущей корзины
        if not check_promo(self.promo_code, user_id=self.user_id)[0]:
            self.promo_code = None

        if self.promo_code:
            self.final_amount = self.total_amount - self.sale
            if self.promo_code.discount_percentage > 0:
                self.final_amount = round(self.total_amount * (100 - self.promo_code.discount_percentage) // 100)
            elif self.promo_code.discount_absolute > 0:
                self.final_amount = round(self.total_amount - self.promo_code.discount_absolute)
            self.promo_sale = self.total_amount - self.final_amount
        else:
            self.final_amount = self.total_amount - self.sale
        self.final_amount -= self.bonus_sale
        self.total_sale = self.bonus_sale + self.promo_sale + self.sale
        self.save()

    def __str__(self):
        return f'{self.user}'


# class ProductOrderUnit(models.Model):
#     product_unit = models.ForeignKey("shipping.ProductUnit", blank=True, on_delete=models.PROTECT, )
#     start_price = models.IntegerField(blank=True, null=True)
#     final_price = models.IntegerField(blank=True, null=True)
#     status = models.CharField(default="", max_length=127)
#
#     def __str__(self):
#         return str(self.product_unit)


class OrderUnit(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="order_units",
                                null=False, blank=False)
    view_size_platform = models.CharField(max_length=255, null=True, blank=True,
                                          default="")  # обработанный размер с платформы
    size_table_platform = models.CharField(max_length=255, null=True, blank=True, default="")  # по какой таблице размер
    size = models.ForeignKey("products.SizeTranslationRows", on_delete=models.CASCADE, related_name="order_units",
                             null=True, blank=True)
    weight = models.IntegerField(default=1)

    start_price = models.IntegerField(null=False, blank=False)  # Старая цена
    final_price = models.IntegerField(null=False, blank=False)  # Новая цена
    delivery_type = models.ForeignKey("shipping.DeliveryType", on_delete=models.CASCADE, related_name='order_units',
                                      null=False, blank=False)
    platform = models.ForeignKey("shipping.Platform", on_delete=models.CASCADE, related_name='order_units',
                                 null=False, blank=False)
    url = models.CharField(max_length=255, null=True, blank=True, default="")
    warehouse = models.BooleanField(default=False)  # на руках ли товар
    is_return = models.BooleanField(default=False)
    is_fast_shipping = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)
    status = models.ForeignKey("Status", on_delete=models.SET_DEFAULT, null=False, blank=False,
                               related_name="order_units", default=get_default_status())
    cancel = models.BooleanField(default=False)
    cancel_reason = models.CharField(default="", max_length=1024)
