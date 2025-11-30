import math
import random
from itertools import count
from time import time

import requests
from django.core import signing
from django.core.management.base import BaseCommand
import json

from django.core.paginator import Paginator
from django.db import transaction, connection
from django.db.models import OuterRef, Subquery, F, BooleanField, Case, When, Count, Max

from orders.models import ShoppingCart, Status, OrderUnit, Order

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo, SizeTable, SizeTranslationRows
from django.core.exceptions import ObjectDoesNotExist

from products.serializers import ProductMainPageSerializer
from promotions.models import PromoCode
from shipping.models import ProductUnit, DeliveryType, AddressInfo
from users.models import User, EmailConfirmation, UserStatus
from products.tools import get_text


class Command(BaseCommand):

    def handle(self, *args, **options):

        # Измеряем время выполнения запроса к базе данных
        pus = Product.objects.filter(up_score=False)
        count = pus.count()
        print(count)
        k = 0
        kk = 0
        for page in range(0, count, 100):
            pus_page = pus[page:page + 100]
            kk += 100

            for p in pus_page:
                sizes = [size for pu in p.product_units.filter(availability=True) for size in pu.size.all()]
                p.sizes.add(*sizes)
                p.up_score = True
                p.save()
            k += 100
            if k % 1000 == 0:
                print(k, count)

# # Обработка результатов запроса
# for row in results:
#     print(row[0], row[1])
