from django.db import models
from utils.models import Currency



class ConfigurationUnit(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="config_units",
                                null=False, blank=False)

    size = models.ForeignKey("products.SizeTranslationRows", on_delete=models.CASCADE, related_name="config_units",
                             null=True, blank=True)  # порядковый номер размера в таблице

class DeliveryType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    days = models.IntegerField(default=0)
    view_name = models.CharField(max_length=100, null=True, blank=True)

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
    post_index = models.CharField(max_length=10, null=False, blank=False)
    is_main = models.BooleanField(default=False)
    other_info = models.JSONField(default=dict)

    def __str__(self):
        return self.address

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_main:
            user = self.users.first()
            if user:
                addresses = user.address.filter(is_main=True)
                for address in addresses:
                    address.is_main = False


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
                                null=False, blank=False)
    size_platform = models.CharField(max_length=255, null=True, blank=True, default="")  # размер с платформы
    view_size_platform = models.CharField(max_length=255, null=True, blank=True,
                                          default="")  # обработанный размер с платформы
    # size_table_platform = models.CharField(max_length=255, null=True, blank=True, default="")  # по какой таблице размер

    size = models.ForeignKey("products.SizeTranslationRows", on_delete=models.CASCADE, related_name="product_units",
                             null=True, blank=True)  # порядковый номер размера в таблице

    color = models.CharField(max_length=255, null=True, blank=True, default="")
    configuration = models.CharField(max_length=255, null=True, blank=True, default="")

    currency = models.ForeignKey("utils.Currency", on_delete=models.CASCADE,
                                 null=False, blank=False, default=get_default_currency)
    start_price = models.IntegerField(null=False, blank=False)  # Старая цена
    final_price = models.IntegerField(null=False, blank=False)  # Новая цена
    delivery_type = models.ForeignKey("DeliveryType", on_delete=models.CASCADE, related_name='product_units',
                                      null=False, blank=False, default=get_default_delivery_type)
    platform = models.ForeignKey("Platform", on_delete=models.CASCADE, related_name='product_units',
                                 null=False, blank=False)
    url = models.CharField(max_length=255, null=True, blank=True, default="")
    availability = models.BooleanField(default=True)
    warehouse = models.BooleanField(default=False)  # на руках ли товар
    is_multiple = models.BooleanField(default=False)  # можно ли несколько позиций взять
    is_return = models.BooleanField(default=False)
    is_fast_shipping = models.BooleanField(default=False)
    is_sale = models.BooleanField(default=False)

    dimensions = models.JSONField(default=dict)
    history_price = models.JSONField(default=list)

    def __str__(self):
        return f"{self.product.model} {self.product.colorway} ]{self.size} {self.platform} {self.delivery_type}"

    def save(self, *args, **kwargs):
        if (not self.product.min_price or self.final_price < self.product.min_price) and self.availability:
            self.product.min_price = self.final_price
            self.product.save()
        super().save(*args, **kwargs)
