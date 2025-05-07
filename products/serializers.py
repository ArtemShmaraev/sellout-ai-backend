from users.models import User
from wishlist.models import Wishlist
from products.models import Product, Category, Line, Brand, Color, Collection, DewuInfo, SizeTable, SizeRow, \
    SizeTranslationRows, Collab
from rest_framework import serializers
from shipping.models import ProductUnit
from django.db.models import Min, Q

# from .views import build_line_tree

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class SizeRowSerializer(serializers.ModelSerializer):
    is_main = serializers.SerializerMethodField()

    class Meta:
        model = SizeRow
        fields = '__all__'

    def get_is_main(self, row):
        user = self.context.get('user')
        if user is not None:
            return user.preferred_shoes_size_row == row or user.preferred_clothes_size_row == row
        return row == row.size_tables.first().default_row


class SizeTableSerializer(serializers.ModelSerializer):
    size_rows = SizeRowSerializer(many=True)

    class Meta:
        model = SizeTable
        exclude = ['default_row', ]
        depth = 2


class SizeTranslationRowsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeTranslationRows
        fields = '__all__'


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


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Добавить дополнительную информацию в полезную нагрузку токена
        token['username'] = user.username

        return token


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'
        # depth = 2 # глубина позволяет возвращать не только id бренда, но и его поля (name)


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        # fields = '__all__'
        exclude = ['full_name']
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class BrandSerializer(serializers.ModelSerializer):
    in_wishlist = serializers.SerializerMethodField()

    class Meta:
        model = Brand
        fields = '__all__'
        # depth = 2 # глубина позволяет возвращать не только id бренда, но и его поля (name)

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
        # depth = 3 # глубина позволяет возвращать не только id бренда, но и его поля (name)


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = '__all__'
        depth = 2  # глубина позволяет возвращать не только id бренда, но и его поля (name)


class ProductUnitPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUnit
        fields = ['final_price']


class ProductSerializer(serializers.ModelSerializer):
    in_wishlist = serializers.SerializerMethodField()
    min_price_product_unit = serializers.SerializerMethodField()  # Сериализатор для связанных ProductUnit

    # is_sale = serializers.SerializerMethodField()
    # is_fast_shipping = serializers.SerializerMethodField()
    # is_return = serializers.SerializerMethodField()
    list_lines = serializers.SerializerMethodField()

    class Meta:
        model = Product
        exclude = ["platform_info", "sizes_prices", "russian_name", "dewu_info", "spu_id"]
        depth = 2

    def get_list_lines(self, obj):
        list_lines = self.context.get('list_lines')
        s = []

        def get_line_parents(line):
            parents = [line]
            current_line = line
            while current_line.parent_line is not None:
                current_line = current_line.parent_line
                parents.append(current_line)
            return parents[::-1]

        if list_lines:
            s = LineSerializer(get_line_parents(obj.main_line), many=True).data
        return s

    # def get_is_return(self, obj):
    #     return obj.product_units.filter(is_return=True).exists()
    #
    # def get_is_fast_shipping(self, obj):
    #     return obj.product_units.filter(is_fast_shipping=True).exists()
    #
    # def get_is_sale(self, obj):
    #     return obj.product_units.filter(is_sale=True).exists()

    def get_min_price_product_unit(self, obj):
        size = self.context.get('size')
        price_max = self.context.get('price_max')
        price_min = self.context.get('price_min')

        # Проверьте, соответствуют ли значения фильтров product_unit
        filters = Q(availability=True)

        if size:
            filters &= Q(size__in=size)

        if price_max:
            filters &= Q(final_price__lte=price_max)

        if price_min:
            filters &= Q(final_price__gte=price_min)

        if filters:
            return obj.product_units.filter(filters).aggregate(min_price=Min('final_price'))['min_price']
        else:
            return obj.min_price

    def get_in_wishlist(self, product):
        # user_id = self.context.get('user_id')
        wishlist = self.context.get('wishlist')
        if wishlist:
            return product in wishlist.products.all()
        return False


class ProductMainPageSerializer(serializers.ModelSerializer):
    in_wishlist = serializers.SerializerMethodField()
    min_price_product_unit = serializers.SerializerMethodField()  # Сериализатор для связанных ProductUnit

    # is_sale = serializers.SerializerMethodField()
    # is_fast_shipping = serializers.SerializerMethodField()
    # is_return = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "in_wishlist", "min_price_product_unit", "model", "colorway", "slug", "is_collab",
                  "collab", "brands", "bucket_link", "rel_num"]
        # exclude = ["platform_info", "sizes_prices", "last_upd", "add_date", "size_table", 'categories',
        #            "size_table_platform", "russian_name", "main_color", "description", "exact_date", "approximate_date",
        #            "fit", "rel_num", "dewu_info", "main_line", "manufacturer_sku", "lines", "colors", "gender",
        #            "spu_id", "has_many_sizes", "has_many_colors", "has_many_configurations", "is_custom",
        #            "recommended_gender", "designer_color", "available_flag", "tags", "id", "min_price"]
        depth = 2

    # def get_is_return(self, obj):
    #     return obj.product_units.filter(is_return=True).exists()
    #
    # def get_is_fast_shipping(self, obj):
    #     return obj.product_units.filter(is_fast_shipping=True).exists()
    #
    # def get_is_sale(self, obj):
    #     return obj.product_units.filter(is_sale=True).exists()

    def get_min_price_product_unit(self, obj):
        size = self.context.get('size')
        price_max = self.context.get('price_max')
        price_min = self.context.get('price_min')

        # Проверьте, соответствуют ли значения фильтров product_unit
        filters = Q(availability=True)

        if size:
            filters &= Q(size__in=size)

        if price_max:
            filters &= Q(final_price__lte=price_max)

        if price_min:
            filters &= Q(final_price__gte=price_min)

        if filters:
            return obj.product_units.filter(filters).aggregate(min_price=Min('final_price'))['min_price']
        else:
            return obj.min_price

    def get_in_wishlist(self, product):
        # user_id = self.context.get('user_id')
        wishlist = self.context.get('wishlist')
        if wishlist:
            return product in wishlist.products.all()
        return False
        # if user_id is not None and user_id > 0:
        #     try:
        #         wishlist = Wishlist.objects.get(user_id=user_id)
        #         return product in wishlist.products.all()
        #     except Wishlist.DoesNotExist:
        #         pass
        # return False
