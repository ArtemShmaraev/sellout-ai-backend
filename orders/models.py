from django.db import models
from django.conf import settings


class Status(models.Model):
    name = models.CharField(max_length=500, null=False, blank=False)

    def __str__(self):
        return self.name


def get_default_status():
    default_object = Status.objects.get_or_create(name="pending")[0]
    return default_object.pk


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=False, blank=False,
                             related_name="orders")
    product_unit = models.ManyToManyField("shipping.ProductUnit", blank=True, related_name="orders")
    total_amount = models.IntegerField(default=0)
    email = models.EmailField(null=False, blank=False)
    tel = models.CharField(max_length=20, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    surname = models.CharField(max_length=100, null=False, blank=False)
    address = models.ForeignKey("shipping.AddressInfo", on_delete=models.PROTECT, related_name="orders")
    promo_code = models.ForeignKey("promotions.PromoCode", on_delete=models.PROTECT, blank=True, null=True,
                                   related_name="orders")
    status = models.ForeignKey("Status", on_delete=models.PROTECT, null=False, blank=False,
                               related_name="orders", default=get_default_status)
    fact_of_payment = models.BooleanField(default=False)


class ShoppingCart(models.Model):
    user = models.OneToOneField("users.User", related_name="shopping_cart", on_delete=models.PROTECT,
                                blank=False)
    product_units = models.ManyToManyField("shipping.ProductUnit", blank=True,
                                           related_name="shopping_carts")

    def __str__(self):
        return f'{self.user} cart: {", ".join([str(pu) for pu in self.product_units.all()])}'


class ProductOrderUnit(models.Model):
    product_unit = models.ForeignKey("shipping.ProductUnit", blank=True, on_delete=models.PROTECT, )
    start_price = models.IntegerField(blank=True, null=True)
    final_price = models.IntegerField(blank=True, null=True)
    status = models.CharField(default="", max_length=127)

    def __str__(self):
        return str(self.product_unit)
