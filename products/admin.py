from django.contrib import admin

# Register your models here.
from .models import Product, Category, Tag, Brand, Gender, Size, Collection, Color, Line


class ProductAdmin(admin.ModelAdmin):
    list_display = ('model', '_brand',)
    search_fields = ("brands__name", "model", "colorway")

    # prepopulated_fields = {'slug': ('name',)}

    def _brand(self, row):
        return ','.join([x.name for x in row.brands.all()])


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


class LineAdmin(admin.ModelAdmin):
    list_display = ('name',)


class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)


class GenderAdmin(admin.ModelAdmin):
    list_display = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name',)


class SizeAdmin(admin.ModelAdmin):
    list_display = ('INT',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Gender, GenderAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Line, LineAdmin)
