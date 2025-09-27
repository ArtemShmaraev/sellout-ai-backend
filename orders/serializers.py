from django.utils import timezone

from .models import ShoppingCart, Order, OrderUnit
from rest_framework import serializers
from products.serializers import ProductMainPageSerializer, ProductSerializer
from shipping.serializers import ProductUnitSerializer, AddressInfoSerializer
from promotions.serializers import PromoCodeSerializer
from users.models import User
from users.serializers import ForAnonUserSerializer, UserSerializer, UserOrderSerializer



class ShoppingCartSerializer(serializers.ModelSerializer):
    promo_code = PromoCodeSerializer()
    product_units = ProductUnitSerializer(many=True, read_only=True)
    user_bonus = serializers.SerializerMethodField()
    user = ForAnonUserSerializer()
    actual_platform_price = serializers.SerializerMethodField()

    class Meta:
        model = ShoppingCart
        fields = '__all__'

    def get_actual_platform_price(self, obj):
        time_threshold = timezone.now() - timezone.timedelta(hours=1)
        for unit in obj.product_units.all():
            if unit.product.last_upd < time_threshold:
                return False
        return True

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        unit_order = instance.unit_order
        ordered_product_units = sorted(representation['product_units'], key=lambda x: unit_order.index(x['id']))
        representation['product_units'] = ordered_product_units
        return representation


    def get_user_bonus(self, obj):
        user_id = self.context.get('user_id')
        if user_id is not None and user_id > 0:
            try:
                user = User.objects.get(id=user_id)
                bonus = 0
                if user.bonuses:
                    bonus = user.bonuses.total_amount
                return bonus
            except User.DoesNotExist:
                pass
        return False



class OrderUnitSerializer(serializers.ModelSerializer):
    product = ProductSerializer()


    class Meta:
        model = OrderUnit
        # fields = '__all__'
        exclude = ["size",]
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class OrderSerializer(serializers.ModelSerializer):
    user = UserOrderSerializer()
    address = AddressInfoSerializer()
    order_units = OrderUnitSerializer(many=True, read_only=True)
    formatted_date = serializers.DateTimeField(source='date', format='%d.%m.%y')

    class Meta:
        model = Order
        fields = '__all__'
        # exclude = ("user",)
        depth = 3