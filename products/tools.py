import asyncio
import math
import random
import json
from functools import lru_cache
from datetime import datetime, date
from time import time

import httpx
import requests
from django.core.cache import cache
from django.db.models import Q, Case, When, Value, IntegerField, Sum
from django.utils import timezone

from products.formula_price import formula_price
# from products.main_page import get_random
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab, Photo, HeaderText, \
    HeaderPhoto

from users.models import UserStatus

from json2xml import json2xml
import xml.etree.ElementTree as ET

def get_fid_product(products):
    yml_catalog = ET.Element('yml_catalog', attrib={"date": str(datetime.now())})
    # Создаем элемент shop и добавляем его в корневой элемент
    shop = ET.Element('shop')
    yml_catalog.append(shop)

    # Создаем элементы внутри shop
    shop_name = ET.Element('name')
    shop_name.text = "Sellout"
    shop_company = ET.Element('company')
    shop_company.text = "Sellout"
    shop_url = ET.Element('url')
    shop_url.text = "https://sellout.su"
    shop_categories = ET.Element('categories')
    shop.append(shop_name)
    shop.append(shop_company)
    shop.append(shop_url)
    shop.append(shop_categories)

    delivery_tag = ET.Element('delivery-options')
    shop.append(delivery_tag)

    deliveries = [(5, 500)]
    for delivery in deliveries:
        delivery_elem = ET.Element('option', attrib={"days": str(delivery[0]),
                                                      "cost": str(delivery[1])})
        delivery_tag.append(delivery_elem)

    # Проходимся по категориям и добавляем их в shop


    categories = Category.objects.order_by("id")
    for category in categories:
        category_elem = ET.Element('category', attrib={"id": str(category.id)})
        category_elem.text = category.name
        if category.parent_category is not None:
            category_elem.set("parentId", str(category.parent_category.id))
        shop_categories.append(category_elem)


    shop_offers = ET.Element('offers')
    for product in products:

        # Создаем элемент offer
        offer = ET.Element('offer', attrib={"id": str(product.id)})
        offer_name = ET.Element('name')

        delivery_tag = ET.Element('delivery-options')
        offer.append(delivery_tag)

        deliveries = [(20, 500)]
        for delivery in deliveries:
            delivery_elem = ET.Element('options', attrib={"days": str(delivery[0]), "cost": str(delivery[1] if product.min_price < 35000 else 0)})
            delivery_tag.append(delivery_elem)

        offer_name.text = product.get_full_name()
        offer_vendor = ET.Element('vendor')
        offer_vendor.text = product.brands.first().name if product.collab is None else product.collab.name
        offer_vendorCode = ET.Element('vendorCode')
        offer_vendorCode.text = product.manufacturer_sku
        offer_url = ET.Element('url')
        offer_url.text = f"https://sellout.su/products/{product.slug}"
        offer_price = ET.Element('price')
        offer_price.text = str(product.min_price)

        if product.min_price != product.min_price_without_sale:
            offer_old_price = ET.Element('oldprice')
            offer_old_price.text = str(product.min_price_without_sale)

        offer_currencyId = ET.Element('currencyId')
        offer_currencyId.text = "RUR"
        offer_picture = ET.Element('picture')
        offer_picture.text = product.bucket_link.order_by("id").first().url
        offer_categoryId = ET.Element('categoryId')
        offer_categoryId.text = str(product.categories.order_by("-id").first().id)
        offer_category = ET.Element('category')
        offer_category.text = product.categories.order_by("-id").first().name
        offer_delivery = ET.Element('delivery')
        offer_delivery.text = "True"
        offer_description = ET.Element('description')
        offer_description.text = f"""<![CDATA[Оригинал {product.get_full_name()} можно заказать прямо сейчас. Выгодные цены и бонусы ждут вас. Сделайте свой шаг в мир моды.]]>"""


        # Добавляем элементы offer в offer и добавляем его в shop
        offer.append(offer_name)
        offer.append(offer_vendor)
        offer.append(offer_vendorCode)
        offer.append(offer_url)
        offer.append(offer_price)
        offer.append(offer_currencyId)
        offer.append(offer_picture)
        offer.append(offer_categoryId)
        offer.append(offer_category)



        product_colors = product.colors.all()
        for color in product_colors:
            offer_params = ET.Element('param', attrib={"name": "Цвет"})
            offer_params.text = color.russian_name
            offer.append(offer_params)

        product_materials = product.materials.all()
        for material in product_materials:
            offer_params = ET.Element('param', attrib={"name": "Материал"})
            offer_params.text = material.name
            offer.append(offer_params)

        offer.append(offer_delivery)
        offer.append(offer_description)

        shop_offers.append(offer)
    shop.append(shop_offers)

    # Создаем XML-документ
    # tree = ET.ElementTree(yml_catalog)
    xml_str = ET.tostring(yml_catalog, encoding='utf8')

    # Преобразуем байтовую строку в строку unicode
    # xml = xml_str.decode('utf-8')

    return xml_str


def get_title_for_products_page(categories, lines, collabs):
    title = ""
    if len(categories) == 1:
        title += Category.objects.get(eng_name=categories[0]).name + " "
    if len(lines) == 1:
        title += Line.objects.get(full_eng_name=lines[0]).view_name
    elif len(collabs) == 1:
        title += Collab.objects.get(query_name=collabs[0]).name

    return title.strip()


def update_score_sneakers(product):
    total_score_line = product.lines.all().aggregate(Sum('score_product_page'))['score_product_page__sum']
    num = product.lines.count()
    score_line = 0
    if num > 0:
        score_line = round((total_score_line) / (num))

    collab = product.collab
    score_collab = 0
    if collab is not None:
        score_collab = collab.score_product_page

    normalize_rel_num = 0
    if product.rel_num > 0:
        normalize_rel_num = min(10000, round(math.log(product.rel_num, 1.0015)))

    product.normalize_rel_num = normalize_rel_num

    if product.likes_month == -1:
        try:
            old_likes = product.rel_num
            new_likes = \
                requests.get(
                    f"https://spucdn.dewu.com/dewu/commodity/detail/simple/{product.spu_id}.json").json()[
                    'data']["favoriteCount"]['count']
            likes_month = new_likes - old_likes
            product.likes_month = likes_month
        except:
            product.likes_month = 0
    likes_week = product.likes_month // 10
    product.likes_week = likes_week

    is_new = 1 if product.is_new else 0
    my_score = product.extra_score

    PLV = 0.27 * normalize_rel_num
    D_PLV = 0.43 * min(100000 * (likes_week / max(1, normalize_rel_num)), 3000)
    NEW = 700 * is_new
    TYPE_SCORE = 0.1 * (score_collab + score_line) * 100
    MY_SCORE = 0.1 * my_score
    total_score = round(PLV + D_PLV + NEW + TYPE_SCORE + MY_SCORE)
    product.score_product_page = total_score
    product.save()
    print(product.score_product_page)

def update_score_clothes(product):
    with open('edit_brand+category_score.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    old = product.score_product_page
    try:
        brand = product.brands.first().name
        category = product.categories.all().order_by("-id").first().name

        brand_and_category_score = data[f"{brand}_{category}"]

    except:
        brand_and_category_score = 1000

    normalize_rel_num = 0
    if product.rel_num > 0:
        normalize_rel_num = min(10000, round(math.log(product.rel_num, 1.0015)))

    product.normalize_rel_num = normalize_rel_num

    rel_num = product.rel_num
    likes_month = product.likes_month

    if likes_month > rel_num:
        new = rel_num + likes_month
        old = rel_num // 0.3
        product.rel_num = old
        product.likes_month = new - old

    if likes_month == -1:
        try:
            old_likes = product.rel_num
            new_likes = \
                requests.get(
                    f"https://spucdn.dewu.com/dewu/commodity/detail/simple/{product.spu_id}.json").json()[
                    'data']["favoriteCount"]['count']
            likes_month = new_likes - old_likes
            product.likes_month = likes_month
        except:
            product.likes_month = 0
    likes_week = product.likes_month // 10
    product.likes_week = likes_week

    # is_new = 1 if product.is_new else 0
    my_score = product.extra_score

    PLV = 0.2 * normalize_rel_num
    D_PLV = 0.3 * (10 * min(max(round(math.log(likes_week, 1.047), 2), 10), 100)) if likes_week > 0 else 0
    # NEW = 700 * is_new
    TYPE_SCORE = 0.4 * brand_and_category_score
    MY_SCORE = 0.1 * my_score
    total_score = round(PLV + D_PLV + TYPE_SCORE + MY_SCORE)
    product.score_product_page = total_score
    product.up_score = True
    product.save()

def platform_update_price(product, request=False):
    async def send_async_request(spu_id):
        async with httpx.AsyncClient() as client:
            print("Денис сукааааа")
            response = await client.get(f"https://sellout.su/product_processing/process_spu_id?spu_id={spu_id}")
            print("Денис сукааааа дважды")
            # Вы можете добавить обработку ответа, если это необходимо
            return response
    if request:
        user_identifier = request.META.get('REMOTE_ADDR')
        # Генерируем уникальный ключ для кэша
        cache_key = f'request_count:{user_identifier}'
        # Получаем текущее количество запросов пользователя
        request_count = cache.get(cache_key, default=0)
        # Увеличиваем количество запросов на 1
        request_count += 1
        # Устанавливаем значение в кэше с истечением через 1 час
        cache.set(cache_key, request_count, 3600)
        if request_count < 5000:
            time_threshold1 = timezone.now() - timezone.timedelta(minutes=5)
            if not product.last_parse_price >= time_threshold1:
                spu_id = product.spu_id
                time_threshold2 = timezone.now() - timezone.timedelta(hours=1)
                if not product.last_upd >= time_threshold2:  # если цена не актуальна
                    product.last_parse_price = timezone.now()
                    product.save()
                    s = requests.get(f"https://sellout.su/intermediate_parser/process_spu_id?spu_id={spu_id}")
                    print("Идет обновление1")
                    # print(s.json())
                    # asyncio.run(send_async_request(spu_id))

    else:
        time_threshold1 = timezone.now() - timezone.timedelta(minutes=5)
        if not product.last_parse_price >= time_threshold1:
            spu_id = product.spu_id
            time_threshold2 = timezone.now() - timezone.timedelta(hours=1)
            if not product.last_upd >= time_threshold2:  # если цена не актуальна
                product.last_parse_price = timezone.now()
                product.save()
                s = requests.get(f"https://sellout.su/intermediate_parser/process_spu_id?spu_id={spu_id}")
                print("Идет обновление2")
                # print(s.json())
                # asyncio.run(send_async_request(spu_id))


def update_price(product):
    if not product.actual_price:
        user_status = UserStatus.objects.get(name="Amethyst")
        for unit in product.product_units.filter(availability=True):
            price = formula_price(product, unit, user_status)
            unit.start_price = price['start_price']
            unit.final_price = price['final_price']
            unit.bonus = price['bonus']
            unit.save()
        product.update_min_price()





def get_queryset_from_list_id(product_ids):
    # print(len(product_ids), "cerf")
    # print(product_ids)
    queryset = Product.objects.filter(id__in=list(product_ids))
    # print(queryset.count())

    # Определение порядка объектов в queryset
    preserved_order = Case(
        *[
            When(id=pk, then=pos) for pos, pk in enumerate(product_ids)
        ],
        default=Value(len(product_ids)),
        output_field=IntegerField()
    )
    queryset = queryset.annotate(order=preserved_order).order_by('order')

    return queryset



class RandomGenerator:
    def __init__(self):
        self.last_value = None
        self.same_count = 0

    def generate(self):
        while True:
            value = random.randint(0, 1)
            if value != self.last_value:
                self.last_value = value
                self.same_count = 1
                return value
            else:
                self.same_count += 1
                if (value == 0 and self.same_count >= 3) or (value == 1 and self.same_count >= 5):
                    self.last_value = 1 - value
                    self.same_count = 1
                    return self.last_value


def get_product_page_photo(params):
    line = params.getlist('line')
    category = params.getlist("category")
    collab = params.getlist("collab")
    res = {}
    header_photos = HeaderPhoto.objects.all()
    header_photos = header_photos.filter(where="product_page")
    text = False
    if category:
        header_photos = header_photos.filter(categories__eng_name__in=category)

    if line and collab:
        if "all" in collab:
            header_photos = header_photos.filter(
                Q(lines__full_eng_name__in=line) | ~Q(collabs=None)
            )
        else:
            header_photos = header_photos.filter(
                Q(lines__full_eng_name__in=line) | Q(collabs__query_name__in=collab)
            )
    elif line:
        header_photos = header_photos.filter(Q(lines__full_eng_name__in=line))

    elif collab:
        if "all" in collab:
            header_photos = header_photos.filter(~Q(collabs=None))
        else:
            header_photos = header_photos.filter(Q(collabs__query_name__in=collab))
    else:
        text = HeaderText.objects.filter(title="sellout")[random.randint(0, 4)]

    header_photos_desktop = header_photos.filter(type="desktop")
    header_photos_mobile = header_photos.filter(type="mobile")
    if header_photos_desktop.count() > 0:
        count = header_photos_desktop.count()
    else:
        header_photos_desktop = HeaderPhoto.objects.filter(type="desktop")
        count = header_photos_desktop.count()

    photo_desktop = header_photos_desktop[random.randint(0, count - 1)]

    if not text:
        text_desktop = get_text(photo_desktop, category)
    else:
        text_desktop = text

    res["desktop"] = {"title": text_desktop.title, "content": text_desktop.text}
    res['desktop']['photo'] = photo_desktop.photo

    if header_photos_mobile.count() > 0:
        count = header_photos_mobile.count()
    else:
        header_photos_mobile = HeaderPhoto.objects.filter(type="mobile")
        count = header_photos_mobile.count()

    photo_mobile = header_photos_mobile[random.randint(0, count - 1)]
    if not text:
        text_mobile = get_text(photo_mobile, category)
    else:
        text_mobile = text

    res["mobile"] = {"title": text_mobile.title, "content": text_mobile.text}
    res['mobile']['photo'] = photo_mobile.photo
    return res


def get_product_text(photo, line, collab, category, new, recommendations, sale):
    texts = HeaderText.objects.all()
    type = photo.type


    if new:
        texts = texts.filter(title="Новинки")
    elif recommendations:
        texts = texts.filter(title="Рекомендации")
    elif sale:
        texts = texts.filter(title="Скидки — еще больше выгоды")

    elif line and collab:
        texts = texts.filter(title="sellout")



    elif line:

        def find_common_ancestor(lines):
            current_line = lines[0]
            parent_lines = set()
            parent_lines.add(current_line)

            while current_line.parent_line:
                parent_lines.add(current_line.parent_line)
                current_line = current_line.parent_line

            # Переберите остальные выбранные линейки и найдите первую общую вершину
            old_lines = list()
            for line in lines[1:]:
                current_line = line
                while current_line:
                    if current_line in parent_lines:
                        old_lines.append(current_line.id)
                    current_line = current_line.parent_line
            if len(lines) == 1:
                return lines[0]
            line = Line.objects.filter(id__in=old_lines).order_by("id").first()
            return line


        selected_lines = Line.objects.filter(full_eng_name__in=line)  # Ваши выбранные линейки
        oldest_line = find_common_ancestor(selected_lines)
        # print(oldest_line)
        # print(photo.lines.all())
        # if len(selected_lines) > 0:
        #     oldest_line = find_common_ancestor(selected_lines)
        #     list_line.append(oldest_line.full_eng_name)
        #     while oldest_line.parent_line:
        #         list_line.append(oldest_line.parent_line.full_eng_name)
        #         oldest_line = oldest_line.parent_line
        # lines = []
        # if oldest_line:
        #     print(oldest_line.name)
        #     lines = [oldest_line.full_eng_name]
        #     # if Line.objects.filter(name=f"Все {oldest_line.name}").exists():
        #     #     line_db = Line.objects.get(name=f"Все {oldest_line.name}")
        #     #     lines.append(line_db.full_eng_name)
        texts = texts.filter(lines__in=photo.lines.all())
        texts = texts.filter(lines=oldest_line)

        # print("вот")
        # print(oldest_line)
        # print(photo.lines.values_list("name", flat=True))
        # print("лист", list_line)
        # print(texts)

    elif collab:
        texts = texts.filter(collabs__in=photo.collabs.all())
        texts = texts.filter(collabs__query_name__in=collab)

    elif category:
        categories = Category.objects.filter(eng_name__in=category)
        list_cat = set()
        for cat in categories:
            list_cat.add(cat.eng_name)
            curent = cat
            while curent.parent_category is not None:
                curent = curent.parent_category
                list_cat.add(curent.eng_name)
        if "sneakers" in list_cat:
            texts = texts.filter(title="Кроссовки")
        elif "shoes_category" in list_cat:
            texts = texts.filter(title="Обувь")
        else:
            texts = texts.filter(title="sellout", type=type)
    elif not line and not collab and not category and not new and not recommendations:
        texts = texts.filter(title="sellout", type=type)
    if not texts.exists():
        texts = HeaderText.objects.filter(title="sellout", type=type)
    text = random.choice(texts)

    return text


def get_text(photo, category):
    if photo.lines.exists():
        line = photo.lines.all().order_by("-id").first()
        texts = HeaderText.objects.all()
        while line.parent_line is not None:
            texts = HeaderText.objects.filter(lines=line)
            if texts.exists():
                break
            line = line.parent_line
    elif photo.collabs.exists():
        collab = photo.collabs.all().first()
        texts = HeaderText.objects.filter(collabs=collab)
    elif "shoes_category" in category or "sneakers" in category or "high_top_sneakers" in category or "low_top_sneakers" in category:
        category = ["shoes_category", "sneakers"]
        texts = HeaderText.objects.filter(categories__eng_name__in=category)
    else:
        texts = HeaderText.objects.filter(title="sellout")

    if not texts.exists():
        texts = HeaderText.objects.filter(title="sellout")
    count = texts.count()
    text = texts[random.randint(0, count - 1)]
    return text

def build_category_tree(categories):
    category_dict = {}
    root_categories = []

    # Создаем словарь для быстрого доступа к категориям по их идентификатору
    for category in categories:
        category_dict[category["id"]] = category

    # Строим иерархическую структуру категорий
    for category in categories:
        parent_ids = category["parent_category"]
        if parent_ids:
            parent_category = category_dict[parent_ids]
            parent_category.setdefault("children", []).append(category)
        else:
            root_categories.append(category)

    def recursive_sort_categories(category):
        if "children" in category:
            category["children"] = sorted(category["children"], key=lambda x: x["id"])
            for child in category["children"]:
                recursive_sort_categories(child)

    # Применить функцию к корневым категориям
    for root_category in root_categories:
        recursive_sort_categories(root_category)

    return root_categories


def category_no_child(cats):
    result = []
    for cat in cats:
        if 'subcategories' not in cat:
            result.append(cat)
        else:
            children = cat['subcategories']
            result.extend(category_no_child(children))
    # result.sort(key=lambda x: x['full_name'])
    return result


@lru_cache(maxsize=2)
def build_line_tree():
    from products.serializers import LineSerializer
    lines = LineSerializer(Line.objects.all(), many=True).data
    line_dict = {}
    root_lines = []
    # Создание словаря линеек с использованием их идентификаторов в качестве ключей
    for line in lines:
        line_dict[line['id']] = line

    # Построение дерева линеек
    for line in lines:
        parent_line = line['parent_line']
        if parent_line is None:
            # Если у линейки нет родительской линейки, она считается корневой линейкой
            del line['parent_line']
            line["is_show"] = True
            root_lines.append(line)
        else:
            parent_id = parent_line['id']
            parent_line = line_dict.get(parent_id)
            if parent_line:
                del line['parent_line']
                # line["is_show"] = True
                # Если родительская линейка найдена, добавляем текущую линейку в список её дочерних линеек
                parent_line.setdefault('children', []).append(line)

    def sort_children(data):
        for item in data:
            children = item.get('children')
            if children:
                # Сначала сортируем элементы, исключая "Другие"
                sorted_children = sorted([child for child in children if "Другие" not in child['name']],
                                         key=lambda x: x["id"])
                # Добавляем элементы с именем "Другие" в конец
                other_children = [child for child in children if "Другие" in child['name']]
                sorted_children += other_children
                item['children'] = sorted_children
                # Рекурсивно сортируем дочерние элементы
                sort_children(item['children'])
        return data

    root_lines = sort_children(root_lines)
    with_children = [x for x in root_lines if x.get('children')]

    without_children = [x for x in root_lines if not x.get('children')]

    sorted_data_with_children = sorted(with_children, key=lambda x: x["id"])

    # Сортируем оставшиеся элементы
    sorted_data_without_children = sorted(without_children, key=lambda x: x['view_name'].lower())
    # Объединяем отсортированные части
    sorted_data = sorted_data_with_children + sorted_data_without_children
    return sorted_data



def line_no_child(lines):
    line_dict = {}
    root_lines = []

    # Создание словаря линеек с использованием их идентификаторов в качестве ключей
    for line in lines:
        line_dict[line['id']] = line

    # Построение дерева линеек
    for line in lines:
        parent_line = line['parent_line']
        if parent_line is None:
            # Если у линейки нет родительской линейки, она считается корневой линейкой
            root_lines.append(line)
        else:
            parent_id = parent_line['id']
            parent_line = line_dict.get(parent_id)
            if parent_line:
                # Если родительская линейка найдена, добавляем текущую линейку в список её дочерних линеек
                parent_line.setdefault('children', []).append(line)

    def get_lines_without_children(lines):
        result = []
        for line in lines:
            if 'children' not in line:
                result.append(line)
            else:
                children = line['children']
                result.extend(get_lines_without_children(children))
        result.sort(key=lambda x: x['name'])
        return result

    return get_lines_without_children(root_lines)


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


