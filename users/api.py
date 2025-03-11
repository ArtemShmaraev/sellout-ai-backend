from django_filters.rest_framework import DjangoFilterBackend

from .models import User
from rest_framework import viewsets, permissions, generics
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = UserSerializer





