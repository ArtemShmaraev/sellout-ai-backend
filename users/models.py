from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Sum

from orders.models import Order
from promotions.models import Bonuses


from django.utils import timezone


class UserStatus(models.Model):
    name = models.CharField(max_length=128, default="1")
    total_orders_amount = models.IntegerField(default=0)
    unit_max_bonuses = models.IntegerField(default=250)
    free_ship_amount = models.IntegerField(default=20000)
    exclusive_sale = models.BooleanField(default=False)
    close_release = models.BooleanField(default=False)
    priority_service = models.BooleanField(default=False)
    birthday_gift = models.BooleanField(default=True)
    start_bonuses = models.BooleanField(default=True)
    base = models.BooleanField(default=True)
    percentage_bonuses = models.IntegerField(default=10)


    def __str__(self):
        return self.name


def get_default_status():
    default_object = \
    UserStatus.objects.get_or_create(name="Amethyst")[0]
    return default_object.pk


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
    patronymic = models.CharField(max_length=100, default="", null=True, blank=True)
    verify_email = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, default="")
    extra_contact = models.CharField(max_length=64, default="")

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

    referral_promo = models.ForeignKey("promotions.PromoCode", on_delete=models.SET_NULL, blank=True, null=True)
    ref_user = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    total_ref_bonus = models.IntegerField(default=0)
    bonuses = models.ForeignKey("promotions.Bonuses", on_delete=models.PROTECT, null=True, blank=True,
                                related_name="user")
    preferred_size_grid = models.CharField(max_length=100, null=True, blank=True)
    # last_viewed_products = models.ManyToManyField("products.Product", related_name='users_viewed',
    #                                               blank=True)
    last_viewed_products = models.JSONField(blank=True, null=True, default=list)
    happy_birthday = models.DateTimeField(null=True, blank=True)
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
    user_status = models.ForeignKey("UserStatus", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username

    def update_user_status(self):
        statuses = UserStatus.objects.filter(base=True).order_by("-total_orders_amount")
        user_total = self.total_amount_order()

        for status in statuses:
            if status.total_orders_amount < user_total:
                self.user_status = status
                break
        self.save()

    def total_amount_order(self):
        user_orders = Order.objects.filter(user=self, order_in_progress=True)
        user_total = user_orders.aggregate(total=Sum('final_amount_without_shipping'))['total']
        if user_total is None:
            user_total = 0
        return user_total



    def save(self, *args, **kwargs):
        from products.models import SizeRow, SizeTable
        # Если гендер мужской, установите значение по умолчанию для мужского размера обуви
        size_info = kwargs.pop('size_info', False)
        if not size_info:
            if self.gender is not None:
                if self.gender.name == 'M':
                    shoes_table = SizeTable.objects.get(name="Shoes_Adults").size_rows.all()
                    self.preferred_shoes_size_row = shoes_table.get(filter_name="Европейский(EU)")

                    clothes_table = SizeTable.objects.get(name="Clothes_Men").size_rows.all()
                    self.preferred_clothes_size_row = clothes_table.get(filter_name="Международный(INT)")
                else:
                    shoes_table = SizeTable.objects.get(name="Shoes_Adults").size_rows.all()
                    self.preferred_shoes_size_row = shoes_table.get(filter_name="Европейский(EU)")

                    clothes_table = SizeTable.objects.get(name="Clothes_Women").size_rows.all()
                    self.preferred_clothes_size_row = clothes_table.get(filter_name="Международный(INT)")

            else:
                shoes_table = SizeTable.objects.get(name="Shoes_Adults").size_rows.all()
                self.preferred_shoes_size_row = shoes_table.get(filter_name="Европейский(EU)")

                clothes_table = SizeTable.objects.get(name="Clothes_Men").size_rows.all()
                self.preferred_clothes_size_row = clothes_table.get(filter_name="Международный(INT)")
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


class SpamEmail(models.Model):
    email = models.CharField(max_length=200, null=False, blank=False)


class Partner(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    tg = models.CharField(max_length=200, null=False, blank=False)
    email = models.CharField(max_length=200, null=False, blank=False)
    chanels = models.CharField(max_length=2000, null=False, blank=False)
    other = models.CharField(max_length=2000, null=False, blank=False)