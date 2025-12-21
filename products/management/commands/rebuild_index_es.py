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
        def choose_product_by_price(price):
            if price <= 5000:
                return "Экономичный выбор"
            elif price <= 10000:
                return "Бюджетный вариант"
            elif price <= 15000:
                return "Средний уровень"
            elif price <= 20000:
                return "Премиум качество"
            elif price <= 30000:
                return "Высококлассный продукт"
            elif price <= 40000:
                return "Люксовый товар"
            elif price <= 60000:
                return "Элитный выбор"
            elif price <= 100000:
                return "Эксклюзивный продукт"
            else:
                return "Исключительная роскошь"

        def remove_chinese_chars(input_string):
            return re.sub(r'[\u4e00-\u9fff]+', '', input_string)

        def unique_words(input_string):
            words = input_string.split()
            unique_words = list(OrderedDict.fromkeys(words))
            output_string = " ".join(unique_words)
            return output_string

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

        lines = open("suggest_brand.txt", encoding="utf-8").read().strip().split('\n')

        # Создание словаря
        dict_brand = {}
        for line in lines:
            key, *values = line.split(', ')
            dict_brand[key.lower()] = list(values)

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
                        'weight': 70000 - level - dop - length
                    }]
                else:
                    line_doc.suggest.append({
                        'input': [slice],
                        'weight': max(0, 70000 - level - (i * 10) - dop - length)
                    })
            line_doc.save()

        collabs = Collab.objects.all()
        for collab in collabs:
            collab_doc = SuggestDocument()
            collab_doc.name = collab.name
            collab_doc.url = f"collab={collab.query_name}"
            collab_doc.type = "Коллаборация"
            collab_name = collab.name.split()
            for i in range(len(collab_name)):
                slice = " ".join(collab_name[i:])
                length = len(slice)
                if i == 0:
                    collab_doc.suggest = [{
                        'input': [slice, collab.name.replace(" x ", " ")],
                        'weight': 50000 - length
                    }]
                else:
                    collab_doc.suggest.append({
                        'input': [slice],
                        'weight': max(0, 50000 - (i * 10) - length)
                    })
            collab_doc.save()

        cats = open("suggest_category.txt", encoding="utf-8").read().strip().split('\n')

        # Создание словаря
        dict_cat = {}
        for cat in cats:
            key, *values = cat.split(', ')
            dict_cat[key.lower()] = list(values)


        cats = Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие')
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
                        'weight': 50000 - length
                    }]
                else:
                    cat_doc.suggest.append({
                        'input': [slice],
                        'weight': max(50000 - (i * 10) - length, 0)
                    })
            cat_doc.save()

        self.stdout.write(self.style.SUCCESS('SUG indexing complete.'))

        f = True
        all_cat_name = set(list(Category.objects.all().values_list("name", flat=True)))
        if f:
            # product_index = ProductDocument._index
            # if product_index.exists():
            #     self.stdout.write(self.style.SUCCESS('Deleting existing index...'))
            #     product_index.delete()
            #
            # self.stdout.write(self.style.SUCCESS('Creating index...'))
            #
            # product_index.create()

            products = Product.objects.filter(available_flag=True, is_custom=False)
            count = products.count()
            print("Товаров", count)
            k = 0
            kk = 0
            for page in range(0, count, 100):
                page_product = products[page:page + 100]

                for product in page_product:
                    kk += 1
                    if kk * 100 / count > k:
                        self.stdout.write(self.style.SUCCESS(f"{k} %"))
                        k += 1
                    product_doc = ProductDocument(meta={'id': product.id})

                    lines = product.lines.exclude(name__icontains='Все').exclude(name__icontains='Другие').exclude(
                        parent_line=None)
                    main_line = ""
                    if lines.count() > 1:
                        main_line = lines.order_by('-id').first().name
                        product_doc.main_line = main_line

                    categories = product.categories.exclude(name__icontains='Все').exclude(
                        name__contains='Другие')
                    if categories.count() > 1:
                        main_category = categories.order_by("-id").first()
                        product_doc.main_category = main_category.name
                        product_doc.main_category_eng = main_category.eng_name

                    brands = [brand.name for brand in product.brands.all()]
                    materials = [material.name for material in product.materials.all().exclude(name="Другой")]
                    categories = [category.name for category in
                                  product.categories.exclude(name__icontains='Все').exclude(
                                      name__contains='Другие').exclude(name__icontains='Вся')]


                    suggest_categories = [" ".join(dict_cat.get(category.name.lower(), [])) for category in
                                          product.categories.exclude(name__icontains='Все').exclude(
                                              name__contains='Другие').exclude(name__icontains='Вся')]

                    categories_eng = [category.eng_name for category in
                                      product.categories.exclude(name__icontains='Все').exclude(
                                          name__contains='Другие').exclude(name__icontains='Вся')]
                    lines = [line.name for line in
                             product.lines.exclude(name__icontains='Все').exclude(name__contains='Другие')]

                    suggest_brand = [" ".join(dict_brand.get(brand.name.lower(), [])) for brand in
                             product.brands.all()]
                    colors = [color.name for color in product.colors.all()] + [color.russian_name for color in
                                                                               product.colors.all()]

                    genders_rus = {"Male": "мужской", "Female": "женский", "Kids": "детский", "M": "мужской",
                                   "F": "женский", "K": "детский"}
                    gender = [genders_rus[gender.name] for gender in product.gender.all()]

                    try:
                        title = product.platform_info["poizon"]["title"]

                    except:
                        title = ""

                    full_name = f'{" ".join(brands)} {product.collab.name if product.collab is not None else ""} {main_line} {product.model if product.model not in all_cat_name else ""} ' \
                                f'{product.colorway} {" ".join(categories)} {" ".join(suggest_categories)} {" ".join(suggest_brand)} {" ".join(categories_eng)} {" ".join(colors)} {" ".join(materials)} {" ".join(gender)} {title} {product.manufacturer_sku}'.lower().replace(
                        "_", " ").replace("/", "")

                    full_name = unique_words(remove_chinese_chars(full_name))
                    product_doc.brands = brands
                    product_doc.text_price = choose_product_by_price(product.min_price)
                    product_doc.materials = materials
                    product_doc.categories = categories
                    product_doc.categories_eng = categories_eng
                    product_doc.lines = lines
                    product_doc.model = product.model if product.model not in all_cat_name else None
                    product_doc.colorway = product.colorway
                    product_doc.manufacturer_sku = product.manufacturer_sku
                    product_doc.min_price = product.min_price
                    product_doc.collab = product.collab.name if (
                                product.is_collab and product.collab is not None) else None
                    product_doc.colors = colors

                    product_doc.gender = gender
                    product_doc.score_product_page = product.score_product_page
                    product_doc.rel_num = product.rel_num
                    product_doc.full_name = full_name
                    product_doc.save()
            self.stdout.write(self.style.SUCCESS(f"{k} %"))

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
