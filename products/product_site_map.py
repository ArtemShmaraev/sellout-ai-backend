import math
import datetime

from django.urls import reverse
from django.contrib.sitemaps import Sitemap
from .models import Product

class ProductSitemap(Sitemap):
    def items(self):
        return Product.objects.filter(available_flag=True).values("slug", "last_upd", "rel_num")

    def lastmod(self, obj):
        date = obj['last_upd']
        return date
    def location(self, obj):
        return obj['slug']

    def calculate_priority(self, obj):
        rel_num = obj['rel_num']
        priority = math.log2(rel_num + 1) / 25
        return round(priority, 2)

    def priority(self, obj):
        return self.calculate_priority(obj)

    def changefreq(self, obj):
        return 'weekly'

    def limit(self):
        return 10000

    def get_urls(self, page=1, site=None, protocol="https"):
        self.limit = self.limit()  # вызываем метод limit() и присваиваем его результат переменной limit
        # site = None
        # protocol = "https"
        return super().get_urls(page=page, site=site, protocol=protocol)