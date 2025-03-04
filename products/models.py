from django.db import models
from django.utils import timezone
from datetime import date


class Brand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Size(models.Model):
    INT = models.CharField(max_length=15)
    US = models.CharField(max_length=15)
    UK = models.CharField(max_length=15)
    EU = models.CharField(max_length=15)
    IT = models.CharField(max_length=15)
    RU = models.CharField(max_length=15)

    product = models.ForeignKey("Product", related_name="sizes", on_delete=models.CASCADE,
                                null=True, blank=True)

    def __str__(self):
        return self.INT


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Gender(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('U', 'Unisex')
    )

    name = models.CharField(max_length=255, choices=GENDER_CHOICES)


class Product(models.Model):
    brands = models.ManyToManyField("Brand", related_name='products',
                                    blank=False)
    categories = models.ManyToManyField("Category", related_name='products',
                                        blank=False)
    name = models.CharField(max_length=255, null=False, blank=False, unique=True)
    tags = models.ManyToManyField("Tag", related_name='products', blank=True)
    bucket_link = models.CharField(max_length=255)
    # sizes are initialized in Size model by ForeignKey
    # product units are initialized in UnitBundle model by ForeignKey
    description = models.TextField()
    sku = models.CharField(max_length=255)  # Артем, это артикул по-английски, не пугайся
    gender = models.ForeignKey("Gender", on_delete=models.PROTECT, related_name='products')
    available_flag = models.BooleanField(default=True)
    last_upd = models.DateTimeField(default=timezone.now)
    add_date = models.DateField(default=date.today)
    fit = models.IntegerField(default=0)
    rel_num = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class SizeTranslationRows(models.Model):
    brand = models.ForeignKey("Brand", on_delete=models.PROTECT, related_name="translations_rows")
    category = models.ForeignKey("Category", on_delete=models.PROTECT)

    US = models.FloatField()
    UK = models.FloatField()
    EU = models.FloatField()
    RU = models.FloatField()
