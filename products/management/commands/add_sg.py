from itertools import count
from django.core.management.base import BaseCommand
import json
from datetime import datetime
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color


class Command(BaseCommand):
    def handle(self, *args, **options):
        all_data = json.load(open("final.json"))
        k = 0
        kk = 0
        mk = len(all_data)
        time0 = datetime.now()
        for data in all_data[k:]:
            k += 1
            kk += 1
            manufacturer_sku = data.get('manufacturer_sku')

            # Удаление существующего продукта с указанным manufacturer_sku
            Product.objects.filter(manufacturer_sku=manufacturer_sku).delete()

            # Создание нового продукта
            product = Product.objects.create(
                model=data.get('model'),
                colorway=data.get('colorway'),
                manufacturer_sku=manufacturer_sku,
                russian_name=data.get('model'),
                slug=manufacturer_sku
            )

            # Обработка брендов
            brands = data.get('brands', [])
            for brand_name in brands:
                brand, _ = Brand.objects.get_or_create(name=brand_name)
                product.brands.add(brand)

            # Обработка тегов
            tags = data.get('tags', [])
            for tag_name in tags:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                product.tags.add(tag)

            # Обработка коллекций
            collections = data.get('collections', [])
            for col_name in collections:
                col, _ = Collection.objects.get_or_create(name=col_name)
                product.collections.add(col)

            # Обработка цветов
            colors = data.get('colors', [])
            for color_name in colors:
                color, _ = Color.objects.get_or_create(name=color_name)
                product.colors.add(color)

            # Обработка основного цвета
            main_color = data.get('main_color')
            if main_color:
                main_color, _ = Color.objects.get_or_create(name=main_color)
                main_color.is_main_color = True
                main_color.save()
                product.main_color = main_color

            # Обработка пола
            genders = data.get('gender', [])
            product.gender.set(Gender.objects.filter(name__in=genders))

            # Обработка рекомендованного пола
            recommended_gender = data.get('recommended_gender')
            product.recommended_gender = Gender.objects.get(name=recommended_gender)

            # Обработка категорий
            categories = data.get('categories', [])

            if categories:
                parent_category = None
                for category_name in categories:
                    category, _ = Category.objects.get_or_create(name=category_name)
                    if parent_category is not None:
                        category.parent_category = parent_category
                    parent_category = category
                    product.categories.add(parent_category)

            # Обработка линий
            lines = data.get('lines', [])
            if len(lines) > 1:
                parent_line = None
                for line_name in lines:
                    if Line.objects.filter(name=line_name, parent_line=parent_line, brand=Brand.objects.get(name=lines[0])).exists():
                        line = Line.objects.get(name=line_name, parent_line=parent_line, brand=Brand.objects.get(name=lines[0]))
                    else:
                        line = Line(name=line_name, parent_line=parent_line, brand=Brand.objects.get(name=lines[0]), full_name=line_name)
                        line.save()
                    parent_line = line
                    product.lines.add(line)

            product.slug = ""
            product.save()

            if k % 10 == 0:
                time2 = datetime.now()
                t = time2 - time0
                # time0 = time2
                itogo = ((mk - k) / kk) * t.seconds
                print(
                    f"{k}/{mk} {round((k / mk) * 100, 3)}% осталось {round(itogo, 2)} сек | эта десятка за {round(t.seconds / (kk / 10), 2)} сек")
            # print()

        print('finished')
