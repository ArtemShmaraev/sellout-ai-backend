from .models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework import serializers



class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Добавить дополнительную информацию в полезную нагрузку токена
        token['username'] = user.username
        token['first_name'] = user.first_name
        token['last_name'] = user.last_name
        token['gender'] = str(user.gender)

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Добавить дополнительную информацию в ответ при успешной аутентификации
        data['username'] = self.user.username
        data['first_name'] = self.user.first_name
        data['last_name'] = self.user.last_name
        data['user_id'] = self.user.id
        data['gender'] = str(self.user.gender)

        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ("password",)
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class UserSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['preferred_shoes_size_row', "preferred_clothes_size_row", "shoes_size", "clothes_size", "height",
                  "weight"]
        # depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class ForAnonUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ("email", "verify_email", "first_name", "last_name", "phone")
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class UserOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("preferred_shoes_size_row", "preferred_clothes_size_row", "password", "address")
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)
