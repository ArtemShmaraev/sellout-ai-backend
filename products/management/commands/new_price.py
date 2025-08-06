import random
from itertools import count
from time import time

from django.core import signing
from django.core.management.base import BaseCommand
import json

from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery, F, BooleanField, Case, When

from orders.models import ShoppingCart, Status

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo, SizeTable, SizeTranslationRows
from django.core.exceptions import ObjectDoesNotExist

from products.serializers import ProductMainPageSerializer
from shipping.models import ProductUnit, DeliveryType, AddressInfo
from users.models import User, EmailConfirmation, UserStatus
from products.tools import get_text
from products.formula_price import formula_price

class Command(BaseCommand):

    def handle(self, *args, **options):
        products = Product.objects.filter(available_flag=True)
        user_status = UserStatus.objects.get(name="Amethyst")
        for page in range(0, products.count(), 100):
            products_page = products[page:page + 100]
            print(page)
            for product in products_page:
                for unit in product.product_units.all():
                    price = formula_price(product, unit, user_status)
                    unit.start_price = price['start_price']
                    unit.final_price = price['final_price']
                    unit.save()
                product.update_min_price()


