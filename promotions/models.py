from django.db import models
from django.conf import settings
from datetime import date


class PromoCode(models.Model):
    string_representation = models.CharField(max_length=100, null=False, blank=False)
    discount_percentage = models.IntegerField(null=True, blank=True)
    discount_absolute = models.IntegerField(null=True, blank=True)

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
                              related_name="promo_codes")
    activation_count = models.IntegerField(default=0)
    max_activation_count = models.IntegerField(default=1)
    active_status = models.BooleanField(default=True)
    active_until_date = models.DateField(default=date.today)

    def __str__(self):
        return self.string_representation
