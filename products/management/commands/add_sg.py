from itertools import count
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color


class Command(BaseCommand):

    def handle(self, *args, **options):
        all_data = json.load(open("final.json"))[6500:]
        k = 6500
        for data in all_data:
            # print(k, data)
            k += 1
            if Product.objects.filter(manufacturer_sku=data['manufacturer_sku']).exists():
                product = Product.objects.get(manufacturer_sku=data['manufacturer_sku'])
                product.delete()
            product = Product(model=data['model'],
                              colorway=data['colorway'],
                              manufacturer_sku=data['manufacturer_sku'],
                              russian_name=data['model'],
                              slug=data['manufacturer_sku']
                              )
            product.save()
            for brand_name in data['brands']:
                brand, created = Brand.objects.get_or_create(name=brand_name)
                brand.save()
                product.brands.add(brand)

            for tag_name in data['tags']:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tag.save()
                product.tags.add(tag)

            for col_name in data['collections']:
                col, created = Collection.objects.get_or_create(name=col_name)
                col.save()
                product.collections.add(col)

            for color_name in data['colors']:
                color, created = Color.objects.get_or_create(name=color_name)
                color.save()
                product.colors.add(color)

            if "main_color" in data:
                main_color, created = Color.objects.get_or_create(name=data['main_color'])
                main_color.save()
                product.main_color = main_color

            for gen in data['gender']:
                product.gender.add(Gender.objects.get(name=gen))

            product.recommended_gender = Gender.objects.get(name=data['recommended_gender'])

            # добавление категорий
            if len(data['categories']) > 0:
                cat, created = Category.objects.get_or_create(name=data['categories'][0])
                if created:
                    cat.save()
                last_cat = cat

                for i in range(1, len(data['categories'])):
                    exists = Category.objects.filter(name=data['categories'][i],
                                                     parrent_categories=last_cat).exists()
                    if not exists:
                        cat = Category(name=data['categories'][i])
                        cat.save()
                        cat.parent_categories.add(last_cat)
                        cat.save()
                    cat = Category.objects.get(name=data['categories'][i],
                                               parrent_categories__name=data['categories'][i - 1])
                    last_cat = cat
                product.categories.add(last_cat)

            # добавление линеек
            if len(data['lines']) > 1:
                line, created = Line.objects.get_or_create(name=data['lines'][0])
                if created:
                    line.save()
                last_line = line

                for i in range(1, len(data['lines'])):
                    exists = Line.objects.filter(name=data['lines'][i],
                                                 parent_line=last_line).exists()
                    if not exists:
                        line = Line(name=data['lines'][i])
                        line.save()
                        line.parent_line = last_line
                        line.save()
                    line = Line.objects.get(name=data['lines'][i],
                                            parent_line=last_line)
                    last_line = line
                product.lines.add(last_line)
            product.slug = ""
            print()
            print(product.lines.all())
            product.save()
            print(product.lines.all())
            print(k)
            # print()

        print('finished')