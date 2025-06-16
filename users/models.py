from django.contrib.auth.models import AbstractUser
from django.db import models
from promotions.models import Bonuses
from products.models import SizeRow

from django.utils import timezone



class User(AbstractUser):
    # Your custom fields and methods here

    class Meta:
        # Set a custom related name for the 'groups' field
        # This will prevent the clash with the built-in 'auth.User.groups' field
        # and allow you to access the groups related to a user via 'my_user.my_groups.all()'
        # instead of 'my_user.groups.all()'
        db_table = 'auth_user'
        swappable = 'AUTH_USER_MODEL'
        verbose_name_plural = 'Users'
        verbose_name = 'User'

    my_groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Groups',
        blank=True,
        related_name='my_users'
    )
    verify_email = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, default="")

    gender = models.ForeignKey("Gender", on_delete=models.PROTECT, null=True, blank=True,
                               related_name="users")

    address = models.ManyToManyField("shipping.AddressInfo", blank=True,
                                     related_name="users")
    favorite_brands = models.ManyToManyField("products.Brand", blank=True,
                                             related_name="users")
    all_purchase_amount = models.IntegerField(default=0)

    personal_discount_percentage = models.IntegerField(default=0)

    is_mailing_list = models.BooleanField(default=False)

    # wishlist and shopping cart are described in Wishlist and ShoppingCart models

    referral_promo = models.CharField(max_length=100, null=True, blank=True)
    ref_user = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    bonuses = models.ForeignKey("promotions.Bonuses", on_delete=models.PROTECT, null=True, blank=True,
                                related_name="user")
    preferred_size_grid = models.CharField(max_length=100, null=True, blank=True)
    # last_viewed_products = models.ManyToManyField("products.Product", related_name='users_viewed',
    #                                               blank=True)
    last_viewed_products = models.JSONField(blank=True, null=True, default=list)
    happy_birthday = models.DateTimeField(auto_now=True)
    preferred_shoes_size_row = models.ForeignKey("products.SizeRow", on_delete=models.SET_NULL, blank=True, null=True,
                                                   related_name='users_with_shoes_table')
    preferred_clothes_size_row = models.ForeignKey("products.SizeRow", on_delete=models.SET_NULL, blank=True,
                                                     null=True, related_name='users_with_clothes_table')
    shoes_size = models.ForeignKey("products.SizeTranslationRows", on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='users_with_shoes_size')
    clothes_size = models.ForeignKey("products.SizeTranslationRows", on_delete=models.SET_NULL, blank=True, null=True,
                                     related_name='users_with_clothes_size')
    height = models.IntegerField(default=175)
    weight = models.IntegerField(default=60)

    wait_list = models.ManyToManyField('shipping.ConfigurationUnit', blank=True, related_name="wait_list_users")

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # Если гендер мужской, установите значение по умолчанию для мужского размера обуви
        size_info = kwargs.pop('size_info', False)
        if not size_info:
            if self.gender is not None:
                if self.gender.name == 'M':
                    self.preferred_shoes_size_row = SizeRow.objects.get(id=1)
                    self.preferred_clothes_size_row = SizeRow.objects.get(id=8)
                else:
                    self.preferred_shoes_size_row = SizeRow.objects.get(id=1)
                    self.preferred_clothes_size_row = SizeRow.objects.get(id=19)
            else:
                self.preferred_shoes_size_row = SizeRow.objects.get(id=1)
                self.preferred_clothes_size_row = SizeRow.objects.get(id=8)
        super(User, self).save(*args, **kwargs)


class Gender(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female')
    )

    name = models.CharField(max_length=255, choices=GENDER_CHOICES)

    def __str__(self):
        d = {"M": 'male', "F": "female"}
        return d[self.name]


class Status(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.name


class EmailConfirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
