import json
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from time import time
import requests
from django.db.models import Sum
import math
from products.models import Product  # Замените products.models на ваш путь к модели Product
from products.tools import update_score_clothes, update_score_sneakers


class Command(BaseCommand):
    def handle(self, *args, **options):
        products = Product.objects.filter(available_flag=True, is_custom=False, categories__name__in=["Кеды", "Кроссовки"])


        ck = products.count()
        print(ck)
        k = 0
        t = time()


        for page_num in range(0, ck, 100):
            page_products = products[page_num:page_num+100]
            k += 100
            print(k, ck, time() - t)
            for product in page_products:
                update_score_sneakers(product)



        print()
        products = Product.objects.filter(available_flag=True, is_custom=False, up_score=False).exclude(categories__name__in=["Кеды", "Кроссовки"]).order_by("score_product_page")
        # products.update(up_score=False)
        dk = 1
        ck = products.count()
        print(ck)

        k = 0
        t = time()

        with open('edit_brand+category_score.json', 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        for page_num in range(0, ck, 100):
            page_products = products[page_num:page_num + 100]
            k += 100
            print(k, ck, time() - t)
            for product in page_products:
                update_score_clothes(product)



