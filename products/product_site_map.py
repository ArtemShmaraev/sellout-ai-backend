import math
import datetime

from django.urls import reverse
from django.contrib.sitemaps import Sitemap
from .models import Product

class ProductSitemap(Sitemap):
    def items(self):
        return Product.objects.filter(available_flag=True, is_custom=False).order_by("-score_product_page").values("slug", "last_upd", "score_product_page")

    def lastmod(self, obj):
        date = obj['last_upd']
        return date
    def location(self, obj):
        return f"/products/{obj['slug']}"

    def calculate_priority(self, obj):
        rel_num = obj['score_product_page'] / 10000
        return round(rel_num, 2)

    def priority(self, obj):
        return self.calculate_priority(obj)

    def changefreq(self, obj):
        return 'weekly'

    def limit(self):
        return 10000

    def get_urls(self, page=1, site=None, protocol="https"):
        self.limit = self.limit()  # вызываем метод limit() и присваиваем его результат переменной limit
        # print(protocol)
        # site = None
        # protocol = "https"
        return super().get_urls(page=page, site=site, protocol="https")