import random
import json
from functools import lru_cache
from datetime import datetime, date
from time import time

from django.db.models import Q

from products.main_page import get_random
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab, Photo, HeaderText, \
    HeaderPhoto, Material, SizeTable, SizeTranslationRows
from products.serializers import LineSerializer
from shipping.models import DeliveryType, ProductUnit, Platform
from utils.models import Currency


def add_product_api(data):
    spu_id = data.get("spuId")
    property_id = data.get("propertyId")
    manufacturer_sku = data.get("manufacturer_sku")

    t1 = time()
    # prs = Product.objects.filter(spu_id=spu_id, property_id=property_id,
    #                              manufacturer_sku=manufacturer_sku)
    # prs.delete()

    product, create = Product.objects.get_or_create(spu_id=spu_id, property_id=property_id,
                                                    manufacturer_sku=manufacturer_sku)
    product_slug = ""
    if not create:
        product_id = product.id
        product.delete()
        product = Product.objects.create(spu_id=spu_id, property_id=property_id,
                                         manufacturer_sku=manufacturer_sku, slug=f"{spu_id}_{property_id}_{manufacturer_sku}")
    else:
        product.slug = product_slug if product_slug != "" else f"{spu_id}_{property_id}_{manufacturer_sku}"
    product.save()
    t2 = time()

    product.is_collab = data["is_collab"]
    if data["is_collab"] and len(data['collab_names']) > 0:
        collab, create = Collab.objects.get_or_create(name=data['collab_names'][0])
        product.collab = collab

    product.model = data['model']
    product.colorway = data['colorway']
    product.is_custom = data['custom']
    product.in_sg = data.get("product_on_stadium_goods", False)

    genders = data.get('gender', [])
    product.gender.set(Gender.objects.filter(name__in=genders))

    if data['date']:
        product.exact_date = datetime.strptime(data['date'], "%d.%m.%Y").date()

    if data['approximate_date']:
        product.approximate_date = data['approximate_date']
    t3 = time()

    for i in range(len(data['lines'])):
        for line in data['lines'][i]:
            line_db = Line.objects.get(name=line)
            product.lines.add(line_db)
            if Line.objects.filter(name=f"Все {line}").exists():
                line_db = Line.objects.get(name=f"Все {line}")
                product.lines.add(line_db)

    for brand in data['brands']:
        brand_db, create = Brand.objects.get_or_create(name=brand)
        product.brands.add(brand_db)

        line, create = Line.objects.get_or_create(name=brand)
        product.lines.add(line)
        if Line.objects.filter(name=f"Все {brand}").exists():
            product.lines.add(Line.objects.get(name=f"Все {brand}"))

    t4 = time()

    for cat in data['categories']:
        category = Category.objects.get(name=cat)
        product.categories.add(category)
        if Category.objects.filter(name=f"Все {category.name.lower()}").exists():
            category_is_all = Category.objects.get(name=f"Все {category.name.lower()}")
            product.categories.add(category_is_all)
        elif Category.objects.filter(name=f"Вся {category.name.lower()}").exists():
            category_is_all = Category.objects.get(name=f"Вся {category.name.lower()}")
            product.categories.add(category_is_all)

        while category.parent_category is not None:
            category = category.parent_category
            product.categories.add(category)

            if Category.objects.filter(name=f"Все {category.name.lower()}").exists():
                category_is_all = Category.objects.get(name=f"Все {category.name.lower()}")
                product.categories.add(category_is_all)
            elif Category.objects.filter(name=f"Вся {category.name.lower()}").exists():
                category_is_all = Category.objects.get(name=f"Вся {category.name.lower()}")
                product.categories.add(category_is_all)

    product.parameters = data['parameters_to_show_in_product']
    product.platform_info = data['platform_info']
    product.rel_num = int(data["poizon_likes_count"])  if str(data["poizon_likes_count"]).isdigit() else 0
    product.similar_product = data.get("similar_products", [])
    product.another_configuration = data.get("another_configuration", [])

    t5 = time()

    for img in data["images"]:
        photo = Photo(url=img["url"])
        photo.save()
        product.bucket_link.add(photo)

    if "colors" in data["parameters_to_use_in_filters"]:
        for color in data["parameters_to_use_in_filters"]['colors']:
            color_db, create = Color.objects.get_or_create(name=color)
            product.colors.add(color_db)
    else:
        color = Color.objects.get(name="multicolour")
        product.colors.add(color)

    if "material" in data["parameters_to_use_in_filters"]:
        for material in data["parameters_to_use_in_filters"]['material']:
            if Material.objects.filter(eng_name=material).exists():
                material_db = Material.objects.get(eng_name=material)
                product.materials.add(material_db)
    else:
        material = Material.objects.get(eng_name="other_material")
        product.materials.add(material)

    t6 = time()

    product.size_table_platform = data['size_tables']

    product.main_size_row_of_unit = data.get('main_size_row_of_unit', "")
    product.main_size_row = data.get('main_size_row', "")
    product.unit_common_name = data.get('unit_common_name', "")
    product.save(product_slug=product_slug)

    t7 = time()

    for unit in data['units']:

        sizes = []
        tables = []
        if "size_table_info" in unit:
            for size in unit["size_table_info"]:
                if size['size_table'] == "undefined":
                    row = SizeTranslationRows.objects.filter(is_one_size=True).first()
                    sizes.append(row.id)
                else:
                    table = SizeTable.objects.get(name=size['size_table'])
                    tables.append(table.id)
                    if size['size_table_row_value'] == 'undefined' or size["size_table_row"] == "undefined":
                        row = SizeTranslationRows.objects.filter(is_one_size=True).first()
                        sizes.append(row.id)
                    else:
                        rows = table.rows.all()
                        for size_row in rows:
                            if size_row.row[size["size_table_row"]] == size["size_table_row_value"]:
                                sizes.append(size_row.id)
                                break
        else:
            row = SizeTranslationRows.objects.filter(is_one_size=True).first()
            sizes.append(row.id)

        platform_info = unit['platform_info']
        poizon_info = platform_info['poizon_info']
        del poizon_info['offers']
        platform_info['poizon_info'] = poizon_info



        for i in range(len(unit['offers'])):
            offer = unit['offers'][i]
            if offer['show']:
                dilivery, create = DeliveryType.objects.get_or_create(
                    name=unit['offers'][i]["delivery_additional_info"],
                    view_name=f'{offer["days_min"]}-{offer["days_max"]}',
                    days_min=offer['days_min'],
                    days_max=offer['days_max'],
                    days_max_to_international_warehouse=offer['days_max_to_international_warehouse'],
                    days_min_to_international_warehouse=offer["days_min_to_international_warehouse"],
                    days_min_to_russian_warehouse=offer['days_min_to_russian_warehouse'],
                    days_max_to_russian_warehouse=offer["days_max_to_russian_warehouse"],
                    absolute_insurance=offer.get('absolute_insurance', 0),
                    decimal_insurance=offer.get('decimal_insurance', 0),
                    delivery_price_per_kg_in_rub=offer['delivery_price_per_kg_in_rub'],
                    extra_charge=offer['extra_charge'] if offer['extra_charge'] else 0,
                    poizon_abroad=offer.get('poizon_abroad', False),
                    delivery_type=offer.get('delivery_type', "standard")
                    )

                platform_info['poizon_info'].update(offer["platform_info"])

                product_unit = ProductUnit.objects.create(
                    product=product,
                    size_platform=unit['unit_name'],
                    view_size_platform=unit['unit_name_with_size'],
                    original_price=unit["offers"][i]['price'],
                    start_price=unit["offers"][i]['price'],
                    final_price=unit["offers"][i]['price'],
                    approximate_price_with_delivery_in_rub=int(round(offer["approximate_price_with_delivery_in_rub"])),
                    delivery_type=dilivery,
                    platform=Platform.objects.get_or_create(platform='poizon', site="poizon")[0],
                    url=data['platform_info']["poizon_info"]['url'],
                    availability=True,
                    currency=Currency.objects.get_or_create(name=unit["offers"][i]["currency"])[0],
                    platform_info=platform_info
                )
                product_unit.size.set(SizeTranslationRows.objects.filter(id__in=sizes))
                product_unit.size_table.set(SizeTable.objects.filter(id__in=tables))
                product_unit.update_history()

    product.update_price()
    sizes_info = {"sizes": [], "filter_logo": ""}
    sizes_id = set()
    for unit in product.product_units.all():
        for s in unit.size.all():
            row = s.table.default_row
            if sizes_info['filter_logo'] == "" and row.filter_logo not in ['SIZE', "INT"]:
                sizes_info['filter_logo'] = row.filter_logo
            if s.id not in sizes_id:
                sizes_info['sizes'].append([s.id, f"{s.row[row.filter_name]}"])
                sizes_id.add(s.id)
    sizes_info['sizes'] = list(map(lambda x: x[1], sorted(sizes_info['sizes'])))
    product.available_sizes = sizes_info
    product.save()

    t8 = time()
    # print(t2-t1)
    # print(t3-t2)
    # print(t4-t3)
    # print(t5-t4)
    # print(t6-t5)
    # print(t7-t6)
    # print(t8-t7)
    # print(t8-t1)

    return product

    # self.stdout.write(self.style.SUCCESS(product))
