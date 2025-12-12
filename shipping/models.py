import math

from django.db import models

# from products.models import SizeTable
from utils.models import Currency


class ConfigurationUnit(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="config_units",
                                null=False, blank=False)

    size = models.ForeignKey("products.SizeTranslationRows", on_delete=models.CASCADE, related_name="config_units",
                             null=True, blank=True)  # порядковый номер размера в таблице


class DeliveryType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    days_min_to_international_warehouse = models.IntegerField(default=0)
    days_max_to_international_warehouse = models.IntegerField(default=0)
    days_min_to_russian_warehouse = models.IntegerField(default=0)
    days_max_to_russian_warehouse = models.IntegerField(default=0)
    days_min = models.IntegerField(default=0)
    days_max = models.IntegerField(default=0)
    delivery_price_per_kg_in_rub = models.IntegerField(default=0)
    decimal_insurance = models.IntegerField(default=0)
    absolute_insurance = models.IntegerField(default=0)
    view_name = models.CharField(max_length=100, null=True, blank=True)
    extra_charge = models.IntegerField(default=0)
    poizon_abroad = models.BooleanField(default=False)
    delivery_type = models.CharField(max_length=64, default="standard")

    def __str__(self):
        return self.name


class Formula(models.Model):
    brand = models.ForeignKey("products.Brand", on_delete=models.CASCADE, related_name="formulas")
    delivery_type = models.ForeignKey("DeliveryType", on_delete=models.CASCADE, related_name="formulas")
    moscow_del_price = models.IntegerField(null=False, blank=False)
    extra_charge_percentage = models.FloatField(null=False, blank=False)
    rounding_step = models.IntegerField(default=500)

    def __str__(self):
        return f'Formula for {self.brand} ({self.delivery_type})'


class AddressInfo(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)
    address = models.CharField(max_length=255, null=False, blank=False)
    post_index = models.CharField(max_length=10, null=False, blank=False, default=0)
    is_main = models.BooleanField(default=False)
    other_info = models.JSONField(default=dict)

    def __str__(self):
        return self.address


class Platform(models.Model):
    platform = models.CharField(max_length=255, null=False, blank=False)
    site = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.platform


def get_default_currency():
    default_object = Currency.objects.get_or_create(name="pending")[0]
    return default_object.pk


def get_default_delivery_type():
    default_object = DeliveryType.objects.get_or_create(name="pending")[0]
    return default_object.pk


class ProductUnit(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="product_units",
                                null=False, blank=False, db_index=True)
    size_platform = models.CharField(max_length=255, null=True, blank=True, default="")  # размер с платформы
    view_size_platform = models.CharField(max_length=255, null=True, blank=True,
                                          default="")  # обработанный размер с платформы
    # size_table_platform = models.CharField(max_length=255, null=True, blank=True, default="")  # по какой таблице размер

    size_table = models.ManyToManyField("products.SizeTable", related_name="product_units", blank=True, db_index=True)

    size = models.ManyToManyField("products.SizeTranslationRows", related_name="product_units",
                                  blank=True, db_index=True)  # порядковый номер размера в таблице

    currency = models.ForeignKey("utils.Currency", on_delete=models.CASCADE,
                                 null=False, blank=False, default=get_default_currency)
    original_price = models.IntegerField(null=False, blank=False, default=0)
    start_price = models.IntegerField(null=False, blank=False)  # Старая цена
    final_price = models.IntegerField(null=False, blank=False, db_index=True)  # Новая цена

    total_profit = models.IntegerField(null=False, blank=False, default=0)
    bonus = models.IntegerField(null=False, blank=False, default=0)
    approximate_price_with_delivery_in_rub = models.IntegerField(null=False, blank=False, default=0)
    delivery_type = models.ForeignKey("DeliveryType", on_delete=models.CASCADE, related_name='product_units',
                                      null=False, blank=False, default=get_default_delivery_type)
    platform = models.ForeignKey("Platform", on_delete=models.CASCADE, related_name='product_units',
                                 null=False, blank=False)
    url = models.CharField(max_length=255, null=True, blank=True, default="")

    availability = models.BooleanField(default=True, db_index=True)
    warehouse = models.BooleanField(default=False)  # на руках ли товар
    is_multiple = models.BooleanField(default=False)  # можно ли несколько позиций взять
    is_return = models.BooleanField(default=False)
    is_fast_shipping = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)


    dimensions = models.JSONField(default=dict)
    weight = models.IntegerField(default=1)
    weight_kg = models.FloatField(default=1.0)
    update_w = models.BooleanField(default=False)

    history_price = models.JSONField(default=list)
    platform_info = models.JSONField(default=dict)
    absolute_profit = models.IntegerField(default=0)

    # class Meta:
    #     indexes = [
    #         models.Index(fields=['product', 'id']),
    #     ]
    #     unique_together = [['product', 'id']]

    def __str__(self):
        return f"{self.id} {self.product.model} {self.product.colorway}"

    def update_history(self):
        self.history_price.append(self.final_price)
        self.save()


    def check_sale(self):
        def round_by_step(value, step=50):
            return math.ceil(value / step) * step

        if self.product.is_sale:
            self.is_sale = True
            if self.product.sale_absolute:
                percentage = round(((100 - self.product.sale_percentage) / 100), 2)
                self.start_price = round_by_step((self.final_price / percentage) + 10, step=100) - 10
            else:
                self.start_price = self.final_price + self.product.sale_absolute
            self.save()

    # def save(self, *args, **kwargs):
    #     if (not self.product.min_price or self.final_price < self.product.min_price) and self.availability:
    #         self.product.min_price = self.final_price
    #         self.product.save()
    #     super().save(*args, **kwargs)
