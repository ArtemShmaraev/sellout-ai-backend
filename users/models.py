from django.contrib.auth.models import AbstractUser
from django.db import models
from promotions.models import Bonuses


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
    phone_number = models.CharField(max_length=20)

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
    ref_user = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)
    bonuses = models.ForeignKey("promotions.Bonuses", on_delete=models.PROTECT, null=True, blank=True,
                                related_name="users")
    preferred_size_grid = models.CharField(max_length=100, null=True, blank=True)
    # last_viewed_products = models.ManyToManyField("products.Product", related_name='users_viewed',
    #                                               blank=True)
    last_viewed_products = models.JSONField(blank=True, null=True, default=list)
    happy_birthday = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


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
