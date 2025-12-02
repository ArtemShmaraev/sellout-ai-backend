from itertools import count
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, HeaderText
from django.core.exceptions import ObjectDoesNotExist

from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        def add_sellout(texts, title):
            for idx, text in enumerate(texts, start=1):
                try:
                    lines = text
                    content = lines.strip()
                    if len(content) > 10:
                        print(content)
                        header_text = HeaderText(title=title, text=content, type="mobile")
                        header_text.save()
                except Exception as e:
                    print(e)

                    print(text)

        def add_line(texts):
            for idx, text in enumerate(texts, start=1):
                try:
                    lines = text.strip().split('\n')
                    if lines:
                        title = lines[0].strip()
                        content = '\n'.join(lines[1:]).strip()

                        line = Line.objects.get(name=title)
                        cat = Category.objects.get(name="Обувь")
                        header_text = HeaderText(title=title, text=content)
                        header_text.save()
                        header_text.lines.add(line)
                        gender_m = Gender.objects.get(id=1)
                        gender_f = Gender.objects.get(id=2)
                        gender_k = Gender.objects.get(id=3)

                        header_text.genders.add(gender_m)
                        header_text.genders.add(gender_f)
                        header_text.genders.add(gender_k)
                        header_text.categories.add(cat)
                        header_text.save()
                except Exception as e:
                    print(e)
                    print(text)
                    print(lines)
                    # print(text)

        def add_collab(texts):
            for idx, text in enumerate(texts, start=1):
                try:
                    lines = text.strip().split('\n')
                    if lines:
                        title = lines[0].strip()
                        content = '\n'.join(lines[1:]).strip()
                        header_text = HeaderText.objects.get(title=title)
                        header_text.text = content
                        header_text.save()

                        # collab = Collab.objects.get(name=title)
                        # cat = Category.objects.get(name="Обувь")
                        # header_text = HeaderText(title=title, text=content)
                        # header_text.save()
                        # header_text.collabs.add(collab)
                        # gender_m = Gender.objects.get(id=1)
                        # gender_f = Gender.objects.get(id=2)
                        # gender_k = Gender.objects.get(id=3)
                        #
                        # header_text.genders.add(gender_m)
                        # header_text.genders.add(gender_f)
                        # header_text.genders.add(gender_k)
                        # header_text.categories.add(cat)
                        # header_text.save()
                except:
                    print(text)

        # h = HeaderText.objects.all()
        # h.delete()
        # with open("текст для страниц/collab.txt", 'r', encoding='utf-8') as file:
        #     texts = file.read().split('\n\n')  # Разделение текстов по пустой строке
        # add_collab(texts)

        # with open("текст для страниц/line.txt", 'r', encoding='utf-8') as file:
        #     texts = file.read().split('\n\n')  # Разделение текстов по пустой строке
        # add_line(texts)
        #
        # with open("текст для страниц/shoes.txt", 'r', encoding='utf-8') as file:
        #     text = file.read()
        #     title = "Обувь"
        #     header_text = HeaderText(title=title, text=text)
        #     header_text.save()
        #     cat = Category.objects.get(name="Обувь")
        #     gender_m = Gender.objects.get(id=1)
        #     gender_f = Gender.objects.get(id=2)
        #     gender_k = Gender.objects.get(id=3)
        #
        #     header_text.genders.add(gender_m)
        #     header_text.genders.add(gender_f)
        #     header_text.genders.add(gender_k)
        #     header_text.categories.add(cat)
        #     header_text.save()

        # with open("текст для страниц/sneakers.txt", 'r', encoding='utf-8') as file:
        #     text = file.read()
        #     title = "Кроссовки"
        #     header_text = HeaderText(title=title, text=text)
        #     header_text.save()
        #     cat = Category.objects.get(name="Кроссовки")
        #     gender_m = Gender.objects.get(id=1)
        #     gender_f = Gender.objects.get(id=2)
        #     gender_k = Gender.objects.get(id=3)
        #
        #     header_text.genders.add(gender_m)
        #     header_text.genders.add(gender_f)
        #     header_text.genders.add(gender_k)
        #     header_text.categories.add(cat)
        #     header_text.save()

        with open("текст для страниц/sellout_mobile.txt", 'r', encoding='utf-8') as file:
            texts = file.read().split('\n\n\n')  # Разделение текстов по пустой строке
        add_sellout(texts, "sellout")

        # with open("текст для страниц/rec.txt", 'r', encoding='utf-8') as file:
        #     texts = file.read().split('\n\n\n')  # Разделение текстов по пустой строке
        # add_sellout(texts, "Рекомендации")
        #
        # with open("текст для страниц/new.txt", 'r', encoding='utf-8') as file:
        #     texts = file.read().split('\n\n\n')  # Разделение текстов по пустой строке
        # add_sellout(texts, "Новинки")
