from .models import ShoppingCart, Order
from rest_framework import serializers
from products.serializers import ProductMainPageSerializer
from shipping.serializers import ProductUnitSerializer, AddressInfoSerializer
from promotions.serializers import PromoCodeSerializer
from users.models import User
from users.serializers import ForAnonUserSerializer, UserSerializer, UserOrderSerializer


class ShoppingCartSerializer(serializers.ModelSerializer):
    promo_code = PromoCodeSerializer()
    product_units = ProductUnitSerializer(many=True, read_only=True)
    bonus = serializers.SerializerMethodField()
    # Вычисляемое поле "сумма покупки"
    # total_amount = serializers.SerializerMethodField()
    #
    # def get_total_amount(self, obj):
    #     # Выполняем вычисление суммы покупки
    #     # Здесь вы можете использовать любую логику, основанную на других полях модели
    #     # В примере суммируем значения полей "price" для каждого товара в корзине
    #     total = sum(unit.final_price for unit in obj.product_units.all())
    #     return total


    def get_bonus(self, obj):
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

    class Meta:
        model = ShoppingCart
        exclude = ['user', ]
        # fields = '__all__'
        depth = 3


class OrderSerializer(serializers.ModelSerializer):
    user = UserOrderSerializer()
    address = AddressInfoSerializer()
    product_units = ProductUnitSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ''
        # exclude = ("user",)
        depth = 3