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
        self.query_name = self.name
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
        self.full_eng_name = self.view_name.lower().replace(" ", "_")

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
            self.query_name = "_".join(self.name.replace(" x ", " ").lower().split())

        super().save(*args, **kwargs)


class Color(models.Model):
    name = models.CharField(max_length=255)
    is_main_color = models.BooleanField(default=False)
    russian_name = models.CharField(max_length=255, default="")
    hex = models.CharField(max_length=255, default="")

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
    main_line = models.ForeignKey("Line", on_delete=models.PROTECT, blank=True, null=True, related_name="main_products")
    # collections = models.ManyToManyField("Collection", related_name='products', blank=True)
    tags = models.ManyToManyField("Tag", related_name='products',
                                  blank=True)

    model = models.CharField(max_length=255, null=False, blank=True)
    colorway = models.CharField(max_length=255, null=False, blank=True)
    russian_name = models.CharField(max_length=255, null=False, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    manufacturer_sku = models.CharField(max_length=255)  # Артем, это артикул по-английски, не пугайся
    description = models.TextField(default="", blank=True)
    bucket_link = models.ManyToManyField("Photo", related_name='product', blank=True, null=True)

    is_custom = models.BooleanField(default=False)
    is_collab = models.BooleanField(default=False)
    collab = models.ForeignKey("Collab", on_delete=models.PROTECT, blank=True, null=True, related_name="products")

    main_color = models.ForeignKey("Color", on_delete=models.PROTECT, blank=True, null=True,
                                   related_name="products_main")
    colors = models.ManyToManyField("Color", related_name='products', blank=True)
    designer_color = models.SlugField(max_length=255, blank=True)

    gender = models.ManyToManyField("Gender", related_name='products', blank=True)
    recommended_gender = models.ForeignKey("Gender", on_delete=models.PROTECT, blank=True, null=True)
    size_table = models.ForeignKey("SizeTable", on_delete=models.PROTECT, blank=True, null=True)

    min_price = models.IntegerField(blank=True, null=True)

    # sizes are initialized in Size model by ForeignKey
    # product units are initialized in UnitBundle model by ForeignKey

    available_flag = models.BooleanField(default=True)

    has_many_sizes = models.BooleanField(default=False)
    has_many_colors = models.BooleanField(default=False)
    has_many_configurations = models.BooleanField(default=False)

    last_upd = models.DateTimeField(default=timezone.now)
    add_date = models.DateField(default=date.today)

    exact_date = models.DateField(default=date.today, blank=True)
    approximate_date = models.CharField(max_length=63, null=False, blank=True, default="")

    fit = models.IntegerField(default=0)
    rel_num = models.IntegerField(default=0)
    platform_info = models.JSONField(blank=True, null=True)

    objects = ProductManager()

    def save(self, *args, **kwargs):
        def add_categories_to_product(category):
            self.categories.add(category)
            # Добавляем текущую категорию к товару
            if category.parent_category:
                if Category.objects.filter(name=f"Все {category.parent_category.name.lower()}").exists():
                    category_is_all = Category.objects.get(name=f"Все {category.parent_category.name.lower()}",
                                                           parent_category=category.parent_category)
                    self.categories.add(category_is_all)
                elif Category.objects.filter(name=f"Вся {category.parent_category.name.lower()}").exists():
                    category_is_all = Category.objects.get(name=f"Вся {category.parent_category.name.lower()}",
                                                           parent_category=category.parent_category)
                    self.categories.add(category_is_all)
                add_categories_to_product(category.parent_category)

        def add_lines_to_product(line):
            self.lines.add(line)
            if line.parent_line:
                if Line.objects.filter(name=f"Все {line.parent_line.name}").exists():
                    line_is_all = Line.objects.get(name=f"Все {line.parent_line.name}", parent_line=line.parent_line)
                    self.lines.add(line_is_all)
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

            lines = self.lines.exclude(name__icontains='Все').exclude(name__contains='Другие')
            if lines:
                self.main_line = lines.order_by('-id').first()

            for brand in self.brands.all():
                line, _ = Line.objects.get_or_create(name=brand.name)
                line.save()
                self.lines.add(line)
                if Line.objects.filter(name=f"Все {brand.name}").exists():
                    self.lines.add(Line.objects.get(name=f"Все {brand.name}"))
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
