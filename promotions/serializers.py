from .models import PromoCode
from rest_framework import serializers


class PromoCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoCode
        fields = '__all__'
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)

