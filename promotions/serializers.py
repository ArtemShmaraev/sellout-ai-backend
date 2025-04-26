from .models import PromoCode
from rest_framework import serializers
from users.serializers import ForAnonUserSerializer


class PromoCodeSerializer(serializers.ModelSerializer):
    owner = ForAnonUserSerializer()


    class Meta:
        model = PromoCode
        fields = '__all__'

        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)

