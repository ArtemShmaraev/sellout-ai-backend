import random

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
from .models import Product, Category, Line, DewuInfo, SizeRow, SizeTable, Collab, HeaderPhoto, HeaderText
from rest_framework import status
from .serializers import SizeTableSerializer, ProductMainPageSerializer, CategorySerializer, LineSerializer, \
    ProductSerializer, \
    DewuInfoSerializer, CollabSerializer
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



class GetHeaderPhoto(APIView):
    def get(self, request):
        return Response(get_header_photo())

class MainPageBlocks(APIView):

    def get(self, request):
        generator = RandomGenerator()
        more = request.query_params.get("more")
        context = {"wishlist": Wishlist.objects.get(user=User(id=self.request.user.id)) if request.user.id else None}
        res = []

        last = "any"
        if not more:
            photo, last = get_sellout_photo_text(last)
            res.append(photo)
        res.append(get_selection(context))
        for i in range(8):
            type = generator.generate()
            if type == 1:
                res.append(get_selection(context))
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
        count = dewu_infos.count()
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

    # @method_decorator(cache_page(60 * 5))
    def get(self, request):

        t0 = time()
        queryset = Product.objects.all()
        t1 = time()
        res = {}
        list_cat = []
        list_line = []
        print("t0", t1 - t0)
        context = {"wishlist": Wishlist.objects.get(user=User(id=self.request.user.id)) if request.user.id else None}

        query = self.request.query_params.get('q')
        size = self.request.query_params.getlist('size')
        if size:
            size = list(map(lambda x: x.split("_")[1], size))

        price_max = self.request.query_params.get('price_max')
        price_min = self.request.query_params.get('price_min')
        ordering = self.request.query_params.get('ordering')

        # Передайте значения фильтров в контекст сериализатора
        context['size'] = size if size else None
        context['price_max'] = price_max if price_max else None
        context['price_min'] = price_min if price_min else None
        context['ordering'] = ordering if ordering else None
        # Создаем объект пагинации

        line = self.request.query_params.getlist('line')
        color = self.request.query_params.getlist('color')
        is_fast_ship = self.request.query_params.get("is_fast_shipx`")
        is_sale = self.request.query_params.get("is_sale")
        is_return = self.request.query_params.get("is_return")
        category = self.request.query_params.getlist("category")
        gender = self.request.query_params.getlist("gender")
        brand = self.request.query_params.getlist("brand")
        collab = self.request.query_params.getlist("collab")
        available = self.request.query_params.get("available")
        custom = self.request.query_params.get("custom")


        if not available:
            queryset = queryset.filter(available_flag=True)
            queryset = queryset.filter(product_units__availability=True)
            queryset = queryset.distinct()
        if not custom:
            queryset = queryset.filter(is_custom=False)


        new = self.request.query_params.get("new")
        if new:
            new_q = queryset.order_by('-exact_date')[:1000]

        recommendations = self.request.query_params.get("recommendations")
        if recommendations:
            recommendations_q = queryset.order_by('-rel_num')[:1000]


        if collab:
            if "all" in collab:
                queryset = queryset.filter(is_collab=True)
            else:
                queryset = queryset.filter(collab__query_name__in=collab)
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
            queryset = queryset.filter(Q(main_color__name__in=color))
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

        filters = Q(product_units__availability=True)

        # Фильтр по цене
        if price_min:
            filters &= Q(product_units__final_price__gte=price_min)

            # Фильтр по максимальной цене
        if price_max:
            filters &= Q(product_units__final_price__lte=price_max)

        # Фильтр по размеру
        if size:
            filters &= Q(product_units__size__in=size)

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
        queryset = queryset.distinct()

        if new:
            queryset = queryset & new_q

        if recommendations:
            queryset = queryset & recommendations_q

        t2 = time()
        print("t1", t2 - t1)
        if query:
            query = query.replace("_", " ")
            search = search_product(query, queryset)
            queryset = search['queryset']
            res['add_filter'] = search['url']

            # if 'category' in search:
            #     category.append(search['category'])
            # if 'collab' in search:
            #     collab.append(search['collab'])
            # if 'line' in search:
            #     line.append(search['line'])
            # if 'color' in search:
            #     color.append(search['color'])

        t3 = time()
        print("t2", t3 - t2)

        ordering = self.request.query_params.get('ordering', '-rel_num')
        if ordering in ['exact_date', 'rel_num', '-rel_num', "-exact_date"]:
            queryset = queryset.order_by(ordering)
        elif ordering == "min_price" or ordering == "-min_price":
            if size:
                queryset = queryset.annotate(
                    min_price_product_unit=Subquery(
                        Product.objects.filter(pk=OuterRef('pk'))
                        .annotate(unit_min_price=Min('product_units__final_price', filter=(
                            Q(product_units__size__in=size))))
                        .values('unit_min_price')[:1]
                    )
                )
                if ordering == "min_price":
                    queryset = queryset.order_by("min_price_product_unit")
                else:
                    queryset = queryset.order_by("-min_price_product_unit")
            else:
                queryset = queryset.order_by(ordering)

        t4 = time()
        print("t3", t4 - t3)

        # paginator = CustomPagination()
        # Применяем пагинацию к списку объектов Product
        # paginated_products = paginator.paginate_queryset(queryset, request)
        # serializer = ProductMainPageSerializer(queryset, many=True, context=context).data
        # res = paginator.get_paginated_response(serializer)

        # res["count"] = queryset.count()
        res['count'] = queryset.values('id').count()

        # res["count"] = 1000
        t5 = time()
        print("t4", t5 - t4)

        page_number = self.request.query_params.get("page")
        page_number = int(page_number if page_number else 1)
        start_index = (page_number - 1) * 48
        queryset = queryset[start_index:start_index + 48]

        t6 = time()
        print("t5", t6 - t5)
        # Сериализуем объекты и возвращаем ответ с пагинированными данными
        serializer = ProductMainPageSerializer(queryset, many=True, context=context)
        t7 = time()
        print("t6", t7 - t6)

        serializer = serializer.data
        t8 = time()
        print("t7", t8 - t7)

        res['results'] = serializer
        t9 = time()
        print("t8", t9 - t8)

        res['next'] = f"http://127.0.0.1:8000/api/v1/product/products/?page={page_number + 1}"
        res["previous"] = f"http://127.0.0.1:8000/api/v1/product/products/?page={page_number - 1}"
        res['min_price'] = 0
        res['max_price'] = 1000000

        header_photos = HeaderPhoto.objects.all()
        header_photos = header_photos.filter(where="product_page")
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



        header_photos_desktop = header_photos.filter(type="desktop")
        header_photos_mobile = header_photos.filter(type="mobile")
        if header_photos_desktop.count() > 0:
            count = header_photos_desktop.count()
        else:
            header_photos_desktop = HeaderPhoto.objects.filter(type="desktop")
            count = header_photos_desktop.count()

        photo_desktop = header_photos_desktop[random.randint(0, count - 1)]
        text_desktop = get_product_text(line, collab, category)
        if text_desktop is None:
            text_desktop = photo_desktop.header_text

        res["desktop"] = {"title": text_desktop.title, "content": text_desktop.text}
        res['desktop']['photo'] = photo_desktop.photo.url

        if header_photos_mobile.count() > 0:
            count = header_photos_mobile.count()
        else:
            header_photos_mobile = HeaderPhoto.objects.filter(type="mobile")
            count = header_photos_mobile.count()

        photo_mobile = header_photos_mobile[random.randint(0, count - 1)]
        text_mobile = get_product_text(line, collab, category)
        if text_mobile is None:
            text_mobile = photo_mobile.header_text

        res["mobile"] = {"title": text_mobile.title, "content": text_mobile.text}
        res['mobile']['photo'] = photo_mobile.photo.url


        # photos = get_product_page_photo(self.request.query_params)
        # res["mobile"] = photos['mobile']
        # res["desktop"] = photos['desktop']

        t10 = time()
        print("t9", t10 - t9)
        print("t", t10 - t0)
        print(res['mobile']['photo'])

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

    def get(self, request):
        cats = CategorySerializer(Category.objects.all(), many=True).data
        return Response(build_category_tree(cats))


class CategoryNoChildView(APIView):
    # authentication_classes = [JWTAuthentication]

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
    @method_decorator(cache_page(60 * 60))
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
            products = Product.objects.filter(id__in=s_products).order_by(
                models.Case(*[models.When(id=id, then=index) for index, id in enumerate(s_products)])
            )
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
