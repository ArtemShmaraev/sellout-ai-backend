from django.db import models
from django.utils import timezone
from datetime import date
from django_slugify_processor.text import slugify
from django.db import models
from django.dispatch import receiver


class Brand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey("Category", related_name='subcat', blank=True, on_delete=models.CASCADE, null=True)
    eng_name = models.CharField(max_length=255, default="")
    full_name = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.parent_category:
            self.full_name = f"{self.parent_category.full_name} | {self.name}"

        super().save(*args, **kwargs)


class Line(models.Model):
    name = models.CharField(max_length=255)
    parent_line = models.ForeignKey("Line", related_name='subline', blank=True, on_delete=models.CASCADE, null=True)
    brand = models.ForeignKey("Brand", on_delete=models.PROTECT, null=True, blank=True, related_name="lines")
    full_name = models.CharField(max_length=255, default="")

    def __str__(self):
        return self.full_name

    def save(self, *args, **kwargs):
        if self.parent_line:
            self.full_name = f"{self.parent_line.full_name} | {self.name}"

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

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=255)
    is_main_color = models.BooleanField(default=False)

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


class Product(models.Model):
    brands = models.ManyToManyField("Brand", related_name='products',
                                    blank=True)
    categories = models.ManyToManyField("Category", related_name='products',
                                        blank=True)
    lines = models.ManyToManyField("Line", related_name='products',
                                   blank=True)
    collections = models.ManyToManyField("Collection", related_name='products',
                                         blank=True)
    tags = models.ManyToManyField("Tag", related_name='products',
                                         blank=True)

    model = models.CharField(max_length=255, null=False, blank=True)
    colorway = models.CharField(max_length=255, null=False, blank=True)
    russian_name = models.CharField(max_length=255, null=False, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    manufacturer_sku = models.CharField(max_length=255)  # Артем, это артикул по-английски, не пугайся
    description = models.TextField(default="", blank=True)
    bucket_link = models.CharField(max_length=255, blank=True)

    main_color = models.ForeignKey("Color", on_delete=models.PROTECT, blank=True, null=True, related_name="main")
    colors = models.ManyToManyField("Color", related_name='products', blank=True)
    designer_color = models.SlugField(max_length=255, blank=True)

    gender = models.ManyToManyField("Gender", related_name='products', blank=True)
    recommended_gender = models.ForeignKey("Gender", on_delete=models.PROTECT, blank=True, null=True)
    size_table = models.ForeignKey("SizeTable", on_delete=models.PROTECT, blank=True, null=True)

    min_price = models.IntegerField(blank=True, null=True)

    # sizes are initialized in Size model by ForeignKey
    # product units are initialized in UnitBundle model by ForeignKey

    available_flag = models.BooleanField(default=True)
    last_upd = models.DateTimeField(default=timezone.now)
    add_date = models.DateField(default=date.today)
    release_date = models.DateField(default=date.today, blank=True)
    fit = models.IntegerField(default=0)
    rel_num = models.IntegerField(default=0)
    objects = ProductManager()

    def save(self, *args, **kwargs):
        def add_categories_to_product(category):
            self.categories.add(category)
            # Добавляем текущую категорию к товару
            if category.parent_category:
                add_categories_to_product(category.parent_category)

        def add_lines_to_product(line):
            line.brand = self.brands.first()
            self.lines.add(line)
            if line.parent_line:
                add_lines_to_product(line.parent_line)

        if not self.slug:
            self.slug = slugify(
                f"{' '.join([x.name for x in self.brands.all()])} {self.model} {self.colorway} {self.id}")
            for line in self.lines.all():
                add_lines_to_product(line)

            for cat in self.categories.all():
                add_categories_to_product(cat)

            if self.main_color:
                if not self.main_color.is_main_color:
                    self.main_color.is_main_color = True
                    self.main_color.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.model


class SizeTable(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    brand = models.ForeignKey("Brand", on_delete=models.PROTECT, blank=True, null=True)
    category = models.ForeignKey("Category", on_delete=models.PROTECT, blank=True, null=True)
    # gender = models.ForeignKey("Gender", on_delete=models.PROTECT, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    size_row = models.ManyToManyField("SizeTranslationRows", related_name='rows', blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.gender}"


class SizeTranslationRows(models.Model):
    table = models.ForeignKey("SizeTable", blank=True, null=True, on_delete=models.PROTECT)
    US = models.CharField(max_length=16, blank=True, null=True)
    UK = models.CharField(max_length=16, blank=True, null=True)
    EU = models.CharField(max_length=16, blank=True, null=True)
    RU = models.CharField(max_length=16, blank=True, null=True)
    CM = models.CharField(max_length=16, blank=True, null=True)


    def __str__(self):
        return f"{self.table} {self.US}"