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
        products = Product.objects.filter(categories__name__in=['Кеды', "Кроссовки"], available_flag=True, score_product_page=0)

        print(products)
        ck = products.count()
        print(ck)
        s = []
        k = 0
        t = time()
        with open('likes.txt', 'w') as f:

            for page in range(0, 1000, 100):
                page_products = products[page:page + 100]
                for product in page_products:
                    k += 1
                    if k % 1000 == 0:
                        print(k, ck, time() - t)
                    # # cat = product.categories.order_by("-id").first()
                    total_score_line = product.lines.all().aggregate(Sum('score_product_page'))['score_product_page__sum']
                    num = product.lines.count()



                    if num > 0:
                        # Рассчитываем среднее значение поля score
                        average_score_type = round((total_score_line) / (num))
                    else:
                        average_score_type = 0


                    collab = product.collab
                    if collab is not None:
                        average_score_type += collab.score_product_page


                    normalize_rel_num = min(100, round(math.log(product.rel_num, 1.16)))

                    total_score = min(100, round((average_score_type * 0.5) + (normalize_rel_num * 0.5)))
                    product.score_product_page = total_score




                    # old_likes = product.rel_num
                    # new_likes = requests.get(f"https://spucdn.dewu.com/dewu/commodity/detail/simple/{product.spu_id}.json").json()['data']["favoriteCount"]['count']
                    # likes_month = new_likes - old_likes
                    # # s.append(likes_month)
                    # f.write(f"{likes_month} {old_likes} {new_likes}\n")
                    # print(k)




                    # print(total_score)
                    product.save()
                    # print(product.score_product_page, normalize_rel_num, average_score_type)



