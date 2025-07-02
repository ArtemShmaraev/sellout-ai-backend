from django.contrib import admin

# Register your models here.
from .models import ProductUnit, Platform, Formula, AddressInfo, DeliveryType


class ProductUnitAdmin(admin.ModelAdmin):
    list_display = ('product', "platform", "delivery_type", "final_price", )


class AddressInfoAdmin(admin.ModelAdmin):
    list_display = ('address', )


class DeliveryTypeAdmin(admin.ModelAdmin):
    list_display = ('name', )


class PlatformAdmin(admin.ModelAdmin):
    list_display = ('platform', )





admin.site.register(ProductUnit, ProductUnitAdmin)
admin.site.register(Platform, PlatformAdmin)
admin.site.register(DeliveryType, DeliveryTypeAdmin)
admin.site.register(AddressInfo, AddressInfoAdmin)
# admin.site.register(UnitBundle, UnitBundleAdmin)
