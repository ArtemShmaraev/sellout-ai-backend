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
        pr = ProductUnit.objects.all()
        for p in pr:
            print(p.view_size_platform)


