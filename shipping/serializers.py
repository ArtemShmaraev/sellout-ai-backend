from products.formula_price import formula_price
from users.models import User, UserStatus
from .models import ProductUnit, AddressInfo, DeliveryType
from rest_framework import serializers
from products.serializers import ProductMainPageSerializer, ProductSerializer


class ProductUnitSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    price = serializers.SerializerMethodField()

    class Meta:
        model = ProductUnit
        # fields = '__all__'
        exclude = ["size",]
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)

    def get_price(self, obj):
        if "user_id" in self.context:
            status = User.objects.get(id=self.context.get("user_id")).user_status
        else:
            status = UserStatus.objects.get(name="Amethyst")
        return formula_price(obj.product, obj, status)






class AddressInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressInfo
        # fields = "__all__"
        exclude = ['other_info']


class DeliveryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryType
        fields = "__all__"
