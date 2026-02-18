from django.contrib import admin

# Register your models here.
from .models import ShoppingCart, Order, Status, OrderUnit


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user',)




class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', "fact_of_payment", 'final_amount', 'status')

    def success_payment(self, request, queryset):
        for obj in queryset:
            obj.success_payment()

    success_payment.short_description = "Success Payment"  # Описание действия в админке


    def start_order(self, request, queryset):
        for obj in queryset:
            obj.start_order()

    start_order.short_description = "Start Order"  # Описание действия в админке

    actions = ['success_payment', 'start_order']  # Добавляем действие в список действий



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