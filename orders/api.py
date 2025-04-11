from django_filters.rest_framework import DjangoFilterBackend

from .models import ShoppingCart
from rest_framework import viewsets, permissions, generics
from .serializers import ShoppingCartSerializer


class ShoppingCartViewSet(viewsets.ModelViewSet):
    queryset = ShoppingCart.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    serializer_class = ShoppingCartSerializer
    filter_backends = [DjangoFilterBackend]


