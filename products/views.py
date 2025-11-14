import asyncio
import copy
import hashlib
import math
import pickle
import random
import threading
from urllib.parse import urlencode

import httpx
from django.core.cache import cache
from django.utils import timezone
from django.utils.functional import cached_property
from django.db import models, transaction
import rest_framework.generics
from django.db.models import Case, When, Value, IntegerField
from django.db.models import Q, Subquery, OuterRef, Min, When, Case
# from haystack.query import SearchQuerySet
from rest_framework.decorators import api_view, action
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import json
from time import time
from django.http import JsonResponse, FileResponse, HttpResponse
from .add_product_api import add_product_api, add_products_spu_id_api
from users.models import User, UserStatus
from wishlist.models import Wishlist
from .models import Product, Category, Line, DewuInfo, SizeRow, SizeTable, Collab, HeaderPhoto, HeaderText, \
    RansomRequest, SGInfo, Brand, Photo, Material
from rest_framework import status

from .product_page import get_product_page, get_product_page_header, count_queryset
from .product_site_map import ProductSitemap
from .serializers import SizeTableSerializer, ProductMainPageSerializer, CategorySerializer, LineSerializer, \
    ProductSerializer, \
    DewuInfoSerializer, CollabSerializer, SGInfoSerializer, BrandSerializer, update_product_serializer, \
    ProductSlugAndPhotoSerializer, ProductAdminSerializer, MaterialSerializer
from .tools import build_line_tree, build_category_tree, category_no_child, line_no_child, add_product, get_text, \
    get_product_page_photo, RandomGenerator, get_product_text, get_queryset_from_list_id, platform_update_price

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from .search_tools import search_best_line, search_best_category, search_best_color, search_best_collab, search_product, \
    similar_product, suggest_search, add_filter_search
from .documents import ProductDocument  # Импортируйте ваш документ
from random import randint
from products.main_page import get_selection, get_photo_text, get_sellout_photo_text, get_header_photo
from sellout.settings import CACHE_TIME
from collections import OrderedDict
from sellout.settings import HOST
from django.contrib.sitemaps import views as sitemaps_views
from django.shortcuts import render, redirect



class MyScoreForProduct(APIView):
    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
            my_score = product.extra_score
            print(my_score)
            return Response({"my_score": my_score})
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, id):
        try:
            product = Product.objects.get(id=id)
            data = json.loads(request.body)
            my_score = data['my_score']
            last = product.extra_score
            product.extra_score = my_score
            product.score_product_page += round((my_score - last) * 0.1)
            product.save()

            return Response({"my_score": my_score})
        except Product.DoesNotExist:
            return Response({"error": "Product does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MaterialView(APIView):
    def get(self, request):
        cache_material = f"materials"  # Уникальный ключ для каждой URL
        cached_data = cache.get(cache_material)

        if cached_data is not None:
            res = cached_data
        else:
            queryset = Material.objects.all()
            res = MaterialSerializer(queryset, many=True).data
            cache.set(cache_material, (res), CACHE_TIME)

        return Response(res)


def sitemap_view(request):
    sitemaps = {
        'products': ProductSitemap,
    }
    response = sitemaps_views.sitemap(request, sitemaps)
    return render(request, 'sitemap.xml', {'urls': response.content})


class SearchBySkuView(APIView):
    def get(self, request):
        params = request.query_params
        type = params.get("type", "product")
        formatted_manufacturer_sku = params.get("formatted_manufacturer_sku")
        if type == "product":
            products = Product.objects.filter(formatted_manufacturer_sku=formatted_manufacturer_sku)
            return Response(ProductSerializer(products, many=True).data)
        elif type == "dewu_info":
            dewu_infos = DewuInfo.objects.filter(formatted_manufacturer_sku=formatted_manufacturer_sku)
            return Response(DewuInfoSerializer(dewu_infos, many=True).data)
        else:
            print(formatted_manufacturer_sku)
            sg_infos = SGInfo.objects.filter(formatted_manufacturer_sku=formatted_manufacturer_sku)
            return Response(SGInfoSerializer(sg_infos, many=True).data)


def view_photo_for_rate(request):
    # Получаем случайное фото из базы данных
    photo_id = int(request.GET.get('id'))
    t = -1
    next = request.GET.get('next', False)
    if next:
        t = 1
    # last_id = HeaderPhoto.objects.order_by("-id").first().id
    last_id = 17290
    # first_id = HeaderPhoto.objects.order_by("id").first().id
    first_id = 15434
    # print(last_id, first_id)
    photo = HeaderPhoto.objects.filter(id=photo_id, where="product_page", rating=4).exists()
    while not photo:
        photo_id += t
        if photo_id <= first_id:
            photo = HeaderPhoto.objects.filter(id=first_id, where="product_page", rating=4).exists()
            photo_id = first_id
        elif photo_id >= last_id:
            photo = HeaderPhoto.objects.filter(id=last_id, where="product_page", rating=4).exists()
            photo_id = last_id
        else:
            photo = HeaderPhoto.objects.filter(id=photo_id, where="product_page", rating=4).exists()
    photo = HeaderPhoto.objects.get(id=photo_id)

    return render(request, 'view_photo.html', {'photo': photo, "next_photo": photo.id + 1, "last_photo": photo.id - 1})


def rate_photo(request):
    if request.method == 'POST':
        photo_id = int(request.POST['photo_id'])
        photo = HeaderPhoto.objects.get(id=photo_id)
        rating = int(request.POST['rating'])
        photo.rating = rating
        photo.save()
        # print(photo.rating)
        # Сохраняем оценку в базе данных
        # Здесь должен быть ваш код для сохранения оценки в модели Photo
        if HOST == "sellout.su":
            return redirect(f"https://{HOST}/api/v1/product/pict?id={photo_id + 1}")
        return redirect(f"http://127.0.0.1:8000/api/v1/product/pict?id={photo_id + 1}")


class ProductSlugAndPhoto(APIView):
    def get(self, request):
        params = request.query_params
        queryset = Product.objects.all()
        page_number = int(params.get("page", 1))
        categories = params.getlist("category", "")
        lines = params.getlist("line", "")

        if categories:
            queryset = queryset.filter(categories__eng_name__in=categories)
        if lines:
            queryset = queryset.filter(lines__full_eng_name__in=lines)

        res = {}

        queryset = queryset.values_list("id", flat=True)
        cache_count_key = f"productcount_{request.build_absolute_uri()}"  # Уникальный ключ для каждой URL
        cached_count = cache.get(cache_count_key)
        if cached_count is not None:

            count = cached_count
        else:
            count = queryset.count()
            cache.set(cache_count_key, (count), CACHE_TIME)

        res['count'] = count

        start_index = (page_number - 1) * 100
        queryset = queryset[start_index:start_index + 100]
        queryset = get_queryset_from_list_id(list(queryset.values_list("id", flat=True)))
        queryset = ProductSlugAndPhotoSerializer(queryset, many=True).data
        res['results'] = queryset
        return Response(res)


class PhotoWhiteList(APIView):
    def get(self, request, product_id):
        product = Product.objects.get(id=product_id)
        for photo in product.black_bucket_link.all():
            product.bucket_link.add(photo)
        product.black_bucket_link.clear()
        product.save()
        return Response("Готово")


class AddPhotoBlackList(APIView):
    def get(self, request, product_id, photo_id):
        try:
            product = Product.objects.get(id=product_id)
            photo = Photo.objects.get(id=photo_id)
        except Product.DoesNotExist:
            return Response("Продукт не найден", status=status.HTTP_404_NOT_FOUND)
        except Photo.DoesNotExist:
            return Response("Фото не найдено", status=status.HTTP_404_NOT_FOUND)

        try:
            # Удаляем фото из bucket_link и добавляем в black_bucket_link
            product.bucket_link.remove(photo)
            product.black_bucket_link.add(photo)
            product.save()
            if not product.bucket_link.exists():
                product.available_flag = False
                product.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response("Готово")


class DewuInfoCount(APIView):
    def get(self, request):
        count = DewuInfo.objects.values_list("id", flat=True).count()
        return Response({"count": count, "page": math.ceil(count / 30)})


class HideProductView(APIView):
    def get(self, request, spu_id, property_id):
        product = Product.objects.filter(spu_id=spu_id, property_id=property_id)
        product.update(available_flag=False)
        return Response("Готово")


class HideProductSpiIdView(APIView):
    def get(self, request, spu_id, ):
        product = Product.objects.filter(spu_id=spu_id)
        product.update(available_flag=False)
        return Response("Готово")


class PopularSpuIdView(APIView):
    def get(self, request):
        count = int(request.query_params.get('count', 5000))
        popular_product = list(
            Product.objects.filter(available_flag=True, is_custom=False).values_list("spu_id", flat=True).order_by(
                "-rel_num"))[:count]

        other = list(
            Product.objects.filter(available_flag=False).values_list("spu_id", flat=True).order_by("-rel_num"))[:10000]

        def remove_duplicates(lst):
            return list(OrderedDict.fromkeys(lst))

        popular_product = remove_duplicates(popular_product)
        return Response(popular_product)


class UpdatePrice(APIView):
    def get(self, request):
        page = int(request.query_params.get('page', 1))

        def update_prices(products, start, end):
            for product_id in products[start:end]:
                product = Product.objects.get(id=product_id)
                with transaction.atomic():
                    product.update_price()

        # Получите все продукты, которые вы хотите обновить
        products = Product.objects.filter(available_flag=True).filter(actual_price=False).values_list("id", flat=True)
        part = page
        num_part = products.count() // 4
        products = products[num_part * (part - 1):num_part * part]
        # products = products[105000:210000]
        # products = products[210000:315000]
        # products = products[315000:429000]

        # Укажите количество потоков
        num_threads = 8

        # Разделите список продуктов на равные части для каждого потока
        batch_size = len(products) // num_threads

        # Создайте потоки и запустите их
        threads = []
        for i in range(num_threads):
            start = i * batch_size
            end = start + batch_size if i < num_threads - 1 else len(products)
            thread = threading.Thread(target=update_prices, args=(products, start, end))
            thread.start()
            threads.append(thread)

        # Дождитесь завершения всех потоков
        for thread in threads:
            thread.join()

        return Response("Цены успешно обновлены.")


class AvailableSize(APIView):
    def get(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)  # Получение объекта Product или 404, если он не найден
            sizes_info = {"sizes": [], "filter_logo": ""}
            sizes_id = set()
            for unit in product.product_units.filter(availability=True):
                for s in unit.size.all():
                    row = s.table.default_row
                    if sizes_info['filter_logo'] == "" and row.filter_logo not in ['SIZE', "INT"]:
                        sizes_info['filter_logo'] = row.filter_logo
                    if s.id not in sizes_id:
                        sizes_info['sizes'].append([s.id, f"{s.row[row.filter_name]}"])
                        sizes_id.add(s.id)
            sizes_info['sizes'] = list(map(lambda x: x[1], sorted(sizes_info['sizes'])))
            return Response(sizes_info)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)


class AddFilterSearch(APIView):
    def get(self, request):
        search_query = request.query_params.get('q', '')
        return Response(add_filter_search(search_query))


class BrandSearchView(APIView):
    def get(self, request):
        context = {"user_id": request.user.id if request.user.id else None}
        search_query = request.query_params.get('q', '')  # Получаем параметр "q" из запроса

        # Используем исключение try-except для обработки ошибок
        try:
            # Ищем бренды, чьи имена содержат поисковой запрос
            brands = Brand.objects.filter(name__icontains=search_query).order_by('name')
            serializer = BrandSerializer(brands, many=True, context=context)  # Сериализуем найденные бренды
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SGInfoListSkuView(APIView):
    def get(self, request):
        sg_infos = SGInfo.objects.values_list('manufacturer_sku', flat=True)
        return Response(sg_infos, status=status.HTTP_200_OK)


# Create your views here.
class SGInfoListView(APIView):
    def get(self, request):
        sg_infos = SGInfo.objects.all()
        # count = dewu_infos.count()
        count = 1
        page_number = request.query_params.get("page")
        page_number = int(page_number if page_number else 1)
        start_index = (page_number - 1) * 100
        queryset = sg_infos[start_index:start_index + 100]
        serializer = SGInfoSerializer(queryset, many=True)
        res = {'count': count, "results": serializer.data}  # Замените на вашу сериализацию
        return Response(res, status=status.HTTP_200_OK)


class SGInfoView(APIView):
    def get(self, request, sku):
        sg_info = SGInfo.objects.filter(manufacturer_sku=sku)
        serializer = SGInfoSerializer(sg_info, many=True)
        # Замените на вашу сериализацию
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, sku):
        data = json.loads(request.body)
        if SGInfo.objects.filter(manufacturer_sku=sku).exists():
            sg_info = SGInfo.objects.get(manufacturer_sku=sku)
        else:
            sg_info = SGInfo(manufacturer_sku=sku)
        if "data" in data:
            sg_info.data = data['data']
        if "formatted_manufacturer_sku" in data:
            sg_info.formatted_manufacturer_sku = data["formatted_manufacturer_sku"]
        if "relevant_number" in data:
            sg_info.relevant_number = int(data['relevant_number'])
        if "novelty_number" in data:
            sg_info.novelty_number = int(data["novelty_number"])
        sg_info.save()
        return Response(SGInfoSerializer(sg_info).data)

    def delete(self, request, sku):
        try:
            sg_info = SGInfo.objects.filter(manufacturer_sku=sku)
            sg_info.delete()

            return Response("Удален", status=status.HTTP_200_OK)
        except DewuInfo.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class MakeRansomRequest(APIView):
    def post(self, request):
        data = json.loads(request.body)
        name = data.get('name')
        tg_name = data.get('tg_name')
        phone_number = data.get('phone_number')
        email = data.get('email')
        url = data.get('url')
        photo = data.get('photo')
        info = data.get('info')

        ransom_request = RansomRequest.objects.create(
            name=name,
            tg_name=tg_name,
            phone_number=phone_number,
            email=email,
            url=url,
            photo=photo,
            info=info
        )
        ransom_request.save()

        return Response(status=status.HTTP_201_CREATED)


class GetHeaderPhoto(APIView):

    def get(self, request):
        cache_photo_key = f"header_photo"  # Уникальный ключ для каждой URL
        cached_data = cache.get(cache_photo_key)

        if cached_data is not None:
            res = cached_data
        else:
            res = get_header_photo()
            cache.set(cache_photo_key, (res), CACHE_TIME)

        return Response(res)


class MainPageBlocks(APIView):

    def get(self, request):
        # number_page = int(request.COOKIES.get('number_main_page', '1'))
        number_page = int(request.query_params.get("page", 1))
        print(number_page)
        next = request.query_params.get("next", False)
        new = request.query_params.get("new", False)
        # print(self.request.COOKIES)
        # print(number_page)
        context = {"wishlist": Wishlist.objects.get(user=User(id=self.request.user.id)) if request.user.id else None}
        res = []
        # 1 подборка
        # 0 фото

        gender = ["M", "F"]
        if request.user.id:
            gender = [request.user.gender.name]
            for page in range(0 if not next else number_page - 1, number_page):
                if page == 0:
                    s = [2, 1, 0, 1, 1, 0, 0]
                else:
                    s = [0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0]
                t1 = time()
                last = "any"
                for i in range(len(s)):
                    type = s[i]
                    if type == 0:
                        cache_photo_key = f"main_page:{i}_{page}_{request.user.id if request.user.id else ''}"  # Уникальный ключ для каждой URL
                        cached_data = cache.get(cache_photo_key)

                        if cached_data is not None and not new:
                            photo, last, list_id = cached_data
                        else:
                            photo, last, list_id = get_photo_text(last, gender)

                            cache.set(cache_photo_key, (photo, last, list_id), CACHE_TIME)

                        queryset = get_queryset_from_list_id(list_id)
                        if queryset.exists():
                            res.append(photo)
                            selection = {"type": "selection", "title": photo['mobile']['title'],
                                         "url": photo['mobile']['url'],
                                         'products': ProductMainPageSerializer(queryset, many=True, context=context).data}
                            res.append(selection)

                    elif type == 1:
                        cache_sellection_key = f"main_page:{i}_{page}_{request.user.id if request.user.id else None}"  # Уникальный ключ для каждой URL
                        cached_data = cache.get(cache_sellection_key)

                        if cached_data is not None and not new:
                            list_id, selection = cached_data
                        else:

                            list_id, selection = get_selection(gender)

                            cache.set(cache_sellection_key, (list_id, selection), CACHE_TIME)

                        queryset = get_queryset_from_list_id(list_id)

                        selection['products'] = ProductMainPageSerializer(queryset, many=True, context=context).data

                        res.append(selection)
                    else:
                        cache_photo_key = f"main_page:{i}_{page}_{request.user.id if request.user.id else None}"  # Уникальный ключ для каждой URL
                        cached_data = cache.get(cache_photo_key)
                        if cached_data is not None and not new:
                            photo, last = cached_data
                        else:

                            photo, last = get_sellout_photo_text(last)
                            cache.set(cache_photo_key, (photo, last), CACHE_TIME)
                        res.append(photo)
            response = Response(res)
            response.set_cookie('number_main_page', str(number_page + 1),
                                max_age=3600)  # Установка нового значения куки (истечет через 1 час)
            # print(len(res))

            return response
        else:
            for page in range(0 if not next else number_page - 1, number_page):
                anon_cache = "main_page_anon"
                cached_data = cache.get(anon_cache)
                if cached_data is not None and not new:
                    res = cached_data
                else:
                    if page == 0:
                        s = [2, 1, 0, 1, 1, 0, 0]
                    else:
                        s = [0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 1, 0]
                    t1 = time()
                    last = "any"
                    for i in range(len(s)):
                        type = s[i]
                        if type == 0:
                            photo, last, list_id = get_photo_text(last, gender)
                            queryset = get_queryset_from_list_id(list_id)
                            if queryset.exists():
                                res.append(photo)
                                selection = {"type": "selection", "title": photo['mobile']['title'],
                                             "url": photo['mobile']['url'],
                                             'products': ProductMainPageSerializer(queryset, many=True,
                                                                                   context=context).data}
                                res.append(selection)

                        elif type == 1:

                            list_id, selection = get_selection(gender)
                            queryset = get_queryset_from_list_id(list_id)
                            selection['products'] = ProductMainPageSerializer(queryset, many=True, context=context).data
                            res.append(selection)
                        else:
                            photo, last = get_sellout_photo_text(last)
                            res.append(photo)
                cache.set(anon_cache, res, CACHE_TIME)
            response = Response(res)
            return response



class ProductSimilarView(APIView):

    def get(self, request, product_id):
        t = time()
        context = {"wishlist": Wishlist.objects.get(user=User(id=self.request.user.id)) if request.user.id else None}
        res = []
        try:
            product = Product.objects.get(id=product_id)
            if Product.objects.filter(Q(spu_id=product.spu_id)).exists():
                another_configuration = Product.objects.filter(spu_id=product.spu_id, available_flag=True).exclude(
                    id=product.id).order_by("min_price")
                if another_configuration.count() > 0:
                    name = "Другие конфигурации" if not product.has_many_colors else "Другие цвета"
                    res.append({"name": name,
                                "products": ProductMainPageSerializer(another_configuration, many=True,
                                                                       context=context).data})

            similar = similar_product(product)
            if similar[1]:
                if similar[0].exists():
                    res.append({"name": "Похожие товары",
                                "products": ProductMainPageSerializer(similar[0], many=True, context=context).data})
            print("similar", time() - t, product.id)
            return Response(res)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductsCountView(APIView):
    def get(self, request):
        count = count_queryset(request)
        return Response({"count": count})


class DewuInfoListSpuIdView(APIView):
    def get(self, request):
        dewu_infos = DewuInfo.objects.values_list('spu_id', flat=True)
        return Response(dewu_infos, status=status.HTTP_200_OK)


# Create your views here.
class DewuInfoListView(APIView):
    def get(self, request):
        web_data = request.query_params.get("web_data")
        if web_data is not None:
            # Параметр был передан, теперь вы можете проверить его значение
            web_data = web_data.lower() == 'true'

            if not web_data:
                dewu_infos = DewuInfo.objects.filter(web_data={})
            else:
                dewu_infos = DewuInfo.objects.all()
        else:
            dewu_infos = DewuInfo.objects.all().order_by('spu_id')
        # count = dewu_infos.count()
        count = 1
        page_number = request.query_params.get("page")
        page_number = int(page_number if page_number else 1)
        start_index = (page_number - 1) * 30
        queryset = dewu_infos[start_index:start_index + 30]
        serializer = DewuInfoSerializer(queryset, many=True)
        res = {'count': count, "results": serializer.data}  # Замените на вашу сериализацию
        return Response(res, status=status.HTTP_200_OK)


class DewuInfoView(APIView):
    def get(self, request, spu_id):
        dewu_info = DewuInfo.objects.filter(spu_id=spu_id)
        # print(dewu_info.web_data['size_table'])
        serializer = DewuInfoSerializer(dewu_info, many=True)
        # Замените на вашу сериализацию
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, spu_id):
        data = json.loads(request.body)
        if DewuInfo.objects.filter(spu_id=spu_id).exists():
            dewu_info = DewuInfo.objects.get(spu_id=spu_id)
        else:
            dewu_info = DewuInfo(spu_id=spu_id)

        if "api_data" in data:
            dewu_info.api_data = data['api_data']
        if "preprocessed_data" in data:
            dewu_info.preprocessed_data = data['preprocessed_data']
        if "web_data" in data:
            dewu_info.web_data = data['web_data']
        # if "processed_data" in data:
        #     dewu_info.processed_data = data["processed_data"]
        if "formatted_manufacturer_sku" in data:
            dewu_info.formatted_manufacturer_sku = data["formatted_manufacturer_sku"]
        dewu_info.save()
        return Response(DewuInfoSerializer(dewu_info).data)

    def delete(self, request, spu_id):
        try:
            dewu_info = DewuInfo.objects.filter(spu_id=spu_id)
            dewu_info.delete()

            return Response("Удален", status=status.HTTP_200_OK)
        except DewuInfo.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductSearchView(APIView):
    def get(self, request):
        query = json.loads(request.body)  # Получение параметра запроса
        search_fields = query

        q_objects = Q()
        for k, v in search_fields.items():
            q_objects &= Q(**{f'{k}__icontains': v})

        products = Product.objects.filter(q_objects)
        count = products.count()
        page_number = self.request.query_params.get("page")
        page_number = int(page_number if page_number else 1)
        start_index = (page_number - 1) * 96
        queryset = products[start_index:start_index + 96]
        serializer = ProductMainPageSerializer(queryset, many=True)
        res = {'count': count, "results": serializer.data}  # Замените на вашу сериализацию

        return Response(res, status=status.HTTP_200_OK)


# class CustomPagination(PageNumberPagination):
#     # default_limit = 60
#     page_size = 60
#     # page_size_query_param = 'page_size'  # Дополнительно можно разрешить клиенту указывать желаемое количество товаров на странице
#     # max_page_size = 120  # Опционально, чтобы ограничить максимальное количество товаров на странице
#     count = False
#
#     #


class ProductView(APIView):
    def get(self, request):

        t0 = time()
        context = {"wishlist": Wishlist.objects.get(user=User(id=self.request.user.id)) if request.user.id else None}
        size = self.request.query_params.getlist('size')
        if size:
            size = list(map(lambda x: x.split("_")[1], size))
        price_max = self.request.query_params.get('price_max')
        price_min = self.request.query_params.get('price_min')
        ordering = self.request.query_params.get('ordering')
        like = self.request.query_params.get('like')
        adminka = self.request.query_params.get('adminka')

        context['size'] = size if size else None
        context['price_max'] = price_max if price_max else None
        context['price_min'] = price_min if price_min else None
        context['ordering'] = ordering if ordering else None
        # params = request.GET.copy()
        url = request.build_absolute_uri()
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_product_key = f"product_page:{url_hash}_{f'{request.user.id}_{request.user.user_status.id}' if request.user.id else 0}"  # Уникальный ключ для каждой URL
        cached_data = cache.get(cache_product_key)
        # url_hash = urlencode(params)
        if request.user.id:
            if cached_data is None or like:
                queryset, res = get_product_page(request, context)
                t_new = time()
                cache.set(cache_product_key, (queryset, res), CACHE_TIME)
                t_old = time()
                print(f"no cache: {t_old - t_new}")

            else:
                t_new = time()
                queryset, res = cached_data
                t_old = time()
                print(f"cache: {t_old - t_new}")

            t6 = time()
            t7 = time()
            print("t6", t7 - t6)
            if adminka:
                serializer = ProductAdminSerializer(queryset, many=True, context=context).data
            else:
                serializer = ProductMainPageSerializer(queryset, many=True, context=context).data
        else:
            if cached_data is None or like:
                queryset, res = get_product_page(request, context)
                t_new = time()
                if adminka:
                    queryset = ProductAdminSerializer(queryset, many=True, context=context).data
                else:
                    queryset = ProductMainPageSerializer(queryset, many=True, context=context).data
                cache.set(cache_product_key, (queryset, res), CACHE_TIME)
                t_old = time()
                print(f"no cache: {t_old - t_new}")

            else:
                t_new = time()
                queryset, res = cached_data
                t_old = time()
                print(f"cache: {t_old - t_new}")

            t6 = time()
            t7 = time()
            print("t6", t7 - t6)
            serializer = queryset


        res["results"] = serializer
        t8 = time()
        print("t7", t8 - t7)

        cache_header_key = f"product_header:{url_hash}"  # Уникальный ключ для каждой URL
        cached_header = cache.get(cache_header_key)
        if cached_header is not None:
            photos = cached_header
        else:
            photos = get_product_page_header(request)
            cache.set(cache_header_key, (photos), CACHE_TIME)
        res["mobile"] = photos['mobile']
        res["desktop"] = photos['desktop']

        t10 = time()
        print("t9", t10 - t8)
        print("t", t10 - t0, request.GET.copy())

        return Response(res)


class SuggestSearch(APIView):
    def get(self, request):
        query = self.request.query_params.get('q')
        return Response(suggest_search(query))


class ProductSlugView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, slug):
        try:
            t1 = time()
            product = Product.objects.get(slug=slug)
            t2 = time()
            print("пятьдесят ", t2 - t1, product.id)

            # user_agent = request.META.get('HTTP_USER_AGENT', '')
            # print(request.META.get('HTTP_USER_AGENT', ''), "блять")
            # # Проверяем, содержит ли User-Agent характерные строки для поисковых ботов
            # is_search_bot = any(
            #     keyword in user_agent.lower() for keyword in ['googlebot', 'bingbot', 'yandexbot', 'duckduckbot'])
            if request.user.id:
                platform_update_price(product, request=request)
                product.rel_num += 1
                product.save()
            # print(product.min_price)
            # print(Wishlist.objects.get(user=User(id=request.user.id)))
            serializer = ProductSerializer(product, context={"list_lines": True,
                                                             "wishlist": Wishlist.objects.get(user=User(
                                                                 id=request.user.id)) if request.user.id else None})
            t3 = time()
            print("два ", t3-t2, product.id)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductIdView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
            serializer = ProductSerializer(product, context={"list_lines": True,
                                                             "wishlist": Wishlist.objects.get(user=User(
                                                                 id=self.request.user.id) if request.user.id else None)})
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class CategoryTreeView(APIView):
    # authentication_classes = [JWTAuthentication]
    @method_decorator(cache_page(CACHE_TIME))
    def get(self, request):
        cats = CategorySerializer(Category.objects.all(), many=True).data
        return Response(build_category_tree(cats))


class CategoryNoChildView(APIView):
    # authentication_classes = [JWTAuthentication]
    @method_decorator(cache_page(CACHE_TIME))
    def get(self, request):
        cats = CategorySerializer(Category.objects.all(), many=True).data
        return Response(category_no_child(build_category_tree(cats)))


class LineTreeView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        q = self.request.query_params.get('q')
        tree = copy.deepcopy(build_line_tree())
        if q:
            q = q.lower()
            start_tree = []
            in_tree = []
            no_tree = []

            for i in range(len(tree)):
                if tree[i]['view_name'].lower().startswith(q) or tree[i]['search_filter_name'].lower().startswith(q):
                    tree[i]['is_show'] = True
                    start_tree.append(tree[i])
                elif q in tree[i]['view_name'].lower() or q in tree[i]['search_filter_name'].lower():
                    tree[i]['is_show'] = True
                    in_tree.append(tree[i])
                else:
                    tree[i]['is_show'] = False
                    no_tree.append(tree[i])
            return Response(start_tree + in_tree + no_tree)
        return Response(tree)


class LineNoChildView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        lines = LineSerializer(Line.objects.all(), many=True).data
        return Response(line_no_child(lines))


class CollabView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request):
        q = self.request.query_params.get('q')

        # Создайте ключ кэша, учитывая параметр q
        cache_key = f'collab_queryset_{q}'

        # Попробуйте сначала получить результат из кэша
        collabs = cache.get(cache_key)

        if collabs is None:
            # Если результат не найден в кэше, выполните запрос к базе данных и сериализуйте его
            queryset = Collab.objects.all()
            collabs = CollabSerializer(queryset, many=True).data
            if q:
                for i in range(len(collabs)):
                    if not (q.lower() in collabs[i]['name'].lower() or q.lower() in collabs[i]['name'].replace(" x ",
                                                                                                               " ").lower()):
                        collabs[i]['is_show'] = False

            # Сохраните результат в кэш с уникальным ключом
            cache.set(cache_key, collabs, CACHE_TIME)

        return Response(collabs)


class ProductUpdateView(APIView):
    # authentication_classes = [JWTAuthentication]

    def delete(self, request, product_id):
        product = Product.objects.get(id=product_id)
        product.delete()
        return Response("Товар успешно удален")

    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        data = json.loads(request.body)
        if 'categories' in data:
            categories = data.get('categories', [])
            product.categories.clear()
            product.categories.add(*categories)

        if 'lines' in data:
            lines = data.get('lines', [])
            product.lines.clear()
            product.lines.add(*lines)

        if 'colors' in data:
            colors = data.get('colors', [])
            product.lines.add(*colors)

        if 'brands' in data:
            brands = data.get('brands', [])
            product.brands.clear()
            product.brands.add(*brands)

        if 'tags' in data:
            tags = data.get('tags', [])
            product.tags.clear()
            product.tags.add(*tags)

        # Обработайте остальные поля по аналогии
        if 'model' in data:
            product.model = data.get('model', product.model)
        if 'colorway' in data:
            product.colorway = data.get('colorway', product.colorway)
        if 'russian_name' in data:
            product.russian_name = data.get('russian_name', product.russian_name)
        if 'manufacturer_sku' in data:
            product.manufacturer_sku = data.get('manufacturer_sku', product.manufacturer_sku)
        if 'description' in data:
            product.description = data.get('description', product.description)
        if 'bucket_link' in data:
            product.bucket_link = data.get('bucket_link', product.bucket_link)
        if 'main_color' in data:
            product.main_color_id = data.get('main_color', product.main_color_id)
        product.slug = ""
        product.save()

        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)


class SizeTableForFilter(APIView):
    def get(self, request):
        try:
            context = {}
            if request.user.id:
                user = User.objects.get(id=request.user.id)
                context = {"user": user}

            # Соберите данные size_tables из базы данных или другого источника
            size_tables = SizeTable.objects.filter(standard=True)

            # Фильтр по цене
            gender = request.query_params.getlist('gender')
            categories = request.query_params.getlist('categories')

            if gender:
                size_tables = size_tables.filter(gender__name__in=gender)
            if categories:
                size_tables = size_tables.filter(category__eng_name__in=categories)

            # Создайте уникальный ключ кэша на основе данных size_tables
            cache_key = hashlib.sha256(pickle.dumps(size_tables)).hexdigest()

            # Попробуйте получить закэшированные данные из кэша
            cached_data = cache.get(cache_key)

            if cached_data is None:
                # Если данные не найдены в кэше, выполните сериализацию и закэшируйте результаты
                size_tables_data = SizeTableSerializer(size_tables, many=True, context=context).data
                cache.set(cache_key, size_tables_data, CACHE_TIME)
            else:
                # Если данные найдены в кэше, используйте закэшированные данные
                size_tables_data = cached_data

            return Response(size_tables_data)
        except User.DoesNotExist:
            return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)


class ProductSizeView(APIView):
    def get(self, request):
        with open('size_table_2.json', 'r', encoding='utf-8') as file:
            product_sizes_data = json.load(file)

        # Верните JSON-данные в ответе
        return Response(product_sizes_data)


class AddProductView(APIView):
    def post(self, request):
        data = json.loads(request.body)
        product = add_product_api(data)
        return Response(ProductSerializer(product).data)


class AddListProductsView(APIView):  # список товаров одного spu_id
    def post(self, request):
        data = json.loads(request.body)
        add_products_spu_id_api(data)
        return Response("Готово")


class ListProductView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            t = time()
            s_products = json.loads(request.body)["products"]
            product_list_string = json.dumps(s_products, sort_keys=True)  # Преобразуем список в строку
            product_list_hash = hashlib.sha256(product_list_string.encode('utf-8')).hexdigest()  # Получаем хеш-сумму

            # Используем хеш-сумму в качестве ключа кэша
            cache_product_key = f"product_list_{product_list_hash}"

            cached_data = cache.get(cache_product_key)

            if cached_data is not None:
                products = cached_data
            else:
                products = Product.objects.filter(id__in=s_products).order_by(
                    models.Case(*[models.When(id=id, then=index) for index, id in enumerate(s_products)])
                )
                cache.set(cache_product_key, products, CACHE_TIME)

            print("лист ", time()-t)

            return Response(ProductMainPageSerializer(products, many=True, context={"wishlist": Wishlist.objects.get(
                user=User(id=self.request.user.id)) if request.user.id else None}).data)
        except json.JSONDecodeError:
            return Response("Invalid JSON data", status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response("One or more product do not exist", status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class ProductMainPageView(rest_framework.generics.ListAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     # pagination_class = PageNumberPagination
#     # permission_classes = [AllowAny,]
#     # filter_backends = [ProductFilter]
#
#     def get_serializer_context(self):
#         context = super().get_serializer_context()
#         context['user_id'] = self.request.user.id
#         return context


# возвращает список продуктов для главной странички всех товаров
# class ProductsView(APIView):
#
#     def get(self, request, page_number):
#         products = Product.objects.get_queryset().order_by('id')
#         page_number = self.request.query_params.get('page_number ', page_number)
#         page_size = self.request.query_params.get('page_size ', 5)
#         try:
#             products = Paginator(products, page_size).page(page_number)
#         except Exception as e:
#             print(e)
#             return Response("Ошибка")
#         list_products = []
#         if request.user.id:
#             for product in products:
#                 list_products.append(product_unit_product_main(product.id, request.user.id))
#         else:
#             for product in products:
#                 list_products.append(product_unit_product_main(product.id, 0))
#
#         ans = {"page number": page_number,
#                'items': list_products}
#         return Response(ans, status=status.HTTP_200_OK)
