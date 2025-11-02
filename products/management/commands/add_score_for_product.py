from concurrent.futures import ThreadPoolExecutor
from django.core.management.base import BaseCommand
from time import time
import requests
from django.db.models import Sum
import math
from products.models import Product  # Замените products.models на ваш путь к модели Product

class Command(BaseCommand):
    def handle(self, *args, **options):
        products = Product.objects.filter(available_flag=True, is_custom=False, categories__name__in=["Кеды", "Кроссовки"]).order_by("-score_product_page")

        ck = products.count()
        print(ck)
        k = 0
        t = time()


        for page_num in range(0, ck, 100):
            page_products = products[page_num:page_num+100]
            k += 100
            print(k, ck, time() - t)
            for product in page_products:
                total_score_line = product.lines.all().aggregate(Sum('score_product_page'))['score_product_page__sum']
                num = product.lines.count()
                score_line = 0
                if num > 0:
                    score_line = round((total_score_line) / (num))


                collab = product.collab
                score_collab = 0
                if collab is not None:
                    score_collab = collab.score_product_page

                normalize_rel_num = 0
                if product.rel_num > 0:
                    normalize_rel_num = min(10000, round(math.log(product.rel_num, 1.0015)))

                product.normalize_rel_num = normalize_rel_num

                if product.likes_month == -1:
                    try:
                        old_likes = product.rel_num
                        new_likes = \
                            requests.get(
                                f"https://spucdn.dewu.com/dewu/commodity/detail/simple/{product.spu_id}.json").json()[
                                'data']["favoriteCount"]['count']
                        likes_month = new_likes - old_likes
                        product.likes_month = likes_month
                    except:
                        product.likes_month = 0
                likes_week = product.likes_month // 10
                product.likes_week = likes_week

                is_new = 1 if product.is_new else 0
                my_score = product.extra_score


                PLV = 0.27 * normalize_rel_num
                D_PLV = 0.43 * min(100000 * (likes_week / normalize_rel_num), 3000)
                NEW = 700 * is_new
                TYPE_SCORE = 0.1 * (score_collab + score_line) * 100
                MY_SCORE = 0.1 * my_score
                total_score = round(PLV + D_PLV + NEW + TYPE_SCORE + MY_SCORE)
                product.score_product_page = total_score
                product.save()
                print(product.score_product_page)

