import datetime

from django.contrib import admin

# Register your models here.
from .models import ShoppingCart, Order, Status, OrderUnit


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user',)




class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", 'user', "fact_of_payment", 'final_amount', 'status', "date")
    list_filter = ("fact_of_payment", )

    def success_payment(self, request, queryset):
        for obj in queryset:
            obj.success_payment()

    success_payment.short_description = "Success Payment"  # Описание действия в админке


    def start_order(self, request, queryset):
        for obj in queryset:
            obj.start_order()

    start_order.short_description = "Start Order"  # Описание действия в админке

    def finish_order(self, request, queryset):
        for obj in queryset:
            obj.finish_order()

    finish_order.short_description = "Finish Order"  # Описание действия в админке

    actions = ['success_payment', 'start_order', 'finish_order']  # Добавляем действие в список действий



class FactOfPaymentFilter(admin.SimpleListFilter):
    title = 'Fact of Payment'
    parameter_name = 'fact_of_payment'

    def lookups(self, request, model_admin):
        return (
            ('true', 'Paid'),
            ('false', 'Not Paid'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'true':
            return queryset.filter(orders__fact_of_payment=True)
        elif self.value() == 'false':
            return queryset.exclude(orders__fact_of_payment=True)




class OrderUnitAdmin(admin.ModelAdmin):
    def get_order_number(self, obj):
        order = obj.orders.first()
        if order:
            return order.number
        return 0

    def get_days_for_msk(self, obj):
        order = obj.orders.first()
        if order:
            if order.is_finish:
                return "Доставлен"
            date = order.date.date()
            today = datetime.date.today()
            return obj.delivery_type.days_max - (today - date).days
        return "None"

    def get_fact_of_payment(self, obj):
        order = obj.orders.first()
        if order:
            return order.fact_of_payment
        return False

    def get_delivery_type_days_max(self, obj):
        return obj.delivery_type.days_max

    get_fact_of_payment.boolean = True
    list_display = ('product', "get_order_number", "original_price", "status", "get_delivery_type_days_max", "get_days_for_msk", "get_fact_of_payment")
    list_filter = (FactOfPaymentFilter,)

    def cancel_unit(self, request, queryset):
        for obj in queryset:
            obj.update_status(cancel=True)
            obj.save()

    cancel_unit.short_description = "Cancel Unit"  # Описание действия в админке
    actions = ('cancel_unit', )


    def save_model(self, request, obj, form, change):
        print("hj,bn")
        obj.save()


class StatusAdmin(admin.ModelAdmin):
    list_display = ("name", )


admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderUnit, OrderUnitAdmin)
admin.site.register(Status, StatusAdmin)