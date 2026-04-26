import copy
import json

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from sellout.settings import CACHE_TIME
from users.models import User

from products.models import (
    Brand, Category, Collab, Line, Material, SizeTable,
    Product,
)
from products.serializers import (
    BrandSerializer, CategorySerializer, CollabSerializer,
    LineSerializer, MaterialSerializer,
)
from products.tools import (
    build_category_tree, build_line_tree, category_no_child, line_no_child,
)


class MaterialView(APIView):
    def get(self, request):
        cache_material = "materials"  # Уникальный ключ для каждой URL
        cached_data = cache.get(cache_material)

        if cached_data is not None:
            res = cached_data
        else:
            queryset = Material.objects.all().order_by("id")
            res = MaterialSerializer(queryset, many=True).data
            cache.set(cache_material, (res), CACHE_TIME)

        return Response(res)


class CategoryTreeView(APIView):
    # authentication_classes = [JWTAuthentication]
    @method_decorator(cache_page(CACHE_TIME))
    def get(self, request):
        cats = CategorySerializer(Category.objects.all().order_by("id"), many=True).data
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
            print(1)
            # Если результат не найден в кэше, выполните запрос к базе данных и сериализуйте его
            queryset = Collab.objects.order_by("order")
            collabs = CollabSerializer(queryset, many=True).data
            if q:
                for i in range(len(collabs)):
                    if not (q.lower() in collabs[i]['name'].lower() or q.lower() in collabs[i]['name'].replace(" x ",
                                                                                                               " ").lower()):
                        collabs[i]['is_show'] = False

            # Сохраните результат в кэш с уникальным ключом
            cache.set(cache_key, collabs, CACHE_TIME)

        return Response(collabs)


class BrandSearchView(APIView):
    def get(self, request):
        context = {"user_id": request.user.id if request.user.id else None}
        search_query = request.query_params.get('q', '')  # Получаем параметр "q" из запроса

        # Используем исключение try-except для обработки ошибок
        try:
            # Ищем бренды, чьи имена содержат поисковой запрос
            brands = Brand.objects.filter(name__icontains=search_query).order_by("query_name")
            serializer = BrandSerializer(brands, many=True, context=context)  # Сериализуем найденные бренды
            return Response(serializer.data)
        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
            categories = request.query_params.getlist('category')

            if gender:
                size_tables = size_tables.filter(gender__name__in=gender)
            if categories:
                size_tables = size_tables.filter(category__eng_name__in=categories)
            size_tables = size_tables.order_by("id")
            name_size_tables = list(size_tables.values_list("name", flat=True))
            return Response(name_size_tables)
            # # Создайте уникальный ключ кэша на основе данных size_tables
            # cache_key = ".".join(list(map(str, size_tables.values_list("id", flat=True))))
            #
            # # Попробуйте получить закэшированные данные из кэша
            # cached_data = cache.get(cache_key)
            # if cached_data is None:
            #     # Если данные не найдены в кэше, выполните сериализацию и закэшируйте результаты
            #     size_tables_data = SizeTableSerializer(size_tables, many=True, context=context).data
            #     cache.set(cache_key, size_tables_data, CACHE_TIME)
            # else:
            #     # Если данные найдены в кэше, используйте закэшированные данные
            #     size_tables_data = cached_data
            #
            # return Response(size_tables_data)
        except User.DoesNotExist:
            return Response("Пользователь не существует", status=status.HTTP_404_NOT_FOUND)


class ProductSizeView(APIView):
    def get(self, request):
        with open('size_table_2.json', encoding='utf-8') as file:
            product_sizes_data = json.load(file)

        # Верните JSON-данные в ответе
        return Response(product_sizes_data)


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
