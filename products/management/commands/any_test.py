from itertools import count

from django.core import signing
from django.core.management.base import BaseCommand
import json

from orders.models import ShoppingCart
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo
from django.core.exceptions import ObjectDoesNotExist
from shipping.models import ProductUnit, DeliveryType
from users.models import User, EmailConfirmation
from products.tools import get_text

class Command(BaseCommand):

    def handle(self, *args, **options):


        # di = DeliveryType.objects.all()
        # for d in di:
        #     d.view_name = f"{d.days_min}-{d.days_max}"
        #     d.save()
        ps = Product.objects.all()
        # ps.delete()
        s = set()
        ps.delete()
        for p in ps:
            if not p.brands.exists():
                s.add(p.spu_id)
        print(sorted(s))












