from .models import Wishlist, WishlistUnit
from rest_framework import serializers


class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'
        # глубина позволяет возвращать не только id бренда, но и его поля (name)


class WishlistUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = WishlistUnit
        fields = '__all__'
        depth = 1
        # глубина позволяет возвращать не только id бренда, но и его поля (name)

