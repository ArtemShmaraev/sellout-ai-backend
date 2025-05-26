from itertools import count

from django.core import signing
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, HeaderPhoto
from django.core.exceptions import ObjectDoesNotExist
from shipping.models import ProductUnit
from users.models import User, EmailConfirmation


class Command(BaseCommand):

    def handle(self, *args, **options):
        pr = HeaderPhoto.objects.all()
        k = 0
        for p in pr:
            k += 1
            if "p" not in p.where:
                print(p.where)
        print(k)

