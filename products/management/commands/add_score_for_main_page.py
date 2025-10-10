from itertools import count
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab
from django.core.exceptions import ObjectDoesNotExist
import users.models


class Command(BaseCommand):

    def handle(self, *args, **options):
        def update_model_scores(model_class, file_name):

            with open(file_name, 'r', encoding="utf-8") as file:
                data = json.load(file)

            for item in data:
                model_name = item.get('name')
                score = item.get('score')

                # Пытаемся найти запись по имени
                model_instance = model_class.objects.filter(name=model_name).first()

                # Если запись не найдена, создаем новую запись
                if model_instance:
                    # Если запись найдена, обновляем поле score
                    model_instance.score = score
                    model_instance.save()
                else:
                    print(model_name)

        # update_model_scores(Line, data)
        update_model_scores(Category, "categories_score.json")
        update_model_scores(Collab, "collabs_score.json")
        update_model_scores(Brand, "brands_score.json")

        print("Данные о брендах успешно обновлены.")

