from .models import ProductUnit, AddressInfo, DeliveryType
from rest_framework import serializers
from products.serializers import ProductMainPageSerializer, ProductSerializer


class ProductUnitSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    class Meta:
        model = ProductUnit
        # fields = '__all__'
        exclude = ["size",]
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class AddressInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressInfo
        # fields = "__all__"
        exclude = ['other_info']


class DeliveryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryType
        fields = "__all__"
