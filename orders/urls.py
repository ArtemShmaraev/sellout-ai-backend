from rest_framework import routers
from .api import ShoppingCartViewSet
from django.urls import path
from .views import ShoppingCartUser, ShoppingCartDelProductUnit, ShoppingCartAddProductUnit

router = routers.DefaultRouter()
router.register("", ShoppingCartViewSet, 'cart')

urlpatterns = router.urls
urlpatterns.append(path('user/<int:user_id>', ShoppingCartUser.as_view()))
urlpatterns.append(path('delete/<int:user_id>/<int:product_unit_id>', ShoppingCartDelProductUnit.as_view()))
urlpatterns.append(path('add/<int:user_id>/<int:product_unit_id>', ShoppingCartAddProductUnit.as_view()))