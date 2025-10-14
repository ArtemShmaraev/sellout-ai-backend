import math
import random
from itertools import count
from time import time

import requests
from django.core import signing
from django.core.management.base import BaseCommand
import json

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import OuterRef, Subquery, F, BooleanField, Case, When, Count, Max, Q, Min, Sum

from orders.models import ShoppingCart, Status, OrderUnit, Order
from orders.serializers import OrderSerializer

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo, SizeTable, SizeTranslationRows, SGInfo
from django.core.exceptions import ObjectDoesNotExist

from products.serializers import ProductMainPageSerializer
from promotions.models import PromoCode
from shipping.models import ProductUnit, DeliveryType, AddressInfo
from users.models import User, EmailConfirmation, UserStatus
from products.tools import get_text
import matplotlib.pyplot as plt
from collections import Counter

class Command(BaseCommand):

    def handle(self, *args, **options):
        products = Product.objects.filter(categories__name__in=['Кеды', "Кроссовки"], available_flag=True)
        print(products)
        ck = products.count()
        k = 0
        for page in range(0, products.count(), 100):
            page_products = products[page:page + 100]
            for product in page_products:
                k += 1
                if k % 10000 == 0:
                    print(k, ck)
                # cat = product.categories.order_by("-id").first()
                total_score_line = product.lines.all().aggregate(Sum('score_product_page'))['score_product_page__sum']
                num = product.lines.count()
                # print(num, total_score_line)


                # collab = product.collab


                if num > 0:
                    # Рассчитываем среднее значение поля score
                    average_score_type = round((total_score_line) / (num))
                else:
                    average_score_type = 0

                collab_score = 0
                collab = product.collab
                if collab is not None:
                    average_score_type += collab.score_product_page
                # collab_score = collab.score_product_page
                #     num += 1
                # print(total_score_line)

                normalize_rel_num = min(100, round(math.log(product.rel_num, 1.16)))

                total_score = min(100, round((average_score_type * 0.5) + (normalize_rel_num * 0.5)))
                product.score_product_page = total_score
                product.save()
                # print(product.score_product_page, normalize_rel_num, average_score_type)



