from .models import ProductUnit, AddressInfo, DeliveryType
from rest_framework import serializers
from products.serializers import ProductMainPageSerializer


class ProductUnitSerializer(serializers.ModelSerializer):
    product = ProductMainPageSerializer()
    class Meta:
        model = ProductUnit
        # fields = '__all__'
        exclude = ["size",]
        depth = 2  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class AddressInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressInfo
        # fields = "__all__"
        exclude = ['other_info']


class DeliveryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryType
        fields = "__all__"
