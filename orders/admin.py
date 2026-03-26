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
    def order_num(self, obj):
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

    def full_name(self, obj):
        try:
            name = f"{obj.product.get_full_name()} | {obj.product.manufacturer_sku} | {obj.view_size_platform} "
        except:
            name = "-"
        return name

    def link(self, obj):
        if obj.product.bucket_link.first():
            name = f'=гиперссылка("https://sellout.su/products/{obj.product.slug}"; image("{obj.product.bucket_link.first().url}"))'
        else:
            name = f'=гиперссылка("https://sellout.su/products/{obj.product.slug}"; image)'
        return name

    # def pict(self, obj):
    #     if obj.product.bucket_link.first():
    #         prod = obj.product.bucket_link.first().url
    #     else:
    #     return prod

    def days_max(self, obj):
        return f"{obj.delivery_type.days_max}"

    def order_final_amount(self, obj):
        order = obj.orders.first()
        if order:
            return order.final_amount
        return False

    def order_date(self, obj):
        order = obj.orders.first()
        if order:
            return order.date.strftime('%d.%m.%Y')
        return False

    def t(self, obj):
        return ""

    def no(self, obj):
        return "нет"

    def client(self, obj):
        order = obj.orders.first()
        if order:
            user = order.user
            f = f"{order.name} {order.surname} {order.patronymic}\n{order.email}\n{order.phone}"
            return f
        return False


    def address(self, obj):
        order = obj.orders.first()
        if order:
            st = f"{order.delivery} | ({order.delivery_price}₽) | {order.address.address if order.address is not None else ''} {order.pvz} | {order.pvz_address}"
            return st
        return False



    get_fact_of_payment.boolean = True
    list_display = ("order_num", "link", 'full_name', "t", "order_date", "days_max", "t",  "no", "client", "address", "order_final_amount", "t", "t", "t",  "get_days_for_msk", "original_price", "status",  "track_number", "get_fact_of_payment")


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