

from wishlist.models import Wishlist
from products.models import Product, Category, Line, Brand, Color, Collection, DewuInfo, SizeTable, SizeRow, \
    SizeTranslationRows, Collab, SGInfo, Material
from rest_framework import serializers
from shipping.models import ProductUnit
from django.db.models import Min, Q, Max, Count
from .formula_price import formula_price
# from .views import build_line_tree
from users.models import User, UserStatus

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


class SGInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SGInfo
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

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = '__all__'
        # depth = 2 # глубина позволяет возвращать не только id бренда, но и его поля (name)


class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        # fields = '__all__'
        exclude = ['full_name']
        depth = 1  # глубина позволяет возвращать не только id бренда, но и его поля (name)



class LineMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        # fields = '__all__'
        exclude = ['full_name', "parent_line"]
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
    # is_fast_shipping = serializers.SerializerMethodField()
    # is_return = serializers.SerializerMethodField()
    list_lines = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        # fields = "__all__"
        exclude = ["platform_info", "sizes_prices", "russian_name", "spu_id", "size_table", "add_date", "last_upd", "lines"]
        depth = 2


    def get_price(self, obj):
        wl = self.context.get('wishlist', "")
        if wl and not wl.user.user_status.base:
            user_status = wl.user.user_status
            unit = \
                    obj.product_units.filter(final_price=obj.min_price).order_by(
                        "approximate_price_with_delivery_in_rub")[0]

            return formula_price(obj, unit, user_status)

        else:
            return {"final_price": obj.min_price, "start_price": obj.min_price_without_sale}


    def get_list_lines(self, obj):
        list_lines = self.context.get('list_lines')
        s = []

        def get_line_parents(line):
            parents = [{"name": line.view_name, "query": f"line={line.full_eng_name}"}]
            current_line = line
            while current_line.parent_line is not None:
                current_line = current_line.parent_line
                parents.append({"name": current_line.view_name, "query": f"line={current_line.full_eng_name}"})
            return parents[::-1]

        def get_cat_parents(cat, line):
            parents = []
            if "Вс" not in cat.name:
                parents.append({"name": f"{cat.name} {line.view_name}", "query": f"line={line.full_eng_name}&category={cat.eng_name}"})
            current_cat = cat
            while current_cat.parent_category is not None:
                current_cat = current_cat.parent_category
                if "Вс" not in current_cat.name:
                    parents.append({"name": f"{current_cat.name} {line.view_name}", "query": f"line={line.full_eng_name}&category={current_cat.eng_name}"})
            return parents[::-1]

        if list_lines:
            s = []
            if obj.main_line is not None:
                s = get_line_parents(obj.main_line)
                if len(s) == 1:
                    s.extend(get_cat_parents(obj.categories.all().order_by("-id").first(), obj.main_line))
        return s

    # def get_is_return(self, obj):
    #     return obj.product_units.filter(is_return=True).exists()
    #
    # def get_is_fast_shipping(self, obj):
    #     return obj.product_units.filter(is_fast_shipping=True).exists()
    #


    def get_in_wishlist(self, product):
        # user_id = self.context.get('user_id')
        wishlist = self.context.get('wishlist')
        if wishlist:
            return product in wishlist.products.all()
        return False



def update_product_serializer(data, context):
    def get_min_price_product_unit(obj, context):
        size = context.get('size')

        # Проверьте, соответствуют ли значения фильтров product_unit
        filters = Q(availability=True)

        if size:
            filters &= (Q(size__in=size) | Q(size__is_one_size=True))

        if filters:
            return obj.product_units.filter(filters).aggregate(min_price=Min('final_price'))['min_price']
        else:
            return obj.min_price

    def get_in_wishlist(product_id, context):
        wishlist = context.get('wishlist')
        if wishlist:
            return wishlist.products.filter(id=product_id).exist()
        return False

    wl = context.get('wishlist')
    wl_set = set()
    if wl:
        wl_set.update(wl.products.values_list("id", flat=True))
    for product in data:
        product['in_wishlist'] = product['id'] in wl_set
        if "size" in context:
            pr = Product.objects.get(id=product['id'])
            product["min_price_product_unit"] = get_min_price_product_unit(pr, context)
        else:
            product["min_price_product_unit"] = product['min_price']
    return data

class ProductMainPageSerializer(serializers.ModelSerializer):
    in_wishlist = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    # is_sale = serializers.SerializerMethodField()
    # is_fast_shipping = serializers.SerializerMethodField()
    # is_return = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", 'in_wishlist', "price", "model", "colorway", "slug", "is_collab","collab", "brands", "bucket_link", "is_sale"]
        # exclude = ["platform_info", "sizes_prices", "last_upd", "add_date", "size_table", 'categories',
        #            "size_table_platform", "russian_name", "main_color", "description", "exact_date", "approximate_date",
        #            "fit", "rel_num", "dewu_info", "main_line", "manufacturer_sku", "lines", "colors", "gender",
        #            "spu_id", "has_many_sizes", "has_many_colors", "has_many_configurations", "is_custom",
        #            "recommended_gender", "designer_color", "available_flag", "tags", "id", "min_price"]
        depth = 2

    def get_price(self, obj):
        size = self.context.get('size')
        from .tools import update_price
        update_price(obj)

        # Проверьте, соответствуют ли значения фильтров product_unit
        filters = Q()

        if size:
            filters &= (Q(size__in=size) | Q(size__is_one_size=True))

        wl = self.context.get('wishlist')
        if wl and not wl.user.user_status.base:
            user_status = wl.user.user_status
            if filters:
                min_final_price = obj.product_units.filter(filters).aggregate(min_price=Min('final_price'))['min_price']
                unit = \
                obj.product_units.filter(final_price=min_final_price).order_by(
                    "approximate_price_with_delivery_in_rub")[0]
            else:
                unit = \
                    obj.product_units.filter(final_price=obj.min_price).order_by(
                        "approximate_price_with_delivery_in_rub")[0]
            return formula_price(obj, unit, user_status)

        else:
            if filters:
                min_final_price = obj.product_units.filter(filters).aggregate(min_price=Min('final_price'))['min_price']
                filters &= Q(final_price=min_final_price)
                corresponding_start_price = obj.product_units.filter(filters).aggregate(max_price=Max('start_price'))['max_price']

                return {"final_price": min_final_price, "start_price": corresponding_start_price}

            else:
                unit = \
                    obj.product_units.filter(final_price=obj.min_price).order_by(
                        "approximate_price_with_delivery_in_rub")[0]
                return formula_price(obj, unit, UserStatus.objects.get(name="Ruby"))
                # return {"final_price": obj.min_price, "start_price": obj.min_price_without_sale}

        #



    def get_in_wishlist(self, product):
        # user_id = self.context.get('user_id')
        wishlist = self.context.get('wishlist')
        if wishlist:
            return product in wishlist.products.all()
        return False
