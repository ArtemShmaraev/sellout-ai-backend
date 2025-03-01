from django.db import models
from django.conf import settings


class Status(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)  # TODO add choices

    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=False, blank=False,
                             related_name="orders")
    product_unit = models.ForeignKey("shipping.ProductUnit", on_delete=models.PROTECT, null=False, blank=False,
                                     related_name="orders")
    total_amount = models.IntegerField(default=0)
    email = models.EmailField(null=False, blank=False)
    tel = models.CharField(max_length=20, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    surname = models.CharField(max_length=100, null=False, blank=False)
    address = models.ForeignKey("shipping.AddressInfo", on_delete=models.PROTECT, related_name="orders")
    promo_code = models.ForeignKey("promotions.PromoCode", on_delete=models.PROTECT, blank=True, null=True,
                                   related_name="orders")
    status = models.ForeignKey("Status", on_delete=models.PROTECT, null=False, blank=False,
                               related_name="orders")  # TODO add default value
    fact_of_payment = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} order: {self.product_unit}'


class ShoppingCart(models.Model):
    user = models.OneToOneField("users.User", related_name="shopping_cart", on_delete=models.PROTECT,
                                blank=False)
    product_units = models.ManyToManyField("shipping.ProductUnit", blank=True,
                                           related_name="shopping_carts")

    def __str__(self):
        return f'{self.user} cart: {", ".join([str(pu) for pu in self.product_units.all()])}'
