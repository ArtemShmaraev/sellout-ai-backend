from .models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ("password", )
        depth = 1     # глубина позволяет возвращать не только id бренда, но и его поля (name)


