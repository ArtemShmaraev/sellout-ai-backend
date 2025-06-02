from random import randint
import json
from functools import lru_cache
from datetime import datetime, date

from django.db.models import Q

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab, Photo, HeaderText, \
    HeaderPhoto
from products.serializers import LineSerializer, ProductMainPageSerializer



def get_header_photo():
    header = HeaderPhoto.objects.exclude(where='product_page')
    brand = get_random(header)
    shoes = get_random(header.filter(categories__eng_name="shoes_category"))
    clothes = get_random(header.filter(categories__eng_name="clothes"))
    accessories = get_random(header.filter(categories__eng_name="accessories"))
    res = {"brand": brand.photo.url,
           "shoes": shoes.photo.url,
           "clothes": clothes.photo.url,
           "accessories": accessories.photo.url}
    return res


def get_random(queryset):
    try:
        total_records = queryset.count()
        random_index = randint(0, total_records - 1)
        random_obj = queryset[random_index]
        return random_obj
    except:
        return None


def get_line_selection():
    lines = Line.objects.filter(~Q(parent_line=None))
    random_line = get_random(lines)
    products = Product.objects.filter(lines=random_line)
    if not products.exists():
        return get_line_selection()
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
        return get_collab_selection()
    else:
        products = products.order_by("-rel_num")[:30]
        title = f"{random_collab.name}"
        url = f"collab={random_collab.query_name}"
        return title, products, url


def get_brand_and_category_selection():
    brands = Brand.objects.all()
    random_brand = get_random(brands)

    category = Category.objects.all().exclude(name__icontains='Все').exclude(name__icontains='Вся')
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



def get_photo():
    photos_desk = HeaderPhoto.objects.filter(type="desktop").filter(where="product_page")
    random_photo_desk = get_random(photos_desk)
    line_desk = random_photo_desk.lines.order_by("-id").first()
    collab_desk = random_photo_desk.collabs.first()

    photos_mobile = HeaderPhoto.objects.filter(type="mobile").filter(where="product_page")

    if line_desk is not None:
        photos_mobile = photos_mobile.filter(lines=line_desk)
    elif collab_desk is not None:
        photos_mobile = photos_mobile.filter(collabs=collab_desk)

    if not photos_mobile.exists():
        photos_mobile = HeaderPhoto.objects.filter(type="mobile").filter(where="product_page")

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
           "desktop": {"type": f"{type}_photo", "photo": random_photo_desk.photo.url,
                       "title": text.title,
                       "content": text.text,
                       "url": ""},
           "mobile": {"photo": random_photo_mobile.photo.url,
                      "title": text.title,
                      "content": text.text,
                      "url": ""}}
    return res, type


def get_photo_text(last):
    type = ["left", "right"]
    if last == "any":
        last = type[randint(0, 1)]

    random_photo_desk, random_photo_mobile = get_photo()


    if random_photo_mobile.lines.exists():
        line = random_photo_mobile.lines.all().order_by("-id").first()
        url_mobile = f"line={line.full_eng_name}"
    elif random_photo_mobile.collabs.exists():
        collab = random_photo_mobile.collabs.first()
        url_mobile = f"collab={collab.query_name}"
    else:
        url_mobile = ""


    if random_photo_desk.lines.exists():
        line = random_photo_desk.lines.all().order_by("-id").first()
        url_desk = f"line={line.full_eng_name}"
    elif random_photo_desk.collabs.exists():
        collab = random_photo_desk.collabs.first()
        url_desk = f"collab={collab.query_name}"
    else:
        url_desk = ""

    type = 'right' if last == 'left' else 'left'
    res = {'type': "photo",
           "desktop": {"type": f"{type}_photo", "photo": random_photo_desk.photo.url,
                       "title": random_photo_desk.header_text.title,
                       "content": random_photo_desk.header_text.text,
                       "url": url_desk},

           "mobile": {"photo": random_photo_mobile.photo.url,
                      "title": random_photo_mobile.header_text.title,
                      "content": random_photo_mobile.header_text.text,
                      "url": url_mobile}}

    return res, type
