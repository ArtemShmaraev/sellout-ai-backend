from django.contrib import admin
from .models import User, Gender
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'id')


class GenderAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(User, UserAdmin)
admin.site.register(Gender, GenderAdmin)