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
        t = time()
        product = Product.objects.all()[:200]
        s = ProductMainPageSerializer(product, many=True).data
        d = s[:]
        print(d[1])
        print(time() - t)

# # Обработка результатов запроса
# for row in results:
#     print(row[0], row[1])
