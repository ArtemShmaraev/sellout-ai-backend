from django.contrib import admin

# Register your models here.
from .models import ShoppingCart, Order


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', )


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Order, OrderAdmin)