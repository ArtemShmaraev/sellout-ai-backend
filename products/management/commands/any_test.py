from itertools import count

from django.core import signing
from django.core.management.base import BaseCommand
import json

from orders.models import ShoppingCart
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo
from django.core.exceptions import ObjectDoesNotExist
from shipping.models import ProductUnit
from users.models import User, EmailConfirmation
from products.tools import get_text

class Command(BaseCommand):

    def handle(self, *args, **options):
        hps = HeaderPhoto.objects.all()
        for h in hps:
            h.header_text = get_text(h, [])
            h.save()





