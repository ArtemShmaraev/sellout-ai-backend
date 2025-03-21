import django_filters
from rest_framework.permissions import AllowAny

from products.models import Product


class CharFilterInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class ProductFilter(django_filters.FilterSet):
    category = CharFilterInFilter(field_name='categories__eng_name', lookup_expr='in')
    brand = CharFilterInFilter(field_name='brands__name', lookup_expr='in')
    gender = django_filters.CharFilter(field_name='gender__name')
    color = django_filters.CharFilter(field_name='colors__name')
    line = CharFilterInFilter(field_name='lines__name', lookup_expr='in')
    # price = django_filters.RangeFilter(field_name="product_units__final_price")
    # price_max = django_filters.NumberFilter()
    # size_us = CharFilterInFilter(field_name='product_units__size__US', lookup_expr='in')

    class Meta:
        model = Product
        fields = ['categories', 'brands', 'gender', 'colors', 'lines']

    def get_queryset(self):
        # print(price_max)
        queryset = super().get_queryset()
        queryset = queryset.values('id').distinct()
        return queryset.distinct()
        # return queryset.filter(**self.filters)



        # # return queryset.filter(**self.filters).distinct()
        # price_min = self.request.query_params.get('price_min')
        # price_max = self.request.query_params.get('price_max')
        # size = self.request.query_params.get('size')
        #
        # if price_min and size:
        #     queryset = queryset.filter(
        #         product_units__size_US=size,
        #         product_units__price__gte=price_min
        #     ).distinct()
        #
        # elif price_max and size:
        #
        #     queryset = queryset.filter(
        #         product_units__size_US=size,
        #         product_units__price__lte=price_max
        #     ).distinct()
        #
        # return queryset

