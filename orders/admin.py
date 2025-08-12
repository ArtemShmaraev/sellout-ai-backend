from django.contrib import admin

# Register your models here.
from .models import ShoppingCart, Order, Status, OrderUnit


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user',)


class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', )


class OrderUnitAdmin(admin.ModelAdmin):
    list_display = ('product', )

    def save_model(self, request, obj, form, change):
        print("hj,bn")
        obj.save()


class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", )


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderUnit, OrderUnitAdmin)
admin.site.register(Status, StatusAdmin)