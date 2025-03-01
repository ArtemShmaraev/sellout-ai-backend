from django.contrib import admin
from .models import Wishlist, WishlistUnit
# Register your models here.


class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user',)


class WishlistUnitAdmin(admin.ModelAdmin):
    list_display = ('product',)


admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(WishlistUnit, WishlistUnitAdmin)