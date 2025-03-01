from django.db import models


class DeliveryType(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name


class Formula(models.Model):
    brand = models.ForeignKey("products.Brand", on_delete=models.PROTECT, related_name="formulas")
    delivery_type = models.ForeignKey("DeliveryType", on_delete=models.PROTECT, related_name="formulas")
    moscow_del_price = models.IntegerField(null=False, blank=False)
    extra_charge_percentage = models.FloatField(null=False, blank=False)
    rounding_step = models.IntegerField(default=500)

    def __str__(self):
        return f'Formula for {self.brand} ({self.delivery_type})'


class AddressInfo(models.Model):
    address = models.CharField(max_length=255, null=False, blank=False)
    post_index = models.CharField(max_length=10, null=False, blank=False)

    def __str__(self):
        return self.address


class Platform(models.Model):
    platform = models.CharField(max_length=255, null=False, blank=False)
    site = models.CharField(max_length=10, null=True, blank=True)


class ProductUnit(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="product_units",
                                null=False, blank=False)
    size = models.ForeignKey("products.Size", on_delete=models.CASCADE, related_name='product_units',
                             null=False, blank=False)

    currency = models.ForeignKey("utils.Currency", on_delete=models.CASCADE,
                                 null=False, blank=False)  # TODO add default value
    final_price = models.IntegerField(null=False, blank=False)
    delivery_type = models.ForeignKey("DeliveryType", on_delete=models.CASCADE, related_name='product_units',
                                      null=False, blank=False)  # TODO add default value
    platform = models.ForeignKey("Platform", on_delete=models.CASCADE, related_name='product_units',
                                 null=False, blank=False)
    availability = models.BooleanField(default=True)
