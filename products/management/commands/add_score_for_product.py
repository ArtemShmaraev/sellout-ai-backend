from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from time import time
import requests
from django.db.models import Sum
import math
from products.models import Product  # Замените products.models на ваш путь к модели Product

class Command(BaseCommand):
    def handle(self, *args, **options):
        products = Product.objects.filter(available_flag=True, is_custom=False, likes_month=-1)
        ck = products.count()
        print(ck)
        s = []
        k = 0
        t = time()

        def process_product(product):
            nonlocal k
            try:
                k += 1
                if k % 10 == 0:
                    print(k, ck, time() - t)

                total_score_line = product.lines.all().aggregate(Sum('score_product_page'))['score_product_page__sum']
                num = product.lines.count()

                if num > 0:
                    average_score_type = round((total_score_line) / (num))
                else:
                    average_score_type = 0

                collab = product.collab
                if collab is not None:
                    average_score_type += collab.score_product_page

                if product.rel_num > 0:
                    normalize_rel_num = min(10000, round(math.log(product.rel_num, 1.0016)))
                else:
                    normalize_rel_num = 0
                product.normalize_rel_num = normalize_rel_num

                total_score = min(10000, round((average_score_type * 0.5 * 100) + (normalize_rel_num * 0.5)))
                product.score_product_page = total_score
                try:
                    old_likes = product.rel_num
                    new_likes = requests.get(f"https://spucdn.dewu.com/dewu/commodity/detail/simple/{product.spu_id}.json").json()['data']["favoriteCount"]['count']
                    likes_month = new_likes - old_likes
                    product.likes_month = likes_month
                except:
                    product.likes_month = 0
                product.save()
            except Exception as e:
                print(f"Error processing product {product.id}: {e}")

        with ThreadPoolExecutor(max_workers=8) as executor:
            for page_num in range(0, products.count(), 100):
                page_products = products[page_num:page_num+100]
                executor.map(process_product, page_products)
                k += len(page_products)
                if k % 10 == 0:
                    print(k, ck, time() - t, page_num)
