from django.core.cache import cache
from rest_framework_simplejwt.authentication import JWTAuthentication

from sellout.settings import CACHE_TIME
from .models import Product, Category, Line, Brand, Color, Collection, Collab, Material
from rest_framework import viewsets, permissions, generics, pagination
from .serializers import ProductMainPageSerializer, ProductSerializer, CategorySerializer, LineSerializer, \
    BrandSerializer, ColorSerializer, CollectionSerializer, MaterialSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from shipping.models import ProductUnit
from django.db.models import ExpressionWrapper, F, Subquery, Min, OuterRef, Max
from django.db.models import Q, Case, When, Value, BooleanField
from .tools import build_line_tree, build_category_tree
from rest_framework.response import Response

from rest_framework.filters import OrderingFilter


class LinesViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthentication]
    queryset = Line.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = LineSerializer


class ColorViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = ColorSerializer

    def get_queryset(self):
        # Попробуйте сначала получить результат из кэша
        queryset = cache.get('color_queryset')

        if queryset is None:
            # Если результат не найден в кэше, выполните запрос к базе данных
            queryset = Color.objects.filter(is_main_color=True)

            # Затем сохраните результат в кэш
            cache.set('color_queryset', queryset, CACHE_TIME)

        return queryset


class MaterialViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = MaterialSerializer

    def get_queryset(self):
        # Попробуйте сначала получить результат из кэша
        queryset = cache.get('mat_queryset')

        if queryset is None:
            # Если результат не найден в кэше, выполните запрос к базе данных
            queryset = Material.objects.all()

            # Затем сохраните результат в кэш
            cache.set('mat_queryset', queryset, CACHE_TIME)

        return queryset


class CategoryViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthentication]
    queryset = Category.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = CategorySerializer


class CollectionViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthentication]
    queryset = Collection.objects.filter()
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = CollectionSerializer


class BrandViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthentication]
    queryset = Brand.objects.all().order_by("name")
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = BrandSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.request.user.id
        return context


class CollabViewSet(viewsets.ModelViewSet):
    # authentication_classes = [JWTAuthentication]
    # queryset = Collab.objects.filter(is_main_collab=True)
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = BrandSerializer

    def get_queryset(self):
        # Попробуйте сначала получить результат из кэша
        queryset = cache.get('collab_queryset')

        if queryset is None:
            # Если результат не найден в кэше, выполните запрос к базе данных
            queryset = Collab.objects.filter(is_main_collab=True)

            # Затем сохраните результат в кэш
            cache.set('collab_queryset', queryset, CACHE_TIME)

        return queryset


class ProductPagination(pagination.PageNumberPagination):
    page_size = 60
    page_size_query_param = 'page_size'
    max_page_size = 120

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)
        # min_price = 9999999999
        # max_price = 0
        #
        # # Calculate min_price and max_price from the data
        # for item in data:
        #     min_price_product_unit = item['min_price_product_unit']
        #     if min_price_product_unit is not None:
        #         if min_price is not None and min_price_product_unit < min_price:
        #             min_price = min_price_product_unit
        #         if max_price is not None and min_price_product_unit > max_price:
        #             max_price = min_price_product_unit

        response.data['min_price'] = Product.objects.aggregate(min_price=Min('min_price'))['min_price']
        response.data['max_price'] = Product.objects.aggregate(min_price=Max('min_price'))['min_price']

        def find_oldest_name(names, target_names, cat=True):
            def find_name_with_children(name, target_names):
                if "children" not in name:
                    return None
                field = "eng_name"
                if not cat:
                    field = "full_" + field
                children_names = [child[field] for child in name["children"]]
                if all(child_name in children_names for child_name in target_names):
                    return name[field]

                for child in name["children"]:
                    found_name = find_name_with_children(child, target_names)
                    if found_name:
                        return found_name

                return None

            for name in names:
                found_name = find_name_with_children(name, target_names)
                if found_name:
                    return found_name

            return None
        request = self.request
        lines = request.query_params.getlist('line')
        categories = request.query_params.getlist('category')
        line = ""
        cat = ""
        if lines:
            tree = build_line_tree(LineSerializer(Line.objects.all(), many=True).data)
            line = find_oldest_name(tree, lines, cat=False)
        if categories:
            tree = build_category_tree(CategorySerializer(Category.objects.all(), many=True).data)
            cat = find_oldest_name(tree, categories)
        response.data["products_page_header"] = str(line) + " " + str(cat)

        return response


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductMainPageSerializer
    filter_backends = [DjangoFilterBackend]
    # filterset_class = ProductFilter
    pagination_class = ProductPagination
    ordering_fields = ['exact_date']

    # def list(self, request, *args, **kwargs):
    #     queryset = self.filter_queryset(self.get_queryset())
    #
    #     # Применение пагинации
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.request.user.id
        # Получите значения фильтров из запроса
        size = self.request.query_params.getlist('size')
        price_max = self.request.query_params.get('price_max')
        price_min = self.request.query_params.get('price_min')
        ordering = self.request.query_params.get('ordering')

        # Передайте значения фильтров в контекст сериализатора
        context['size'] = context['size_us'] = size if size else None
        context['price_max'] = price_max if price_max else None
        context['price_min'] = price_min if price_min else None
        context['ordering'] = ordering if ordering else None
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        price_max = self.request.query_params.get('price_max')
        price_min = self.request.query_params.get('price_min')
        size_us = self.request.query_params.getlist('size_us')

        # Применение сортировки к queryset
        ordering = self.request.query_params.get('ordering')
        if ordering in self.ordering_fields:
            queryset = queryset.order_by(ordering)
        elif ordering == "min_price" or ordering == "-min_price":
            if size_us:

                if price_max is not None:
                    queryset = queryset.annotate(
                        min_price_product_unit=Subquery(
                            Product.objects.filter(pk=OuterRef('pk'))
                            .annotate(unit_min_price=Min('product_units__final_price', filter=(
                                    Q(product_units__size__US__in=size_us) & Q(
                                product_units__final_price__lte=price_max))))
                            .values('unit_min_price')[:1]
                        )
                    )
                if price_min is not None:
                    queryset = queryset.annotate(
                        min_price_product_unit=Subquery(
                            Product.objects.filter(pk=OuterRef('pk'))
                            .annotate(unit_min_price=Min('product_units__final_price', filter=(
                                    Q(product_units__size__US__in=size_us) & Q(
                                product_units__final_price__gte=price_min))))
                            .values('unit_min_price')[:1]
                        )
                    )

                if ordering == "min_price":
                    queryset = queryset.order_by("min_price_product_unit")
                else:
                    queryset = queryset.order_by("-min_price_product_unit")
            else:
                queryset = queryset.order_by(ordering)
        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        size_us = self.request.query_params.getlist('size_us')
        price_max = self.request.query_params.get('price_max')
        price_min = self.request.query_params.get('price_min')
        line = self.request.query_params.getlist('line')
        color = self.request.query_params.getlist('color')
        is_fast_shipping = self.request.query_params.get("is_fast_shipping")
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
        if not custom:
            queryset = queryset.filter(is_custom=False)
        if collab:
            if collab == "all":
                queryset = queryset.filter(is_collab=True)
            else:
                queryset = queryset.filter(collab__query_name__in=collab)
        if brand:
            for brand_name in brand:
                queryset = queryset.filter(brands__query_name=brand_name)
        if line:
            queryset = queryset.filter(lines__full_eng_name__in=line)
        if color:
            queryset = queryset.filter(Q(main_color__name__in=color))
        if category:
            queryset = queryset.filter(Q(categories__eng_name__in=category))
        if gender:
            queryset = queryset.filter(Q(gender__name__in=gender))

        """фильтры по продукт юнитам"""

        # if is_fast_shipping:
        #     queryset = queryset.filter(product_size_units__product_units__is_fast_shipping=(is_fast_shipping == "is_fast_shipping"))
        # if is_sale:
        #     queryset = queryset.filter(product_size_units__product_units__is_sale=(is_sale == "is_sale"))
        # if is_return:
        #     queryset = queryset.filter(product_size_units__product_units__is_sale=(is_sale == "is_return"))
        # if price_max:
        #     queryset = queryset.filter(Q(product_size_units__product_units__final_price__lte=price_max))
        # if price_min:
        #     queryset = queryset.filter(Q(product_size_units__product_units__final_price__gte=price_min))
        #
        # # color = self.request.query_params.getlist('line')
        # if size_us != [] and price_max and price_min:
        #     # вариант №0
        #     queryset = queryset.filter(
        #         Q(product_units__size__US__in=size_us) & Q(product_units__final_price__lte=price_max) & Q(
        #             product_units__final_price__gte=price_min)
        #     )
        #
        #     # надо затестить что быстрее это №1
        #     # queryset = queryset.filter(
        #     #     product_units__size__US=size_us,
        #     #     product_units__final_price__lte=price_max
        #     # )
        #
        #     # надо затестить что быстрее это №2
        #     # queryset = queryset.annotate(
        #     #     has_valid_size=Case(
        #     #         When(Q(product_units__size__US=size_us) & Q(product_units__final_price__lte=price_max), then=Value(True)),
        #     #         default=Value(False),
        #     #         output_field=BooleanField()
        #     #     )
        #     # ).filter(has_valid_size=True)
        # elif size_us and price_min:
        #     queryset = queryset.filter(
        #         Q(product_units__size__US__in=size_us) & Q(product_units__final_price__gte=price_min)
        #     )
        #
        # elif size_us and price_max:
        #     queryset = queryset.filter(
        #         Q(product_units__size__US__in=size_us) & Q(product_units__final_price__lte=price_max)
        #     )
        # elif size_us:
        #     queryset = queryset.filter(product_units__size__US__in=size_us)

        queryset = queryset.distinct()
        return queryset

# def filter_queryset(self, queryset):
#     queryset = super().filter_queryset(queryset)
#
#     size_us = self.request.query_params.getlist('size_us')
#     price_max = self.request.query_params.get('price_max')
#     price_min = self.request.query_params.get('price_min')
#     line = self.request.query_params.getlist('line')
#     color = self.request.query_params.getlist('color')
#     is_fast_shipping = self.request.query_params.get("is_fast_shipping")
#     is_sale = self.request.query_params.get("is_sale")
#     category = self.request.query_params.getlist("category")
#     gender = self.request.query_params.getlist("gender")
#
#     annotations = {}
#     filters = Q()
#
#     if line:
#         annotations['lines__full_eng_name'] = 'lines__full_eng_name'
#         filters &= Q(lines__full_eng_name__in=line)
#
#     if color:
#         annotations['main_color__name'] = 'main_color__name'
#         filters &= Q(main_color__name__in=color)
#
#     if category:
#         filters &= Q(categories__eng_name__in=category)
#
#     if gender:
#         filters &= Q(gender__name__in=gender)
#
#     if is_fast_shipping:
#         filters &= Q(is_fast_shipping=is_fast_shipping)
#
#     if is_sale:
#         filters &= Q(is_sale=is_sale)
#
#     if size_us and price_max and price_min:
#         filters &= Q(
#             product_units__size__US__in=size_us,
#             product_units__final_price__lte=price_max,
#             product_units__final_price__gte=price_min
#         )
#     elif size_us and price_min:
#         filters &= Q(
#             product_units__size__US__in=size_us,
#             product_units__final_price__gte=price_min
#         )
#     elif size_us and price_max:
#         filters &= Q(
#             product_units__size__US__in=size_us,
#             product_units__final_price__lte=price_max
#         )
#     elif size_us:
#         filters &= Q(product_units__size__US__in=size_us)
#
#     queryset = queryset.annotate(**annotations).filter(filters).distinct()
#     return queryset
