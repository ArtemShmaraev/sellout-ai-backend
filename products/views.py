import hashlib
import random

from django.core.cache import cache
from django.utils.functional import cached_property
from django.db import models
import rest_framework.generics

from django.db.models import Q, Subquery, OuterRef, Min, When, Case
# from haystack.query import SearchQuerySet
from rest_framework.decorators import api_view, action
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
import json
from time import time
from django.http import JsonResponse, FileResponse

from users.models import User
from wishlist.models import Wishlist
from .models import Product, Category, Line, DewuInfo, SizeRow, SizeTable, Collab, HeaderPhoto, HeaderText, \
    RansomRequest, SGInfo
from rest_framework import status

from .product_page import get_product_page, get_product_page_header
from .serializers import SizeTableSerializer, ProductMainPageSerializer, CategorySerializer, LineSerializer, \
    ProductSerializer, \
    DewuInfoSerializer, CollabSerializer, SGInfoSerializer
from .tools import build_line_tree, build_category_tree, category_no_child, line_no_child, add_product, get_text, \
    get_product_page_photo, RandomGenerator, get_product_text

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response

from .search_tools import search_best_line, search_best_category, search_best_color, search_best_collab, search_product, \
    similar_product, suggest_search
from .documents import ProductDocument  # Импортируйте ваш документ
from random import randint
from products.main_page import get_selection, get_photo_text, get_sellout_photo_text, get_header_photo
from sellout.settings import CACHE_TIME



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
            sg_info =SGInfo.objects.get(manufacturer_sku=sku)
        else:
            sg_info = SGInfo(manufacturer_sku=sku)

        if "data" in data:
            sg_info.data = data['data']

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
    @method_decorator(cache_page(CACHE_TIME))
    def get(self, request):
        return Response(get_header_photo())


class MainPageBlocks(APIView):

    def get(self, request):
        more = request.query_params.get("more")
        context = {"wishlist": Wishlist.objects.get(user=User(id=self.request.user.id)) if request.user.id else None}
        res = []
        s = [2, 1, 1, 0, 1, 1, 0, 0, 1]

        last = "any"
        if not more:
            for i in range(9):
                type = s[i]
                if type == 0:
                    cache_photo_key = f"main_page:{i}"  # Уникальный ключ для каждой URL
                    cached_data = cache.get(cache_photo_key)

                    if cached_data is not None:
                        photo, last = cached_data
                    else:
                        photo, last = get_photo_text(last)
                        cache.set(cache_photo_key, (photo, last), 60 * 60 * 5)
                    res.append(photo)

                elif type == 1:
                    cache_sellection_key = f"main_page:{i}"  # Уникальный ключ для каждой URL
                    cached_data = cache.get(cache_sellection_key)

                    if cached_data is not None:
                        queryset, selection = cached_data
                    else:
                        queryset, selection = get_selection()
                        cache.set(cache_sellection_key, (queryset, selection), 60 * 60 * 5)
                    selection['products'] = ProductMainPageSerializer(queryset, many=True, context=context).data
                    res.append(selection)
                else:
                    cache_photo_key = f"main_page:{i}"  # Уникальный ключ для каждой URL
                    cached_data = cache.get(cache_photo_key)
                    if cached_data is not None:
                        photo, last = cached_data
                    else:
                        photo, last = get_sellout_photo_text(last)
                        cache.set(cache_photo_key, (photo, last), 60 * 60 * 5)
                    res.append(photo)
        else:
            generator = RandomGenerator()
            for i in range(9):
                type = generator.generate()
                if type == 1:
                    queryset, selection = get_selection()
                    selection['products'] = ProductMainPageSerializer(queryset, many=True, context=context).data
                    res.append(selection)
                elif type == 0:
                    photo, last = get_photo_text(last)
                    res.append(photo)
            del generator
        return Response(res)


class ProductSimilarView(APIView):

    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            similar = similar_product(product)
            return Response(ProductMainPageSerializer(similar, many=True).data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


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
        start_index = (page_number - 1) * 100
        queryset = dewu_infos[start_index:start_index + 100]
        serializer = DewuInfoSerializer(queryset, many=True)
        res = {'count': count, "results": serializer.data}  # Замените на вашу сериализацию
        return Response(res, status=status.HTTP_200_OK)


class DewuInfoView(APIView):
    def get(self, request, spu_id):
        dewu_info = DewuInfo.objects.filter(spu_id=spu_id)
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

        context['size'] = size if size else None
        context['price_max'] = price_max if price_max else None
        context['price_min'] = price_min if price_min else None
        context['ordering'] = ordering if ordering else None

        url = request.build_absolute_uri()
        url_hash = hashlib.md5(url.encode()).hexdigest()

        cache_product_key = f"product_page:{url_hash}"  # Уникальный ключ для каждой URL
        cached_data = cache.get(cache_product_key)

        if cached_data is not None:
            queryset, res = cached_data
        else:
            queryset, res = get_product_page(request)
            cache.set(cache_product_key, (queryset, res), CACHE_TIME)

        t6 = time()
        print("t5", t6 - t0)
        # Сериализуем объекты и возвращаем ответ с пагинированными данными
        serializer = ProductMainPageSerializer(queryset, many=True, context=context)
        t7 = time()
        print("t6", t7 - t6)
        serializer = serializer.data
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
        print("t", t10 - t0)

        return Response(res)


class SuggestSearch(APIView):
    def get(self, request):
        query = self.request.query_params.get('q')
        return Response(suggest_search(query))


class ProductSlugView(APIView):
    # authentication_classes = [JWTAuthentication]

    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)

            product.rel_num += 1
            product.save()
            serializer = ProductSerializer(product, context={"list_lines": True,
                                                             "wishlist": Wishlist.objects.get(user=User(
                                                                 id=self.request.user.id)) if request.user.id else None})
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
        tree = build_line_tree()[:]
        if q:
            q = q.lower()
            start_tree = []
            in_tree = []
            no_tree = []

            for i in range(len(tree)):
                if tree[i]['view_name'].lower().startswith(q):
                    tree[i]['is_show'] = True
                    start_tree.append(tree[i])
                elif q in tree[i]['view_name'].lower():
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
        collabs = CollabSerializer(Collab.objects.all(), many=True).data
        if q:
            for i in range(len(collabs)):
                if not (q.lower() in collabs[i]['name'].lower() or q.lower() in collabs[i]['name'].replace(" x ",
                                                                                                           " ").lower()):
                    collabs[i]['is_show'] = False

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
    @method_decorator(cache_page(CACHE_TIME))
    def get(self, request):
        try:
            context = {}
            if request.user.id:
                user = User.objects.get(id=request.user.id)
                context = {"user": user}
            gender = self.request.query_params.getlist("gender")
            categories = self.request.query_params.getlist("category")

            filters = {}
            size_tables = SizeTable.objects.all()

            # Фильтр по цене
            if gender:
                filters['gender__name__in'] = gender
            if categories:
                list_cat = []
                for category in categories:
                    category_model = Category.objects.filter(eng_name=category).first()
                    list_cat.append(category_model.eng_name)
                    while category_model.parent_category:
                        list_cat.append(category_model.parent_category.eng_name)
                        category_model = category_model.parent_category
                filters['category__eng_name__in'] = list_cat

            if filters:
                size_tables = size_tables.filter(**filters)

            return Response(
                SizeTableSerializer(size_tables, many=True, context=context).data)
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
        product = add_product(data)
        return Response(product.manufacturer_sku)


class ListProductView(APIView):
    # authentication_classes = [JWTAuthentication]

    def post(self, request):
        try:
            s_products = json.loads(request.body)["products"]
            product_list_string = json.dumps(s_products, sort_keys=True)  # Преобразуем список в строку
            product_list_hash = hashlib.sha256(product_list_string.encode('utf-8')).hexdigest()  # Получаем хеш-сумму
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
