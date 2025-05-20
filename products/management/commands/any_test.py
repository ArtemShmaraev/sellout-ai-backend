from itertools import count

from django.core import signing
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, HeaderPhoto
from django.core.exceptions import ObjectDoesNotExist

from users.models import User, EmailConfirmation


class Command(BaseCommand):

    def handle(self, *args, **options):
        ph = HeaderPhoto.objects.filter(type="desktop")
        ph = ph.filter(where="product_page")
        for p in ph:

            if len(p.lines.all()) == 0:
                print(p.photo.url)
                print(p.type)
                print(p.where)
                print(p.collabs.all())


