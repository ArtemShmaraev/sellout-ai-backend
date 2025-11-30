from datetime import datetime

from django.db import models
from django.conf import settings
from django.db.models import F


from django.utils import timezone

from promotions.models import AccrualBonus
from shipping.models import AddressInfo, ProductUnit
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
    user = models.ForeignKey("users.User", related_name="orders", on_delete=models.CASCADE,
                             blank=False)
    order_units = models.ManyToManyField("OrderUnit", blank=True, related_name="orders")
    total_amount = models.IntegerField(default=0)
    final_amount = models.IntegerField(default=0)
    final_amount_without_shipping = models.IntegerField(default=0)
    email = models.EmailField(null=False, blank=False)
    phone = models.CharField(max_length=25, null=False, blank=False)
    phone_int = models.CharField(max_length=20, default="", blank=False)
    name = models.CharField(max_length=100, default="", blank=False)
    surname = models.CharField(max_length=100, null=False, blank=False)
    patronymic = models.CharField(max_length=100, default="")
    delivery = models.CharField(max_length=100, default="")
    delivery_price = models.IntegerField(default=0)
    delivery_view_price = models.IntegerField(default=0)
    groups_delivery = models.JSONField(default=list)
    track_numbers = models.JSONField(default=list)
    address = models.ForeignKey("shipping.AddressInfo", on_delete=models.PROTECT, related_name="orders", null=True,
                                blank=True)
    pvz = models.CharField(default="", max_length=100, blank=True)
    pvz_address = models.CharField(default="", max_length=2048, blank=True)
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
    date_of_buy_out = models.DateTimeField(default=timezone.now)
    cancel = models.BooleanField(default=False)
    cancel_reason = models.CharField(default="", max_length=1024)
    order_in_progress = models.BooleanField(default=False)
    total_bonus = models.IntegerField(default=0)
    invoice_data = models.JSONField(default=dict)

    def start_order(self):
        self.date_of_buy_out = timezone.now()
        self.order_in_progress = True
        self.save()

    def get_total_bonus(self):
        user = self.user
        sum_bonus = 0
        if user.user_status.base:
            orders_count = Order.objects.filter(user=user).count()
            units = self.order_units.order_by("-bonus")
            k = 0
            sum_bonus = 0
            for unit in units:
                if orders_count == 1 and k == 0:
                    sum_bonus += 1000

                else:
                    sum_bonus += unit.bonus
                k += 1
        self.total_bonus = sum_bonus
        self.save()


    def accrue_bonuses(self):
        user = self.user
        if user.user_status.base:
            sum_bonus = self.total_bonus
            accrual_bonus = AccrualBonus(amount=sum_bonus)
            accrual_bonus.save()
            user.bonuses.accrual.add(accrual_bonus)
            user.bonuses.update_total_amount()
            user.update_user_status()

            if self.promo_code is not None:
                self.promo_code.activation_count += 1
                self.promo_code.save()

                if self.promo_code.ref_promo:
                    ref_user = self.promo_code.owner
                    ref_accrual_bonus = AccrualBonus(amount=self.promo_sale, type="Приглашение")
                    ref_accrual_bonus.save()
                    ref_user.total_ref_bonus += self.promo_sale
                    ref_user.bonuses.accrual.add(ref_accrual_bonus)
                    user.ref_user = ref_user
                    user.save()
                    ref_user.save()

    def update_order_status(self):
        for ou in self.order_units.all():
            ou.update_status()
        # Получаем все статусы юнитов этого заказа
        unit_statuses = self.order_units.values_list('status__name', flat=True)
        s = ["Заказ принят", "В пути до международного склада", 'В пути до московского склада', "Прибыл в Москву",
             "Передан в службу доставки по России", "Доставлен"]

        # Проверяем условия и определяем статус заказа
        if 'Отменён' in unit_statuses:
            self.status = Status.objects.get(name='Отменён')

        if 'В пути до международного склада' in unit_statuses:
            self.status = Status.objects.get(name='В пути до международного склада')

        if 'В пути до московского склада' in unit_statuses:
            self.status = Status.objects.get(name='В пути до московского склада')

        if "Прибыл в Москву" in unit_statuses:
            if all(status == 'Прибыл в Москву' for status in unit_statuses):
                self.status = Status.objects.get(name='Прибыл в Москву')
            else:
                self.status = Status.objects.get(name='Частично прибыл в Москву')

        if "Передан в службу доставки по России" in unit_statuses:
            if all(status == 'Передан в службу доставки по России' for status in unit_statuses):
                self.status = Status.objects.get(name='Передан в службу доставки по России')
            else:
                self.status = Status.objects.get(name='Частично передан в службу доставки по России')

        if all(status == "Доставлен" for status in unit_statuses):
            self.status = Status.objects.get(name='Доставлен')

        self.save()

    def evenly_distribute_discount(self):
        # final_price = self.total_amount
        discount = self.total_sale
        total_cost = self.total_amount
        discount_per_cost = discount / total_cost
        # print(discount_per_cost, self.total_amount)
        new_item_costs = []
        sum_unit = 0
        # Распределение скидки на позиции (кроме последней)
        k = self.order_units.count()
        ck = 0
        for unit in self.order_units.all():
            ck += 1
            if ck == k:
                last_item_cost = self.total_amount - sum_unit - discount
                unit.final_price = last_item_cost
                unit.save()
            else:

                item_discount = round(unit.start_price * discount_per_cost)
                unit.final_price = unit.start_price - item_discount
                unit.save()
                # print(unit.final_price)
                sum_unit += unit.final_price


    def get_invoice_data(self):
        invoice_data = {}
        items = []
        for order_unit in self.order_units.all():
            position = {}
            position["code"] = str(order_unit.product.id)
            position['name'] = order_unit.product.get_full_name()
            position['price'] = order_unit.start_price
            position['unit'] = "piece"
            position['quantity'] = 1
            position['sum'] = order_unit.start_price
            position['vat_mode'] = 'none'
            if order_unit.start_price != order_unit.final_price:
                position['discount_amount'] = order_unit.start_price - order_unit.final_price
            position['payment_object'] = "service"
            items.append(position)

        position = {}
        position["code"] = "1"
        position['name'] = "Доставка"
        position['price'] = self.delivery_view_price
        position['unit'] = "piece"
        position['quantity'] = 1
        position['sum'] = self.delivery_view_price
        position['vat_mode'] = 'none'
        position['payment_object'] = "service"
        items.append(position)

        invoice_data['items'] = items
        # print(invoice_data)
        self.invoice_data = invoice_data
        self.save()

    def add_order_unit(self, product_unit, user_status):
        if user_status.base:
            product_unit.product.update_price()
            price = formula_price(product_unit.product, product_unit, user_status)
        else:
            price = formula_price(product_unit.product, product_unit, user_status)
        order_unit = OrderUnit(
            product=product_unit.product,
            view_size_platform=product_unit.view_size_platform,
            weight=product_unit.weight_kg,
            size_platform=product_unit.size_platform,
            start_price=price['start_price'],
            final_price=price['final_price'],
            delivery_type=product_unit.delivery_type,
            platform=product_unit.platform,
            url=product_unit.url,
            warehouse=product_unit.warehouse,
            is_return=product_unit.is_return,
            is_fast_shipping=product_unit.is_fast_shipping,
            is_sale=product_unit.is_sale,
            bonus=price["bonus"],
            original_price=product_unit.original_price,
            total_profit=product_unit.total_profit
        )
        order_unit.save()
        self.order_units.add(order_unit)


class ShoppingCart(models.Model):
    user = models.ForeignKey("users.User", related_name="shopping_cart", on_delete=models.CASCADE,
                             blank=False)
    product_units = models.ManyToManyField("shipping.ProductUnit", blank=True,
                                           related_name="shopping_carts")#, on_delete=models.DO_NOTHING)
    unit_order = models.JSONField(default=list)
    promo_code = models.ForeignKey("promotions.PromoCode", on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name="carts")
    total_amount = models.IntegerField(default=0)
    sale = models.IntegerField(default=0)
    bonus_sale = models.IntegerField(default=0)
    first_order_bonus = models.IntegerField(default=0)
    promo_sale = models.IntegerField(default=0)
    total_sale = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    is_update = models.BooleanField(default=False)
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
        for product_unit in self.product_units.filter(availability=True):
            if user_status.base:
                product_unit.product.update_price()
                price = formula_price(product_unit.product, product_unit, user_status)
                sum_bonus += price['bonus']
                max_bonus = max(max_bonus, price['bonus'])
            else:
                price = formula_price(product_unit.product, product_unit, user_status)
            total_amount += price['start_price']
            sale += price['start_price'] - price['final_price']


        # Обновить поле total_amount для текущей корзины
        self.total_amount = total_amount
        self.sale = sale
        self.first_order_bonus = 0
        if user_status.base:
            orders_count = Order.objects.filter(user=self.user).count()
            if orders_count == 0:
                sum_bonus += max(0, 1000 - max_bonus)
                self.first_order_bonus = 1000

        # Выполнить проверку активности промокода и его применимости
        # Ваш код для проверки промокода здесь
        # Если промокод активен и применим, обновить поле promo_code для текущей корзины

        # if not self.promo_code.check_promo(user_id=self.user_id)[0]:
        #     self.promo_code = None
        self.final_amount = self.total_amount - self.sale
        if self.promo_code:
            promo_sale = self.promo_code.check_promo_in_cart(self)
            if promo_sale != 0:
                self.promo_sale = promo_sale
                if self.first_order_bonus == 1000:
                    self.first_order_bonus = 0
                    sum_bonus -= 1000
                    sum_bonus += max_bonus
            else:
                self.promo_code = None
                self.promo_sale = 0
        else:
            self.promo_sale = 0


        if not user_status.base:
            self.bonus = 0
        else:
            self.bonus = sum_bonus

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
    size_platform = models.CharField(max_length=255, null=True, blank=True, default="")  # по какой таблице размер
    size = models.ForeignKey("products.SizeTranslationRows", on_delete=models.CASCADE, related_name="order_units",
                             null=True, blank=True)
    weight = models.FloatField(default=1)

    start_price = models.IntegerField(null=False, blank=False)  # Старая цена
    final_price = models.IntegerField(null=False, blank=False)  # Новая цена
    original_price = models.IntegerField(null=False, blank=False, default=0)
    total_profit = models.IntegerField(null=False, blank=False, default=0)
    bonus = models.IntegerField(null=False, blank=False, default=0)
    delivery_type = models.ForeignKey("shipping.DeliveryType", on_delete=models.CASCADE, related_name='order_units',
                                      null=False, blank=False)
    track_number = models.CharField(default="", max_length=1024)
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

    def update_status(self, cancel=False, next=False):
        new_status = self.status.name
        order_date = self.orders.first().date

        # Приводим order_date к типу datetime.date
        order_date = order_date.date()

        # Получаем текущую дату
        current_date = datetime.now().date()

        # Вычисляем разницу в днях
        days_passed = (current_date - order_date).days

        # Вычисляем разницу в днях
        days_passed = (current_date - order_date).days
        if days_passed <= self.delivery_type.days_max_to_international_warehouse:
            new_status = "В пути до международного склада"
        if self.delivery_type.days_max_to_international_warehouse < days_passed <= self.delivery_type.days_max:
            new_status = "В пути до московского склада"
        # if days_passed > self.delivery_type.days_max:
        #     new_status = "Прибыл в Москву"
        self.status = Status.objects.get(name=new_status)

        if cancel:
            self.status = Status.objects.get(name="Отменён")

        if next:
            s = ["Заказ принят", "В пути до международного склада", 'В пути до московского склада', "Прибыл в Москву", "Передан в службу доставки по России", "Доставлен"]

            for i in range(len(s)):
                if self.status.name == s[i]:
                    new_status = s[min(i + 1, 5)]
                    break
            self.status = Status.objects.get(name=new_status)
        self.save()

