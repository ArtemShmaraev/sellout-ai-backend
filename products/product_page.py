import functools
import math
import random
from datetime import date, timedelta

from django.core.cache import cache
from django.db.models import Q, Subquery, OuterRef, Min, When, Case, Count

from sellout.settings import CACHE_TIME
from .tools import get_queryset_from_list_id
from time import time
from django.http import JsonResponse, FileResponse

from users.models import User
from wishlist.models import Wishlist
from .models import Product, Category, Line, DewuInfo, SizeRow, SizeTable, Collab, HeaderPhoto, HeaderText, \
    SizeTranslationRows
from rest_framework import status
from .serializers import SizeTableSerializer, ProductMainPageSerializer, CategorySerializer, LineSerializer, \
    ProductSerializer, \
    DewuInfoSerializer, CollabSerializer
from .tools import get_product_text
from urllib.parse import urlencode
from rest_framework.response import Response

from .search_tools import search_best_line, search_best_category, search_best_color, search_best_collab, search_product
from django.views.decorators.cache import cache_page


# Используйте декоратор с заданным временем жизни (в секундах)


def get_product_page_header(request):
    res = {}

    line = request.query_params.getlist('line')
    category = request.query_params.getlist("category")
    collab = request.query_params.getlist("collab")
    new = request.query_params.get("new")
    recommendations = request.query_params.get("recommendations")
    header_photos = HeaderPhoto.objects.all()
    header_photos = header_photos.filter(where="product_page")
    # if category:
    #     header_photos = header_photos.filter(categories__eng_name__in=category)

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

    if not header_photos.exists():
        header_photos = header_photos.filter(where="product_page")

    header_photos_desktop = header_photos.filter(type="desktop", rating=5)
    header_photos_mobile = header_photos.filter(type="mobile", rating=5)
    if not header_photos_desktop.exists():
        header_photos_desktop = header_photos.filter(type="desktop")
        if not header_photos_desktop.exists():
            header_photos_desktop = HeaderPhoto.objects.filter(type="desktop")
    count = header_photos_desktop.count()

    photo_desktop = header_photos_desktop[random.randint(0, count - 1)]
    text_desktop = get_product_text(photo_desktop, line, collab, category, new, recommendations)
    if text_desktop is None:
        text_desktop = photo_desktop.header_text

    res["desktop"] = {"title": text_desktop.title, "content": text_desktop.text}
    res['desktop']['photo'] = photo_desktop.photo

    if not header_photos_mobile.exists():
        header_photos_mobile = header_photos.filter(type="mobile")
        if not header_photos_mobile.exists():
            header_photos_mobile = HeaderPhoto.objects.filter(type="mobile")
    count = header_photos_mobile.count()

    photo_mobile = header_photos_mobile[random.randint(0, count - 1)]
    text_mobile = get_product_text(photo_mobile, line, collab, category, new, recommendations)
    if text_mobile is None:
        text_mobile = photo_mobile.header_text

    res["mobile"] = {"title": text_mobile.title, "content": text_mobile.text}
    res['mobile']['photo'] = photo_mobile.photo
    return res


def count_queryset(request):
    params = request.GET.copy()
    queryset = filter_products(request)
    # print(queryset.query)
    # print(queryset.query)
    # print(queryset.query)
    if 'page' in params:
        del params['page']

    cache_count_key = f"count:{urlencode(params)}"  # Уникальный ключ для каждой URL
    cached_count = cache.get(cache_count_key)
    if cached_count is not None:
        count_q = cached_count
    else:
        count_q = math.ceil(queryset.count() / 60)
        cache.set(cache_count_key, (count_q), CACHE_TIME)
    return count_q


def get_new_products():
    cached_result = cache.get('new_products_cache')

    # Если результат найден в кэше, возвращаем его
    if cached_result:
        return cached_result

    current_date = date.today()

    # Вычисляем дату, которая находится полгода назад
    six_months_ago = current_date + timedelta(days=180)
    filtered_products = Product.objects.filter(
        Q(exact_date__lte=six_months_ago) &
        (Q(gender__name='M') | Q(gender__name='F')) & Q(categories__name__in=["Обувь", "Одежда"])
    )
    sort_products = filtered_products.order_by("-exact_date").values_list("id", flat=True)[:600]
    new_sneakers = filtered_products.filter(categories__name__in=["Кроссовки"]).order_by("-exact_date").values_list("id", flat=True)[:200]

    result = Product.objects.filter(Q(id__in=sort_products) | Q(id__in=new_sneakers)).values_list("id", flat=True)

    # Кэшируем результат на 10 минут
    cache.set('new_products_cache', result, CACHE_TIME)
    return result




def filter_products(request):
    params = request.query_params
    t0 = time()
    queryset = Product.objects.all()
    t1 = time()

    print("t0", t1 - t0)

    query = params.get('q')
    size = params.getlist('size')
    table = []
    if size:
        size = list(map(lambda x: x.split("_")[1], size))

        for s in size:
            table.append(SizeTranslationRows.objects.get(id=s).table.id)

    price_max = params.get('price_max')
    price_min = params.get('price_min')

    line = params.getlist('line')
    color = params.getlist('color')
    is_fast_ship = params.get("is_fast_shipx`")
    is_sale = params.get("is_sale")
    is_return = params.get("is_return")
    category = params.getlist("category")
    material = params.getlist("material")
    gender = params.getlist("gender")
    brand = params.getlist("brand")
    collab = params.getlist("collab")
    available = params.get("available")
    custom = params.get("custom")

    category_id = request.query_params.getlist('category_id')
    category_name = request.query_params.getlist('category_name')
    level1_category_id = request.query_params.getlist('level1_category_id')
    level2_category_id = request.query_params.getlist('level2_category_id')
    title = request.query_params.get('title')

    if not available:
        queryset = queryset.filter(available_flag=True)
        # queryset = queryset.filter(product_units__availability=True)
    if not custom:
        queryset = queryset.filter(is_custom=False)

    if category_id:
        queryset = queryset.filter(category_id__in=category_id)
    if category_name:
        for name in category_name:
            queryset = queryset.filter(category_name__icontains=name)
    if level1_category_id:
        queryset = queryset.filter(level1_category_id__in=level1_category_id)
    if level2_category_id:
        queryset = queryset.filter(level2_category_id__in=level2_category_id)
    if title:
        queryset = queryset.filter(platform_info__poizon__title__icontains=title)

    new = params.get("new")
    if new and not query:
        # new_q = queryset.order_by('-exact_date')[:250]
        new_q = get_new_products()

    recommendations = params.get("recommendations")
    if recommendations and not query:
        recommendations_q = queryset.order_by('-rel_num')[:250]
    if gender:
        queryset = queryset.filter(gender__name__in=gender)

    if collab:
        if "all" in collab:
            queryset = queryset.filter(is_collab=True)
        else:
            queryset = queryset.filter(collab__query_name__in=collab)
    if material:
        queryset = queryset.filter(materials__eng_name__in=material)
    if brand:
        for brand_name in brand:
            queryset = queryset.filter(brands__query_name=brand_name)
    if line:
        queryset = queryset.filter(lines__full_eng_name__in=line)

    if color:
        queryset = queryset.filter(colors__name__in=color)
    if category:
        queryset = queryset.filter(categories__eng_name__in=category)

    filters = Q()

    # Фильтр по цене
    if price_min:
        if size:
            filters &= Q(product_units__final_price__gte=price_min)
        else:
            filters &= Q(min_price__gte=price_min)

        # Фильтр по максимальной цене
    if price_max:
        if size:
            filters &= Q(product_units__final_price__lte=price_max)
        else:
            filters &= Q(min_price__lte=price_max)

    # Фильтр по размеру
    if size:
        filters &= ((Q(product_units__size__in=size) | (
                    Q(product_units__size__is_one_size=True) & Q(product_units__size_table__in=table))))

    # Фильтр по наличию скидки
    if is_sale:
        filters &= Q(is_sale=(is_sale == "is_sale"))
    if is_return:
        filters &= Q(product_units__is_return=(is_return == "is_return"))
    if is_fast_ship:
        filters &= Q(product_units__fast_shipping=(is_fast_ship == "is_fast_ship"))
    if filters:
        # filters &= Q(product_units__availability=True)
        # Выполняем фильтрацию
        queryset = queryset.filter(filters)

    if new and not query:
        queryset = queryset.filter(id__in=new_q)

    if recommendations and not query:
        queryset = queryset.filter(id__in=recommendations_q)

    t2 = time()
    print("t1", t2 - t1)
    if query:
        query = query.replace("_", " ")
        search = search_product(query, queryset)
        queryset = search['queryset']

    t3 = time()
    print("t2", t3 - t2)

    # queryset = queryset.distinct()

    # unique_product_ids = queryset.values("id")
    # queryset = Product.objects.filter(id__in=Subquery(unique_product_ids)).values_list("id", flat=True)

    queryset = queryset.values_list("id", flat=True).distinct()
    # print(queryset.query)

    # print(queryset.query)
    # print(queryset.count())
    return queryset


def get_product_page(request, context):
    res = {'add_filter': ""}

    params = request.query_params
    queryset = filter_products(request)
    t3 = time()
    query = params.get('q')
    size = params.getlist('size')
    if size:
        size = list(map(lambda x: x.split("_")[1], size))
        table = []
        for s in size:
            table.append(SizeTranslationRows.objects.get(id=s).table.id)

    new = params.get("new")
    recommendations = params.get("recommendations")

    page_number = int(params.get("page", 1))

    # params = request.GET.copy()
    # if 'page' in params:
    #     del params['page']
    #
    # cache_count_key = f"count:{urlencode(params)}"  # Уникальный ключ для каждой URL
    # cached_count = cache.get(cache_count_key)
    # if cached_count is not None:
    #
    #     count = cached_count
    # else:
    #     count = 100
    #     cache.set(cache_count_key, (count), CACHE_TIME)

    res['count'] = 100
    t4 = time()
    print("t3", t4 - t3)

    default_ordering = "-rel_num"
    if new:
        default_ordering = "-exact_date"
    if query:
        default_ordering = ""

    ordering = params.get('ordering', default_ordering)
    if ordering in ['exact_date', 'rel_num', '-rel_num', "-exact_date"]:
        queryset = queryset.order_by(ordering)
    elif ordering == "min_price" or ordering == "-min_price":
        if size:
            queryset = queryset.annotate(
                min_price_product_unit=Subquery(
                    Product.objects.filter(pk=OuterRef('pk'))
                    .annotate(unit_min_price=Min('product_units__final_price', filter=(
                            Q(product_units__size__in=size) | Q(product_units__size__is_one_size=True))))
                    .values('unit_min_price')[:1]
                )
            )
            if ordering == "min_price":
                queryset = queryset.order_by("min_price_product_unit")
            else:

                queryset = queryset.order_by("-min_price_product_unit")

        else:
            queryset = queryset.order_by(ordering)

    # paginator = CustomPagination()
    # Применяем пагинацию к списку объектов Product
    # paginated_products = paginator.paginate_queryset(queryset, request)
    # serializer = ProductMainPageSerializer(queryset, many=True, context=context).data
    # res = paginator.get_paginated_response(serializer)

    t5 = time()
    print("t4", t5 - t4)

    start_index = (page_number - 1) * 60
    # print(queryset[0].id)
    # queryset = queryset.distinct()
    queryset = queryset[start_index:start_index + 60]
    print(queryset.query)
    queryset = get_queryset_from_list_id(list(queryset.values_list("id", flat=True)))

    res['next'] = f"http://127.0.0.1:8000/api/v1/product/products/?page={page_number + 1}"
    res["previous"] = f"http://127.0.0.1:8000/api/v1/product/products/?page={page_number - 1}"
    res['min_price'] = 0
    res['max_price'] = 50_000_000
    t6 = time()
    print("t5", t6 - t5)
    t7 = time()
    print("t6", t7 - t6)
    # t7 = time()
    # print("t6", t7 - t6)
    # queryset = list(serializer.data)

    # print(queryset)
    return queryset, res
