import random
from itertools import count
from django.core.management.base import BaseCommand
import json
from datetime import datetime
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab


class Command(BaseCommand):
    def handle(self, *args, **options):

        def check_color_in_list(color_name):
            for color in colors_data:
                if color['name'] == color_name:
                    return color
            return False

        all_data = json.load(open("final.json"))
        colors_data = json.load(open("colors.json"))
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


            # Обработка цветов
            colors = data.get('colors', [])
            for color_name in colors:
                color, _ = Color.objects.get_or_create(name=color_name)
                product.colors.add(color)

            # Обработка основного цвета
            main_color = data.get('main_color')
            if main_color:
                color_in = check_color_in_list(main_color)
                if color_in:
                    main_color, _ = Color.objects.get_or_create(name=main_color)
                    main_color.hex = color_in['hex']
                    main_color.russian_name = color_in['russian_name']
                else:
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


            main_collabs = ["Nike x Off-White", "Adidas Yeezy", "Nike x Travis Scott", "Jordan x Travis Scott",
                     "Nike x Supreme", "Nike x Union", "Nike x Louis Vuitton",
                     "Nike x Sacai", "Nike x Kaws", "Nike x Acronym", "Supreme x Louis Vuitton",
                     "Vans x Supreme", "Stone Island x Supreme", "Nike x Nocta", "Nike x Stussy"]


            collab = data.get('collab')
            if collab:
                if Collab.objects.filter(name=collab).exists():
                    collab = Collab.objects.get(name=collab)
                else:
                    collab = Collab(name=collab)
                    if collab.name in main_collabs:
                        collab.is_main_collab = True
                    else:
                        collab.query_name = brand.query_name
                    collab.save()
                product.collab = collab


            # collections = data.get('collections', [])
            # for col in collections:
            #     if Collection.objects.filter(name=col).exists():
            #         product.collections.add(Collection.objects.get(name=col))
            #     else:
            #         collection = Collection(name=col)
            #         collection.save()
            #         product.collections.add(collection)


            # Обработка линий
            lines = data.get('lines', [])
            if lines:
                parent_line = None
                for line_name in lines:
                    if Line.objects.filter(name=line_name, parent_line=parent_line,
                                           brand=Brand.objects.get(name=lines[0])).exists():
                        line = Line.objects.get(name=line_name, parent_line=parent_line,
                                                brand=Brand.objects.get(name=lines[0]))
                    else:
                        line = Line(name=line_name, parent_line=parent_line, brand=Brand.objects.get(name=lines[0]),
                                    full_name=line_name)
                        line.save()
                    if parent_line is not None:
                        if Line.objects.filter(name=f"Все {parent_line.name}", brand=Brand.objects.get(name=lines[0]),
                                               parent_line=parent_line).exists():
                            line_all = Line.objects.get(name=f"Все {parent_line.name}", parent_line=parent_line,
                                                        brand=Brand.objects.get(name=lines[0]))
                        else:
                            line_all = Line(name=f"Все {parent_line.name}", parent_line=parent_line,
                                            brand=Brand.objects.get(name=lines[0]),
                                            full_name=line_name)
                            line_all.save()
                        product.lines.add(line_all)

                    parent_line = line
                    product.lines.add(line)

            # product.min_price = random.randint(10, 200) * 500 - 10
            product.slug = ""
            product.save()

            if k % 10 == 0:
                time2 = datetime.now()
                t = time2 - time0
                # time0 = time2
                itogo = ((mk - k) / kk) * t.seconds
                self.stdout.write(self.style.SUCCESS(
                    f"{k}/{mk} {round((k / mk) * 100, 3)}% осталось {round(itogo, 2)} сек | эта десятка за {round(t.seconds / (kk / 10), 2)} сек"))
            # print()

        print('finished')
