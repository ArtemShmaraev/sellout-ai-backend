import math
import random
from itertools import count
from time import time

import requests
from django.core.management.base import BaseCommand
import json

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import OuterRef, Subquery, F, BooleanField, Case, When, Count, Max, Q, Min, Sum


from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo, SizeTable, SizeTranslationRows, SGInfo
class Command(BaseCommand):

    def handle(self, *args, **options):
        products = Product.objects.filter(categories__name__in=['Кеды', "Кроссовки"], available_flag=True).order_by("-rel_num")

        print(products)
        ck = products.count()
        print(ck)
        s = []
        k = 0
        t = time()
        for page in range(0, 1000, 100):
            page_products = products[page:page + 100]
            for product in page_products:
                k += 1
                if k % 10 == 0:
                    print(k, ck, time() - t)

                old_likes = product.rel_num
                new_likes = \
                requests.get(f"https://spucdn.dewu.com/dewu/commodity/detail/simple/{product.spu_id}.json").json()[
                    'data']["favoriteCount"]['count']
                likes_month = new_likes - old_likes
                product.likes_month = likes_month
                product.save()




