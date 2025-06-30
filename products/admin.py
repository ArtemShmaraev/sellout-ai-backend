from django.contrib import admin

# Register your models here.
from .models import Product, Category, Tag, Brand, Gender, Collection, Color, Line, SizeTable, SizeTranslationRows, SizeRow, Collab, HeaderPhoto, HeaderText


class ProductAdmin(admin.ModelAdmin):
    list_display = ('_brand', 'model', 'colorway', '_line',)
    search_fields = ("brands__name", "model", "colorway", "lines__name", 'manufacturer_sku', 'categories__name',)

    # prepopulated_fields = {'slug': ('name',)}

    def _brand(self, row):
        return ','.join([x.name for x in row.brands.all()])

    def _line(self, row):
        return ','.join([x.name for x in row.lines.all()])


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('full_name',)


class CollabAdmin(admin.ModelAdmin):
    list_display = ('name',)



class SizeTranslationRowsAdmin(admin.ModelAdmin):
    list_display = ('id', 'row',)


class LineAdmin(admin.ModelAdmin):
    list_display = ('full_name', "full_eng_name")


class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)


class HeaderPhotoAdmin(admin.ModelAdmin):
    list_display = ('type',)

class HeaderTextAdmin(admin.ModelAdmin):
    list_display = ('title',)


class GenderAdmin(admin.ModelAdmin):
    list_display = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name',)




class SizeTableAdmin(admin.ModelAdmin):
    list_display = ("id", 'name',)


class SizeRowAdmin(admin.ModelAdmin):
    list_display = ("id", 'filter_name', "sizes")


admin.site.register(Product, ProductAdmin)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Gender, GenderAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Line, LineAdmin)
admin.site.register(SizeTable, SizeTableAdmin)
admin.site.register(SizeTranslationRows, SizeTranslationRowsAdmin)
admin.site.register(SizeRow, SizeRowAdmin)
admin.site.register(Collab, CollabAdmin)
admin.site.register(HeaderPhoto, HeaderPhotoAdmin)
admin.site.register(HeaderText, HeaderTextAdmin)

