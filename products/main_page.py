from random import randint
import json
from functools import lru_cache
from datetime import datetime, date

from django.db.models import Q

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab, Photo, HeaderText, \
    HeaderPhoto
from products.serializers import LineSerializer, ProductMainPageSerializer
from products.tools import get_text


def get_random(queryset):
    total_records = queryset.count()
    random_index = randint(0, total_records - 1)
    random_obj = queryset[random_index]
    return random_obj


def get_line_selection():
    lines = Line.objects.filter(~Q(parent_line=None))
    random_line = get_random(lines)
    products = Product.objects.filter(lines=random_line)
    if not products.exists():
        return get_brand_and_category_selection()
    else:
        products = products.order_by("-rel_num")[:30]
        title = f"{random_line.name}"
        url = f"line={random_line.full_eng_name}"
        return title, products, url


def get_collab_selection():
    collabs = Collab.objects.all()
    random_collab = get_random(collabs)
    products = Product.objects.filter(collab=random_collab)
    if not products.exists():
        return get_brand_and_category_selection()
    else:
        products = products.order_by("-rel_num")[:30]
        title = f"{random_collab.name}"
        url = f"collab={random_collab.query_name}"
        return title, products, url


def get_brand_and_category_selection():
    brands = Brand.objects.all()
    random_brand = get_random(brands)

    category = Category.objects.all()
    random_category = get_random(category)

    products = Product.objects.filter(Q(categories=random_category) & Q(brands=random_brand))
    if not products.exists():
        return get_brand_and_category_selection()
    else:
        products = products.order_by("-rel_num")[:30]
        title = f"{random_category.name} {random_brand.name}"
        url = f"category={random_category.eng_name}&line={random_brand.query_name}"
        return title, products, url


def get_selection(context):
    type = randint(1, 3)
    if type == 1:
        title, queryset, url = get_brand_and_category_selection()
    elif type == 2:
        title, queryset, url = get_collab_selection()
    else:
        title, queryset, url = get_line_selection()
    res = {"type": "selection", "title": title, "url": url}

    products = ProductMainPageSerializer(queryset, many=True, context=context).data
    res["products"] = products
    return res


def get_sellout_photo(last):
    type = ["left", "right"]
    if last == "any":
        last = type[randint(0, 1)]

    photos_desk = HeaderPhoto.objects.filter(type="desktop")
    photos_mobile = HeaderPhoto.objects.filter(type="mobile")
    random_photo_desk = get_random(photos_desk)
    random_photo_mobile = get_random(photos_mobile)
    texts = HeaderText.objects.filter(title="sellout")
    count = texts.count()
    text = texts[randint(0, count - 1)]

    type = 'right' if last == 'left' else 'left'
    res = {'type': "photo",
           "desktop": {"type": f"{type}_photo", "photo": random_photo_desk.photo.url,
                       "title": text.title,
                       "content": text.text},
           "mobile": {"photo": random_photo_mobile.photo.url,
                      "title": text.title,
                      "content": text.text}}
    return res, type


def get_photo(last):
    type = ["left", "right"]
    if last == "any":
        last = type[randint(0, 1)]

    photos_desk = HeaderPhoto.objects.filter(type="desktop").filter(where="product_page")
    photos_mobile = HeaderPhoto.objects.filter(type="mobile").filter(where="product_page")
    random_photo_desk = get_random(photos_desk)
    random_photo_mobile = get_random(photos_mobile)
    text_desk = get_text(random_photo_desk, list(random_photo_desk.categories.values_list("eng_name", flat=True)))
    text_mobile = get_text(random_photo_mobile, list(random_photo_desk.categories.values_list("eng_name", flat=True)))
    type = 'right' if last == 'left' else 'left'
    res = {'type': "photo",
           "desktop": {"type": f"{type}_photo", "photo": random_photo_desk.photo.url,
                       "title": text_desk.title,
                       "content": text_desk.text},
           "mobile": {"photo": random_photo_mobile.photo.url,
                      "title": text_mobile.title,
                      "content": text_mobile.text}}

    return res, type
