from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from products.models import Brand, Category, Collab, Collection, Color, DewuInfo, Line, Material, SGInfo
from users.models import User
from wishlist.models import Wishlist


class CollabSerializer(serializers.ModelSerializer):
    is_show = serializers.SerializerMethodField()

    class Meta:
        model = Collab
        fields = '__all__'

    def get_is_show(self, row):
        return True


class DewuInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DewuInfo
        fields = '__all__'


class SGInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SGInfo
        fields = '__all__'


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        return token


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'


class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        exclude = ['full_name']
        depth = 1


class LineMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        exclude = ['full_name', "parent_line"]
        depth = 1


class BrandSerializer(serializers.ModelSerializer):
    in_wishlist = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = '__all__'

    def get_in_wishlist(self, brand):
        user_id = self.context.get('user_id')
        if user_id is not None and user_id > 0:
            try:
                user = User.objects.get(id=user_id)
                fv_brands = user.favorite_brands.all()
                return brand in fv_brands
            except Wishlist.DoesNotExist:
                pass
        return False


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'
        depth = 2
