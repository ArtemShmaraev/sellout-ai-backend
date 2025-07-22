import functools
import random

from django.db.models import Q, Subquery, OuterRef, Min, When, Case
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

    header_photos_desktop = header_photos.filter(type="desktop")
    header_photos_mobile = header_photos.filter(type="mobile")
    if not header_photos_desktop.exists():
        header_photos_desktop = HeaderPhoto.objects.filter(type="desktop")
    count = header_photos_desktop.count()

    photo_desktop = header_photos_desktop[random.randint(0, count - 1)]
    text_desktop = get_product_text(photo_desktop, line, collab, category, new, recommendations)
    if text_desktop is None:
        text_desktop = photo_desktop.header_text

    res["desktop"] = {"title": text_desktop.title, "content": text_desktop.text}
    res['desktop']['photo'] = photo_desktop.photo

    if header_photos_mobile.count() > 0:
        count = header_photos_mobile.count()
    else:
        header_photos_mobile = HeaderPhoto.objects.filter(type="mobile")
        count = header_photos_mobile.count()

    photo_mobile = header_photos_mobile[random.randint(0, count - 1)]
    text_mobile = get_product_text(photo_mobile, line, collab, category, new, recommendations)
    if text_mobile is None:
        text_mobile = photo_mobile.header_text

    res["mobile"] = {"title": text_mobile.title, "content": text_mobile.text}
    res['mobile']['photo'] = photo_mobile.photo
    return res



def get_product_page(request, context):
    params = request.query_params
    t0 = time()
    queryset = Product.objects.all()
    t1 = time()
    res = {'add_filter': ""}
    print("t0", t1 - t0)

    query = params.get('q')
    size = params.getlist('size')
    if size:
        size = list(map(lambda x: x.split("_")[1], size))
        table = []
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

    if not available:
        queryset = queryset.filter(available_flag=True)
    if not custom:
        queryset = queryset.filter(is_custom=False)



    new = params.get("new")
    if new and not query:
        new_q = queryset.order_by('-exact_date')[:250]

    recommendations = params.get("recommendations")
    if recommendations and not query:
        recommendations_q = queryset.order_by('-rel_num')[:250]

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

        # def find_common_ancestor(lines):
        #     # Создаем множество для хранения всех родительских линеек
        #     # Добавляем все родительские линейки в множество
        #     current_line = lines[0]
        #     parent_lines = set()
        #     parent_lines.add(current_line)
        #
        #     while current_line.parent_line:
        #         parent_lines.add(current_line.parent_line)
        #         current_line = current_line.parent_line
        #
        #     # Переберите остальные выбранные линейки и найдите первую общую вершину
        #     for line in lines[1:]:
        #         current_line = line
        #         while current_line:
        #             if current_line in parent_lines:
        #                 return current_line
        #             current_line = current_line.parent_line
        #     print(parent_lines)
        #     if len(lines) == 1:
        #         return lines[0]
        #     return None  # Если общей родительской линейки не найдено

        # Пример использования
        # selected_lines = Line.objects.filter(full_eng_name__in=line)  # Ваши выбранные линейки
        # if len(selected_lines) > 0:
        #     oldest_line = find_common_ancestor(selected_lines)
        #     list_line.append(oldest_line)
        #     while oldest_line.parent_line:
        #         list_line.append(oldest_line.parent_line)
        #         oldest_line = oldest_line.parent_line

    if color:
        queryset = queryset.filter(colors__name__in=color)
    if category:
        queryset = queryset.filter(categories__eng_name__in=category)

        # def find_common_ancestor(categories):
        #
        #     current_cat = categories[0]
        #     parent_cats = set()
        #     parent_cats.add(current_cat)
        #
        #     while current_cat.parent_category:
        #         parent_cats.add(current_cat.parent_category)
        #         current_cat = current_cat.parent_category
        #
        #     # Переберите остальные выбранные линейки и найдите первую общую вершину
        #     for cat in categories[1:]:
        #         current_cat = cat
        #         while current_cat:
        #             if current_cat in parent_cats:
        #                 return current_cat
        #             current_cat = current_cat.parent_category
        #     if len(categories) == 1:
        #         return categories[0]
        #     return None
        #
        # selected_cat = Category.objects.filter(eng_name__in=category)  # Ваши выбранные линейки
        # if len(selected_cat) > 0:
        #     oldest_cat = find_common_ancestor(selected_cat)
        #     list_cat.append(oldest_cat)
        #     while oldest_cat.parent_category:
        #         list_cat.append(oldest_cat.parent_category)
        #         oldest_cat = oldest_cat.parent_category

    if gender:
        queryset = queryset.filter(gender__name__in=gender)

    filters = Q()

    # Фильтр по цене
    if price_min:
        filters &= Q(product_units__final_price__gte=price_min)

        # Фильтр по максимальной цене
    if price_max:
        filters &= Q(product_units__final_price__lte=price_max)


    # Фильтр по размеру
    if size:
        filters &= ((Q(product_units__size__in=size) | Q(product_units__size__is_one_size=True)))

    # Фильтр по наличию скидки
    if is_sale:
        filters &= Q(product_units__is_sale=(is_sale == "is_sale"))
    if is_return:
        filters &= Q(product_units__is_return=(is_return == "is_return"))
    if is_fast_ship:
        filters &= Q(product_units__fast_shipping=(is_fast_ship == "is_fast_ship"))
    if filters:
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

    unique_ids = queryset.values('id').distinct()
    res['count'] = unique_ids.count()

    # Получите queryset объектов с уникальными id
    queryset = Product.objects.filter(id__in=unique_ids)
    # res['count'] = 1000
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

    page_number = params.get("page")
    page_number = int(page_number if page_number else 1)

    start_index = (page_number - 1) * 48
    # print(queryset[0].id)
    queryset = queryset[start_index:start_index + 48]
    # queryset = [product.id for product in queryset]
    res['next'] = f"http://127.0.0.1:8000/api/v1/product/products/?page={page_number + 1}"
    res["previous"] = f"http://127.0.0.1:8000/api/v1/product/products/?page={page_number - 1}"
    res['min_price'] = 0
    res['max_price'] = 1000000
    t6 = time()
    print("t5", t6 - t5)
    # list_id = list(queryset.values_list("id", flat=True))
    # print(time() - t6)
    # queryset = get_queryset_from_list_id(list_id)

    queryset = ProductMainPageSerializer(queryset, many=True, context=context).data
    t7 = time()
    print("t6", t7-t6)
    # t7 = time()
    # print("t6", t7 - t6)
    # queryset = list(serializer.data)

    # print(queryset)
    return queryset, res