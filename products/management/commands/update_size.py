import math
import random
from itertools import count
from time import time, sleep

import requests
from django.core import signing
from django.core.cache import cache
from django.core.management.base import BaseCommand
import json
import xml.etree.ElementTree as ET
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import OuterRef, Subquery, F, BooleanField, Case, When, Count, Max, Q, Min, Sum

from orders.models import ShoppingCart, Status, OrderUnit, Order
from orders.serializers import OrderSerializer
from orders.tools import send_email_confirmation_order
from products.add_product_api import add_product_v2, add_product_api, add_products_spu_id_api

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo, SizeTable, SizeTranslationRows, SGInfo, RansomRequest
from django.core.exceptions import ObjectDoesNotExist

from products.serializers import ProductMainPageSerializer, ProductSerializer
from promotions.models import PromoCode
from shipping.models import ProductUnit, DeliveryType, AddressInfo
from users.models import User, EmailConfirmation, UserStatus, Partner, SpamEmail
from products.tools import get_text
from utils.models import Currency


class Command(BaseCommand):

    def handle(self, *args, **options):
        def update_gender_size(product):
            sizes = []
            genders = list(product.gender.values_list('name', flat=True))
            for unit in product.product_units.filter(availability=True):
                for s in unit.size.all():
                    if 'Европейский(EU)' in s.row and not ("M" in genders and "F" in genders):
                        size_eu = float(s.row['Европейский(EU)'])
                        if size_eu <= 41:
                            product.gender.add(Gender.objects.get(name="F"))
                        if size_eu >= 40:
                            product.gender.add(Gender.objects.get(name="M"))
                    sizes.append(s.id)

            product.sizes.clear()
            product.sizes.add(*SizeTranslationRows.objects.filter(id__in=sizes))


        product = Product.objects.filter(is_custom=False, categories__in=Category.objects.filter(name__in=["Кроссовки", "Кеды", "Зимние кроссовки и ботинки"]))
        count = product.count()
        for page in range(0, count, 100):
            page_product = Product.objects.filter(is_custom=False, categories__in=Category.objects.filter(name__in=["Кроссовки", "Кеды", "Зимние кроссовки и ботинки"])).order_by("id")[page: page + 100]
            for product in page_product:
                update_gender_size(product)
            print(page, count)

