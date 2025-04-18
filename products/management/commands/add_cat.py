from itertools import count
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab
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

        collab = Collab(name="Другие коллаборации", query_name="other_collab", is_main_collab=True)
        collab.save()
        collab = Collab(name="Все коллаборации", query_name="all", is_all=True, is_main_collab=True)
        collab.save()
        main_collab = [
            "Nike x Off-White",
            "Nike x Travis Scott",
            "adidas Yeezy",
            "Nike x Supreme",
            "Nike x Union",
            "Nike x Clot",
            "Nike x Sacai",
            "Nike x Stüssy",
            "Nike x Ambush",
            "Nike x A Ma Maniére",
            "adidas x Pharrell Williams",
            "Supreme x The North Face",
            "New Balance x Salehe Bembury"
        ]
        for collab_name in main_collab:
            collab = Collab(name=collab_name, query_name="all", is_all=True, is_main_collab=True)
            collab.save()


        all_data = json.load(open("category.json", encoding="utf-8"))["categories"]
        self.create_categories(all_data)
        print('finished')
