from django.db import models
from django.conf import settings
from django.db.models import F


from django.utils import timezone

from shipping.models import AddressInfo
from .tools import get_delivery_costs, get_delivery_price, round_to_nearest
from products.formula_price import formula_price


class Status(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False)

    def __str__(self):
        return self.name


def get_default_status():
    default_object = Status.objects.get_or_create(name="Заказ принят")[0]
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
    pvz_address = models.CharField(default="", max_length=2048)
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

    def update_order_status(self):
        # Получаем все статусы юнитов этого заказа
        unit_statuses = self.order_units.values_list('status__name', flat=True)

        # Проверяем условия и определяем статус заказа
        if 'Отменён' in unit_statuses:
            self.status = Status.objects.get(name='Отменён')
        elif 'Доставлен' in unit_statuses:
            self.status = Status.objects.get(name='Доставлен')
        elif 'В пути' in unit_statuses and 'Получен' not in unit_statuses:
            self.status = Status.objects.get(name='В пути')
        elif 'Прибыл в Москву' in unit_statuses and ('В пути до международного склада' in unit_statuses or 'В пути до московского склада' in unit_statuses):
            self.status = Status.objects.get(name='Частично прибыл в Москву')
        elif 'Готов к самовывозу' in unit_statuses and ('В пути до международного склада' in unit_statuses or 'В пути до московского склада' in unit_statuses):
            self.status = Status.objects.get(name='Частично готов к самовывозу')
        elif all(status == 'Готов к самовывозу' or status == 'Получен' for status in unit_statuses):
            self.status = Status.objects.get(name='Готов к самовывозу')
        elif 'Передан в службу доставки по России' in unit_statuses and ('В пути до международного склада' in unit_statuses or 'В пути до московского склада' in unit_statuses):
            self.status = Status.objects.get(name='Частично передан в службу доставки по России')
        elif all(status == 'Передан в службу доставки по России' or status == 'Получен' for status in unit_statuses):
            self.status = Status.objects.get(name='Передан в службу доставки по России')
        else:
            self.status = Status.objects.get(name='Заказ принят')

        self.save()

    def add_order_unit(self, product_unit, user_status):
        if user_status.base:
            product_unit.product.update_price()
            price = {"start_price": product_unit.start_price, "final_price": product_unit.final_price}
        else:
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
            is_sale=product_unit.is_sale,
            bonus=product_unit.bonus,
            original_price=product_unit.original_price,
            total_profit=product_unit.total_profit
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
    bonus = models.IntegerField(default=0)
    final_amount = models.IntegerField(default=0)

    def clear(self):
        self.product_units.clear()
        self.promo_code = None
        self.bonus_sale = 0
        self.bonus = 0
        self.total_amount = 0
        self.final_amount = 0
        self.promo_sale = 0
        self.sale = 0
        self.unit_order = []
        self.total()


    def total(self):

        # Пересчитать total_amount на основе product_units и их цен
        total_amount = 0
        sale = 0
        user_status = self.user.user_status
        sum_bonus = 0
        max_bonus = 0
        for product_unit in self.product_units.all():
            if user_status.base:
                product_unit.product.update_price()
                price = {"start_price": product_unit.start_price, "final_price": product_unit.final_price}
                sum_bonus += price['bonus']
                max_bonus = max(max_bonus, price['bonus'])
            else:
                price = formula_price(product_unit.product, product_unit, user_status)
            total_amount += price['start_price']
            sale += price['start_price'] - price['final_price']


        # Обновить поле total_amount для текущей корзины
        self.total_amount = total_amount
        self.sale = sale

        orders_count = Order.objects.filter(user=self.user).count()
        if orders_count == 0:
            sum_bonus += max(0, 1000 - max_bonus)

        # Выполнить проверку активности промокода и его применимости
        # Ваш код для проверки промокода здесь
        # Если промокод активен и применим, обновить поле promo_code для текущей корзины

        # if not self.promo_code.check_promo(user_id=self.user_id)[0]:
        #     self.promo_code = None
        self.final_amount = self.total_amount - self.sale
        if self.promo_code:
            if self.promo_code.ref_promo:
                ref_sale = 0
                if 3000 <= self.final_amount < 5000:
                    ref_sale = 500
                elif 5000 <= self.final_amount < 15000:
                    ref_sale = 750
                elif 15000 <= self.final_amount < 35000:
                    ref_sale = 1000
                elif 35000 <= self.final_amount < 70000:
                    ref_sale = 1250
                elif 70000 <= self.final_amount < 130000:
                    ref_sale = 2000
                elif 130000 <= self.final_amount < 150000:
                    ref_sale = 2500
                elif self.final_amount >= 150000:
                    ref_sale = 3000
                self.final_amount = self.total_amount - ref_sale
            elif self.promo_code.discount_percentage > 0:
                self.final_amount = round(self.total_amount * (100 - self.promo_code.discount_percentage) // 100)
            elif self.promo_code.discount_absolute > 0:
                self.final_amount = round(self.total_amount - self.promo_code.discount_absolute)
            self.promo_sale = self.total_amount - self.final_amount

        self.final_amount -= self.bonus_sale
        self.total_sale = self.bonus_sale + self.promo_sale + self.sale
        self.bonus = sum_bonus
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
    original_price = models.IntegerField(null=False, blank=False, default=0)
    total_profit = models.IntegerField(null=False, blank=False, default=0)
    bonus = models.IntegerField(null=False, blank=False, default=0)
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
