from django.contrib import admin
from .models import User, Gender
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'id', "get_bonuses_total_amount", "user_status", "verify_email")

    def get_bonuses_total_amount(self, obj):
        if obj.bonuses is not None:
            return obj.bonuses.total_amount
        return -1



class GenderAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(User, UserAdmin)
admin.site.register(Gender, GenderAdmin)