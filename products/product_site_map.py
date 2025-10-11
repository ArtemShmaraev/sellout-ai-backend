import math
from math import log
from django.urls import reverse
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.contrib.sitemaps import Sitemap
from .models import Product  # Предположим, что у вас есть модель Product

class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority_default = 0.5
    #
    def items(self):
        all_products = Product.objects.filter(available_flag=True)
        total_products = all_products.count()
        products_per_sitemap = total_products // 100

        # Создаем список списков товаров для каждой карты
        sitemaps = []
        start_index = 0
        end_index = products_per_sitemap
        for i in range(100):
            sitemap_products = all_products[start_index:end_index]
            sitemaps.append(sitemap_products)
            start_index = end_index
            end_index += products_per_sitemap

        return sitemaps

    def lastmod(self, obj):
        return obj.last_upd

    def location(self, obj):
        return reverse('product_detail', args=[obj.slug])  # Предположим, что ваш URL-путь к товару - 'product_detail'

    def calculate_priority(self, obj):
        rel_num = obj.rel_num
        priority_value = min(1, math.log2(rel_num) / 24)
        return round(priority_value, 2)  # Округляем до 2 знаков после запятой

    def priority(self, obj):
        return self.calculate_priority(obj)
