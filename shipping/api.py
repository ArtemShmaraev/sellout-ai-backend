from django_filters.rest_framework import DjangoFilterBackend

from .models import ProductUnit
from rest_framework import viewsets, permissions, generics
from .serializers import ProductUnitSerializer


class ProductUnitViewSet(viewsets.ModelViewSet):
    queryset = ProductUnit.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    serializer_class = ProductUnitSerializer
    filter_backends = [DjangoFilterBackend]





