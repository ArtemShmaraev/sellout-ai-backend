import json
from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from time import time
import requests
from django.db.models import Sum, Min
import math
from django.db.models import Count
from products.models import Product  # Замените products.models на ваш путь к модели Product
from products.tools import update_score_sneakers, update_score_clothes


class Command(BaseCommand):
    def handle(self, *args, **options):

        grouped_products = (
            Product.objects.filter(spu_id__gt=5718600).values('spu_id')
            .annotate(total_count=Count('spu_id'))
            .filter(total_count__gt=1)
        )

        # Вывод результатов
        for group in grouped_products:
            spu_id = group['spu_id']
            total_count = group['total_count']


            print(f"Товары с SPU_ID {spu_id}: {total_count} шт.")
            # Получение товаров для текущего spu_id
            cheapest_product = \
            Product.objects.filter(spu_id=spu_id, has_many_colors=False, min_price__gt=0).order_by("min_price").first()
            if cheapest_product is not None:
                cats = cheapest_product.categories.values_list("name", flat=True)
                if "Кеды" in cats or "Кроссовки" in cats:
                    update_score_sneakers(cheapest_product)
                else:
                    update_score_clothes(cheapest_product)
                if cheapest_product is not None:
                    products_for_spu_id = Product.objects.filter(spu_id=spu_id, has_many_colors=False).exclude(id=cheapest_product.id).values_list("id", flat=True)
                    products = Product.objects.filter(id__in=products_for_spu_id)
                else:
                    # Handle the case where there is no product with the specified spu_id
                    products = None
            # print()
                products.update(score_product_page=-5000)
            # for p in products_for_spu_id:
            #     print(p.score_product_page)