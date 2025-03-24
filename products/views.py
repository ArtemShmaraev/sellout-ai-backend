import rest_framework.generics
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from wishlist.models import Wishlist, WishlistUnit
from products.models import Product, Category, Line
from rest_framework import status
import json
from django.core.paginator import Paginator
from rest_framework.pagination import PageNumberPagination
from .serializers import ProductSerializer, ProductMainPageSerializer, CategorySerializer, LineSerializer


# Create your views here.


class ProductSlugView(APIView):
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductMainPageSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


class ProductIdView(APIView):
    def get(self, request, id):
        try:
            product = Product.objects.get(id=id)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response("Товар не найден", status=status.HTTP_404_NOT_FOUND)


def build_category_tree(categories):
    category_dict = {}
    root_categories = []

    # Создаем словарь для быстрого доступа к категориям по их идентификатору
    for category in categories:
        category_dict[category["id"]] = category

    # Строим иерархическую структуру категорий
    for category in categories:
        parent_ids = category["parent_category"]
        if parent_ids:
            parent_category = category_dict[parent_ids]
            parent_category.setdefault("subcategories", []).append(category)
        else:
            root_categories.append(category)
    return root_categories


class CategoryTreeView(APIView):
    def get(self, request):
        cats = CategorySerializer(Category.objects.all(), many=True).data
        return Response(build_category_tree(cats))


def build_line_tree(lines):
    line_dict = {}
    root_lines = []

    # Создание словаря линеек с использованием их идентификаторов в качестве ключей
    for line in lines:
        line_dict[line['id']] = line

    # Построение дерева линеек
    for line in lines:
        parent_line = line['parent_line']
        if parent_line is None:
            # Если у линейки нет родительской линейки, она считается корневой линейкой
            root_lines.append(line)
        else:
            parent_id = parent_line['id']
            parent_line = line_dict.get(parent_id)
            if parent_line:
                # Если родительская линейка найдена, добавляем текущую линейку в список её дочерних линеек
                parent_line.setdefault('children', []).append(line)

    def sort_children(data):
        order = {'low': 0, 'mid': 1, 'high': 2, "air jordan 1": 3,
                 "air jordan 2": 4, "air jordan 3": 5, "air jordan 4": 6,
                 "air jordan 5": 7, "air jordan 6": 8, "air jordan 7": 9,
                 "air jordan 8": 10, "air jordan 9": 11, "air jordan 10": 12,
                 "air jordan 11": 13, "air jordan 12": 14, "air jordan 13": 15,
                 "air jordan 14": 16, "air jordan 15": 17}

        def sort_key(child):
            name = child['name'].lower()
            if 'все' in name:
                return 0, '', ''
            return 1, order.get(name, float('inf')), name

        for item in data:
            children = item.get('children')
            if children:
                item['children'] = sorted(children, key=sort_key)
                sort_children(item['children'])
        return data

    root_lines = sort_children(root_lines)

    with_children = [x for x in root_lines if x.get('children')]
    without_children = [x for x in root_lines if not x.get('children')]

    sorted_data_with_children = sorted(with_children, key=lambda x: x['name'].lower())

    # Сортируем оставшиеся элементы
    sorted_data_without_children = sorted(without_children, key=lambda x: x['name'].lower())

    # Объединяем отсортированные части
    sorted_data = sorted_data_with_children + sorted_data_without_children

    return sorted_data



class LineTreeView(APIView):
    def get(self, request):
        lines = LineSerializer(Line.objects.all(), many=True).data
        return Response(build_line_tree(lines))


class ProductUpdateView(APIView):
    def put(self, request, product_id):
        product = Product.objects.get(id=product_id)
        data = request.data
        if 'categories' in data:
            categories = data.get('categories', [])
            product.categories.add(*categories)

        if 'lines' in data:
            lines = data.get('lines', [])
            product.lines.add(*lines)

        if 'colors' in data:
            colors = data.get('colors', [])
            product.lines.add(*colors)

        if 'brands' in data:
            brands = data.get('brands', [])
            product.brands.add(*brands)

        if 'tags' in data:
            tags = data.get('tags', [])
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
        # Добавьте обработку для других полей ManyToMany, например, brands, lines, collections, tags
        product.slug = ""
        product.save()

        return Response(ProductMainPageSerializer(product).data, status=status.HTTP_200_OK)

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
