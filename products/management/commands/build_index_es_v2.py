import re
from django.core.management.base import BaseCommand
from elasticsearch_dsl.connections import connections
from products.documents import (
    ProductDocument, LineDocument, CategoryDocument,
    ColorDocument, CollabDocument, SuggestDocument
)
from products.models import Product, Line, Category, Color, Collab
from sellout.settings import ELASTIC_HOST


class Command(BaseCommand):
    help = 'Index products in Elasticsearch'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection_params = {
            'hosts': [ELASTIC_HOST],
            'http_auth': ("elastic", "espass2024word"),
            'scheme': "http",
            'port': 9200,
        }

    def _init_connection(self):
        """Initialize Elasticsearch connection."""
        connections.create_connection(**self.connection_params)

    def _load_suggestion_dict(self, filename):
        """Load suggestion dictionary from file."""
        with open(filename, encoding="utf-8") as f:
            lines = f.read().strip().split('\n')

        result = {}
        for line in lines:
            key, *values = line.split(', ')
            result[key.lower()] = values
        return result

    def _get_line_weight_params(self, line):
        """Calculate weight parameters for line suggestions."""
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

        return level, line_name, dop

    def _create_suggest_doc(self, obj, obj_type, url_field, name_field, weight_base, dict_data=None):
        """Create and save SuggestDocument for an object."""
        doc = SuggestDocument()
        doc.name = getattr(obj, name_field)
        doc.type = obj_type
        doc.url = f"{obj_type.lower()}={getattr(obj, url_field).rstrip('_')}"

        name_parts = getattr(obj, name_field).split()
        suggestions = []

        for i in range(len(name_parts)):
            slice_text = " ".join(name_parts[i:])
            length = len(slice_text)

            inputs = [slice_text]
            if i == 0:
                if dict_data:
                    inputs.extend(dict_data.get(getattr(obj, name_field).lower(), []))
                if obj_type == "Коллаборация" and hasattr(obj, 'name'):
                    inputs.append(obj.name.replace(" x ", " "))
                elif obj_type == "Категория" and hasattr(obj, 'eng_name'):
                    inputs.append(obj.eng_name)

            weight = weight_base - length
            if obj_type == "Линейка":
                level, _, dop = self._get_line_weight_params(obj)
                weight = weight - level - dop
                if i > 0:
                    weight -= (i * 10)
            elif i > 0:
                weight -= (i * 10)

            weight = max(0, weight)

            if obj_type == "Линейка":
                weight += Product.objects.filter(lines=obj).count()
            elif obj_type == "Коллаборация":
                weight += Product.objects.filter(collab=obj).count()
            elif obj_type == "Категория":
                weight += Product.objects.filter(categories=obj).count()

            suggestions.append({
                'input': inputs,
                'weight': weight
            })

        if len(suggestions) == 1:
            doc.suggest = suggestions
        else:
            doc.suggest = suggestions[0]
            for sug in suggestions[1:]:
                doc.suggest.append(sug)

        doc.save()
        return doc

    def _index_lines(self):
        """Index lines with their suggestions."""
        line_index = LineDocument._index
        if line_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing line index...'))
            line_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating line index...'))
        line_index.create()

        lines = Line.objects.exclude(name__icontains='Все').exclude(name__contains='Другие')
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

    def _index_categories(self):
        """Index categories with their suggestions."""
        category_index = CategoryDocument._index
        if category_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing category index...'))
            category_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating category index...'))
        category_index.create()

        categories = Category.objects.exclude(name__icontains='Все').exclude(name__contains='Другие')
        for category in categories:
            category_doc = CategoryDocument(meta={'id': category.id})
            category_doc.name = category.name
            category_doc.suggest = {
                'input': [category.name],
                'weight': 1
            }
            category_doc.save()

        self.stdout.write(self.style.SUCCESS('Category indexing complete.'))

    def _index_colors(self):
        """Index colors with their suggestions."""
        color_index = ColorDocument._index
        if color_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing color index...'))
            color_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating color index...'))
        color_index.create()

        colors = Color.objects.filter(russian_name__isnull=False).exclude(russian_name='')
        for color in colors:
            color_doc = ColorDocument(meta={'id': color.id})
            color_doc.russian_name = color.russian_name
            color_doc.eng_name = color.name
            color_doc.save()

        self.stdout.write(self.style.SUCCESS('Color indexing complete.'))

    def _index_collabs(self):
        """Index collaborations with their suggestions."""
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

    def _index_suggestions(self):
        """Index all suggestions."""
        sug_index = SuggestDocument._index
        if sug_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing SUG index...'))
            sug_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating SUG index...'))
        sug_index.create()

        # Load suggestion dictionaries
        dict_brand = self._load_suggestion_dict("suggest_brand.txt")
        dict_cat = self._load_suggestion_dict("suggest_category.txt")

        # Index lines
        lines = Line.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие')
        for line in lines:
            self._create_suggest_doc(line, "Линейка", "full_eng_name", "view_name", 70000, dict_brand)

        # Index collaborations
        collabs = Collab.objects.all()
        for collab in collabs:
            self._create_suggest_doc(collab, "Коллаборация", "query_name", "name", 50000)

        # Index categories
        cats = Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие').exclude(
            name__icontains='Вся')
        for cat in cats:
            self._create_suggest_doc(cat, "Категория", "eng_name", "name", 50000, dict_cat)

        # Index combined category-line suggestions
        categories = Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие')
        main_lines = Line.objects.filter(parent_line=None)

        self.stdout.write(f"Total category-line combinations to process: {categories.count() * main_lines.count()}")

        for i, category in enumerate(categories, 1):
            for j, line in enumerate(main_lines, 1):
                if Product.objects.filter(categories=category, lines=line).exists():
                    cat_doc = SuggestDocument()
                    cat_doc.name = f"{category.name} {line.view_name}"
                    cat_doc.type = "Категория"
                    cat_doc.url = f"category={category.eng_name.rstrip('_')}&line={line.full_eng_name.rstrip('_')}"

                    count = Product.objects.filter(categories=category, lines=line).count()
                    weight = 40000 - len(f"{category.name} {line.view_name}") + count

                    cat_doc.suggest = [{
                        'input': [
                            f"{category.name} {line.view_name}",
                            f"{line.view_name} {category.name}"
                        ],
                        'weight': weight
                    }]
                    cat_doc.save()

        self.stdout.write(self.style.SUCCESS('SUG indexing complete.'))

    def _index_products(self):
        """Index products."""
        product_index = ProductDocument._index
        if product_index.exists():
            self.stdout.write(self.style.SUCCESS('Deleting existing product index...'))
            product_index.delete()

        self.stdout.write(self.style.SUCCESS('Creating product index...'))
        Product.objects.all().update(in_search=False)
        product_index.create()

        self.stdout.write(self.style.SUCCESS('Product index created (bulk indexing would go here).'))

    def handle(self, *args, **options):
        self._init_connection()

        # Process indexes in optimal order
        self._index_suggestions()
        self._index_products()
        self._index_lines()
        self._index_categories()
        self._index_colors()
        self._index_collabs()

        self.stdout.write(self.style.SUCCESS('All indexing operations completed successfully.'))