from itertools import count

from django.core import signing
from django.core.management.base import BaseCommand
import json

from orders.models import ShoppingCart
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo, SizeTable
from django.core.exceptions import ObjectDoesNotExist
from shipping.models import ProductUnit, DeliveryType, AddressInfo
from users.models import User, EmailConfirmation
from products.tools import get_text

class Command(BaseCommand):

    def handle(self, *args, **options):
        # st = SizeRow.objects.all()
        #
        # for s in st:
        #     new_js = []
        #     js = s.sizes
        #
        #     name_t = s.size_tables.first().filter_name
        #     for siz in js:
        #         js = siz
        #         js['view_name_in_line'] = f"{name_t}: {siz['size']} {s.filter_logo if s.filter_logo not in ['SIZE', 'INT'] else ''}".strip()
        #         new_js.append(js)
        #     s.sizes = new_js
        #     s.save()


        # ps = ProductUnit.objects.all()
        pr = ProductUnit.objects.count()
        print(pr)
        # for p in ps:
        #     for s in p.size.all():
        #         if not s.is_one_size:
        #             table = s.table
        #             p.size_table.add(table)
        #     p.save()




        # phs = Photo.objects.all()
        # for p in phs:
        #     if not p.product.exists():
        #         p.delete()


        # # di = DeliveryType.objects.all()
        # # for d in di:
        # #     d.view_name = f"{d.days_min}-{d.days_max}"
        # #     d.save()
        # ps = Product.objects.all().values("brands", "spu_id", "id")
        # # ps.delete()
        # s = set()
        # # ps.delete()
        # list_id = []
        # for p in ps:
        #     if p["brands"] == None:
        #         s.add(p["spu_id"])
        #         list_id.append(p["id"])
        #
        # ps = Product.objects.filter(id__in=list_id)
        # ps.delete()
        #
        # print(sorted(s))
        # f = open("list.txt", "w")
        # f.write(str(sorted(s)))














