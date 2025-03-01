from django.contrib import admin

# Register your models here.
from .models import ShoppingCart


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user',)


admin.site.register(ShoppingCart, ShoppingCartAdmin)