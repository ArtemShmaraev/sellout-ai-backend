from itertools import count

from django.core import signing
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo
from django.core.exceptions import ObjectDoesNotExist
from shipping.models import ProductUnit
from users.models import User, EmailConfirmation
from products.tools import get_text

class Command(BaseCommand):

    def handle(self, *args, **options):
        # header = HeaderPhoto.objects.exclude(where='product_page')
        # brand = header.count()
        # shoes = header.filter(categories__eng_name="shoes_category").count()
        # clothes = header.filter(categories__eng_name="clothes").count()
        # accessories = header.filter(categories__eng_name="accessories").count()
        # print(brand, shoes, clothes, accessories)
        dvs = DewuInfo.objects.all()
        k= 0
        for dv in dvs:
            k += 1
            if k % 1000 == 0:
                print(k)
            if dv.spu_id == 1178815:
                # dv = DewuInfo.objects.get(spu_id=1178815)
                print(dv.web_data['size_table'])





