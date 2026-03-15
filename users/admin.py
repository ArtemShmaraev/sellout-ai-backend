from django.contrib import admin
from .models import User, Gender, UserStatus


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'id', "first_name", "last_name", "get_bonuses_total_amount", "user_status", "verify_email")

    def get_bonuses_total_amount(self, obj):
        if obj.bonuses is not None:
            return obj.bonuses.total_amount
        return -1


class UserStatusAdmin(admin.ModelAdmin):
    list_display = ("name", )

class GenderAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(User, UserAdmin)
admin.site.register(Gender, GenderAdmin)
admin.site.register(UserStatus, UserStatusAdmin)