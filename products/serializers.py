from wishlist.models import Wishlist, WishlistUnit
from .models import Product
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        depth = 2  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class ProductMainPageSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"
        depth = 2

    def get_is_favorite(self, product):
        user_id = self.context.get('user_id')
        if user_id is not None and user_id > 0:
            try:
                wishlist = Wishlist.objects.get(user_id=user_id)
                data = WishlistUnit.objects.get(wishlist=wishlist, product=product)
                return True
            except WishlistUnit.DoesNotExist:
                pass
        return False

    # def get_is_favorite(self, product_id, wishlist):
    #     if self.context.get('user_id') > 0:
    #         data = WishlistUnit.objects.filter(wishlist=wishlist, product_id=product_id)
    #         return len(data) > 0
    #     return False
    #
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     wishlist = Wishlist.objects.get(user_id=self.context.get('user_id'))
    #     data['is_favorite'] = self.get_is_favorite(data['id'], wishlist)
    #     return data


