import re
import time

from django.core.management.base import BaseCommand
from elasticsearch_dsl.connections import connections
from products.documents import ProductDocument, LineDocument, CategoryDocument, ColorDocument, CollabDocument, \
    SuggestDocument  # Замените на путь к вашему документу
from products.models import Product, Line, Category, Color, Collab, Brand  # Замените на путь к вашей модели Product
from sellout.settings import ELASTIC_HOST
from collections import OrderedDict


class Command(BaseCommand):
    help = 'Index products in Elasticsearch'

    def handle(self, *args, **options):

        hosts = [f"{ELASTIC_HOST}:9200"]
        connections.create_connection(
            hosts=[ELASTIC_HOST],
            http_auth=("elastic", "espass2024word"),
            scheme="http",  # Используйте "https", если ваш сервер настроен для безопасного соединения
            port=9200,
        )
        # connections.create_connection(hosts=hosts)  # Замените на адрес вашего Elasticsearch-сервера

        sug_index = SuggestDocument._index
        if sug_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing SUG index...'))
            sug_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating SUG index...'))
        sug_index.create()
        #
        #
        #
        lines = open("suggest_brand.txt", encoding="utf-8").read().strip().split('\n')

        # Создание словаря
        dict_brand = {}
        for line in lines:
            key, *values = line.split(', ')
            dict_brand[key.lower()] = list(values)
        #
        lines = Line.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие')
        for line in lines:

            line_doc = SuggestDocument()
            line_doc.name = line.name
            line_doc.type = "Линейка"
            line_doc.url = f"line={line.full_eng_name.rstrip('_')}"
            level = 1
            current_line = line
            while current_line.parent_line is not None:
                current_line = current_line.parent_line
                level += 1
            brand = current_line.view_name

            line_name = line.view_name.split()
            dop = 0
            match = re.search(r'\d+', " ".join(line_name[:]))
            if match:
                dop = int(match.group())
            for i in range(len(line_name)):
                slice = " ".join(line_name[i:])
                length = len(slice)

                if i == 0:
                    line_doc.suggest = [{
                        'input': [slice] + dict_brand.get(line.view_name.lower(), []),
                        'weight': 70000 - level - dop - length + Product.objects.filter(lines=line).count()
                    }]
                else:
                    line_doc.suggest.append({
                        'input': [slice],
                        'weight': max(0, 70000 - level - (i * 10) - dop - length) + Product.objects.filter(lines=line).count()
                    })
            line_doc.save()

        collabs = Collab.objects.all()
        for collab in collabs:
            collab_doc = SuggestDocument()
            collab_doc.name = collab.name
            collab_doc.url = f"collab={collab.query_name.rstrip('_')}"
            collab_doc.type = "Коллаборация"
            collab_name = collab.name.split()
            for i in range(len(collab_name)):
                slice = " ".join(collab_name[i:])
                length = len(slice)
                if i == 0:
                    collab_doc.suggest = [{
                        'input': [slice, collab.name.replace(" x ", " ")],
                        'weight': 50000 - length + Product.objects.filter(collab=collab).count()
                    }]
                else:
                    collab_doc.suggest.append({
                        'input': [slice],
                        'weight': max(0, 50000 - (i * 10) - length) + Product.objects.filter(collab=collab).count()
                    })
            collab_doc.save()
        #
        cats = open("suggest_category.txt", encoding="utf-8").read().strip().split('\n')
        #
        # # Создание словаря
        dict_cat = {}
        for cat in cats:
            key, *values = cat.split(', ')
            dict_cat[key.lower()] = list(values)
        #
        #
        cats = Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие').exclude(name__icontains='Вся')
        for cat in cats:
            cat_doc = SuggestDocument()
            cat_doc.name = cat.name
            cat_doc.type = "Категория"
            cat_doc.url = f"category={cat.eng_name.rstrip('_')}"
            cat_name = cat.name.split()
            for i in range(len(cat_name)):
                slice = " ".join(cat_name[i:])
                length = len(slice)
                if i == 0:
                    cat_doc.suggest = [{
                        'input': [slice, cat.eng_name] + dict_cat.get(cat.name.lower(), []),
                        'weight': 50000 - length + Product.objects.filter(categories=cat).count()
                    }]
                else:
                    cat_doc.suggest.append({
                        'input': [slice],
                        'weight': max(50000 - (i * 10) - length, 0) + Product.objects.filter(categories=cat).count()
                    })
            cat_doc.save()

        self.stdout.write(self.style.SUCCESS('SUG indexing complete.'))

        s1 = Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие').count()
        s2 = Line.objects.filter(parent_line=None).count()
        print(s1 * s2)
        kkk = 0
        for category in Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие'):
            for line in Line.objects.filter(parent_line=None):
                kkk += 1
                print(kkk)
                if Product.objects.filter(categories=category, lines=line).count() > 0:
                    cat_doc = SuggestDocument()
                    cat_doc.name = f"{category.name} {line.view_name}"
                    cat_doc.type = "Категория"
                    cat_doc.url = f"category={category.eng_name.rstrip('_')}&line={line.full_eng_name.rstrip('_')}"

                    cat_doc.suggest = [{
                        'input': [f"{category.name} {line.view_name}", f"{line.view_name} {category.name}"],
                        'weight': 40000 - len(f"{category.name} {line.view_name}") + Product.objects.filter(categories=category, lines=line).count()
                    }]
                    cat_doc.save()

        product_index = ProductDocument._index
        if product_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing index...'))
            product_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating index...'))

        product_index.create()



        line_index = LineDocument._index
        if line_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing line index...'))
            line_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating line index...'))
        line_index.create()

        lines = Line.objects.all().exclude(name__icontains='Все').exclude(name__contains='Другие')

        for line in lines:

            line_doc = LineDocument(meta={'id': line.id})
            line_doc.name = line.view_name
            if line.parent_line is None:
                line_doc.suggest = {
                    'input': [line.view_name],
                    'weight': 1
                }
            line_doc.save()

        self.stdout.write(self.style.SUCCESS('Line indexing complete.'))

        category_index = CategoryDocument._index
        if category_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing category index...'))
            category_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating category index...'))
        category_index.create()

        categories = Category.objects.all().exclude(name__icontains='Все').exclude(name__contains='Другие')

        for category in categories:
            category_doc = CategoryDocument(meta={'id': category.id})
            category_doc.name = category.name
            category_doc.save()
            category_doc.suggest = {
                'input': [category.name],
                'weight': 1
            }

        self.stdout.write(self.style.SUCCESS('Category indexing complete.'))

        color_index = ColorDocument._index
        if color_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing color index...'))
            color_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating color index...'))
        color_index.create()

        colors = Color.objects.all()

        for color in colors:
            if color.russian_name != "":
                print(color.russian_name)
                color_doc = ColorDocument(meta={'id': color.id})
                color_doc.russian_name = color.russian_name
                color_doc.eng_name = color.name
                color_doc.save()

        self.stdout.write(self.style.SUCCESS('Color indexing complete.'))

        collab_index = CollabDocument._index
        if collab_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing collab index...'))
            collab_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating collab index...'))
        collab_index.create()

        collabs = Collab.objects.filter(is_main_collab=True)

        for collab in collabs:
            collab_doc = CollabDocument(meta={'id': collab.id})
            collab_doc.name = collab.name
            collab_doc.save()

        self.stdout.write(self.style.SUCCESS('Collab indexing complete.'))

        self.stdout.write(self.style.SUCCESS('Indexing complete.'))
