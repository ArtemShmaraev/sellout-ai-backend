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
        order = Order.objects.get(id=153)
        order.accrue_bonuses()
        for ou in order.order_units.all():
            ou.status = Status.objects.get(name="В пути до международного склада")
            print(ou.status)
            ou.save()
        print(order.status)
        order.status = Status.objects.get(name="В пути до международного склада")
        order.save()
    #     for i in range(50):
    #         sql_query = """SELECT COUNT(*)
    # FROM products_product
    # WHERE available_flag = true AND is_custom = false;"""
    #         t = time()
    #         # Выполняем SQL-запрос
    #         with connection.cursor() as cursor:
    #             cursor.execute(sql_query)
    #             results = cursor.fetchall()
    #         # print(results)
    #         print(time() - t)

#         sql_query = """SELECT COUNT("products_product"."id")
# FROM "products_product"
# INNER JOIN "shipping_productunit" ON ("products_product"."id" = "shipping_productunit"."product_id")
# WHERE ("products_product"."available_flag" AND NOT "products_product"."is_custom" AND "shipping_productunit"."final_price" <= 10000);"""
#         t = time()
#         # Выполняем SQL-запрос
#         with connection.cursor() as cursor:
#             cursor.execute(sql_query)
#             results = cursor.fetchall()
#         print(results)
#         print(time() - t)

        # # Обработка результатов запроса
        # for row in results:
        #     print(row[0], row[1])
