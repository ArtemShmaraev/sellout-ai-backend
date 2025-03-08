import django_filters
from rest_framework.permissions import AllowAny

from products.models import Product


class CharFilterInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    pass


class ProductFilter(django_filters.FilterSet):
    categories = CharFilterInFilter(field_name='categories__name', lookup_expr='in')
    brands = CharFilterInFilter(field_name='brands__name', lookup_expr='in')
    gender = django_filters.CharFilter(field_name='gender__name')
    colors = django_filters.CharFilter(field_name='colors__name')
    min_price = django_filters.RangeFilter()
    lines = CharFilterInFilter(field_name='lines__name', lookup_expr='in')

    class Meta:
        model = Product
        fields = ['categories', 'brands', 'gender', 'colors', 'min_price', 'lines']

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(**self.filters)
