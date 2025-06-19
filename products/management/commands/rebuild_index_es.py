from django.core.management.base import BaseCommand
from elasticsearch_dsl.connections import connections
from products.documents import ProductDocument, LineDocument, CategoryDocument, ColorDocument, CollabDocument, \
    SuggestDocument  # Замените на путь к вашему документу
from products.models import Product, Line, Category, Color, Collab, Brand  # Замените на путь к вашей модели Product
from sellout.settings import HOST

class Command(BaseCommand):
    help = 'Index products in Elasticsearch'

    def handle(self, *args, **options):
        hosts = [f"{HOST}:9200"]
        connections.create_connection(hosts=hosts)  # Замените на адрес вашего Elasticsearch-сервера

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
            line_doc.url = f"line={line.full_eng_name}"
            level = 1
            current_line = line
            while current_line.parent_line is not None:
                current_line = current_line.parent_line
                level += 1
            brand = current_line.view_name

            if line.parent_line is None:
                line_doc.suggest = [{
                    'input': [line.view_name] + dict_brand.get(line.view_name.lower(), []),
                    'weight': 6 - level
                }]
            else:

                line_name = line.name.replace(brand, "").strip()

                line_doc.suggest = [{
                    'input': [line.view_name],
                    'weight': 5 - level
                }]
                if line_name != line.view_name:
                    line_doc.suggest.append({
                        'input': [line_name],
                        'weight': 4 - level
                    })
            line_doc.save()

        collabs = Collab.objects.all()
        for collab in collabs:
            collab_doc = SuggestDocument()
            collab_doc.name = collab.name
            collab_doc.url = f"collab={collab.query_name}"
            collab_doc.type = "Коллаборация"
            collab_doc.suggest = [{
                'input': [collab.name, collab.name.replace(" x ", " ")],
                'weight': 4
            }]
            collab_doc.save()

        cats = Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие')
        for cat in cats:
            cat_doc = SuggestDocument()
            cat_doc.name = cat.name
            cat_doc.type = "Категория"
            cat_doc.url = f"category={cat.eng_name}"
            cat_doc.suggest = [{
                'input': [cat.name, cat.eng_name],
                'weight': 4
            }]
            cat_doc.save()

        self.stdout.write(self.style.SUCCESS('SUG indexing complete.'))

        f = True
        if f:
            product_index = ProductDocument._index
            if product_index.exists():
                self.stdout.write(self.style.SUCCESS('Deleting existing index...'))
                product_index.delete()

            self.stdout.write(self.style.SUCCESS('Creating index...'))
            product_index.create()

            products = Product.objects.all()
            count = products.count()
            k = 0
            kk = 0
            for product in products:
                kk += 1
                if kk * 100 / count > k:
                    self.stdout.write(self.style.SUCCESS(f"{k} %"))
                    k += 1
                product_doc = ProductDocument(meta={'id': product.id})

                lines = product.lines.exclude(name__icontains='Все').exclude(name__icontains='Другие')
                if lines:
                    main_line = lines.order_by('-id').first()
                    product_doc.main_line = main_line.name

                categories = product.categories.exclude(name__icontains='Все').exclude(
                                              name__contains='Другие')
                if categories:
                    main_category = categories.order_by("-id").first()
                    product_doc.main_category = main_category.name
                    product_doc.main_category_eng = main_category.eng_name




                product_doc.brands = [brand.name for brand in product.brands.all()]
                product_doc.categories = [category.name for category in
                                          product.categories.exclude(name__icontains='Все').exclude(
                                              name__contains='Другие')]
                product_doc.categories_eng = [category.eng_name for category in
                                          product.categories.exclude(name__icontains='Все').exclude(
                                              name__contains='Другие')]

                product_doc.lines = [line.name for line in
                                     product.lines.exclude(name__icontains='Все').exclude(name__contains='Другие')]
                product_doc.model = product.model
                product_doc.colorway = product.colorway
                # product_doc.russian_name = product.russian_name
                product_doc.manufacturer_sku = product.manufacturer_sku
                # product_doc.description = product.description
                product_doc.collab = product.collab.name if (product.is_collab and product.collab is not None) else None
                # product_doc.main_color = product.main_color.name if product.main_color else None
                # product_doc.colors = [color.name for color in product.colors.all()]
                # product_doc.designer_color = product.designer_color
                product_doc.gender = [gender.name for gender in product.gender.all()]
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
