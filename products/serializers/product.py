import concurrent.futures

from django.db.models import Min, Q
from django.utils import timezone
from rest_framework import serializers

from products.formula_price import formula_price
from products.models import Photo, Product
from shipping.models import ProductUnit


def serialize_data_chunk(data_chunk, context, serializer_class):
    serializer = serializer_class(data_chunk, many=True, context=context)
    return serializer.data


def serialize_in_threads(queryset, context, serializer_class):
    num_threads = 6
    chunk_size = len(queryset) // num_threads

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []
        serialized_data = []

        for i in range(num_threads):
            start_index = i * chunk_size
            end_index = start_index + chunk_size if i < num_threads - 1 else len(queryset)
            data_chunk = queryset[start_index:end_index]
            future = executor.submit(serialize_data_chunk, data_chunk, context, serializer_class)
            futures.append(future)

        for future in concurrent.futures.as_completed(futures):
            serialized_chunk = future.result()
            serialized_data.extend(serialized_chunk)
    return serialized_data


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = "__all__"


class ProductUnitPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductUnit
        fields = ['final_price']


class ProductAdminSerializer(serializers.ModelSerializer):
    list_lines = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        exclude = ["available_sizes", "size_table_platform"]
        depth = 2

    def get_price(self, obj):
        try:
            from products.tools import update_price
            update_price(obj)
            wl = self.context.get('wishlist', "")
            if wl and wl.user.user_status.name != "Amethyst":
                user_status = wl.user.user_status
                unit = obj.product_units.filter(availability=True).order_by("final_price", "-start_price").first()
                return formula_price(obj, unit, user_status)
        except:  # noqa: E722
            obj.actual_price = False
            obj.save()
            obj.update_price()
        return {"final_price": obj.min_price, "start_price": obj.min_price_without_sale, "bonus": obj.max_bonus,
                "max_bonus": obj.max_bonus}

    def get_list_lines(self, obj):
        list_lines = self.context.get('list_lines')
        s = []

        def get_line_parents(line):
            parents = [{"name": line.view_name, "query": f"line={line.full_eng_name.rstrip('_')}"}]
            current_line = line
            while current_line.parent_line is not None:
                current_line = current_line.parent_line
                parents.append(
                    {"name": current_line.view_name, "query": f"line={current_line.full_eng_name.rstrip('_')}"})
            return parents[::-1]

        def get_cat_parents(cat, line):
            parents = []
            if cat is not None:
                if "Вс" not in cat.name:
                    parents.append({"name": f"{cat.name} {line.view_name}",
                                    "query": f"line={line.full_eng_name.rstrip('_')}&category={cat.eng_name.rstrip('_')}"})
                current_cat = cat
                while current_cat.parent_category is not None:
                    current_cat = current_cat.parent_category
                    if "Вс" not in current_cat.name:
                        parents.append({"name": f"{current_cat.name} {line.view_name}",
                                        "query": f"line={line.full_eng_name.rstrip('_')}&category={current_cat.eng_name.rstrip('_')}"})
                return parents[::-1]
            return []

        if list_lines:
            s = []
            if obj.main_line is not None:
                s = get_line_parents(obj.main_line)
                if len(s) == 1:
                    s.extend(get_cat_parents(obj.categories.all().order_by("-id").first(), obj.main_line))
        return s


class ProductSerializer(serializers.ModelSerializer):
    in_wishlist = serializers.SerializerMethodField()
    list_lines = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    actual_platform_price = serializers.SerializerMethodField()
    bucket_link = serializers.SerializerMethodField()

    class Meta:
        model = Product
        exclude = [
            "likes_month", "likes_week", "is_new", "extra_score", "up_score", "platform_info", "sizes_prices",
            "russian_name", "size_table", "add_date", "lines", "level2_category_id", "category_id", "category_name",
            "level1_category_id", "min_price", "min_price_without_sale", "max_bonus", "fit", "spu_id", "property_id",
            "is_custom", "max_profit", "similar_product", "rel_num", "another_configuration", "in_sg", "tags",
            "gender", "materials", "colors", "black_bucket_link", "categories", "recommended_gender", "main_color",
            "content_sources", "last_parse_price", "one_update", "available_sizes", "last_upd", "normalize_rel_num",
        ]
        depth = 2

    def get_bucket_link(self, obj):
        photos = obj.bucket_link.order_by('id')
        photo_serializer = PhotoSerializer(photos, many=True, context=self.context)
        return photo_serializer.data

    def get_actual_platform_price(self, obj):
        time_threshold = timezone.now() - timezone.timedelta(hours=1)
        return obj.last_upd >= time_threshold or 'wishlist' not in self.context

    def get_price(self, obj):
        try:
            obj.update_price()
            wl = self.context.get('wishlist', "")
            if wl and wl.user.user_status.name != "Amethyst":
                user_status = wl.user.user_status
                unit = obj.product_units.filter(availability=True).order_by("final_price", "-start_price").first()
                return formula_price(obj, unit, user_status)
        except:  # noqa: E722
            obj.actual_price = False
            obj.save()
            obj.update_price()
        return {"final_price": obj.min_price, "start_price": obj.min_price_without_sale, "bonus": obj.max_bonus,
                "max_bonus": obj.max_bonus}

    def get_list_lines(self, obj):
        list_lines = self.context.get('list_lines')
        s = []

        def get_line_parents(line):
            parents = [{"name": line.view_name, "query": f"line={line.full_eng_name.rstrip('_')}"}]
            current_line = line
            while current_line.parent_line is not None:
                current_line = current_line.parent_line
                parents.append(
                    {"name": current_line.view_name, "query": f"line={current_line.full_eng_name.rstrip('_')}"})
            return parents[::-1]

        def get_cat_parents(cat, line):
            parents = []
            if cat is not None:
                if "Вс" not in cat.name:
                    parents.append({"name": f"{cat.name} {line.view_name}",
                                    "query": f"line={line.full_eng_name.rstrip('_')}&category={cat.eng_name.rstrip('_')}"})
                current_cat = cat
                while current_cat.parent_category is not None:
                    current_cat = current_cat.parent_category
                    if "Вс" not in current_cat.name:
                        parents.append({"name": f"{current_cat.name} {line.view_name}",
                                        "query": f"line={line.full_eng_name.rstrip('_')}&category={current_cat.eng_name.rstrip('_')}"})
                return parents[::-1]
            return []

        if list_lines:
            s = []
            if obj.main_line is not None:
                s = get_line_parents(obj.main_line)
                if len(s) == 1:
                    s.extend(get_cat_parents(obj.categories.all().order_by("-id").first(), obj.main_line))
                if len(s) == 2:
                    s1 = s[1]
                    cat = obj.categories.all().order_by("-id").first()
                    line = obj.lines.all().exclude(name__icontains='Все').exclude(
                        name__icontains='Другие').order_by("id").first()
                    s[1] = {"name": f"{cat.name} {line.view_name}",
                            "query": f"line={line.full_eng_name.rstrip('_')}&category={cat.eng_name.rstrip('_')}"}
                    s.append(s1)
        return s

    def get_in_wishlist(self, product):
        wishlist = self.context.get('wishlist')
        if wishlist:
            return product in wishlist.products.all()
        return False


def update_product_serializer(data, context):
    def get_min_price_product_unit(obj, context):
        size = context.get('size')
        filters = Q(availability=True)

        if size:
            filters &= (Q(size__in=size) | Q(size__is_one_size=True))

        if filters:
            return obj.product_units.filter(filters).aggregate(min_price=Min('final_price'))['min_price']
        else:
            return obj.min_price

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


class ProductSlugAndPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "slug", "bucket_link"]
        depth = 2


class ProductMainPageSerializer(serializers.ModelSerializer):
    in_wishlist = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    bucket_link = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", 'in_wishlist', "price", "model", "colorway", "slug", "is_collab", "collab", "brands",
                  "bucket_link", "is_sale", "available_sizes"]
        depth = 2

    def get_bucket_link(self, obj):
        photos = obj.bucket_link.order_by('id')
        photo_serializer = PhotoSerializer(photos, many=True, context=self.context)
        return photo_serializer.data

    def get_price(self, obj):
        try:
            size = self.context.get('size')
            filters = Q()

            if size:
                filters &= (Q(size__in=size) & Q(availability=True))

            wl = self.context.get('wishlist')
            if wl and not wl.user.user_status.base:
                user_status = wl.user.user_status
                if filters:
                    unit = obj.product_units.filter(filters).order_by("final_price", "-start_price").first()
                else:
                    unit = obj.product_units.filter(availability=True).order_by("final_price", "-start_price").first()
                if unit is None:
                    return {"final_price": obj.min_price, "start_price": obj.min_price_without_sale}
                return formula_price(obj, unit, user_status)

            else:
                if filters:
                    unit = obj.product_units.filter(filters).order_by("final_price", "-start_price").first()
                    min_final_price = unit.final_price
                    corresponding_start_price = unit.start_price
                    return {"final_price": min_final_price, "start_price": corresponding_start_price}

                else:
                    return {"start_price": obj.min_price_without_sale, "final_price": obj.min_price}
        except:  # noqa: E722
            obj.actual_price = False
            obj.save()
            obj.update_price()
        return {"final_price": obj.min_price, "start_price": obj.min_price_without_sale}

    def get_in_wishlist(self, product):
        wishlist = self.context.get('wishlist')
        if wishlist:
            return product in wishlist.products.all()
        return False
