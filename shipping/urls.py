from rest_framework import routers
from .api import ProductUnitViewSet
from django.urls import path, re_path
from .views import ProductUnitProductView, ProductUnitProductMainView

router = routers.DefaultRouter()
router.register("", ProductUnitViewSet, 'product_unit')

urlpatterns = router.urls
urlpatterns.append(path('product/<int:product_id>/', ProductUnitProductView.as_view()))
urlpatterns.append(path('product_main/<int:product_id>/<int:user_id>/', ProductUnitProductMainView.as_view()))


