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
            query = """EXPLAIN SELECT DISTINCT "products_product"."id", "products_product"."rel_num" FROM "products_product" INNER JOIN "shipping_productunit" ON ("products_product"."id" = "shipping_productunit"."product_id") INNER JOIN "shipping_productunit_size" ON ("shipping_productunit"."id" = "shipping_productunit_size"."productunit_id") INNER JOIN "products_sizetranslationrows" ON ("shipping_productunit_size"."sizetranslationrows_id" = "products_sizetranslationrows"."id") LEFT OUTER JOIN "shipping_productunit_size_table" ON ("shipping_productunit"."id" = "shipping_productunit_size_table"."productunit_id") WHERE ("products_product"."available_flag" AND NOT "products_product"."is_custom" AND ("shipping_productunit_size"."sizetranslationrows_id" IN (247) OR ("products_sizetranslationrows"."is_one_size" AND "shipping_productunit_size_table"."sizetable_id" IN (10)))) ORDER BY "products_product"."rel_num" DESC LIMIT 60
"""
            with connection.cursor() as cursor:
                cursor.execute(query)
                explain_result = cursor.fetchall()
            return explain_result

        sql_query = """SELECT "products_product"."id" FROM "products_product" INNER JOIN "products_product_gender" ON ("products_product"."id" = "products_product_gender"."product_id") INNER JOIN "products_gender" ON ("products_product_gender"."gender_id" = "products_gender"."id") WHERE ("products_product"."available_flag" AND NOT "products_product"."is_custom" AND "products_gender"."name" IN (M))
"""
        explain_result = explain_query()
        for row in explain_result:
            print(row)
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
