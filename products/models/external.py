from django.db import models


class DewuInfo(models.Model):
    spu_id = models.IntegerField(default=0, db_index=True)
    api_data = models.JSONField(default=dict)
    preprocessed_data = models.JSONField(default=dict)
    web_data = models.JSONField(default=dict)
    formatted_manufacturer_sku = models.CharField(default="", max_length=128, db_index=True)


class SGInfo(models.Model):
    manufacturer_sku = models.CharField(max_length=256, default="")
    data = models.JSONField(default=dict)
    relevant_number = models.IntegerField(default=0)
    novelty_number = models.IntegerField(default=0)
    formatted_manufacturer_sku = models.CharField(default="", max_length=128, db_index=True)


class RansomRequest(models.Model):
    name = models.CharField(max_length=128, default="")
    tg_name = models.CharField(max_length=128, default="")
    phone_number = models.CharField(max_length=64, default="")
    email = models.CharField(max_length=128, default="")
    url = models.CharField(max_length=512, default="")
    photo = models.CharField(max_length=512, default="")
    info = models.CharField(max_length=1024, default="")
