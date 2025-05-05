from itertools import count
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):

    def handle(self, *args, **options):
        sr = SizeRow.objects.all()
        for s in sr:
            sizes = s.sizes
            for t in sizes:
                new_v = t
                if t['size'] == "Один размер":
                    t['id'] = [t['query'][0].split("_")[1]]
                # sizes = new_v
            s.sizes = sizes
            s.save()

