from itertools import count
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):

    def handle(self, *args, **options):
        collabs = Collab.objects.all()
        for collab in collabs:
            collab.save()

