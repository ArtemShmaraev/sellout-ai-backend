from .models import Product
from rest_framework import viewsets, permissions, generics, pagination
from .serializers import ProductMainPageSerializer, ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .service import ProductFilter


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


