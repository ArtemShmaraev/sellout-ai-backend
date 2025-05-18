from django.contrib import admin

# Register your models here.
from .models import ShoppingCart, Order, Status


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', )

class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", )


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Status, StatusAdmin)