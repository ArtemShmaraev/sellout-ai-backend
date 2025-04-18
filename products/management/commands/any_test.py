from itertools import count
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):

    def handle(self, *args, **options):
        ps = Product.objects.all()
        k = 0
        for p in ps:
            k += 1
            if p.available_flag:
                # print(p.platform_info)
                try:
                    a = json.loads(p.platform_info)['poizon']['detail']['spuId']

                except Exception as e:
                    print(p)
                    print(1)
        print('f')
