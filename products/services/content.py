"""
Content service — page headers, main page blocks, selections.
Объединяет логику из product_page.py и main_page.py.
"""
from datetime import datetime, timedelta
import math
import random
from random import choice, randint, sample
import unicodedata
from urllib.parse import urlencode

from django.core.cache import cache
from django.db.models import Min, OuterRef, Q, Subquery

from products.models import (
    Brand,
    Category,
    Collab,
    Color,
    HeaderPhoto,
    HeaderText,
    Line,
    Product,
)
from products.search_tools import search_product
from products.tools import get_product_text, get_queryset_from_list_id, get_title_for_products_page
from sellout.settings import CACHE_TIME

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_product_for_selecet(queryset):
    return sample(list(queryset[:100].values_list("id", flat=True)), min(15, queryset.count()))


def get_random(queryset):
    try:
        return choice(queryset)
    except:  # noqa: E722
        return None


def get_random_model(model, type):
    cached_data = cache.get(f'random_{type}_data')

    if cached_data:
        queryset, probabilities = cached_data
    else:
        queryset = model.objects.filter(score__gt=0)
        total_score = sum(model.score for model in queryset)
        probabilities = [model.score / total_score for model in queryset]
        cache.set(f'random_{type}_data', (queryset, probabilities), 600)

    return random.choices(queryset, probabilities)[0]


# ---------------------------------------------------------------------------
# Product page
# ---------------------------------------------------------------------------

def get_product_page_header(request):
    def is_russian_letter(char):
        return 'CYRILLIC' in unicodedata.name(char, '')

    res = {}

    line = request.query_params.getlist('line')
    category = request.query_params.getlist("category")
    gender = request.query_params.getlist("gender")
    collab = request.query_params.getlist("collab")
    collection = request.query_params.getlist("collection")
    new = request.query_params.get("new")
    sale = request.query_params.get("is_sale")
    recommendations = request.query_params.get("recommendations")
    q = request.query_params.get("q", "")
    header_photos = HeaderPhoto.objects.filter(where="product_page")

    if len(line) == 1 and len(collab) == 0:
        header_photos = header_photos.filter(Q(lines__full_eng_name__in=line))
    elif len(collab) == 1 and len(line) == 0:
        header_photos = header_photos.filter(Q(collabs__query_name__in=collab))

    if not header_photos.exists():
        header_photos = HeaderPhoto.objects.filter(where="product_page")

    header_photos_desktop = header_photos.filter(type="desktop", rating=5)
    header_photos_mobile = header_photos.filter(type="mobile", rating=5)
    if not header_photos_desktop.exists():
        header_photos_desktop = header_photos.filter(type="desktop")
        if not header_photos_desktop.exists():
            header_photos_desktop = HeaderPhoto.objects.filter(type="desktop")
    count = header_photos_desktop.count()

    photo_desktop = header_photos_desktop[random.randint(0, count - 1)]
    text_desktop = get_product_text(photo_desktop, line, collab, category, new, recommendations, sale)
    if text_desktop is None:
        text_desktop = photo_desktop.header_text

    title_desktop_gender = text_desktop.title

    res["desktop"] = {"title": text_desktop.title, "content": text_desktop.text,
                      "title_with_gender": title_desktop_gender}
    res['desktop']['photo'] = photo_desktop.photo
    res['desktop']['subtitle'] = ""

    if text_desktop.title == "sellout":
        title_desktop, subtitle_desktop = get_title_for_products_page(category, line, collab, collection)
        title_desktop = title_desktop.replace("Все", "").replace("Вся", "").strip()
        if title_desktop and is_russian_letter(title_desktop[0]):
            title_desktop = title_desktop[0].upper() + title_desktop[1:]
        res['desktop']['title'] = title_desktop
        res['desktop']['subtitle'] = subtitle_desktop
        res['desktop']['title_with_gender'] = title_desktop
        res['desktop']['content'] = ""
        res['desktop']['photo'] = ""

    if not header_photos_mobile.exists():
        header_photos_mobile = header_photos.filter(type="mobile")
        if not header_photos_mobile.exists():
            header_photos_mobile = HeaderPhoto.objects.filter(type="mobile")
    count = header_photos_mobile.count()

    photo_mobile = header_photos_mobile[random.randint(0, count - 1)]
    text_mobile = get_product_text(photo_mobile, line, collab, category, new, recommendations, sale)
    if text_mobile is None:
        text_mobile = photo_mobile.header_text

    title_mobile_gender = text_mobile.title

    res["mobile"] = {"title": text_mobile.title, "content": text_mobile.text,
                     "title_with_gender": title_mobile_gender}
    res['mobile']['photo'] = photo_mobile.photo
    res['mobile']['subtitle'] = ""

    if text_mobile.title == "sellout":
        title_mobile, subtitle_mobile = get_title_for_products_page(category, line, collab, collection)
        title_mobile = title_mobile.replace("Все", "").replace("Вся", "").strip()
        if title_mobile and is_russian_letter(title_mobile[0]):
            title_mobile = title_mobile[0].upper() + title_mobile[1:]
        res['mobile']['title'] = title_mobile
        res['mobile']['subtitle'] = subtitle_mobile
        res['mobile']['title_with_gender'] = title_mobile
        res['mobile']['content'] = ""
        res['mobile']['photo'] = ""

    res['desktop']['gender'] = gender
    res['desktop']['category'] = category
    res['desktop']['collab'] = collab
    res['desktop']['line'] = line
    res['desktop']['q'] = q
    res['desktop']['collection'] = collection

    res['mobile']['gender'] = gender
    res['mobile']['category'] = category
    res['mobile']['collab'] = collab
    res['mobile']['line'] = line
    res['mobile']['q'] = q
    res['mobile']['collection'] = collection
    return res


def count_queryset(request):
    params = request.GET.copy()
    queryset = filter_products(request).values_list("id", flat=True)
    if 'page' in params:
        del params['page']
    cache_count_key = f"count:{urlencode(params)}"
    cached_count = cache.get(cache_count_key)
    if cached_count is not None:
        count_q = cached_count
    else:
        count_q = math.ceil(queryset.count() / 60)
        cache.set(cache_count_key, count_q, CACHE_TIME)
    return count_q


def filter_products(request):
    params = request.query_params
    queryset = Product.objects.filter(available_flag=True, is_custom=False)

    if params.get('is_sale'):
        queryset = queryset.filter(is_sale=True)

    category_filters = Q()
    if params.getlist('category_id'):
        category_filters |= Q(category_id__in=params.getlist('category_id'))
    if params.getlist('category_name'):
        for name in params.getlist('category_name'):
            category_filters |= Q(category_name__icontains=name)
    if category_filters:
        queryset = queryset.filter(category_filters)

    if params.getlist('gender'):
        queryset = queryset.filter(gender__name__in=params.getlist('gender'))

    if params.getlist('line'):
        queryset = queryset.filter(lines__full_eng_name__in=params.getlist('line'))

    if params.getlist('category'):
        queryset = queryset.filter(categories__eng_name__in=params.getlist('category'))

    if params.getlist('color'):
        queryset = queryset.filter(colors__name__in=params.getlist('color'))

    if params.getlist('brand'):
        for brand_name in params.getlist('brand'):
            queryset = queryset.filter(brands__query_name=brand_name)

    if params.getlist('material'):
        queryset = queryset.filter(materials__eng_name__in=params.getlist('material'))

    if params.getlist('tag'):
        queryset = queryset.filter(tags__name__in=params.getlist('tag'))

    if params.getlist('collection'):
        queryset = queryset.filter(collections__query_name__in=params.getlist('collection'))

    if params.getlist('collab'):
        if "all" in params.getlist('collab'):
            queryset = queryset.filter(is_collab=True)
        else:
            queryset = queryset.filter(collab__query_name__in=params.getlist('collab'))

    price_filters = Q()
    if params.get('price_min'):
        price_filters &= Q(min_price__gte=params.get('price_min'))
    if params.get('price_max'):
        price_filters &= Q(min_price__lte=params.get('price_max'))
    if price_filters:
        queryset = queryset.filter(price_filters)

    if params.getlist('size'):
        size_ids = [s.split("_")[1] for s in params.getlist('size')]
        queryset = queryset.filter(sizes__in=size_ids)

    if params.get("recommendations") and not params.get('q'):
        three_months_ago = datetime.now() - timedelta(days=1000)
        queryset = (queryset.filter(is_recommend=True, last_upd__gte=three_months_ago)
                    .order_by('-rel_num', '-last_upd'))
    elif params.get("new") and not params.get('q'):
        one_month_ago = datetime.now() - timedelta(days=1000)
        queryset = queryset.filter(is_new=True, add_date__gte=one_month_ago)

    if params.get('q'):
        if request.user.id:
            queryset = queryset.filter(gender__name=request.user.gender.name)
        search_result = search_product(params.get('q'), queryset)
        queryset = search_result['queryset']

    return queryset.values_list('id', flat=True)


def get_product_page(request, context):
    res = {'add_filter': ""}
    params = request.query_params
    queryset = filter_products(request)

    query = params.get('q')
    size = params.getlist('size')
    if size:
        size = [s.split("_")[1] for s in size]

    new = params.get("new")

    page_number = int(params.get("page", 1))

    res['count'] = 100

    default_ordering = "-rel_num"
    if new:
        default_ordering = "-rel_num"
    if query:
        default_ordering = ""

    ordering = params.get('ordering', default_ordering)
    if ordering in ["rel_num", "-rel_num"]:
        ordering = ordering.replace("rel_num", "score_product_page")

    if ordering in ['exact_date', 'score_product_page', '-score_product_page', "-exact_date", "-normalize_rel_num",
                    "last_upd", "-last_upd"]:
        queryset = queryset.order_by(ordering)
    elif ordering in ("min_price", "-min_price"):
        if size:
            queryset = queryset.annotate(
                min_price_product_unit=Subquery(
                    Product.objects.filter(pk=OuterRef('pk'))
                    .annotate(unit_min_price=Min('product_units__final_price', filter=(
                            Q(product_units__size__in=size) | Q(product_units__size__is_one_size=True))))
                    .values('unit_min_price')[:1]
                )
            )
            queryset = queryset.order_by(
                "min_price_product_unit" if ordering == "min_price" else "-min_price_product_unit")
        else:
            queryset = queryset.order_by(ordering)
    elif ordering == "random":
        queryset = queryset.order_by("?")
    queryset = queryset.values_list("id", flat=True)

    start_index = (page_number - 1) * 60
    queryset = queryset[start_index:start_index + 60]
    queryset = get_queryset_from_list_id(list(queryset))

    res['min_price'] = 0
    res['max_price'] = 50_000_000

    return queryset, res


# ---------------------------------------------------------------------------
# Main page selections (formerly main_page.py)
# ---------------------------------------------------------------------------

def get_header_photo():
    header = HeaderPhoto.objects.exclude(where='product_page')
    brand = choice(header)
    shoes = choice(header.filter(categories__name="Обувь"))
    clothes = choice(header.filter(categories__name="Одежда"))
    accessories = choice(header.filter(categories__name="Аксессуары"))
    bags = choice(header.filter(categories__name="Сумки"))
    return {
        "brand": brand.photo,
        "shoes": shoes.photo,
        "clothes": clothes.photo,
        "bags": bags.photo,
        "accessories": accessories.photo,
    }


def get_line_selection(gender, line=None):
    filters = Q(available_flag=True, is_custom=False, gender__name__in=gender)
    if line is None:
        line = get_random_model(Line, "line")
        products = Product.objects.filter(lines=line).filter(filters).order_by("-score_product_page")
        if products.count() < 10:
            return get_line_selection(gender)
    else:
        products = Product.objects.filter(lines=line).filter(filters).order_by("-score_product_page")

    title = f"{line.name}"
    url = f"line={line.full_eng_name}"
    list_id = get_product_for_selecet(products)
    return title, list_id, url


def get_collab_selection(gender, collab=None):
    filters = Q(available_flag=True, is_custom=False, gender__name__in=gender)
    if collab is None:
        collab = get_random_model(Collab, "collab")
        products = Product.objects.filter(collab=collab).filter(filters).order_by("-score_product_page")
        if products.count() < 10:
            return get_collab_selection(gender)
    else:
        products = Product.objects.filter(collab=collab).filter(filters).order_by("-score_product_page")

    title = f"{collab.name}"
    url = f"collab={collab.query_name}"
    list_id = get_product_for_selecet(products)
    return title, list_id, url


def get_color_and_line_selection(gender):
    colors = Color.objects.filter(is_main_color=True)
    random_color = get_random(colors)
    line = get_random_model(Line, "line")
    filters = Q(available_flag=True, is_custom=False, gender__name__in=gender)
    products = Product.objects.filter(Q(lines=line) & Q(colors=random_color)).filter(filters).order_by(
        "-score_product_page")
    if products.count() < 10:
        return get_color_and_line_selection(gender)
    list_id = get_product_for_selecet(products)
    return f"{line.name}", list_id, f"line={line.full_eng_name}"


def get_color_and_category_selection(gender):
    colors = Color.objects.filter(is_main_color=True)
    random_color = get_random(colors)
    random_category = get_random_model(Category, "category")
    filters = Q(available_flag=True, is_custom=False, gender__name__in=gender)
    products = Product.objects.filter(Q(categories=random_category) & Q(colors=random_color)).filter(
        filters).order_by("-score_product_page")
    if products.count() < 10:
        return get_color_and_category_selection(gender)
    list_id = get_product_for_selecet(products)
    return f"{random_category.name}", list_id, f"category={random_category.eng_name}"


def get_color_and_brand_selection(gender):
    colors = Color.objects.filter(is_main_color=True)
    random_color = get_random(colors)
    random_brand = get_random_model(Brand, "brand")
    filters = Q(available_flag=True, is_custom=False, gender__name__in=gender)
    products = Product.objects.filter(Q(brands=random_brand) & Q(colors=random_color)).filter(
        filters).order_by("-score_product_page")
    if products.count() < 10:
        return get_color_and_brand_selection(gender)
    list_id = get_product_for_selecet(products)
    return f"{random_brand.name}", list_id, f"line={random_brand.query_name}"


def get_brand_and_category_selection(gender):
    random_brand = get_random_model(Brand, "brand")
    random_category = get_random_model(Category, "category")
    filters = Q(available_flag=True, is_custom=False, gender__name__in=gender)
    products = Product.objects.filter(Q(categories=random_category) & Q(brands=random_brand)).filter(
        filters).order_by("-score_product_page")
    if products.count() < 10:
        return get_brand_and_category_selection(gender)
    list_id = get_product_for_selecet(products)
    return (f"{random_category.name} {random_brand.name}", list_id,
            f"category={random_category.eng_name}&line={random_brand.query_name}")


def get_brand_selection(gender):
    random_brand = get_random_model(Brand, "brand")
    filters = Q(available_flag=True, is_custom=False, gender__name__in=gender)
    products = Product.objects.filter(Q(brands=random_brand)).filter(filters).order_by("-score_product_page")
    if products.count() < 10:
        return get_brand_selection(gender)
    list_id = get_product_for_selecet(products)
    return f"{random_brand.name}", list_id, f"line={random_brand.query_name}"


def get_category_selection(gender):
    random_cat = get_random_model(Category, "category")
    filters = Q(available_flag=True, is_custom=False, gender__name__in=gender)
    products = Product.objects.filter(Q(categories=random_cat)).filter(filters).order_by("-score_product_page")
    if products.count() < 10:
        return get_category_selection(gender)
    list_id = get_product_for_selecet(products)
    return f"{random_cat.name}", list_id, f"category={random_cat.eng_name}"


def get_selection(gender):
    type_num = randint(1, 100)
    if 1 <= type_num < 15:
        title, queryset, url = get_brand_and_category_selection(gender)
    elif 15 <= type_num < 30:
        title, queryset, url = get_category_selection(gender)
    elif 30 <= type_num < 48:
        title, queryset, url = get_collab_selection(gender)
    elif 48 <= type_num < 60:
        title, queryset, url = get_color_and_brand_selection(gender)
    elif 60 <= type_num < 85:
        title, queryset, url = get_brand_selection(gender)
    else:
        title, queryset, url = get_line_selection(gender)
    if len(gender) == 1:
        url += f"&gender={gender[0]}"
    return queryset, {"type": "selection", "title": title, "url": url}


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

    return get_random(photos_desk), get_random(photos_mobile)


def get_sellout_photo_text(last):
    types = ["left", "right"]
    if last == "any":
        last = types[randint(0, 1)]

    random_photo_desk, random_photo_mobile = get_photo()

    texts_mobile = HeaderText.objects.filter(title="sellout", type="mobile")
    texts_desktop = HeaderText.objects.filter(title="sellout", type="desktop")

    text_mobile = texts_mobile[randint(0, texts_mobile.count() - 1)]
    text_desktop = texts_desktop[randint(0, texts_desktop.count() - 1)]

    current_type = 'right' if last == 'left' else 'left'
    res = {
        'type': "photo",
        "desktop": {"type": f"{current_type}_photo", "photo": random_photo_desk.photo,
                    "title": text_desktop.title, "content": text_desktop.text, "url": "", "button": "Все товары"},
        "mobile": {"photo": random_photo_mobile.photo, "title": text_mobile.title, "content": text_mobile.text,
                   "url": "", "button": "Все товары"},
    }
    return res, current_type


def get_photo_text(last, gender):
    types = ["left", "right"]
    if last == "any":
        last = types[randint(0, 1)]

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

    selection = queryset if f else []

    current_type = 'right' if last == 'left' else 'left'
    res = {
        'type': "photo",
        "desktop": {"type": f"{current_type}_photo", "photo": random_photo_desk.photo,
                    "title": random_photo_desk.header_text.title, "content": random_photo_desk.header_text.text,
                    "url": url_desk, "button": "Посмотреть все"},
        "mobile": {"photo": random_photo_mobile.photo, "title": random_photo_mobile.header_text.title,
                   "content": random_photo_mobile.header_text.text, "url": url_mobile, "button": "Посмотреть все"},
    }
    return res, current_type, selection
