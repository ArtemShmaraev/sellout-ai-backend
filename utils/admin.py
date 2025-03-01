from django.contrib import admin
from .models import Currency

# Register your models here.


class CurrencyAdmin(admin.ModelAdmin):
    list_display = ('name', )


admin.site.register(Currency, CurrencyAdmin)