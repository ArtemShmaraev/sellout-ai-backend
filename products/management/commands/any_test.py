from itertools import count

from django.core import signing
from django.core.management.base import BaseCommand
import json

from orders.models import ShoppingCart
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo
from django.core.exceptions import ObjectDoesNotExist
from shipping.models import ProductUnit
from users.models import User, EmailConfirmation
from products.tools import get_text

class Command(BaseCommand):

    def handle(self, *args, **options):
        # header = HeaderPhoto.objects.exclude(where='product_page')
        # brand = header.count()
        # shoes = header.filter(categories__eng_name="shoes_category").count()
        # clothes = header.filter(categories__eng_name="clothes").count()
        # accessories = header.filter(categories__eng_name="accessories").count()
        # print(brand, shoes, clothes, accessories)
        carts = ShoppingCart.objects.all()
        for cart in carts:
            s = []
            for unit in cart.product_units.all():
                s.append(unit.id)
            cart.unit_order = s
            cart.total()
            cart.save()
            print(cart.user, cart.final_amount, cart.product_units.count())







