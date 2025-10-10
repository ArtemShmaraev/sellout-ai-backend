import random
from random import randint, choice, sample
import json
from functools import lru_cache
from datetime import datetime, date
from time import time

from django.core.cache import cache
from django.db.models import Q

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab, Photo, HeaderText, \
    HeaderPhoto
from products.serializers import LineSerializer, ProductMainPageSerializer

def get_product_for_selecet(queryset):
    return sample(list(queryset[:100].values_list("id", flat=True)), min(10, queryset.count()))



def get_random_model(model, type):
    # Попытаться получить данные из кэша
    cached_data = cache.get(f'random_{type}_data')

    if cached_data:
        queryset, probabilities = cached_data
    else:
        # Если данные не найдены в кэше, вычислить их
        queryset = model.objects.filter(score__gt=0)
        total_score = sum(model.score for model in queryset)
        probabilities = [model.score / total_score for model in queryset]

        # Сохранить данные в кэше на 10 минут
        cache.set(f'random_{type}_data', (queryset, probabilities), 600)

    random_model = random.choices(queryset, probabilities)[0]
    # print(random_model, random_model.score)
    return random_model

def get_header_photo():
    header = HeaderPhoto.objects.exclude(where='product_page')
    brand = choice(header)
    shoes = choice(header.filter(categories__eng_name="shoes_category"))
    clothes = choice(header.filter(categories__eng_name="clothes"))
    accessories = choice(header.filter(categories__eng_name="accessories"))
    bags = choice(header.filter(categories__eng_name="bags"))
    res = {"brand": brand.photo,
           "shoes": shoes.photo,
           "clothes": clothes.photo,
           "bags": bags.photo,
           "accessories": accessories.photo}
    return res


def get_random(queryset):
    try:
        # total_records = queryset.values("id").count()
        # random_index = randint(0, total_records - 1)
        # random_obj = queryset[random_index]
        return choice(queryset)
    except:
        return None


def get_line_selection(gender, line=None):
    filters = Q(available_flag=True)
    filters &= Q(is_custom=False)
    filters &= Q(gender__name__in=gender)
    if line is None:
        lines = Line.objects.filter(~Q(parent_line=None))
        # line = get_random_model(Line, "line")
        line = get_random(lines)
        products = Product.objects.filter(lines=line)

        products = products.filter(filters).order_by("-rel_num")
        if products.count() < 10:
            return get_line_selection(gender)
        else:
            title = f"{line.name}"
            url = f"line={line.full_eng_name}"
    else:
        products = Product.objects.filter(lines=line)

        products = products.filter(filters).order_by("-rel_num")
        title = f"{line.name}"
        url = f"line={line.full_eng_name}"

    list_id = get_product_for_selecet(products)

    return title, list_id, url


def get_collab_selection(gender, collab=None):
    filters = Q(available_flag=True)
    filters &= Q(is_custom=False)
    filters &= Q(gender__name__in=gender)
    if collab is None:
        collab = get_random_model(Collab, "collab")
        products = Product.objects.filter(collab=collab)

        products = products.filter(filters).order_by("-rel_num")
        if products.count() < 10:
            return get_collab_selection(gender)
        else:
            title = f"{collab.name}"
            url = f"collab={collab.query_name}"
    else:
        products = Product.objects.filter(collab=collab)
        products = products.filter(filters).order_by("-rel_num")
        title = f"{collab.name}"
        url = f"collab={collab.query_name}"

    list_id = get_product_for_selecet(products)

    return title, list_id, url


def get_color_and_line_selection(gender):
    colors = Color.objects.filter(is_main_color=True)
    random_color = get_random(colors)
    lines = Line.objects.filter(~Q(parent_line=None))
    line = get_random(lines)
    # line = get_random_model(Line, "line")
    products = Product.objects.filter(Q(lines=line) & Q(colors=random_color))
    filters = Q(available_flag=True)
    filters &= Q(is_custom=False)
    filters &= Q(gender__name__in=gender)
    products = products.filter(filters).order_by("-rel_num")
    if products.count() < 10:
        return get_color_and_line_selection(gender)
    else:
        title = f"{line.name}"
        url = f"line={line.full_eng_name}&color={random_color.name}"
    list_id = get_product_for_selecet(products)
    return title, list_id, url


def get_color_and_category_selection(gender):
    colors = Color.objects.filter(is_main_color=True)
    random_color = get_random(colors)
    random_category = get_random_model(Category, "category")

    products = Product.objects.filter(Q(categories=random_category) & Q(colors=random_color))
    filters = Q(available_flag=True)
    filters &= Q(is_custom=False)
    filters &= Q(gender__name__in=gender)
    products = products.filter(filters).order_by("-rel_num")
    if products.count() < 10:
        return get_color_and_category_selection(gender)
    else:
        title = f"{random_category.name}"
        url = f"category={random_category.eng_name}&color={random_color.name}"
    list_id = get_product_for_selecet(products)
    return title, list_id, url


def get_color_and_brand_selection(gender):
    colors = Color.objects.filter(is_main_color=True)
    random_color = get_random(colors)

    random_brand = get_random_model(Brand, "brand")

    products = Product.objects.filter(Q(brands=random_brand) & Q(colors=random_color))
    filters = Q(available_flag=True)
    filters &= Q(is_custom=False)
    filters &= Q(gender__name__in=gender)
    products = products.filter(filters).order_by("-rel_num")
    if products.count() < 10:
        return get_color_and_brand_selection(gender)
    else:
        title = f"{random_brand.name}"
        url = f"line={random_brand.query_name}&color={random_color.name}"
    list_id = get_product_for_selecet(products)
    return title, list_id, url


def get_brand_and_category_selection(gender):
    random_brand = get_random_model(Brand, "brand")

    random_category = get_random_model(Category, "category")

    products = Product.objects.filter(Q(categories=random_category) & Q(brands=random_brand))
    filters = Q(available_flag=True)
    filters &= Q(is_custom=False)
    filters &= Q(gender__name__in=gender)
    products = products.filter(filters).order_by("-rel_num")

    if products.count() < 10:
        return get_brand_and_category_selection(gender)
    else:
        title = f"{random_category.name} {random_brand.name}"
        url = f"category={random_category.eng_name}&line={random_brand.query_name}"
    list_id = get_product_for_selecet(products)
    return title, list_id, url


def get_brand_selection(gender):
    random_brand = get_random_model(Brand, "brand")
    products = Product.objects.filter(Q(brands=random_brand))
    filters = Q(available_flag=True)
    filters &= Q(is_custom=False)
    filters &= Q(gender__name__in=gender)
    products = products.filter(filters).order_by("-rel_num")
    if products.count() < 10:
        return get_brand_selection(gender)
    else:
        title = f"{random_brand.name}"
        url = f"line={random_brand.query_name}"
    list_id = get_product_for_selecet(products)
    return title, list_id, url


def get_category_selection(gender):
    random_cat = get_random_model(Category, "category")
    products = Product.objects.filter(Q(categories=random_cat))
    filters = Q(available_flag=True)
    filters &= Q(is_custom=False)
    filters &= Q(gender__name__in=gender)
    products = products.filter(filters).order_by("-rel_num")
    if products.count() < 10:
        return get_category_selection(gender)
    else:
        title = f"{random_cat.name}"
        url = f"category={random_cat.eng_name}"
    list_id = get_product_for_selecet(products)
    return title, list_id, url

def get_selection(gender):
    type = randint(1, 100)
    if 1 <= type < 15:
        title, queryset, url = get_brand_and_category_selection(gender)
    elif 15 <= type < 25:
        title, queryset, url = get_category_selection(gender)
    elif 25 <= type < 40:
        title, queryset, url = get_collab_selection(gender)
    elif 40 <= type < 48:
        title, queryset, url = get_color_and_category_selection(gender)
    elif 48 <= type < 60:
        title, queryset, url = get_color_and_brand_selection(gender)
    elif 60 <= type < 75:
        title, queryset, url = get_brand_selection(gender)
    elif 75 <= type < 85:
        title, queryset, url = get_color_and_line_selection(gender)
    else:
        title, queryset, url = get_line_selection(gender)
    res = {"type": "selection", "title": title, "url": url}

    return queryset, res


def get_photo():
    photos_desk = HeaderPhoto.objects.filter(type="desktop", where="product_page", rating=5)
    random_photo_desk = get_random(photos_desk)
    line_desk = random_photo_desk.lines.order_by("-id").first()
    collab_desk = random_photo_desk.collabs.first()

    photos_mobile = HeaderPhoto.objects.filter(type="mobile", where="product_page", rating=5)
    if line_desk is not None:
        photos_mobile = photos_mobile.filter(lines=line_desk)

    elif collab_desk is not None:
        photos_mobile = photos_mobile.filter(collabs=collab_desk)

    if not photos_mobile.exists():
        photos_mobile = HeaderPhoto.objects.filter(type="mobile", where="product_page", rating=5)

    random_photo_mobile = get_random(photos_mobile)
    return random_photo_desk, random_photo_mobile


def get_sellout_photo_text(last):
    type = ["left", "right"]
    if last == "any":
        last = type[randint(0, 1)]

    random_photo_desk, random_photo_mobile = get_photo()

    texts = HeaderText.objects.filter(title="sellout")
    count = texts.count()
    text = texts[randint(0, count - 1)]

    type = 'right' if last == 'left' else 'left'
    res = {'type': "photo",
           "desktop": {"type": f"{type}_photo", "photo": random_photo_desk.photo,
                       "title": text.title,
                       "content": text.text,
                       "url": "",
                       "button": "Все товары"},
           "mobile": {"photo": random_photo_mobile.photo,
                      "title": text.title,
                      "content": text.text,
                      "url": "",
                      "button": "Все товары"}}
    return res, type


def get_photo_text(last, gender):
    type = ["left", "right"]
    if last == "any":
        last = type[randint(0, 1)]

    random_photo_desk, random_photo_mobile = get_photo()

    f = True
    if random_photo_mobile.lines.exists():
        line = random_photo_mobile.lines.all().order_by("-id").first()
        url_mobile = f"line={line.full_eng_name}"
        title, queryset, url = get_line_selection(gender, line=line)
    elif random_photo_mobile.collabs.exists():
        collab = random_photo_mobile.collabs.first()
        url_mobile = f"collab={collab.query_name}"
        title, queryset, url = get_collab_selection(gender, collab=collab)

    else:
        url_mobile = ""
        f = False

    if random_photo_desk.lines.exists():
        line = random_photo_desk.lines.all().order_by("-id").first()
        url_desk = f"line={line.full_eng_name}"
    elif random_photo_desk.collabs.exists():
        collab = random_photo_desk.collabs.first()
        url_desk = f"collab={collab.query_name}"
    else:
        url_desk = ""

    selection = []
    if f:
        selection = queryset

    type = 'right' if last == 'left' else 'left'
    res = {'type': "photo",
           "desktop": {"type": f"{type}_photo", "photo": random_photo_desk.photo,
                       "title": random_photo_desk.header_text.title,
                       "content": random_photo_desk.header_text.text,
                       "url": url_desk,
                       "button": "Посмотреть все"},

           "mobile": {"photo": random_photo_mobile.photo,
                      "title": random_photo_mobile.header_text.title,
                      "content": random_photo_mobile.header_text.text,
                      "url": url_mobile,
                      "button": "Посмотреть все"
                      }}

    return res, type, selection
