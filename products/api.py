from .models import Product, Category, Line, Brand, Color
from rest_framework import viewsets, permissions, generics, pagination
from .serializers import ProductMainPageSerializer, ProductSerializer, CategorySerializer, LineSerializer, \
    BrandSerializer, ColorSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .service import ProductFilter
from rest_framework.filters import OrderingFilter
from shipping.models import ProductUnit
from django.db.models import ExpressionWrapper, F, Subquery, Min, OuterRef
from django.db.models import Q, Case, When, Value, BooleanField

from rest_framework.filters import OrderingFilter


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

    def get_paginated_response(self, data):
        response = super().get_paginated_response(data)

        min_price = 9999999999
        max_price = 0

        # Calculate min_price and max_price from the data
        for item in data:
            min_price_product_unit = item['min_price_product_unit']
            if min_price_product_unit is not None:
                if min_price is not None and min_price_product_unit < min_price:
                    min_price = min_price_product_unit
                if max_price is not None and min_price_product_unit > max_price:
                    max_price = min_price_product_unit

        response.data['min_price'] = min_price
        response.data['max_price'] = max_price

        return response


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductMainPageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = ProductPagination
    ordering_fields = ['release_date']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.request.user.id
        # Получите значения фильтров из запроса
        size_us = self.request.query_params.getlist('size_us')
        price_max = self.request.query_params.get('price_max')
        price_min = self.request.query_params.get('price_min')
        ordering = self.request.query_params.get('ordering')

        # Передайте значения фильтров в контекст сериализатора
        context['size_us'] = context['size_us'] = size_us if size_us else None
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
            if size_us is not None:

                if price_max is not None:
                    queryset = queryset.annotate(
                            min_price_product_unit=Subquery(
                                Product.objects.filter(pk=OuterRef('pk'))
                                .annotate(unit_min_price=Min('product_units__final_price', filter=(Q(product_units__size__US__in=size_us) & Q(product_units__final_price__lte=price_max))))
                                .values('unit_min_price')[:1]
                            )
                        )
                if price_min is not None:
                    queryset = queryset.annotate(
                        min_price_product_unit=Subquery(
                            Product.objects.filter(pk=OuterRef('pk'))
                            .annotate(unit_min_price=Min('product_units__final_price', filter=(Q(product_units__size__US__in=size_us) & Q(product_units__final_price__gte=price_min))))
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
        if size_us and price_max and price_min:
            # вариант №0
            queryset = queryset.filter(
                Q(product_units__size__US__in=size_us) & Q(product_units__final_price__lte=price_max) & Q(product_units__final_price__gte=price_min)
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
        elif size_us and price_min:
            queryset = queryset.filter(
                Q(product_units__size__US__in=size_us) & Q(product_units__final_price__gte=price_min)
            )

        elif size_us and price_max:
            queryset = queryset.filter(
                Q(product_units__size__US__in=size_us) & Q(product_units__final_price__lte=price_max)
            )
        elif size_us:
            queryset = queryset.filter(product_units__size__US__in=size_us)

        queryset = queryset.distinct()
        return queryset
