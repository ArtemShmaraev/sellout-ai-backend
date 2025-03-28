from itertools import count
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color
from django.core.exceptions import ObjectDoesNotExist
import users.models


class Command(BaseCommand):

    def create_categories(self, json_data, parent=None):

        for category_data in json_data:
            category_name = category_data['name']
            category_eng_name = category_data['eng_name']
            subcategories = category_data['subcategories']

            try:
                category = Category.objects.get(name=category_name, eng_name=category_eng_name, full_name=category_name)
            except ObjectDoesNotExist:
                category = Category(name=category_name, eng_name=category_eng_name, full_name=category_name)
                category.save()

            if parent is not None:
                category.parent_category = parent
                category.save()
                print(category)

            self.create_categories(subcategories, parent=category)

    def handle(self, *args, **options):
        gender = Gender(name="M")
        gender.save()
        gender = Gender(name="F")
        gender.save()
        gender = Gender(name="K")
        gender.save()

        gender = users.models.Gender(name="M")
        gender.save()
        gender = users.models.Gender(name="F")
        gender.save()

        all_data = json.load(open("category.json", encoding="utf-8"))["categories"]
        self.create_categories(all_data)
        print('finished')