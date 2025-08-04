from django.contrib import admin
from .models import PromoCode, Bonuses, AccrualBonus
# Register your models here.

class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('string_representation', )


class BonusesAdmin(admin.ModelAdmin):
    list_display = ("total_amount", "user_name")

    def user_name(self, obj):
        user = obj.user.all().first()  # Получить первого пользователя, связанного с этим объектом Bonuses
        return user.username if user is not None else ''




class AccrualBonusAdmin(admin.ModelAdmin):
    list_display = ("amount", )


admin.site.register(AccrualBonus, AccrualBonusAdmin)
admin.site.register(Bonuses, BonusesAdmin)
admin.site.register(PromoCode, PromoCodeAdmin)