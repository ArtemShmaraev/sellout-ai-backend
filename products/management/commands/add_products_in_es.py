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

        connections.create_connection(
            hosts=[ELASTIC_HOST],
            http_auth=("elastic", "espass2024word"),
            scheme="http",  # Используйте "https", если ваш сервер настроен для безопасного соединения
            port=9200,
        )
        lines = open("suggest_brand.txt", encoding="utf-8").read().strip().split('\n')

        dict_brand = {}
        for line in lines:
            key, *values = line.split(', ')
            dict_brand[key.lower()] = list(values)
        cats = open("suggest_category.txt", encoding="utf-8").read().strip().split('\n')

        dict_cat = {}
        for cat in cats:
            key, *values = cat.split(', ')
            dict_cat[key.lower()] = list(values)



        all_cat_name = set(list(Category.objects.all().values_list("name", flat=True)))

        products = Product.objects.filter(is_custom=False, in_search=False)
        count = products.count()
        print("Товаров", count)
        k = 0
        kk = 0
        for page in range(0, count, 100):
            page_product = products[:100]

            for product in page_product:
                try:
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
                    product.in_search = True
                    product.save()
                except:
                    continue
        self.stdout.write(self.style.SUCCESS(f"{k} %"))
        self.stdout.write(self.style.SUCCESS('Indexing complete.'))
