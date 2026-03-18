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
from products.tools import update_score_sneakers, update_score_clothes
from shipping.models import DeliveryType, ProductUnit, Platform
from utils.models import Currency


def get_hk_delivery_offers(sku, data):
    units = []
    price = sku["zh_price"]

    sanya = 13.6

    standard_delivery = {
        "name": "standard_delivery",
        "currency": sanya,
        "days_min": 15,
        "days_max": 19,
        "delivery_price": 800,
        "delivery_currency": "rub",
        "decimal_insurance": 1,
        "absolute_insurance": 0,
        "maximum_price": 0,
        "commission": 350 if price <= 1500 else 450 if price <= 3000 else 800 if price <= 6000 else 1200,
        "commission_currency": "rub",
        "country_ship": "China",
        "price_currency": "cny",
        "currency_rate": "other",
        "available_statuses": ['Amethyst', 'Sapphire', 'Emerald', 'Ruby', 'Diamond', 'Privileged',
                               'Friends & Family']}
    if price <= 1500:
        express_delivery = {
            "name": "express_delivery",
            "currency": sanya,
            "days_min": 4,
            "days_max": 6,
            "delivery_price": 2500,
            "delivery_currency": "rub",
            "decimal_insurance": 1,
            "absolute_insurance": 0,
            "maximum_price": 1500,
            "commission": 350 if price <= 1500 else 450 if price <= 3000 else 800 if price <= 6000 else 1200,
            "commission_currency": "rub",
            "country_ship": "China",
            "price_currency": "cny",
            "currency_rate": "other",
            "available_statuses": ['Amethyst', 'Sapphire', 'Emerald', 'Ruby', 'Diamond', 'Privileged',
                                   'Friends & Family']
        }
    else:
        express_delivery = {
            "name": "express_delivery",
            "currency": sanya,
            "days_min": 4,
            "days_max": 6,
            "delivery_price": 2000,
            "delivery_currency": "rub",
            "decimal_insurance": 1,
            "absolute_insurance": 0,
            "maximum_price": 0,
            "price_currency": "cny",
            "commission": 350 if price <= 1500 else 450 if price <= 3000 else 800 if price <= 6000 else 1200,
            "commission_currency": "rub",
            "country_ship": "China",
            "currency_rate": "other",
            "available_statuses": ['Amethyst', 'Sapphire', 'Emerald', 'Ruby', 'Diamond', 'Privileged',
                                   'Friends & Family']
        }

    units.append(standard_delivery)
    units.append(express_delivery)
    return units

def add_product_hk(data):
    if not data.get("images", []):
        return "Пустой товар"
    # file_path = "picture.json"
    # with open(file_path, 'r', encoding='utf-8') as file:
    #     data = json.load(file)

    # f = False
    # for sku in data['skus']:
    #     price = sku["zh_price"]
    #     f = price and "view_name" in sku
    #     if f:
    #         break
    # if not f:
    #     return "Нет цен"

    # short_to_long_name_size = я

    spu_id = data['spu_id']
    # property_id = data["propertyId"]
    manufacturer_sku = data.get("formatted_manufacturer_sku", "")
    products = Product.objects.filter(spu_id=spu_id)
    print(products.count())
    if products.count() > 1:
        product_slug = products.first().slug
        products.delete()
        create = True
        product = Product.objects.create(spu_id=spu_id, formatted_manufacturer_sku=manufacturer_sku)
    elif products.count() == 1:
        product = products.first()
        create = False
        product.clear_all_fields()
        product.product_units.update(availability=False)
        product_slug = product.slug if product.slug != "" else f"{spu_id}_{manufacturer_sku}"
    else:
        product_slug = f"{spu_id}_{manufacturer_sku}"
        create = True
        product = Product.objects.create(spu_id=spu_id, formatted_manufacturer_sku=manufacturer_sku)
    product.slug = product_slug
    product.save()

    product.is_collab = data["is_collab"]
    if data["is_collab"] and len(data['collab_names']) > 0:
        collab, create = Collab.objects.get_or_create(name=data['collab_names'][0])
        product.collab = collab

    product.model = data['model']
    product.colorway = data['colorway']
    product.is_custom = data['custom']
    product.formatted_manufacturer_sku = data.get("formatted_manufacturer_sku", "")
    product.manufacturer_sku = data.get("manufacturer_sku", "")
    genders = data.get('gender', [])
    product.gender.set(Gender.objects.filter(name__in=genders))

    if data['date']:
        product.exact_date = datetime.strptime(data['date'], "%d.%m.%Y").date()

    if data['approximate_date']:
        product.approximate_date = data['approximate_date']

    product.lines.clear()
    for i in range(len(data['lines'])):
        for line in data['lines'][i]:
            line_db = Line.objects.get(name=line)
            product.lines.add(line_db)
            if Line.objects.filter(name=f"Все {line}").exists():
                line_db = Line.objects.get(name=f"Все {line}")
                product.lines.add(line_db)

    product.brands.clear()
    for brand in data['brands']:
        brand_db, create = Brand.objects.get_or_create(name=brand)
        product.brands.add(brand_db)

        line, create = Line.objects.get_or_create(name=brand)
        product.lines.add(line)
        if Line.objects.filter(name=f"Все {brand}").exists():
            product.lines.add(Line.objects.get(name=f"Все {brand}"))

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

    product.parameters = data['view_parameters']
    # product.platform_info = data['platform_info']
    rel_num = int(data['poizon_likes_count']) if str(data['poizon_likes_count']).isdigit() else 0
    product.rel_num = rel_num


    product.actual_price = False

    blacklisted_urls = product.black_bucket_link.values_list("url", flat=True)
    new_urls = [img for img in data["images"] if img not in blacklisted_urls]
    new_photos = []
    for url in new_urls:
        new_photo = Photo(url=url)
        new_photos.append(new_photo)
    Photo.objects.bulk_create(new_photos)
    all_photos = new_photos
    product.bucket_link.clear()
    product.bucket_link.add(*all_photos)


    if "colors" in data["filter_parameters"]:
        for color in data["filter_parameters"]['colors']:
            color_db, create = Color.objects.get_or_create(russian_name=color)
            product.colors.add(color_db)
    # else:
    #     color = Color.objects.get(name="multicolour")
    #     product.colors.add(color)

    if "material" in data["filter_parameters"]:
        for material in data["filter_parameters"]['material']:
            if Material.objects.filter(name=material).exists():
                material_db = Material.objects.get(name=material)
                product.materials.add(material_db)
    # else:
    #     material = Material.objects.get(eng_name="other_material")
    #     product.materials.add(material)

    product.size_table_platform = data['tables']
    # product.size_table_platform = {'tables': {'default_table': {}, 'main_regular_table': {}, 'tables_recommendations': {}, 'main_measurements_table': {}}, 'size_fit': 0, 'main_sizes': [], 'main_size_table_row': 'undefined', 'size_fit_recommendation': 'Данная модель соответствует своему размеру. Мы рекомендуем выбирать <b>Ваш обычный размер</b>'}

    # product.size_row_name = data.get('size_row_name', "")
    # product.extra_name = data.get('extra_name', "")
    # product.description = data.get('description', "")
    # product.content_sources = data.get("content_sources")
    print(product.slug)
    product.save(product_slug=product_slug)
    product.product_units.update(availability=False)
    for sku in data['skus']:
        if sku['zh_price'] == 0 or "view_name" not in sku or not sku['zh_price']:
            continue
        # print(sku)
        delivery_offers = get_hk_delivery_offers(sku, data)
        sizes = []
        tables = []

        if "filter_table_name" in sku and 'filter_sizes' in sku:

            for size in sku["filter_sizes"]:
                if sku['filter_table_name'] == "undefined" or sku['filter_table_name'] == "":
                    row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
                    sizes.append(row.id)
                else:
                    table = SizeTable.objects.get(name=sku["filter_table_name"])
                    tables.append(table.id)

                    if size == 'undefined' or sku['filter_table_row_name'] == "undefined" or sku['filter_table_row_name'] == "":
                        row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
                        sizes.append(row.id)
                    else:
                        rows = table.rows.all()
                        for size_row in rows:
                            # print(size_row.row)
                            print(size_row.row)
                            if size_row.row[sku["filter_table_row_name"]] == size:
                                sizes.append(size_row.id)
                                product.has_many_sizes = True
                                break
        else:
            row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
            sizes.append(row.id)
        # platform_info = unit['platform_info']
        # poizon_info = platform_info['poizon']
        # del poizon_info['offers']
        # platform_info['poizon'] = poizon_info

        # header = poizon_info['header']

        for delivery_offer in delivery_offers:
            days_min = delivery_offer['days_min'] + sku['delivery_info']['min_platform_delivery']
            days_max = delivery_offer['days_max'] + sku['delivery_info']['max_platform_delivery']

            view_name = f'{days_min}-{days_max} {sklon_days(int(days_max))}'
            if days_min == days_max:
                view_name = f'{days_max} {sklon_days(int(days_max))}'

            delivery = DeliveryType.objects.create(
                name=delivery_offer['name'],
                view_name=view_name,
                days_min=days_min,
                days_max=days_max,
                days_max_to_international_warehouse=sku['delivery_info']['max_platform_delivery'],
                days_min_to_international_warehouse=sku['delivery_info']['min_platform_delivery'],
                days_min_to_russian_warehouse=delivery_offer['days_min'],
                days_max_to_russian_warehouse=delivery_offer['days_max'],
                absolute_insurance=delivery_offer.get('absolute_insurance', 0),
                decimal_insurance=delivery_offer.get('decimal_insurance', 0),
                delivery_price_per_kg_in_rub=delivery_offer['delivery_price'],

                # extra_charge=offer['extra_charge'] if offer['extra_charge'] else 0,
                # poizon_abroad=offer["platform_info"].get('poizon_abroad', False),
                commission=delivery_offer.get('comission', 0),
                delivery_type=delivery_offer['name'],
                currency=delivery_offer['currency'])

            if product.product_units.filter(view_size_platform=sku['view_name'],
                                            delivery_type__delivery_type=delivery_offer['name']).exists():
                product_unit = product.product_units.get(view_size_platform=sku['view_name'],
                                                         delivery_type__delivery_type=delivery_offer['name'])
                # product_unit.delivery_type.delete()
                product_unit.delivery_type = delivery
                product_unit.original_price = sku['zh_price']


            else:
                product_unit = ProductUnit.objects.create(
                    product=product,
                    size_platform=sku['propertyDesc'],
                    view_size_platform=sku['view_name'],
                    original_price=sku['zh_price'],
                    start_price=sku['zh_price'],
                    final_price=sku['zh_price'],
                    delivery_type=delivery,
                    platform=Platform.objects.get_or_create(platform='poizon',
                                                            site="poizon")[0],
                    # url=data['platform_info']["poizon"]['url'],
                    availability=True,
                    currency=
                    Currency.objects.get_or_create(name="CNY")[0],
                    # platform_info=platform_info,
                    weight_kg=data['weight'],
                    # dimensions={"length": unit['length'],
                    #             "height": unit['height'],
                    #             "width": unit['width']}
                    # commission=delivery_offer['commission']

                )
            product_unit.availability = True
            if 'poizon' not in product_unit.platform_info:
                product_unit.platform_info['poizon'] = {}
            product_unit.platform_info['poizon']['sku'] = sku['skuId']
            product_unit.update_history()

            product_unit.size.set(SizeTranslationRows.objects.filter(id__in=sizes))
            product.sizes.add(*SizeTranslationRows.objects.filter(id__in=sizes))
            product_unit.size_table.set(SizeTable.objects.filter(id__in=tables))

            product_unit.check_sale()

    product.update_price()
    t11 = time()
    product.check_sale()
    if product.is_sale:
        product.add_sale(product.sale_absolute, product.sale_percentage)

    sizes_info = {"sizes": [], "filter_logo": ""}
    sizes_id = set()
    for unit in product.product_units.filter(availability=True):
        for s in unit.size.all():
            row = s.table.default_row
            if row.filter_name != "Один размер":
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
    if product.bucket_link is None:
        product.available_flag = False

    if create:
        cats = product.categories.values_list("name", flat=True)
        if "Кеды" in cats or "Кроссовки" in cats:
            update_score_sneakers(product)
        else:
            update_score_clothes(product)
    product.in_process_update = False
    print(product.slug, '111')
    product.save()
    return product











def get_ps_delivery_offers(sku, data):
    units = []
    price = sku["cnyPrice"]

    standard = {  # саня дефолт
        "name": "standard",
        "days_min": 10,
        "days_max": 15,
        "delivery_price": 800,
        "delivery_currency": "rub",
        "decimal_insurance": 1,
        "absolute_insurance": 0,
        "maximum_price": 0,
        "commission": 350 if price <= 1500 else 450 if price <= 3000 else 800 if price <= 6000 else 1200,
        "commission_currency": "rub",
        "country_ship": "China",
        "price_currency": "cny",
        "currency_rate": "other",
        "available_statuses": ['Amethyst', 'Sapphire', 'Emerald', 'Ruby', 'Diamond', 'Privileged',
                               'Friends & Family']
    }
    our_delivery = {  # dobropost
        "name": "our_delivery",
        "days_min": 10,
        "days_max": 15,
        "delivery_price": 750,
        "delivery_currency": "rub",
        "decimal_insurance": 1,
        "absolute_insurance": 0,
        "maximum_price": 1000,
        "maximum_price_currency": "eur",
        "country_ship": "China",
        "price_currency": "cny",
        "currency_rate": "our",
        "available_statuses": ['Privileged', 'Friends & Family']
    }
    sanya = 13.15

    standard_delivery = {
        "name": "standard_delivery",
        "currency": sanya,
        "days_min": 11,
        "days_max": 16,
        "delivery_price": 800,
        "delivery_currency": "rub",
        "decimal_insurance": 1,
        "absolute_insurance": 0,
        "maximum_price": 0,
        "commission": 350 if price <= 1500 else 450 if price <= 3000 else 800 if price <= 6000 else 1200,
        "commission_currency": "rub",
        "country_ship": "China",
        "price_currency": "cny",
        "currency_rate": "other",
        "available_statuses": ['Amethyst', 'Sapphire', 'Emerald', 'Ruby', 'Diamond', 'Privileged',
                               'Friends & Family']}
    if price <= 1500:
        express_delivery = {
            "name": "express_delivery",
            "currency": sanya,
            "days_min": 2,
            "days_max": 3,
            "delivery_price": 2500,
            "delivery_currency": "rub",
            "decimal_insurance": 1,
            "absolute_insurance": 0,
            "maximum_price": 1500,
            "commission": 350 if price <= 1500 else 450 if price <= 3000 else 800 if price <= 6000 else 1200,
            "commission_currency": "rub",
            "country_ship": "China",
            "price_currency": "cny",
            "currency_rate": "other",
            "available_statuses": ['Amethyst', 'Sapphire', 'Emerald', 'Ruby', 'Diamond', 'Privileged',
                                   'Friends & Family']
        }
    else:
        express_delivery = {
            "name": "express_delivery",
            "currency": sanya,
            "days_min": 2,
            "days_max": 3,
            "delivery_price": 2000,
            "delivery_currency": "rub",
            "decimal_insurance": 1,
            "absolute_insurance": 0,
            "maximum_price": 0,
            "price_currency": "cny",
            "commission": 350 if price <= 1500 else 450 if price <= 3000 else 800 if price <= 6000 else 1200,
            "commission_currency": "rub",
            "country_ship": "China",
            "currency_rate": "other",
            "available_statuses": ['Amethyst', 'Sapphire', 'Emerald', 'Ruby', 'Diamond', 'Privileged',
                                   'Friends & Family']
        }

    units.append(standard_delivery)
    units.append(express_delivery)
    return units


def add_product_v2(data):
    f = False
    for sku in data['skus']:
        price = sku["cnyPrice"]
        f = price > 0 and "view_name" in sku
        if f:
            break
    if not f:
        return "Нет цен"
    spu_id = data['spuId']
    property_id = data["propertyId"]
    manufacturer_sku = data.get("formatted_manufacturer_sku", "")

    # print(spu_id)
    # print(property_id)
    # print(manufacturer_sku)

    product, create = Product.objects.get_or_create(spu_id=spu_id, property_id=property_id)
    print(product.slug)
    product_slug = ""
    if not create:
        print("go")
        # time_threshold = timezone.now() - timezone.timedelta(hours=1)
        # if product.last_upd >= time_threshold or product.in_process_update:
        #     product.available_flag = True
        #     product.save()
        #     return "Товар актуальный))"
        # product.delete()
        # return 1
        product.clear_all_fields()
        product.product_units.update(availability=False)
        product_slug = product.slug if product.slug != "" else f"{spu_id}_{property_id}_{manufacturer_sku}"
    else:
        product_slug = f"{spu_id}_{property_id}_{manufacturer_sku}"

    product.slug = product_slug
    product.save()


    product.is_collab = data["is_collab"]
    if data["is_collab"] and len(data['collab_names']) > 0:
        collab, create = Collab.objects.get_or_create(name=data['collab_names'][0])
        product.collab = collab

    product.model = data['model']
    product.colorway = data['colorway']
    product.is_custom = data['custom']
    product.formatted_manufacturer_sku = data.get("formatted_manufacturer_sku", "")
    product.manufacturer_sku = data.get("manufacturer_sku", "")

    # product.in_sg = data.get("product_on_stadium_goods", False)
    # product.category_id = data['platform_info']["poizon"].get("categoryId", 0)
    # product.category_name = data['platform_info']["poizon"].get("categoryName", "")
    # product.level1_category_id = data['platform_info']["poizon"].get("level1CategoryId", 0)
    # product.level2_category_id = data['platform_info']["poizon"].get("level2CategoryId", 0)
    genders = data.get('gender', [])
    product.gender.set(Gender.objects.filter(name__in=genders))

    if data['date']:
        product.exact_date = datetime.strptime(data['date'], "%d.%m.%Y").date()

    if data['approximate_date']:
        product.approximate_date = data['approximate_date']

    product.lines.clear()
    for i in range(len(data['lines'])):
        for line in data['lines'][i]:
            line_db = Line.objects.get(name=line)
            product.lines.add(line_db)
            if Line.objects.filter(name=f"Все {line}").exists():
                line_db = Line.objects.get(name=f"Все {line}")
                product.lines.add(line_db)

    product.brands.clear()
    for brand in data['brands']:
        brand_db, create = Brand.objects.get_or_create(name=brand)
        product.brands.add(brand_db)

        line, create = Line.objects.get_or_create(name=brand)
        product.lines.add(line)
        if Line.objects.filter(name=f"Все {brand}").exists():
            product.lines.add(Line.objects.get(name=f"Все {brand}"))

    for cat in data['categories'][0]:
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

    # product.parameters = data['parameters_to_show_in_product']
    # product.platform_info = data['platform_info']
    rel_num = int(data['poizon_likes_count']) if str(data['poizon_likes_count']).isdigit() else 0
    product.rel_num = rel_num

    product.similar_product = data['similar_products']
    # product.another_configuration = data['platform_info']["poizon"].get("another_configuration", [])
    product.actual_price = False

    blacklisted_urls = product.black_bucket_link.values_list("url", flat=True)
    new_urls = [img for img in data["images"] if img not in blacklisted_urls]
    new_photos = []
    for url in new_urls:
        new_photo = Photo(url=url)
        new_photos.append(new_photo)
    Photo.objects.bulk_create(new_photos)
    all_photos = new_photos
    product.bucket_link.clear()
    product.bucket_link.add(*all_photos)

    # if "colors" in data["parameters_to_use_in_filters"]:
    #     for color in data["parameters_to_use_in_filters"]['colors']:
    #         color_db, create = Color.objects.get_or_create(name=color)
    #         product.colors.add(color_db)
    # else:
    #     color = Color.objects.get(name="multicolour")
    #     product.colors.add(color)

    # if "material" in data["parameters_to_use_in_filters"]:
    #     for material in data["parameters_to_use_in_filters"]['material']:
    #         if Material.objects.filter(eng_name=material).exists():
    #             material_db = Material.objects.get(eng_name=material)
    #             product.materials.add(material_db)
    # else:
    #     material = Material.objects.get(eng_name="other_material")
    #     product.materials.add(material)

    product.size_table_platform = data['size_tables']
    # product.size_table_platform = {'tables': {'default_table': {}, 'main_regular_table': {}, 'tables_recommendations': {}, 'main_measurements_table': {}}, 'size_fit': 0, 'main_sizes': [], 'main_size_table_row': 'undefined', 'size_fit_recommendation': 'Данная модель соответствует своему размеру. Мы рекомендуем выбирать <b>Ваш обычный размер</b>'}


    # product.size_row_name = data.get('size_row_name', "")
    # product.extra_name = data.get('extra_name', "")
    # product.description = data.get('description', "")
    # product.content_sources = data.get("content_sources")

    # product.has_many_sizes = data.get("many_sizes")
    # product.has_many_colors = data.get("many_colors")
    # product.has_many_configurations = data.get("many_configurations")

    product.save(product_slug=product_slug)
    product.product_units.update(availability=False)
    for sku in data['skus']:
        if sku['cnyPrice'] == 0 or "view_name" not in sku:
            continue
        delivery_offers = get_ps_delivery_offers(sku, data)
        sizes = []
        tables = []

        if "table_name" in sku and 'filter_sizes' in sku:

            for size in sku["filter_sizes"]:
                if sku['table_name'] == "undefined":
                    row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
                    sizes.append(row.id)
                else:
                    table = SizeTable.objects.get(name=sku["table_name"])
                    tables.append(table.id)
                    if size == 'undefined' or sku['row_name'] == "undefined":
                        row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
                        sizes.append(row.id)
                    else:
                        rows = table.rows.all()
                        for size_row in rows:
                            if size_row.row[sku["row_name"]] == size:
                                sizes.append(size_row.id)
                                break
        else:
            row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
            sizes.append(row.id)
        # platform_info = unit['platform_info']
        # poizon_info = platform_info['poizon']
        # del poizon_info['offers']
        # platform_info['poizon'] = poizon_info

        # header = poizon_info['header']

        for delivery_offer in delivery_offers:
            days_min = delivery_offer['days_min'] + sku['delivery_info']['min_platform_delivery']
            days_max = delivery_offer['days_max'] + sku['delivery_info']['max_platform_delivery']

            view_name = f'{days_min}-{days_max} {sklon_days(int(days_max))}'
            if days_min == days_max:
                view_name = f'{days_max} {sklon_days(int(days_max))}'

            delivery = DeliveryType.objects.create(
                name=delivery_offer['name'],
                view_name=view_name,
                days_min=days_min,
                days_max=days_max,
                days_max_to_international_warehouse=sku['delivery_info']['max_platform_delivery'],
                days_min_to_international_warehouse=sku['delivery_info']['min_platform_delivery'],
                days_min_to_russian_warehouse=delivery_offer['days_min'],
                days_max_to_russian_warehouse=delivery_offer['days_max'],
                absolute_insurance=delivery_offer.get('absolute_insurance', 0),
                decimal_insurance=delivery_offer.get('decimal_insurance', 0),
                delivery_price_per_kg_in_rub=delivery_offer['delivery_price'],

                # extra_charge=offer['extra_charge'] if offer['extra_charge'] else 0,
                # poizon_abroad=offer["platform_info"].get('poizon_abroad', False),
                commission = delivery_offer.get('comission', 0),
                delivery_type=delivery_offer['name'],
                currency=delivery_offer['currency'])

            if product.product_units.filter(view_size_platform=sku['view_name'],
                                            delivery_type__delivery_type=delivery_offer['name']).exists():
                product_unit = product.product_units.get(view_size_platform=sku['view_name'],
                                                         delivery_type__delivery_type=delivery_offer['name'])
                product_unit.delivery_type.delete()
                product_unit.delivery_type = delivery
                product_unit.original_price = sku['cnyPrice']


            else:
                product_unit = ProductUnit.objects.create(
                    product=product,
                    size_platform=sku['size'],
                    view_size_platform=sku['view_name'],
                    original_price=sku['cnyPrice'],
                    start_price=sku['cnyPrice'],
                    final_price=sku['cnyPrice'],
                    delivery_type=delivery,
                    platform=Platform.objects.get_or_create(platform='poizon',
                                                            site="poizon")[0],
                    # url=data['platform_info']["poizon"]['url'],
                    availability=True,
                    currency=
                    Currency.objects.get_or_create(name="CNY")[0],
                    # platform_info=platform_info,
                    weight_kg=sku['weight'],
                    # dimensions={"length": unit['length'],
                    #             "height": unit['height'],
                    #             "width": unit['width']}
                    # commission=delivery_offer['commission']

                )
            product_unit.availability = sku['cnyPrice'] != 0
            if 'poizon' not in product_unit.platform_info:
                product_unit.platform_info['poizon'] = {}
            product_unit.platform_info['poizon']['sku'] = sku['skuId']
            product_unit.update_history()

            product_unit.size.set(SizeTranslationRows.objects.filter(id__in=sizes))
            product.sizes.add(*SizeTranslationRows.objects.filter(id__in=sizes))
            product_unit.size_table.set(SizeTable.objects.filter(id__in=tables))

            product_unit.check_sale()

    product.update_price()
    t11 = time()
    product.check_sale()
    if product.is_sale:
        product.add_sale(product.sale_absolute, product.sale_percentage)

    sizes_info = {"sizes": [], "filter_logo": ""}
    sizes_id = set()
    for unit in product.product_units.filter(availability=True):
        for s in unit.size.all():
            row = s.table.default_row
            if row.filter_name != "Один размер":
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
    if product.bucket_link is None:
        product.available_flag = False

    if create:
        cats = product.categories.values_list("name", flat=True)
        if "Кеды" in cats or "Кроссовки" in cats:
            update_score_sneakers(product)
        else:
            update_score_clothes(product)
    product.in_process_update = False

    product.save()
    return product



def add_product_ps_api(data):
    print("Обновление цен")

    # print(spu_id)
    #     data = {"spuId": 1,
    #             "skus": [{"skuId": 542, "cnyPrice": 0}, {"skuId": 544, "cnyPrice": 0}, {"skuId": 557, "cnyPrice": 0},
    #                      {"skuId": 560, "cnyPrice": 0}, {"skuId": 561, "cnyPrice": 6559}, {"skuId": 565, "cnyPrice": 7199},
    #                      {"skuId": 589, "cnyPrice": 6989}, {"skuId": 592, "cnyPrice": 0}, {"skuId": 607, "cnyPrice": 6989},
    #                      {"skuId": 612, "cnyPrice": 7599}, {"skuId": 613, "cnyPrice": 6999},
    #                      {"skuId": 618, "cnyPrice": 7999}, {"skuId": 626, "cnyPrice": 0}, {"skuId": 627, "cnyPrice": 0},
    #                      {"skuId": 631, "cnyPrice": 9009}, {"skuId": 641, "cnyPrice": 0}, {"skuId": 642, "cnyPrice": 6999},
    #                      {"skuId": 644, "cnyPrice": 0}, {"skuId": 648, "cnyPrice": 0}, {"skuId": 652, "cnyPrice": 0}]}
    spu_id = data['spuId']
    products = Product.objects.filter(spu_id=spu_id)
    products.update(actual_price=False)
    products.update(in_process_update=True)

    # time_threshold = timezone.now() - timezone.timedelta(hours=1)
    # if products.exists():
    #     product = products.first()
    #     if product.last_upd >= time_threshold or product.in_process_update:
    #         return "Товар актуальный))"

    product_units = ProductUnit.objects.filter(product__spu_id=spu_id)
    # product_units.update(availability=False)
    skus = data.get("skus")

    f = False
    for sku in skus:
        if sku['cnyPrice'] != 0:
            product_unit = product_units.filter(platform_info__poizon__sku=sku['skuId'])
            product_unit.update(original_price=sku['cnyPrice'])
            product_unit.update(availability=True)
            print(sku['cnyPrice'])
            # product_unit.save()
            f = True
        # else:
        #     product_unit = product_units.filter(platform_info__poizon__sku=sku['skuId'])
        #     # product_unit.update(original_price=sku['cnyPrice'])
        #     product_unit.update(availability=False)

    if not f:
        products.update(available_flag=f)
    for product in products:
        sizes_info = {"sizes": [], "filter_logo": ""}
        sizes_id = set()
        for unit in product.product_units.filter(availability=True):
            for s in unit.size.all():
                row = s.table.default_row
                if row.filter_name != "Один размер":
                    if sizes_info['filter_logo'] == "" and row.filter_logo not in ['SIZE', "INT"]:
                        sizes_info['filter_logo'] = row.filter_logo
                    if s.id not in sizes_id:
                        sizes_info['sizes'].append([s.id, f"{s.row[row.filter_name]}"])
                        sizes_id.add(s.id)
        sizes_info['sizes'] = list(map(lambda x: x[1], sorted(sizes_info['sizes'])))
        print(sizes_info)
        product.available_sizes = sizes_info
        product.one_update = True
        product.last_upd = timezone.now()
        if product.bucket_link == None:
            product.available_flag = False
        product.in_process_update = False
        if product.is_sale:
            product.add_sale(product.sale_absolute, product.sale_percentage)
        product.save()
        product.update_price()


def add_products_spu_id_api(data):
    print("321")
    print(data)
    # property_ids = []
    # spu_id = 0
    # for product in data:
    #     property_ids.append(product['platform_info']['poizon']["propertyId"])
    #     spu_id = product['platform_info']['poizon']["spuId"]
    # # print(spu_id)
    # products = Product.objects.filter(spu_id=spu_id)
    # print(list(products.values_list("slug", flat=True)))
    # products.update(available_flag=False)
    s = []
    for product in data:
        add = add_product_v2(product)
        if type(add) == type(""):
            s.append(add)
        else:
            s.append(add.slug)
    return s


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
    manufacturer_sku = data.get("manufacturer_sku", "")

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
        print("go")
        time_threshold = timezone.now() - timezone.timedelta(hours=1)
        if product.last_upd >= time_threshold or product.in_process_update:
            product.available_flag = True
            product.save()
            return "Товар актуальный))"

        product.clear_all_fields()
        product.product_units.update(availability=False)
        product_slug = product.slug if product.slug != "" else f"{spu_id}_{property_id}_{manufacturer_sku}"
    else:

        product_slug = f"{spu_id}_{property_id}_{manufacturer_sku}"
    product.slug = product_slug
    product.save()

    product.is_collab = data["is_collab"]
    if data["is_collab"] and len(data['collab_names']) > 0:
        collab, create = Collab.objects.get_or_create(name=data['collab_names'][0])
        product.collab = collab

    product.model = data['model']
    product.colorway = data['colorway']
    product.is_custom = data['custom']
    product.formatted_manufacturer_sku = data.get("formatted_manufacturer_sku", "")
    product.manufacturer_sku = manufacturer_sku
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

    product.lines.clear()
    for i in range(len(data['lines'])):
        for line in data['lines'][i]:
            line_db = Line.objects.get(name=line)
            product.lines.add(line_db)
            if Line.objects.filter(name=f"Все {line}").exists():
                line_db = Line.objects.get(name=f"Все {line}")
                product.lines.add(line_db)

    product.brands.clear()
    for brand in data['brands']:
        brand_db, create = Brand.objects.get_or_create(name=brand)
        product.brands.add(brand_db)

        line, create = Line.objects.get_or_create(name=brand)
        product.lines.add(line)
        if Line.objects.filter(name=f"Все {brand}").exists():
            product.lines.add(Line.objects.get(name=f"Все {brand}"))

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
    rel_num = int(data['platform_info']["poizon"]["poizon_likes_count"]) if str(
        data['platform_info']["poizon"]["poizon_likes_count"]).isdigit() else 0
    product.rel_num = rel_num
    product.similar_product = data['platform_info']["poizon"].get("similar_products", [])
    product.another_configuration = data['platform_info']["poizon"].get("another_configuration", [])
    product.actual_price = False

    blacklisted_urls = product.black_bucket_link.values_list("url", flat=True)
    new_urls = [img["url"] for img in data["images"] if img["url"] not in blacklisted_urls]
    new_photos = []
    for url in new_urls:
        new_photo = Photo(url=url)
        new_photos.append(new_photo)
    Photo.objects.bulk_create(new_photos)
    all_photos = new_photos
    product.bucket_link.clear()
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

    product.size_table_platform = data['size_tables']
    product.size_row_name = data.get('size_row_name', "")
    product.extra_name = data.get('extra_name', "")
    product.description = data.get('description', "")
    product.content_sources = data.get("content_sources")

    product.has_many_sizes = data.get("many_sizes")
    product.has_many_colors = data.get("many_colors")
    product.has_many_configurations = data.get("many_configurations")

    product.save(product_slug=product_slug)
    for unit in data['units']:
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

            if not create and i < len(ids):
                product_unit = ProductUnit.objects.create(
                    id=ids[i],
                    product=product,
                    size_platform=unit['unit_name'],
                    view_size_platform=unit['unit_name'],
                    original_price=offer['price'],
                    start_price=offer['price'],
                    final_price=offer['price'],
                    delivery_type=dilivery,
                    platform=Platform.objects.get_or_create(platform='poizon', site="poizon")[0],
                    url=data['platform_info']["poizon"]['url'],
                    availability=True,
                    currency=Currency.objects.get_or_create(name=offer["currency"])[0],
                    platform_info=platform_info,
                    weight_kg=unit['weight'],
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
                    weight_kg=unit['weight'],
                    dimensions={"length": unit['length'],
                                "height": unit['height'],
                                "width": unit['width']}
                )
            product_unit.size.set(SizeTranslationRows.objects.filter(id__in=sizes))
            product.sizes.add(*SizeTranslationRows.objects.filter(id__in=sizes))
            product_unit.size_table.set(SizeTable.objects.filter(id__in=tables))
            # product_unit.check_sale()
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
        for s in unit.size.all():
            row = s.table.default_row
            if row.filter_name != "Один размер":
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
    if product.bucket_link == None:
        product.available_flag = False

    if create:
        cats = product.categories.values_list("name", flat=True)
        if "Кеды" in cats or "Кроссовки" in cats:
            update_score_sneakers(product)
        else:
            update_score_clothes(product)
    product.in_process_update = False
    if product.is_sale:
        product.add_sale(product.sale_absolute, product.sale_percentage)
    product.save()
    print(product.available_flag)
    print(product.manufacturer_sku)

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
