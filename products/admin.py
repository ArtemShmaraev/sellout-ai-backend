from django.contrib import admin

# Register your models here.
from .models import Product, Category, Tag, Brand, Gender, Size


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', '_brand', )


    def _brand(self, row):
        return ','.join([x.name for x in row.brands.all()])


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', )


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', )


class GenderAdmin(admin.ModelAdmin):
    list_display = ('name', )


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', )


class SizeAdmin(admin.ModelAdmin):
    list_display = ('INT', )


admin.site.register(Product, ProductAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Gender, GenderAdmin)
admin.site.register(Category, CategoryAdmin)
