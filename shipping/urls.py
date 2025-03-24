from rest_framework import routers
from .api import ProductUnitViewSet
from django.urls import path, re_path
from .views import ProductUnitProductView, ProductUnitProductMainView, ProductUnitProductSlugView

router = routers.DefaultRouter()
router.register("", ProductUnitViewSet, 'product_unit')

urlpatterns = router.urls
urlpatterns.append(
    path('product/<int:product_id>/', ProductUnitProductView.as_view(), name="product_units_for_product_id"))
urlpatterns.append(
    path('product/<str:slug>/', ProductUnitProductSlugView.as_view(), name="product_units_for_product_slug"))
urlpatterns.append(path('product_main/<int:product_id>/<int:user_id>/', ProductUnitProductMainView.as_view(),
                        name="product_main_view"))
