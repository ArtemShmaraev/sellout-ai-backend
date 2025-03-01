from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False)


class RoubleRate(models.Model):
    currency = models.ForeignKey("Currency", on_delete=models.PROTECT, related_name="rouble_rate",
                                 null=False, blank=False)
    rate = models.FloatField(null=False, blank=False)
