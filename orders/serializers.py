from .models import ShoppingCart, Order
from rest_framework import serializers
from products.serializers import ProductMainPageSerializer
from shipping.serializers import ProductUnitSerializer
from promotions.serializers import PromoCodeSerializer


class ShoppingCartSerializer(serializers.ModelSerializer):
    promo_code = PromoCodeSerializer()
    # product_unit = ProductUnitSerializer()
    # Вычисляемое поле "сумма покупки"
    # total_amount = serializers.SerializerMethodField()
    #
    # def get_total_amount(self, obj):
    #     # Выполняем вычисление суммы покупки
    #     # Здесь вы можете использовать любую логику, основанную на других полях модели
    #     # В примере суммируем значения полей "price" для каждого товара в корзине
    #     total = sum(unit.final_price for unit in obj.product_units.all())
    #     return total

    class Meta:
        model = ShoppingCart
        exclude = ['user', ]
        # fields = '__all__'
        depth = 3


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        # exclude = ("user",)
        depth = 2