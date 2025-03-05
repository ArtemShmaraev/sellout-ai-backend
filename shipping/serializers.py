from .models import ProductUnit, AddressInfo
from rest_framework import serializers


class ProductUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUnit
        fields = '__all__'
        depth = 2  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class AddressInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressInfo
        fields = "__all__"
