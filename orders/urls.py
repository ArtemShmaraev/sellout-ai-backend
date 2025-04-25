from rest_framework import routers
from .api import ShoppingCartViewSet
from django.urls import path
from .views import UseBonus, ShoppingCartUser, CheckOutView, AllOrdersView, UserOrdersView, OrderView, ListProductUnitOrderView

router = routers.DefaultRouter()
router.register("", ShoppingCartViewSet, 'cart')

urlpatterns = router.urls
urlpatterns.append(path('cart/<int:user_id>/<int:product_unit_id>', ShoppingCartUser.as_view()))
urlpatterns.append(path('cart/<int:user_id>', ShoppingCartUser.as_view()))
urlpatterns.append(path('cart_list/<int:user_id>', ListProductUnitOrderView.as_view()))

urlpatterns.append(path('checkout/<int:user_id>', CheckOutView.as_view()))
urlpatterns.append(path('orders', AllOrdersView.as_view()))
urlpatterns.append(path('user_orders/<int:user_id>', UserOrdersView.as_view()))
urlpatterns.append(path('info/<int:order_id>', OrderView.as_view()))

urlpatterns.append(path('cart/use_bonus/<int:user_id>', UseBonus.as_view()))
