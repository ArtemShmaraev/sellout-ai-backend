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

        def explain_query():
            query = """SELECT "products_product"."id" FROM "products_product" WHERE "products_product"."id" IN (SELECT U0."id" FROM "products_product" U0 WHERE (U0."available_flag" AND NOT U0."is_custom")) ORDER BY "products_product"."score_product_page" DESC"""
            with connection.cursor() as cursor:
                cursor.execute(query)
                explain_result = cursor.fetchall()
            return explain_result

        t = time()
        explain_result = explain_query()
        # print(explain_result)
        print(time() - t)

# # Обработка результатов запроса
# for row in results:
#     print(row[0], row[1])
