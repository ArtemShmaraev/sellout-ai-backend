from wishlist.models import Wishlist, WishlistUnit
from .models import Product, Category, Line, Brand, Color
from rest_framework import serializers
from shipping.models import ProductUnit
from django.db.models import Min


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'
        # depth = 2  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = '__all__'
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = '__all__'
        # depth = 2  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        # depth = 3  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        depth = 2  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class ProductUnitPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUnit
        fields = ['final_price']


class ProductMainPageSerializer(serializers.ModelSerializer):
    in_wishlist = serializers.SerializerMethodField()
    min_price_product_unit = serializers.SerializerMethodField()  # Сериализатор для связанных ProductUnit
    main_line = serializers.SerializerMethodField()
    is_sale = serializers.SerializerMethodField()
    is_fast_shipping = serializers.SerializerMethodField()
    is_return = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"
        depth = 2

    def get_is_return(self, obj):
        return obj.product_units.filter(is_return=True).exists()

    def get_is_fast_shipping(self, obj):
        return obj.product_units.filter(is_fast_shipping=True).exists()

    def get_is_sale(self, obj):
        return obj.product_units.filter(is_sale=True).exists()

    def get_main_line(self, obj):
        lines = obj.lines.exclude(name__icontains='Все')
        if lines:
            main_line = lines.order_by('-id').first()
            return main_line.full_name
        return None

    def get_min_price_product_unit(self, obj):
        size_us = self.context.get('size_us')
        price_max = self.context.get('price_max')
        price_min = self.context.get('price_min')

        # Проверьте, соответствуют ли значения фильтров product_unit
        if size_us and price_max and price_min:
            # Верните поле final_price
            return obj.product_units.filter(size__US__in=size_us, final_price__lte=price_max,
                                            final_price__gte=price_min).aggregate(min_price=Min('final_price'))[
                'min_price']
        elif size_us and price_max:
            return obj.product_units.filter(size__US__in=size_us, final_price__lte=price_max).aggregate(
                min_price=Min('final_price'))['min_price']

        elif size_us and price_min:
            return obj.product_units.filter(size__US__in=size_us, final_price__gte=price_min).aggregate(
                min_price=Min('final_price'))['min_price']

        elif size_us:
            return obj.product_units.filter(size__US__in=size_us).aggregate(
                min_price=Min('final_price'))['min_price']
        else:
            return obj.min_price

    def get_in_wishlist(self, product):
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
