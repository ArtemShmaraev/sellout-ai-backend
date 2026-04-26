from django.db import models


class HeaderText(models.Model):
    genders = models.ManyToManyField("products.Gender", related_name='headers_text', blank=True)
    categories = models.ManyToManyField("products.Category", related_name='headers_text', blank=True)
    lines = models.ManyToManyField("products.Line", related_name='headers_text', blank=True)
    collabs = models.ManyToManyField("products.Collab", related_name='headers_text', blank=True)
    title = models.CharField(max_length=256, default="")
    text = models.CharField(max_length=8096, default="")
    type = models.CharField(max_length=64, default="")


class HeaderPhoto(models.Model):
    genders = models.ManyToManyField("products.Gender", related_name='headers_photos', blank=True)
    categories = models.ManyToManyField("products.Category", related_name='headers_photos', blank=True)
    lines = models.ManyToManyField("products.Line", related_name='headers_photos', blank=True)
    collabs = models.ManyToManyField("products.Collab", related_name='headers_photos', blank=True)
    type = models.CharField(max_length=64, default="")
    where = models.CharField(max_length=64, default="")
    photo = models.CharField(max_length=1024, default="")
    header_text = models.ForeignKey("HeaderText", related_name='headers_photo', blank=True, on_delete=models.CASCADE,
                                    null=True)
    rating = models.IntegerField(default=0)


class FooterText(models.Model):
    genders = models.ManyToManyField("products.Gender", related_name='footer_text', blank=True)
    categories = models.ManyToManyField("products.Category", related_name='footer_text', blank=True)
    lines = models.ManyToManyField("products.Line", related_name='footer_text', blank=True)
    collabs = models.ManyToManyField("products.Collab", related_name='footer_text', blank=True)
    title = models.CharField(max_length=512, default="")
    text = models.CharField(max_length=16096, default="")
    type = models.CharField(max_length=64, default="")


class HeaderPage(models.Model):
    text = models.ForeignKey("HeaderText", blank=True, null=True, on_delete=models.PROTECT)
    photo = models.ForeignKey("HeaderPhoto", blank=True, null=True, on_delete=models.PROTECT)


class MainPage(models.Model):
    text = models.ForeignKey("HeaderText", blank=True, null=True, on_delete=models.PROTECT)
    photo = models.ForeignKey("HeaderPhoto", blank=True, null=True, on_delete=models.PROTECT)
    button = models.BooleanField(default=True)
    button_text = models.CharField(max_length=64, default="")
