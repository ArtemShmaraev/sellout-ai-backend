import random
from itertools import count
from django.core.management.base import BaseCommand
import json
import os
import json
from datetime import datetime, date
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab, Photo


class Command(BaseCommand):
    def handle(self, *args, **options):
        colors_data = json.load(open("colors.json", encoding="utf-8"))
        singular_data = json.load(open("categories_singular.json", encoding="utf-8"))

        def check_color_in_list(color_name):
            for color in colors_data:
                if color['name'] == color_name:
                    return color
            return False

        def add_prodoct(data):
            # print(data)
            rel_num = data.get('platform_info').get("poizon").get("detail").get('likesCount', 0)
            if Product.objects.filter(manufacturer_sku=data.get('manufacturer_sku'),
                                      is_custom=False).exists() and not data.get('is_custom'):
                # Product.objects.filter(manufacturer_sku=data.get('manufacturer_sku')).delete()
                product = Product.objects.get(manufacturer_sku=data.get('manufacturer_sku'), is_custom=False)
                product.available_flag = True
                product.rel_num = int(rel_num if rel_num else 0)

                product.is_collab = data.get('is_collab')

            else:
                Product.objects.filter(manufacturer_sku=data.get('manufacturer_sku')).delete()
                # Создание нового продукта
                product = Product.objects.create(
                    model=data.get('model'),
                    manufacturer_sku=data.get('manufacturer_sku'),
                    russian_name=data.get('model'),
                    slug=data.get('manufacturer_sku'),
                    rel_num=int(rel_num if rel_num else 0),
                    is_collab=data.get('is_collab')
                )

                # Обработка брендов
                brands = data.get('brands', [])
                for brand_name in brands:
                    brand, _ = Brand.objects.get_or_create(name=brand_name)
                    product.brands.add(brand)

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

                lines = data.get('lines', [])
                if len(lines) != 0:
                    lines = lines[0]

                f = True
                # проверка что линека уже существует
                for line in lines:
                    if not Line.objects.filter(view_name=line).exists():
                        f = False
                if f:  # если линейка уже существует
                    for line in lines:
                        product.lines.add(Line.objects.get(view_name=line))
                else:
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
                            if Line.objects.filter(name=f"Все {parent_line.name}",
                                                   brand=Brand.objects.get(name=lines[0]),
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


                product.slug = ""
                product.save()
                # print(product.main_line.view_name)
                if product.main_line is not None:
                    model = product.main_line.view_name
                    for brand in brands:
                        model = model.replace(brand, "") if brand != "Jordan" and "Air" not in model else model
                    model = " ".join(model.split())
                    if not Brand.objects.filter(name=model).exists():
                        product.model = model

                        product.colorway = data.get('model')

            categories = data.get('categories')
            if not isinstance(categories, list):
                categories = [categories]
            for category_name in categories:
                category, _ = Category.objects.get_or_create(name=category_name)
                product.categories.add(category)

            product.platform_info = json.dumps(data.get("platform_info"))

            product.is_custom = data.get('is_custom', False)
            # Обработка пола
            genders = data.get('gender', [])
            product.gender.set(Gender.objects.filter(name__in=genders))

            if data['date']:
                product.exact_date = datetime.strptime(data['date'], "%d.%m.%Y").date()

            if data['approximate_date']:
                product.approximate_date = data['approximate_date']

            # # Обработка рекомендованного пола Возможно тут список из одного элемента!!!
            # recommended_gender = data.get('recommended_gender')
            # product.recommended_gender = Gender.objects.get(name=recommended_gender)
            photos = data.get('bucket_link', [])
            for photo in photos:
                photo, _ = Photo.objects.get_or_create(url=photo)
                product.bucket_link.add(photo)

            if product.is_collab:
                collab, _ = Collab.objects.get_or_create(name=data.get('collab_name'))
                product.collab = collab
            product.slug = ""
            product.save()
            if (Category.objects.get(name="Кроссовки") not in product.categories.all() or product.model == "") and product.main_line is None:
                product.colorway = product.model
                product.model = singular_data[categories[0]]
            product.save()

            # self.stdout.write(self.style.SUCCESS(product))

        for count in range(1, 2):
            folder_path = f'dewu/{count}m'  # Укажите путь к папке, содержащей JSON-файлы
            k = 0
            ek = 0
            t0 = datetime.now()
            # Перебор всех файлов в папке
            for filename in os.listdir(folder_path)[:]:
                if filename.endswith('.json'):  # Проверка, что файл имеет расширение .json
                    file_path = os.path.join(folder_path, filename)  # Полный путь к файлу
                    k += 1
                    if k % 100 == 0:
                        t1 = datetime.now()
                        print(f"{k}: эта сотка за {(t1 - t0).seconds} сек")
                        t0 = t1
                    # Открытие файла и чтение его содержимого
                    with open(file_path, 'r') as file:
                        json_content = file.read()

                    # Преобразование содержимого файла в словарь

                    data = json.loads(json_content)
                    add_prodoct(data)

        print('finished')
