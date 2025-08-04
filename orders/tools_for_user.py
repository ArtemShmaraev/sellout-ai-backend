from django.db.models import Sum

from orders.models import Order
from users.models import UserStatus


def update_user_status(user):
    statuses = UserStatus.objects.filter(base=True).order_by("-total_orders_amount")
    user_orders = Order.objects.filter(user=user)
    user_total = user_orders.aggregate(total=Sum('final_amount_without_shipping'))['total']

    for status in statuses:
        if status.total_orders_amount < user_total:
            user.user_status = status
            break
    user.save()
