from django_filters.rest_framework import DjangoFilterBackend

from .models import User
from rest_framework import viewsets, permissions, generics
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    serializer_class = UserSerializer

    # def list(self, request, *args, **kwargs):
    #     # Получение текущего пользователя, совершившего запрос
    #     current_user = self.request.user
    #
    #     # Дальнейшая логика работы с текущим пользователем, например, фильтрация запроса
    #     queryset = self.filter_queryset(self.get_queryset())
    #
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)





