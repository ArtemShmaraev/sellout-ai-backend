from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=255)
    query_name = models.CharField(max_length=255, default="")
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.query_name = self.name.lower().replace(" ", "_")
        super().save(*args, **kwargs)


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent_category = models.ForeignKey("Category", related_name='subcat', blank=True, on_delete=models.CASCADE,
                                        null=True)
    eng_name = models.CharField(max_length=255, default="")
    is_all = models.BooleanField(default=False)
    full_name = models.CharField(max_length=255, default="")
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
    view_name = models.CharField(max_length=255, default="")
    full_name = models.CharField(max_length=255, default="")
    full_eng_name = models.CharField(max_length=255, default="", db_index=True)
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

        if "все" in self.name.lower():
            self.is_all = True
            self.parent_line.full_eng_name = self.parent_line.full_eng_name + "_"
            self.parent_line.save()
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=1024, default="")
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
