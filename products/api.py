from .models import Product, Category, Line, Brand, Color
from rest_framework import viewsets, permissions, generics, pagination
from .serializers import ProductMainPageSerializer, ProductSerializer, CategorySerializer, LineSerializer, \
    BrandSerializer, ColorSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .service import ProductFilter
from rest_framework.filters import OrderingFilter
from django.db.models import Q, F
from django.db.models import Q, Case, When, Value, BooleanField


class LinesViewSet(viewsets.ModelViewSet):
    queryset = Line.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = LineSerializer


class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.filter(is_main_color=True)
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = ColorSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = CategorySerializer


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = BrandSerializer


class ProductPagination(pagination.PageNumberPagination):
    page_size = 60
    page_size_query_param = 'page_size'
    max_page_size = 120


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductMainPageSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = ProductPagination
    ordering_fields = ['model', 'min_price']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.request.user.id
        # Получите значения фильтров из запроса
        size_us = self.request.query_params.getlist('size_us')
        price_max = self.request.query_params.get('price_max')
        price_min = self.request.query_params.get('price_min')

        # Передайте значения фильтров в контекст сериализатора
        context['size_us'] = context['size_us'] = size_us if size_us else None
        context['price_max'] = price_max if price_max else None
        context['price_min'] = price_min if price_min else None
        return context

    def get_queryset(self):
        queryset = super().get_queryset()

        # Применение сортировки к queryset
        ordering = self.request.query_params.get('ordering')
        if ordering in self.ordering_fields:
            queryset = queryset.order_by(ordering)

        return queryset

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        size_us = self.request.query_params.getlist('size_us')
        price_max = self.request.query_params.get('price_max')
        price_min = self.request.query_params.get('price_min')
        if size_us and price_max:
            # вариант №0
            queryset = queryset.filter(
                Q(product_units__size__US__in=size_us) & Q(product_units__final_price__lte=price_max)
            )

            # надо затестить что быстрее это №1
            # queryset = queryset.filter(
            #     product_units__size__US=size_us,
            #     product_units__final_price__lte=price_max
            # )

            # надо затестить что быстрее это №2
            # queryset = queryset.annotate(
            #     has_valid_size=Case(
            #         When(Q(product_units__size__US=size_us) & Q(product_units__final_price__lte=price_max), then=Value(True)),
            #         default=Value(False),
            #         output_field=BooleanField()
            #     )
            # ).filter(has_valid_size=True)
        elif size_us:
            queryset = queryset.filter(product_units__size__US__in=size_us)
        elif price_max:
            queryset = queryset.filter(min_price__lte=price_max)

        if size_us and price_min:
            queryset = queryset.filter(
                Q(product_units__size__US__in=size_us) & Q(product_units__final_price__gte=price_min)
            )
        elif price_min:
            queryset = queryset.filter(min_price__gte=price_min)
        queryset = queryset.distinct()
        sort_param = self.request.query_params.get('sort')

        # Примените сортировку к queryset
        if sort_param:
            queryset = queryset.order_by(sort_param)

        return queryset
