import random
import json
from functools import lru_cache
from datetime import datetime, date
from time import time
from django.utils import timezone
from django.db.models import Q

from orders.models import ShoppingCart
from products.main_page import get_random
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab, Photo, HeaderText, \
    HeaderPhoto, Material, SizeTable, SizeTranslationRows
from products.serializers import LineSerializer, ProductSerializer
from shipping.models import DeliveryType, ProductUnit, Platform
from utils.models import Currency



def add_products_spu_id_api(data):
    property_ids = []
    spu_id = 0
    for product in data:
        property_ids.append(product['platform_info']['poizon']["propertyId"])
        spu_id = product['platform_info']['poizon']["spuId"]
    # print(spu_id)
    products = Product.objects.filter(spu_id=spu_id)
    # print(list(products.values_list("slug", flat=True)))
    products.update(available_flag=False)
    for product in data:
        add_product_api(product)




def sklon_days(n):
    if n % 10 == 1 and n % 100 != 11:
        return "день"
    elif 2 <= n % 10 <= 4 and (n % 100 < 10 or n % 100 >= 20):
        return "дня"
    else:
        return "дней"


def add_product_api(data):
    spu_id = data['platform_info']["poizon"].get("spuId")
    property_id = data['platform_info']["poizon"].get("propertyId")
    manufacturer_sku = data.get("manufacturer_sku")

    t1 = time()
    # prs = Product.objects.filter(spu_id=spu_id, property_id=property_id,
    #                              manufacturer_sku=manufacturer_sku)
    # prs.delete()
    print(spu_id)
    print(property_id)
    print(manufacturer_sku)

    product, create = Product.objects.get_or_create(spu_id=spu_id, property_id=property_id)
    print(product.slug)
    product_slug = ""
    if not create:
        product.clear_all_fields()
        product.product_units.update(availability=False)
        product_slug = product.slug if product.slug != "" else f"{spu_id}_{property_id}_{manufacturer_sku}"
    else:
        product_slug = f"{spu_id}_{property_id}_{manufacturer_sku}"
    product.slug = product_slug
    product.save()
    t2 = time()

    product.is_collab = data["is_collab"]
    if data["is_collab"] and len(data['collab_names']) > 0:
        collab, create = Collab.objects.get_or_create(name=data['collab_names'][0])
        product.collab = collab

    product.model = data['model']
    product.colorway = data['colorway']
    product.is_custom = data['custom']
    if "formatted_manufacturer_sku" in data:
        product.formatted_manufacturer_sku = data["formatted_manufacturer_sku"]
    product.in_sg = data.get("product_on_stadium_goods", False)

    product.category_id = data['platform_info']["poizon"].get("categoryId", 0)
    product.category_name = data['platform_info']["poizon"].get("categoryName", "")
    product.level1_category_id = data['platform_info']["poizon"].get("level1CategoryId", 0)
    product.level2_category_id = data['platform_info']["poizon"].get("level2CategoryId", 0)

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
    rel_num = int(data['platform_info']["poizon"]["poizon_likes_count"]) if str(data['platform_info']["poizon"]["poizon_likes_count"]).isdigit() else 0
    if not product.categories.filter(name__in=["Обувь", "Одежда"]).exists():
        rel_num = int(rel_num * 0.3)
    product.rel_num = rel_num
    product.similar_product = data['platform_info']["poizon"].get("similar_products", [])
    product.another_configuration = data['platform_info']["poizon"].get("another_configuration", [])
    product.actual_price = False

    t5 = time()
    blacklisted_urls = product.black_bucket_link.values_list("url", flat=True)
    # Получить список URL-ов из ваших данных, которых нет в черном списке
    new_urls = [img["url"] for img in data["images"] if img["url"] not in blacklisted_urls]
    # Найти фотографии, которые уже существуют среди новых URL-ов
    existing_photos = Photo.objects.filter(url__in=new_urls)
    # Создать новые фотографии для отсутствующих URL-ов
    new_photos = []
    for url in new_urls:
        if url not in existing_photos.values_list("url", flat=True):
            new_photo = Photo(url=url)
            new_photos.append(new_photo)
    # Сохранить новые фотографии в базе данных
    Photo.objects.bulk_create(new_photos)
    # Получить все фотографии (включая новые и существующие)
    all_photos = existing_photos | Photo.objects.filter(url__in=new_urls)
    # Добавить все фотографии в bucket_link продукта
    product.bucket_link.add(*all_photos)


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
    product.size_row_name = data.get('size_row_name', "")
    product.extra_name = data.get('extra_name', "")
    product.description = data.get('description', "")
    product.content_sources = data.get("content_sources")

    product.has_many_sizes = data.get("many_sizes")
    product.has_many_colors = data.get("many_colors")
    product.has_many_configurations = data.get("many_configurations")

    product.save(product_slug=product_slug)

    t7 = time()
    for unit in data['units']:
        product.available_flag = True
        sizes = []
        tables = []
        if "size_table_info" in unit:
            for size in unit["size_table_info"]:
                if size['size_table'] == "undefined":
                    row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
                    sizes.append(row.id)
                else:
                    table = SizeTable.objects.get(name=size['size_table'])
                    tables.append(table.id)
                    if size['size_table_row_value'] == 'undefined' or size["size_table_row"] == "undefined":
                        row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
                        sizes.append(row.id)
                    else:
                        rows = table.rows.all()
                        for size_row in rows:
                            if size_row.row[size["size_table_row"]] == size["size_table_row_value"]:
                                sizes.append(size_row.id)
                                break
        else:
            row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
            sizes.append(row.id)
        platform_info = unit['platform_info']
        poizon_info = platform_info['poizon']
        del poizon_info['offers']
        platform_info['poizon'] = poizon_info
        header = poizon_info['header']

        show_true_offers = [offer for offer in unit['offers']]
        sort_offers = sorted(show_true_offers, key=lambda x: x["days_max"])
        ids = []
        if not create:
            units = product.product_units.filter(platform_info__poizon__header=header).order_by(
                "delivery_type__days_max")

            ids = list(units.values_list("id", flat=True))
            # print(ids)

            for del_unit in units[:len(sort_offers)]:
                del_unit.delete()
        for i in range(len(sort_offers)):
            offer = sort_offers[i]
            view_name = f'{offer["days_min"]}-{offer["days_max"]} {sklon_days(int(offer["days_max"]))}'
            if offer['days_min'] == offer['days_max']:
                view_name = f'{offer["days_max"]} {sklon_days(int(offer["days_max"]))}'

            dilivery = DeliveryType.objects.create(
                name=sort_offers[i]["platform_info"]['poizon']["delivery_additional_info"],
                view_name=view_name,
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
                poizon_abroad=offer["platform_info"].get('poizon_abroad', False),
                delivery_type=offer.get('delivery_type', "standard")
            )

            platform_info['poizon'].update(offer["platform_info"])
            # 670870
            # print(100)
            if not create and i < len(ids):
                # print(ids[i])
                product_unit = ProductUnit.objects.create(
                    id=ids[i],
                    product=product,
                    size_platform=unit['unit_name'],
                    view_size_platform=unit['unit_name'],
                    original_price=offer['price'],
                    start_price=offer['price'],
                    final_price=offer['price'],
                    delivery_type=dilivery,
                    platform=Platform.objects.get_or_create(platform='poizon',
                                                            site="poizon")[0],
                    url=data['platform_info']["poizon"]['url'],
                    availability=True,
                    currency=
                    Currency.objects.get_or_create(name=offer["currency"])[0],
                    platform_info=platform_info,
                    weight=unit['weight'],
                    dimensions={"length": unit['length'],
                                "height": unit['height'],
                                "width": unit['width']}
                )
            else:
                product_unit = ProductUnit.objects.create(
                    product=product,
                    size_platform=unit['unit_name'],
                    view_size_platform=unit['unit_name'],
                    original_price=offer['price'],
                    start_price=offer['price'],
                    final_price=offer['price'],
                    delivery_type=dilivery,
                    platform=Platform.objects.get_or_create(platform='poizon',
                                                            site="poizon")[0],
                    url=data['platform_info']["poizon"]['url'],
                    availability=True,
                    currency=
                    Currency.objects.get_or_create(name=offer["currency"])[0],
                    platform_info=platform_info,
                    weight=unit['weight'],
                    dimensions={"length": unit['length'],
                                "height": unit['height'],
                                "width": unit['width']}
                )
            product_unit.size.set(SizeTranslationRows.objects.filter(id__in=sizes))
            product_unit.size_table.set(SizeTable.objects.filter(id__in=tables))
            product_unit.update_history()
    t9 = time()

    for ost_unit in product.product_units.filter(availability=False):
        has_product_unit_in_cart = ShoppingCart.objects.filter(product_units=ost_unit).exists()
        if not has_product_unit_in_cart:
            ost_unit.delete()
    t10 = time()

    product.update_price()
    t11 = time()
    sizes_info = {"sizes": [], "filter_logo": ""}
    sizes_id = set()
    for unit in product.product_units.filter(availability=True):
        # print(unit.size.all())
        for s in unit.size.all():
            row = s.table.default_row
            # print(row.filter_name)
            if row.filter_name != "Один размер":
                # print("сука")
                if sizes_info['filter_logo'] == "" and row.filter_logo not in ['SIZE', "INT"]:
                    sizes_info['filter_logo'] = row.filter_logo
                if s.id not in sizes_id:
                    sizes_info['sizes'].append([s.id, f"{s.row[row.filter_name]}"])
                    sizes_id.add(s.id)
    t12 = time()

    sizes_info['sizes'] = list(map(lambda x: x[1], sorted(sizes_info['sizes'])))
    product.available_sizes = sizes_info
    product.one_update = True
    product.last_upd = timezone.now()
    product.save()

    # print(product.slug)
    t13 = time()

    # print(t2-t1)
    # print(t3-t2)
    # print(t4-t3)
    # print(t5-t4)
    # print(t6-t5)
    # print(t7-t6)
    # print(t9-t7)
    # print(t10-t9)
    # print(t11-t10)
    # print(t12-t11)
    # print(t13-t12)
    # print(product.slug)
    return product

    # self.stdout.write(self.style.SUCCESS(product))




# def update_product_api(data):
#     spu_id = data.get("spuId")
#     property_id = data.get("propertyId")
#     manufacturer_sku = data.get("manufacturer_sku")
#
#     t1 = time()
#     # prs = Product.objects.filter(spu_id=spu_id, property_id=property_id,
#     #                              manufacturer_sku=manufacturer_sku)
#     # prs.delete()
#
#     product = Product.objects.get(spu_id=spu_id, property_id=property_id,
#                                                     manufacturer_sku=manufacturer_sku)
#     product.product_units.update(availability=False)
#
#
#     t2 = time()
#
#     for unit in data['units']:
#
#         sizes = []
#         tables = []
#         if "size_table_info" in unit:
#             for size in unit["size_table_info"]:
#                 if size['size_table'] == "undefined":
#                     row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
#                     sizes.append(row.id)
#                 else:
#                     table = SizeTable.objects.get(name=size['size_table'])
#                     tables.append(table.id)
#                     if size['size_table_row_value'] == 'undefined' or size["size_table_row"] == "undefined":
#                         row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
#                         sizes.append(row.id)
#                     else:
#                         rows = table.rows.all()
#                         for size_row in rows:
#                             if size_row.row[size["size_table_row"]] == size["size_table_row_value"]:
#                                 sizes.append(size_row.id)
#                                 break
#         else:
#             row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
#             sizes.append(row.id)
#
#         platform_info = unit['platform_info']
#         poizon_info = platform_info['poizon_info']
#         del poizon_info['offers']
#         platform_info['poizon_info'] = poizon_info
#         header = poizon_info['header']
#
#         show_true_offers = [offer for offer in unit['offers'] if offer.get('show') == True]
#         sort_offers = sorted(show_true_offers, key=lambda x: x["days_max"])
#
#         units = product.product_units.filter(platform_info__poizon_info__header=header).order_by(
#             "delivery_type__days_max")
#
#         ids = list(units.values_list("id", flat=True))
#
#         for del_unit in units[:len(sort_offers)]:
#             del_unit.delete()
#
#         for i in range(len(sort_offers)):
#             offer = sort_offers[i]
#             if offer['show']:
#                 dilivery, create = DeliveryType.objects.get_or_create(
#                     name=sort_offers[i]["delivery_additional_info"],
#                     view_name=f'{offer["days_min"]}-{offer["days_max"]}',
#                     days_min=offer['days_min'],
#                     days_max=offer['days_max'],
#                     days_max_to_international_warehouse=offer['days_max_to_international_warehouse'],
#                     days_min_to_international_warehouse=offer["days_min_to_international_warehouse"],
#                     days_min_to_russian_warehouse=offer['days_min_to_russian_warehouse'],
#                     days_max_to_russian_warehouse=offer["days_max_to_russian_warehouse"],
#                     absolute_insurance=offer.get('absolute_insurance', 0),
#                     decimal_insurance=offer.get('decimal_insurance', 0),
#                     delivery_price_per_kg_in_rub=offer['delivery_price_per_kg_in_rub'],
#                     extra_charge=offer['extra_charge'] if offer['extra_charge'] else 0,
#                     poizon_abroad=offer["platform_info"].get('poizon_abroad', False),
#                     delivery_type=offer.get('delivery_type', "standard")
#                 )
#
#                 platform_info['poizon_info'].update(offer["platform_info"])
#                 # 670870
#                 if i < len(ids):
#                     product_unit = ProductUnit.objects.create(
#                         id=ids[i],
#                         product=product,
#                         size_platform=unit['unit_name'],
#                         view_size_platform=unit['unit_name_with_size'],
#                         original_price=offer['price'],
#                         start_price=offer['price'],
#                         final_price=offer['price'],
#                         approximate_price_with_delivery_in_rub=int(round(
#                             offer["approximate_price_with_delivery_in_rub"])),
#                         delivery_type=dilivery,
#                         platform=Platform.objects.get_or_create(platform='poizon',
#                                                                 site="poizon")[0],
#                         url=data['platform_info']["poizon_info"]['url'],
#                         availability=True,
#                         currency=
#                         Currency.objects.get_or_create(name=offer["currency"])[0],
#                         platform_info=platform_info
#                     )
#                 else:
#                     product_unit = ProductUnit.objects.create(
#                         product=product,
#                         size_platform=unit['unit_name'],
#                         view_size_platform=unit['unit_name_with_size'],
#                         original_price=offer['price'],
#                         start_price=offer['price'],
#                         final_price=offer['price'],
#                         approximate_price_with_delivery_in_rub=int(round(
#                             offer["approximate_price_with_delivery_in_rub"])),
#                         delivery_type=dilivery,
#                         platform=Platform.objects.get_or_create(platform='poizon',
#                                                                 site="poizon")[0],
#                         url=data['platform_info']["poizon_info"]['url'],
#                         availability=True,
#                         currency=
#                         Currency.objects.get_or_create(name=offer["currency"])[0],
#                         platform_info=platform_info
#                     )
#                 product_unit.size.set(SizeTranslationRows.objects.filter(id__in=sizes))
#                 product_unit.size_table.set(SizeTable.objects.filter(id__in=tables))
#                 product_unit.update_history()
#
#     for ost_unit in product.product_units.filter(availability=False):
#         has_product_unit_in_cart = ShoppingCart.objects.filter(product_units=ost_unit).exists()
#         if not has_product_unit_in_cart:
#             ost_unit.delete()
#
#     product.update_price()
#     sizes_info = {"sizes": [], "filter_logo": ""}
#     sizes_id = set()
#     for unit in product.product_units.filter(availability=True):
#         for s in unit.size.all():
#             row = s.table.default_row
#             if sizes_info['filter_logo'] == "" and row.filter_logo not in ['SIZE', "INT"]:
#                 sizes_info['filter_logo'] = row.filter_logo
#             if s.id not in sizes_id:
#                 sizes_info['sizes'].append([s.id, f"{s.row[row.filter_name]}"])
#                 sizes_id.add(s.id)
#     sizes_info['sizes'] = list(map(lambda x: x[1], sorted(sizes_info['sizes'])))
#     product.available_sizes = sizes_info
#     product.save()
#
#     t8 = time()
#     # print(t2-t1)
#     # print(t3-t2)
#     # print(t4-t3)
#     # print(t5-t4)
#     # print(t6-t5)
#     # print(t7-t6)
#     # print(t8-t7)
#     # print(t8-t1)
#
#     return product
#
