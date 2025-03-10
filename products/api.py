from .models import Product
from rest_framework import viewsets, permissions, generics, pagination
from .serializers import ProductMainPageSerializer, ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .service import ProductFilter
from django.db.models import Q, F
from django.db.models import Q, Case, When, Value, BooleanField


class ProductPagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductMainPageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter
    pagination_class = ProductPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user_id'] = self.request.user.id
        return context

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        size_us = self.request.query_params.get('size_us')
        price_max = self.request.query_params.get('price_max')
        print(price_max)

        if size_us and price_max:
            print(111)
            # вариант №0
            queryset = queryset.filter(
                Q(product_units__size__US=size_us) & Q(product_units__final_price__lte=price_max)
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
            queryset = queryset.filter(product_units__size__US=size_us)
        elif price_max:
            queryset = queryset.filter(product_units__final_price__lte=price_max)

        return queryset.distinct()


