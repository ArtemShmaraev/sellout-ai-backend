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
    formatted_happy_birthday_date = serializers.DateTimeField(source='happy_birthday', format='%d.%m.%y')
    class Meta:
        model = User
        # fields = '__all__'
        exclude = ("password", "wait_list")
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
        fields = ("email", "verify_email", "first_name", "last_name", "phone_number")
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class UserOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("preferred_shoes_size_row", "preferred_clothes_size_row", "password", "address", "ref_user", "wait_list", "date_joined",
                   "phone_number", "is_mailing_list", "happy_birthday", "last_viewed_products", "preferred_size_grid", "referral_promo", "verify_email", "is_active", "is_superuser", "last_login", "shoes_size", "clothes_size", "user_permissions",
                   "my_groups", "favorite_brands", "all_purchase_amount", "personal_discount_percentage", "height", "weight", "bonuses", "groups")
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)
