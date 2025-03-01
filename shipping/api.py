from .models import ProductUnit
from rest_framework import viewsets, permissions, generics
from .serializers import ProductUnitSerializer


class ProductUnitViewSet(viewsets.ModelViewSet):
    queryset = ProductUnit.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductUnitSerializer





