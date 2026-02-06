import math
import random

from django.db import models
from django.utils import timezone
from datetime import date
from django_slugify_processor.text import slugify
from django.db import models
from django.dispatch import receiver

from products.formula_price import formula_price
from users.models import UserStatus


class Photo(models.Model):
    url = models.CharField(max_length=512, db_index=True)

    def __str__(self):
        return str(self.product)


class Brand(models.Model):
    name = models.CharField(max_length=255)
    query_name = models.CharField(max_length=255, default="")
    score = models.IntegerField(default=0)
    # search_filter_name = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.query_name = self.name.lower().replace(" ", "_")
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey("Category", related_name='subcat', blank=True, on_delete=models.CASCADE,
                                        null=True)
    eng_name = models.CharField(max_length=255, default="")  # для запросов
    is_all = models.BooleanField(default=False)
    full_name = models.CharField(max_length=255, default="")  # полный путь
    score = models.IntegerField(default=0)
    score_product_page = models.IntegerField(default=0)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.parent_category:
            self.full_name = f"{self.parent_category.full_name} | {self.name}"
        if "все" in self.name.lower() or "вся" in self.name.lower() or "всё" in self.name.lower():
            self.is_all = True
            self.parent_category.eng_name = self.parent_category.eng_name + "_"
            self.parent_category.save()

        super().save(*args, **kwargs)


class Line(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    parent_line = models.ForeignKey("Line", related_name='subline', blank=True, on_delete=models.CASCADE, null=True)
    is_all = models.BooleanField(default=False)
    view_name = models.CharField(max_length=255, default="")  # для отображения в фильтрах
    full_name = models.CharField(max_length=255, default="")  # полный путь
    full_eng_name = models.CharField(max_length=255, default="", db_index=True)  # для отправки запроса
    search_filter_name = models.CharField(max_length=255, default="")
    score = models.IntegerField(default=0)
    score_product_page = models.IntegerField(default=0)

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.parent_line:
            self.full_name = f"{self.parent_line.full_name} | {self.name}"
        else:
            self.full_name = self.name
        self.view_name = self.name
        # if "все" in self.name.lower() or "другие" in self.name.lower():
        #     self.view_name = self.name
        # else:
        #     st = self.full_name.replace("|", "").split()
        #     new_st = []
        #     for s in st:
        #         if "все" not in s.lower():
        #             new_st.append(s)
        #
        #     self.view_name = " ".join(" ".join(st).replace("Jordan Air Jordan", "Air Jordan").replace("Blazer Blazer", "Blazer", 1).replace(
        #         "Dunk Dunk", "Dunk", 1).split())
        # self.full_eng_name = self.view_name.lower().replace(" ", "_").replace("все_", "all_").strip()

        if "все" in self.name.lower():
            self.is_all = True
            self.parent_line.full_eng_name = self.parent_line.full_eng_name + "_"
            self.parent_line.save()
        super().save(*args, **kwargs)


# class Size(models.Model):
#     INT = models.CharField(max_length=15)
#     US = models.CharField(max_length=15)
#     UK = models.CharField(max_length=15)
#     EU = models.CharField(max_length=15)
#     IT = models.CharField(max_length=15)
#     RU = models.CharField(max_length=15)
#
#     product = models.ForeignKey("Product", related_name="sizes", on_delete=models.CASCADE,
#                                 null=True, blank=True)
#
#     def __str__(self):
#         return self.INT


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=1024, default="")
    # is_collab = models.BooleanField(default=False)
    in_filter = models.BooleanField(default=False)
    query_name = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.query_name:
            self.query_name = "_".join(self.name.replace(" x ", " ").lower().split())

        super().save(*args, **kwargs)


class Collab(models.Model):
    name = models.CharField(max_length=255)
    query_name = models.CharField(max_length=255, blank=True, null=True)
    is_main_collab = models.BooleanField(default=False)
    is_all = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    score_product_page = models.IntegerField(default=0)
    order = models.IntegerField(default=1000)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.query_name:
            self.query_name = "_".join(self.name.lower().split())

        super().save(*args, **kwargs)


class Color(models.Model):
    name = models.CharField(max_length=255)
    is_main_color = models.BooleanField(default=False)
    russian_name = models.CharField(max_length=255, default="")
    hex = models.CharField(max_length=255, default="")
    # poryadok = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Material(models.Model):
    name = models.CharField(max_length=255)
    eng_name = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.name


class Gender(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('K', 'Kids')
    )
    name = models.CharField(max_length=255, choices=GENDER_CHOICES)

    def __str__(self):
        return self.name


class ProductManager(models.Manager):
    def fix_empty_slugs(self):
        products = self.filter(slug='')
        for product in products:
            product.slug = slugify(product.name)
            product.save()


class DewuInfo(models.Model):
    spu_id = models.IntegerField(default=0, db_index=True)
    api_data = models.JSONField(default=dict)
    preprocessed_data = models.JSONField(default=dict)
    web_data = models.JSONField(default=dict)
    # processed_data = models.JSONField(default=list)
    formatted_manufacturer_sku = models.CharField(default="", max_length=128, db_index=True)


class SGInfo(models.Model):
    manufacturer_sku = models.CharField(max_length=256, default="")
    data = models.JSONField(default=dict)
    relevant_number = models.IntegerField(default=0)
    novelty_number = models.IntegerField(default=0)
    formatted_manufacturer_sku = models.CharField(default="", max_length=128, db_index=True)


class Product(models.Model):
    spu_id = models.IntegerField(default=0, db_index=True)
    property_id = models.IntegerField(default=0)
    # dewu_info = models.ForeignKey("DewuInfo", on_delete=models.PROTECT, blank=True, null=True, related_name="products")
    brands = models.ManyToManyField("Brand", related_name='products',
                                    blank=True)
    categories = models.ManyToManyField("Category", related_name='products',
                                        blank=True, db_index=True)
    lines = models.ManyToManyField("Line", related_name='products',
                                   blank=True, db_index=True)
    main_line = models.ForeignKey("Line", on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name="main_products")
    # collections = models.ManyToManyField("Collection", related_name='products', blank=True)
    tags = models.ManyToManyField("Tag", related_name='products',
                                  blank=True)
    collections = models.ManyToManyField("Collection", related_name='products', blank=True)

    model = models.CharField(max_length=255, null=False, blank=True)
    colorway = models.CharField(max_length=255, null=False, blank=True)
    russian_name = models.CharField(max_length=255, null=False, blank=True, default="")
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True)
    manufacturer_sku = models.CharField(max_length=255, default="")  # Артем, это артикул по-английски, не пугайся
    description = models.TextField(default="", blank=True)
    bucket_link = models.ManyToManyField("Photo", related_name='product', blank=True)
    black_bucket_link = models.ManyToManyField("Photo", related_name='black_product', blank=True)

    is_custom = models.BooleanField(default=False, db_index=True)
    is_collab = models.BooleanField(default=False)
    collab = models.ForeignKey("Collab", on_delete=models.SET_NULL, blank=True, null=True, related_name="products", db_index=True)

    main_color = models.ForeignKey("Color", on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name="products_main")
    colors = models.ManyToManyField("Color", related_name='products', blank=True, db_index=True)
    designer_color = models.SlugField(max_length=255, blank=True, default="")

    materials = models.ManyToManyField("Material", related_name='products', blank=True, db_index=True)

    gender = models.ManyToManyField("Gender", related_name='products', blank=True, db_index=True)
    recommended_gender = models.ForeignKey("Gender", on_delete=models.SET_NULL, blank=True, null=True)
    size_table = models.ForeignKey("SizeTable", on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='products')
    size_table_platform = models.JSONField(default=dict)

    min_price = models.IntegerField(blank=True, null=True, default=0, db_index=True)
    max_profit = models.IntegerField(blank=True, null=True, default=0)
    max_bonus = models.IntegerField(blank=True, null=True, default=0)
    min_price_without_sale = models.IntegerField(blank=True, null=True, default=0)

    # sizes are initialized in Size model by ForeignKey
    # product units are initialized in UnitBundle model by ForeignKey

    available_flag = models.BooleanField(default=False, db_index=True)

    has_many_sizes = models.BooleanField(default=False)
    has_many_colors = models.BooleanField(default=False)
    has_many_configurations = models.BooleanField(default=False)

    last_upd = models.DateTimeField(default=timezone.now)
    add_date = models.DateField(default=date.today)

    exact_date = models.DateField(default=date.today, blank=True, db_index=True)
    approximate_date = models.CharField(max_length=63, null=False, blank=True, default="")

    fit = models.IntegerField(default=0)
    rel_num = models.IntegerField(default=0, db_index=True)
    normalize_rel_num = models.IntegerField(default=0)
    platform_info = models.JSONField(blank=True, null=True, default=dict)
    sizes_prices = models.JSONField(blank=True, null=True, default=list)

    parameters = models.JSONField(blank=True, null=True, default=dict)
    similar_product = models.JSONField(blank=True, null=True, default=list)
    another_configuration = models.JSONField(blank=True, null=True, default=list)
    size_row_name = models.CharField(max_length=255, null=True, blank=True, default="")
    extra_name = models.CharField(max_length=255, null=True, blank=True, default="")
    is_sale = models.BooleanField(default=False, db_index=True)


    sale_absolute = models.IntegerField(default=0)
    sale_percentage = models.IntegerField(default=0)


    in_sg = models.BooleanField(default=False, db_index=True)
    # percentage_sale = models.IntegerField(default=0)
    available_sizes = models.JSONField(blank=True, null=True, default=dict)
    sizes = models.ManyToManyField("SizeTranslationRows", related_name='products', blank=True, default=None, db_index=True)
    actual_price = models.BooleanField(default=False)
    one_update = models.BooleanField(default=False)
    last_parse_price = models.DateTimeField(default=timezone.now)

    content_sources = models.JSONField(blank=True, null=True, default=dict)
    category_id = models.IntegerField(default=0)
    category_name = models.CharField(max_length=128, default="")
    level1_category_id = models.IntegerField(default=0)
    level2_category_id = models.IntegerField(default=0)
    formatted_manufacturer_sku = models.CharField(default="", max_length=128)
    score_product_page = models.IntegerField(default=0, db_index=True)
    likes_month = models.IntegerField(default=0)
    likes_week = models.IntegerField(default=0)
    is_new = models.BooleanField(default=False, db_index=True)
    is_recommend = models.BooleanField(default=False, db_index=True)
    extra_score = models.IntegerField(default=0)
    up_score = models.BooleanField(default=False)
    in_process_update = models.BooleanField(default=False)

    objects = ProductManager()

    def clear_all_fields(self):
        self.brands.clear()
        self.categories.clear()
        self.lines.clear()
        self.main_line = None
        # collections = models.ManyToManyField("Collection", related_name='products', blank=True)
        # self.tags.clear()

        self.model = ""
        self.colorway = ""
        self.russian_name = ""

        # self.description = ""
        self.bucket_link.clear()

        self.is_custom = False
        self.is_collab = False
        self.collab = None
        # self.main_color = None
        # self.colors.clear()
        # self.designer_color = ""
        # self.materials.clear()

        # self.gender.clear()
        # self.recommended_gender = None
        # self.size_table = None
        # self.size_table_platform = {}

        self.min_price = 0
        self.max_bonus = 0
        self.min_price_without_sale = 0

        # sizes are initialized in Size model by ForeignKey
        # product units are initialized in UnitBundle model by ForeignKey

        self.available_flag = False

        # self.has_many_sizes = False
        # self.has_many_colors = False
        # self.has_many_configurations = False

        # self.rel_num = 0
        # self.platform_info = {}
        self.sizes_prices = []

        # self.parameters = {}
        # self.similar_product = []
        # self.another_configuration = []
        # self.size_row_name = ""
        # self.extra_name = ""
        # self.percentage_sale = 0
        self.available_sizes = {}
        self.actual_price = False
        self.content_sources = {}
        self.in_process_update = True
        self.sizes.clear()
        self.save()

    def add_sale(self, absolute, percentage):
        def round_by_step(value, step=50):
            return math.ceil(value / step) * step
        self.is_sale = True
        self.sale_absolute = absolute
        self.sale_percentage = percentage
        pus = self.product_units.all()
        for pu in pus:
            pu.is_sale = True
            if self.sale_percentage != 0:
                percentage = round(((100 - self.sale_percentage) / 100), 2)
                pu.start_price = round_by_step((pu.final_price / percentage) + 10, step=100) - 10
            else:
                pu.start_price = pu.final_price + self.sale_absolute
            pu.save()
        self.save()
        self.update_min_price()

    def del_sale(self):
        self.is_sale = False
        pus = self.product_units.all()
        for pu in pus:
            pu.is_sale = False
            pu.start_price = pu.final_price
            pu.save()
        self.save()
        self.update_min_price()

    def update_available_status(self):
        if not self.product_units.filter(availability=True).exists():
            self.available_flag = False
            self.save()

    def update_price(self, in_sale=True):
        if not self.actual_price:
            user_status = UserStatus.objects.get(name="Amethyst")
            min_price = 0
            max_bonus = 0
            max_profit = 0
            min_price_without_sale = 0
            # print(self.product_units.all())
            for unit in self.product_units.filter(availability=True):
                price = formula_price(self, unit, user_status, in_sale=in_sale)
                # print(price)
                # print(price)
                unit.start_price = price['start_price']
                unit.final_price = price['final_price']
                unit.total_profit = price['total_profit']
                unit.bonus = price['bonus']
                unit.save()
                if (unit.final_price <= min_price or min_price == 0) and unit.availability:
                    min_price = unit.final_price
                    min_price_without_sale = unit.start_price
                if (unit.bonus > max_bonus or max_bonus == 0) and unit.availability:
                    max_bonus = unit.bonus
                    max_profit = unit.total_profit
            self.max_profit = max_profit
            self.max_bonus = max_bonus
            # if self.min_price < min_price:
            #     self.is_sale = False
            #     self.product_units.update(is_sale=False)

            self.min_price = min_price
            self.min_price_without_sale = min_price_without_sale
            self.actual_price = True
            if self.min_price != 0:
                self.available_flag = True
            else:
                self.available_flag = False
            self.save()


    # class Meta:
    #     indexes = [
    #         models.Index(fields=['id']),
    #         models.Index(fields=['spu_id']),
    #         models.Index(fields=['slug']),
    #         models.Index(fields=['manufacturer_sku']),
    #         models.Index(fields=['is_custom']),
    #         models.Index(fields=['min_price']),
    #         models.Index(fields=['rel_num']),
    #         models.Index(fields=['available_flag']),
    #
    #         # Добавьте индексы для остальных полей с db_index=True
    #     ]

    def check_sale(self):
        def round_by_step(value, step=50):
            return math.ceil(value / step) * step
        min_price = 0
        min_price_unit = ""
        is_sale = False
        max_procent = 0
        for product_unit in self.product_units.filter(availability=True):
            if product_unit.start_price > product_unit.final_price:
                max_procent = max(max_procent, round((1 - (product_unit.final_price/product_unit.start_price)) * 100))
        if max_procent != 0:
            self.is_sale = True
            for product_unit in self.product_units.filter(availability=True):
                if product_unit.start_price == product_unit.final_price:
                    percentage = round(((100 - max_procent) / 100), 2)
                    price_without_sale = round_by_step((product_unit.final_price / percentage) + 10, step=100) - 10
                    product_unit.start_price = price_without_sale
                    product_unit.is_sale = True
        else:
            pu = self.product_units.filter(availability=True)
            pu.update(is_sale=False)
            self.is_sale = 0
            self.sale_absolute = 0
            self.sale_percentage = 0




    def get_full_name(self):
        return f"{self.brands.first().name if self.collab is None else self.collab.name} {self.model} {self.colorway}"

    def update_min_price(self):
        self.min_price = 0
        # min_price = 0
        if self.product_units.exists():
            product_units = self.product_units.filter(availability=True)
            for product_unit in product_units:
                if (product_unit.final_price <= self.min_price or self.min_price == 0) and product_unit.availability:
                    # print(product_unit.start_price)
                    self.min_price = product_unit.final_price
                    self.min_price_without_sale = product_unit.start_price

        self.actual_price = True

        self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.spu_id}_{self.property_id}_{self.manufacturer_sku}"

        product_slug = kwargs.pop('product_slug', "1")
        if product_slug != "1":
            if f"{self.spu_id}_{self.property_id}" in product_slug:
                self.slug = slugify(
                    f"{' '.join([x.name for x in self.brands.all()])} {self.model} {self.colorway} {self.id}")
                print("новый слаг")
                print(self.slug)
            else:
                self.slug = product_slug

            lines = self.lines.exclude(name__icontains='Все').exclude(name__icontains='Другие')
            if self.is_collab:
                k = 0
                collab_brand_names = []
                for brnad in self.brands.all():
                    if k == 0:
                        k += 1
                        continue
                    collab_brand_names.append(brnad.name)
                lines = lines.exclude(name__in=collab_brand_names)

            if lines:
                self.main_line = lines.order_by('-id').first()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.model


class SizeTable(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    filter_name = models.CharField(max_length=255, blank=True, null=True)
    category = models.ManyToManyField("Category", related_name='size_tables', blank=True)
    gender = models.ManyToManyField("Gender", related_name='size_tables', blank=True)
    size_rows = models.ManyToManyField("SizeRow", related_name='size_tables', blank=True)
    default_row = models.ForeignKey("SizeRow", related_name='default_size_table', blank=True, on_delete=models.PROTECT,
                                    null=True)
    standard = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class SizeRow(models.Model):
    filter_name = models.CharField(max_length=128, default="")
    filter_logo = models.CharField(max_length=128, default="")
    sizes = models.JSONField(default=list)


class SizeTranslationRows(models.Model):
    table = models.ForeignKey("SizeTable", blank=True, null=True, on_delete=models.CASCADE, related_name="rows", db_index=True)
    row = models.JSONField(blank=True, null=True)
    is_one_size = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['id']), models.Index(fields=['is_one_size'])]

    def __str__(self):
        return f"{self.table} {self.id}"


class HeaderPhoto(models.Model):
    genders = models.ManyToManyField("Gender", related_name='headers_photos', blank=True)
    categories = models.ManyToManyField("Category", related_name='headers_photos',
                                        blank=True)
    lines = models.ManyToManyField("Line", related_name='headers_photos',
                                   blank=True)
    collabs = models.ManyToManyField("Collab", related_name='headers_photos', blank=True)
    type = models.CharField(max_length=64, default="")
    where = models.CharField(max_length=64, default="")
    photo = models.CharField(max_length=1024, default="")
    header_text = models.ForeignKey("HeaderText", related_name='headers_photo', blank=True, on_delete=models.CASCADE,
                                    null=True)
    rating = models.IntegerField(default=0)


class HeaderText(models.Model):
    genders = models.ManyToManyField("Gender", related_name='headers_text', blank=True)
    categories = models.ManyToManyField("Category", related_name='headers_text',
                                        blank=True)
    lines = models.ManyToManyField("Line", related_name='headers_text',
                                   blank=True)
    collabs = models.ManyToManyField("Collab", related_name='headers_text', blank=True)
    title = models.CharField(max_length=256, default="")
    text = models.CharField(max_length=8096, default="")
    type = models.CharField(max_length=64, default="")


class HeaderPage(models.Model):
    text = models.ForeignKey("HeaderText", blank=True, null=True, on_delete=models.PROTECT)
    photo = models.ForeignKey("HeaderPhoto", blank=True, null=True, on_delete=models.PROTECT)


class MainPage(models.Model):
    text = models.ForeignKey("HeaderText", blank=True, null=True, on_delete=models.PROTECT)
    photo = models.ForeignKey("HeaderPhoto", blank=True, null=True, on_delete=models.PROTECT)
    button = models.BooleanField(default=True)
    button_text = models.CharField(max_length=64, default="")


class RansomRequest(models.Model):
    name = models.CharField(max_length=128, default="")
    tg_name = models.CharField(max_length=128, default="")
    phone_number = models.CharField(max_length=64, default="")
    email = models.CharField(max_length=128, default="")
    url = models.CharField(max_length=512, default="")
    photo = models.CharField(max_length=512, default="")
    info = models.CharField(max_length=1024, default="")
