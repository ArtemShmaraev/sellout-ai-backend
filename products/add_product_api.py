import random
import json
from functools import lru_cache
from datetime import datetime, date

from django.db.models import Q

from products.main_page import get_random
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab, Photo, HeaderText, \
    HeaderPhoto
from products.serializers import LineSerializer



print()
colors_data = json.load(open("colors.json", encoding="utf-8"))
singular_data = json.load(open("categories_singular.json", encoding="utf-8"))


def check_color_in_list(color_name):
    for color in colors_data:
        if color['name'] == color_name:
            return color
    return False


def add_product2(data):
    rel_num = data.get('platform_info').get("poizon").get("detail").get('likesCount', 0)
    product, create = Product.objects.get_or_create(
        model=data.get('model'),
        manufacturer_sku=data.get('manufacturer_sku'),
        russian_name=data.get('model'),
        slug=data.get('manufacturer_sku') + str(random.randint(1, 50)),
        rel_num=int(rel_num if rel_num else 0),
        is_collab=data.get('is_collab'),
        main_color=Color.objects.get_or_create(name="multicolour")[0]
    )
    # if not create:


def add_product(data, SG_PRODUCTS=Product.objects.filter(id__lte=19000)):


    # print(data)
    rel_num = data.get('platform_info').get("poizon").get("detail").get('likesCount', 0)
    manufactorer_sku = data.get('manufacturer_sku').replace(" ", "").replace("-", "")
    if SG_PRODUCTS.filter(manufacturer_sku=manufactorer_sku).exists() and not data.get('is_custom'):
        print("повтор")
        return 0
        # Product.objects.filter(manufacturer_sku=data.get('manufacturer_sku')).delete()
        product = Product.objects.get(manufacturer_sku=manufactorer_sku, is_custom=False)
        product.manufacturer_sku = data.get('manufacturer_sku')
        product.available_flag = True
        product.rel_num = int(rel_num if rel_num else 0)
        product.is_collab = data.get('is_collab')

    else:
        # Создание нового продукта
        product = Product.objects.create(
            model=data.get('model'),
            manufacturer_sku=data.get('manufacturer_sku'),
            russian_name=data.get('model'),
            slug=data.get('manufacturer_sku') + str(random.randint(1, 50)),
            rel_num=int(rel_num if rel_num else 0),
            is_collab=data.get('is_collab'),
            main_color=Color.objects.get_or_create(name="multicolour")[0]
        )
        # product.save()

        # Обработка брендов
        brands = data.get('brands', [])
        for brand_name in brands:
            brand, _ = Brand.objects.get_or_create(name=brand_name)
            product.brands.add(brand)
        # Обработка цветов

        # colors = data.get('colors', [])
        # for color_name in colors:
        #     color, _ = Color.objects.get_or_create(name=color_name)
        #     product.colors.add(color)
        #
        # # Обработка основного цвета
        # main_color = data.get('main_color')
        # if main_color:
        #     color_in = check_color_in_list(main_color)
        #     if color_in:
        #         main_color, _ = Color.objects.get_or_create(name=main_color)
        #         main_color.hex = color_in['hex']
        #         main_color.russian_name = color_in['russian_name']
        #     else:
        #         main_color, _ = Color.objects.get_or_create(name=main_color)
        #     main_color.is_main_color = True
        #     main_color.save()
        #     product.main_color = main_color

        # print(product.main_line.view_name)

    categories = data.get('categories')
    if not isinstance(categories, list):
        categories = [categories]
    for category_name in categories:
        category = Category.objects.get(name=category_name)
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
        # линейка всегда существует, сюда код не дойдет
        print("ПИЗДАААААААА")
        # parent_line = None
        # for line_name in lines:
        #     if Line.objects.filter(name=line_name, parent_line=parent_line).exists():
        #         line = Line.objects.get(name=line_name, parent_line=parent_line)
        #     else:
        #         line = Line(name=line_name, parent_line=parent_line, full_name=line_name)
        #         line.save()
        #     if parent_line is not None:
        #         if Line.objects.filter(name=f"Все {parent_line.name}",
        #                                parent_line=parent_line).exists():
        #             line_all = Line.objects.get(name=f"Все {parent_line.name}", parent_line=parent_line, )
        #         else:
        #             line_all = Line(name=f"Все {parent_line.name}", parent_line=parent_line,
        #                             full_name=line_name)
        #             line_all.save()
        #         product.lines.add(line_all)
        #     parent_line = line
        #     product.lines.add(line)

    # product.slug = ""
    product.save(custom_param=True)

    if product.main_line is not None:
        brands = data.get('brands', [])
        model = product.main_line.view_name
        for brand in brands:
            model = model.replace(brand, "") if brand != "Jordan" and "Air" not in model else model
        model = " ".join(model.split())
        if not Brand.objects.filter(name=model).exists():
            product.model = model

            product.colorway = data.get('model')

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

    if "кроссовки" not in "_".join(categories):
        product.colorway = product.model
        product.model = singular_data[categories[0]]
    product.save()
    print(product)
    return product

    # self.stdout.write(self.style.SUCCESS(product))


