from products.serializers import ProductMainPageSerializer
from .models import Wishlist
from rest_framework import serializers


class WishlistSerializer(serializers.ModelSerializer):
    product = ProductMainPageSerializer(many=True)
    class Meta:
        model = Wishlist
        # fields = '__all__'
        exclude = ['user', ]
        depth = 2
        # глубина позволяет возвращать не только id бренда, но и его поля (name)


# class WishlistUnitSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WishlistUnit
#         fields = '__all__'
#         depth = 1
        # глубина позволяет возвращать не только id бренда, но и его поля (name)

