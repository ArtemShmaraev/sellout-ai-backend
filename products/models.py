import random

from django.db import models
from django.utils import timezone
from datetime import date
from django_slugify_processor.text import slugify
from django.db import models
from django.dispatch import receiver


class Photo(models.Model):
    url = models.CharField(max_length=512)

    def __str__(self):
        return str(self.product)


class Brand(models.Model):
    name = models.CharField(max_length=255)
    query_name = models.CharField(max_length=255, default="")

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

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.parent_category:
            self.full_name = f"{self.parent_category.full_name} | {self.name}"
        if "все" in self.name.lower() or "вся" in self.name.lower() or "всё" in self.name.lower():
            self.is_all = True

        super().save(*args, **kwargs)


class Line(models.Model):
    name = models.CharField(max_length=255)
    parent_line = models.ForeignKey("Line", related_name='subline', blank=True, on_delete=models.CASCADE, null=True)
    is_all = models.BooleanField(default=False)
    view_name = models.CharField(max_length=255, default="")  # для отображения в фильтрах
    full_name = models.CharField(max_length=255, default="")  # полный путь
    full_eng_name = models.CharField(max_length=255, default="")  # для отправки запроса

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
        self.full_eng_name = self.view_name.lower().replace(" ", "_").replace("все_", "").strip()

        if "все" in self.name.lower():
            self.is_all = True
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
    is_collab = models.BooleanField(default=False)
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
    processed_data = models.JSONField(default=list)


class SGInfo(models.Model):
    manufacturer_sku = models.CharField(max_length=256, default="")
    data = models.JSONField(default=dict)

class Product(models.Model):
    spu_id = models.IntegerField(default=0, db_index=True)
    property_id = models.IntegerField(default=0, db_index=True, )
    # dewu_info = models.ForeignKey("DewuInfo", on_delete=models.PROTECT, blank=True, null=True, related_name="products")
    brands = models.ManyToManyField("Brand", related_name='products',
                                    blank=True, db_index=True)
    categories = models.ManyToManyField("Category", related_name='products',
                                        blank=True, db_index=True)
    lines = models.ManyToManyField("Line", related_name='products',
                                   blank=True, db_index=True)
    main_line = models.ForeignKey("Line", on_delete=models.SET_NULL, blank=True, null=True, related_name="main_products")
    # collections = models.ManyToManyField("Collection", related_name='products', blank=True)
    tags = models.ManyToManyField("Tag", related_name='products',
                                  blank=True)

    model = models.CharField(max_length=255, null=False, blank=True, db_index=True)
    colorway = models.CharField(max_length=255, null=False, blank=True, db_index=True)
    russian_name = models.CharField(max_length=255, null=False, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, db_index=True)
    manufacturer_sku = models.CharField(max_length=255)  # Артем, это артикул по-английски, не пугайся
    description = models.TextField(default="", blank=True)
    bucket_link = models.ManyToManyField("Photo", related_name='product', blank=True, null=True, db_index=True)

    is_custom = models.BooleanField(default=False, db_index=True)
    is_collab = models.BooleanField(default=False, db_index=True)
    collab = models.ForeignKey("Collab", on_delete=models.SET_NULL, blank=True, null=True, related_name="products", db_index=True)

    main_color = models.ForeignKey("Color", on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name="products_main", db_index=True)
    colors = models.ManyToManyField("Color", related_name='products', blank=True, db_index=True)
    designer_color = models.SlugField(max_length=255, blank=True)

    materials = models.ManyToManyField("Material", related_name='products', blank=True, db_index=True)

    gender = models.ManyToManyField("Gender", related_name='products', blank=True, db_index=True)
    recommended_gender = models.ForeignKey("Gender", on_delete=models.SET_NULL, blank=True, null=True)
    size_table = models.ForeignKey("SizeTable", on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='products')
    size_table_platform = models.JSONField(default=dict)

    min_price = models.IntegerField(blank=True, null=True, db_index=True)

    # sizes are initialized in Size model by ForeignKey
    # product units are initialized in UnitBundle model by ForeignKey

    available_flag = models.BooleanField(default=True, db_index=True)

    has_many_sizes = models.BooleanField(default=False)
    has_many_colors = models.BooleanField(default=False)
    has_many_configurations = models.BooleanField(default=False)

    last_upd = models.DateTimeField(default=timezone.now)
    add_date = models.DateField(default=date.today)

    exact_date = models.DateField(default=date.today, blank=True)
    approximate_date = models.CharField(max_length=63, null=False, blank=True, default="")

    fit = models.IntegerField(default=0)
    rel_num = models.IntegerField(default=0, db_index=True)
    platform_info = models.JSONField(blank=True, null=True)
    sizes_prices = models.JSONField(blank=True, null=True, default=list)

    parameters = models.JSONField(blank=True, null=True, default=dict)
    similar_product = models.JSONField(blank=True, null=True, default=list)
    another_configuration = models.JSONField(blank=True, null=True, default=list)
    main_size_row_of_unit = models.CharField(max_length=255, null=True, blank=True)
    main_size_row = models.CharField(max_length=255, null=True, blank=True)
    unit_common_name = models.CharField(max_length=255, null=True, blank=True)

    objects = ProductManager()

    class Meta:
        indexes = [
            models.Index(fields=['id']),
            models.Index(fields=['spu_id']),
            models.Index(fields=['model']),
            models.Index(fields=['colorway']),
            models.Index(fields=['slug']),
            models.Index(fields=['manufacturer_sku']),
            models.Index(fields=['is_custom']),
            models.Index(fields=['is_collab']),
            models.Index(fields=['min_price']),
            models.Index(fields=['rel_num']),
            models.Index(fields=['available_flag']),

            # Добавьте индексы для остальных полей с db_index=True
        ]


    def update_min_price(self):
        if self.product_units.all():
            product_units = self.product_units.all()
            for product_unit in product_units:
                if product_unit.final_price < self.min_price and product_unit.availability:
                    self.min_price = product_unit.final_price

        self.save()

    def save(self, *args, **kwargs):


        custom_param = kwargs.pop('custom_param', False)
        if custom_param:
            self.slug = slugify(
                f"{' '.join([x.name for x in self.brands.all()])} {self.model} {self.colorway} {self.id}")

            lines = self.lines.exclude(name__icontains='Все').exclude(name__icontains='Другие')
            if lines:
                self.main_line = lines.order_by('-id').first()

            # for line in self.lines.all():
            #     add_lines_to_product(line)
            #
            # for cat in self.categories.all():
            #     add_categories_to_product(cat)

            # if self.main_color:
            #     if not self.main_color.is_main_color:
            #         self.main_color.is_main_color = True

            # for brand in self.brands.all():
            #     line, _ = Line.objects.get_or_create(name=brand.name)
            #     line.save()
            #     self.lines.add(line)
            #     if Line.objects.filter(name=f"Все {brand.name}").exists():
            #         self.lines.add(Line.objects.get(name=f"Все {brand.name}"))

            # lines = self.lines.exclude(name__icontains='Все').exclude(name__icontains='Другие')
            # if lines:
            #     self.main_line = lines.order_by('-id').first()

        # super(Product, self).save(*args, **kwargs)
        # print()
        super().save(*args, **kwargs)


    def __str__(self):
        return self.model


class SizeTable(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
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
    table = models.ForeignKey("SizeTable", blank=True, null=True, on_delete=models.CASCADE, related_name="rows")
    row = models.JSONField(blank=True, null=True)
    is_one_size = models.BooleanField(default=False)

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
    header_text = models.ForeignKey("HeaderText", related_name='headers_photo', blank=True, on_delete=models.CASCADE, null=True)


class HeaderText(models.Model):
    genders = models.ManyToManyField("Gender", related_name='headers_text', blank=True)
    categories = models.ManyToManyField("Category", related_name='headers_text',
                                        blank=True)
    lines = models.ManyToManyField("Line", related_name='headers_text',
                                   blank=True)
    collabs = models.ManyToManyField("Collab", related_name='headers_text', blank=True)
    title = models.CharField(max_length=256, default="")
    text = models.CharField(max_length=8096, default="")



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
    photo = models.CharField(max_length=128, default="")
    info = models.CharField(max_length=1024, default="")



