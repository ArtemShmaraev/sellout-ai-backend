import json
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from time import time
import requests
from django.db.models import Sum
import math
from django.db.models import Count
from products.models import Product  # Замените products.models на ваш путь к модели Product

class Command(BaseCommand):
    def handle(self, *args, **options):

        grouped_products = (
            Product.objects
            .values('spu_id')
            .annotate(total_count=Count('spu_id'))
            .filter(total_count__gt=1)
        )

        # Вывод результатов
        for group in grouped_products:
            spu_id = group['spu_id']
            total_count = group['total_count']

            print(f"Товары с SPU_ID {spu_id}: {total_count} шт.")
            # Получение товаров для текущего spu_id
            products_for_spu_id = Product.objects.filter(spu_id=spu_id, has_many_colors=False).order_by("min_price").values_list("id", flat=True)
            # print(products_for_spu_id.values("has_many_colors"))
            products = Product.objects.filter(id__in=products_for_spu_id)
            # print()
            products.update(score_product_page=-5000)
            # for p in products_for_spu_id:
            #     print(p.score_product_page)