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
        return Product.objects.filter(available_flag=True)

    def lastmod(self, obj):
        return obj.last_upd   # Предполагается, что у вас есть поле updated_at в вашей модели Product

    def location(self, obj):
        return reverse('product_detail', args=[obj.slug])  # Предположим, что ваш URL-путь к товару - 'product_detail'

    def calculate_priority(self, obj):
        rel_num = obj.rel_num
        priority_value = min(1, math.log2(rel_num) / 24)
        return round(priority_value, 2)  # Округляем до 2 знаков после запятой

    def priority(self, obj):
        return self.calculate_priority(obj)
