from rest_framework import routers
from .api import ProductUnitViewSet
from django.urls import path, re_path
from .views import TotalPriceForListProductUnitView, ProductUnitProductView, ProductUnitProductMainView, ProductUnitProductSlugView, MinPriceForSizeView, DeliveryForSizeView, ListProductUnitView

router = routers.DefaultRouter()
router.register("", ProductUnitViewSet, 'product_unit')

urlpatterns = router.urls
urlpatterns.append(
    path('product/<int:product_id>/', ProductUnitProductView.as_view(), name="product_units_for_product_id"))
urlpatterns.append(
    path('product/<str:slug>/', ProductUnitProductSlugView.as_view(), name="product_units_for_product_slug"))
urlpatterns.append(path('product_main/<int:product_id>/<int:user_id>/', ProductUnitProductMainView.as_view(),
                        name="product_main_view"))
urlpatterns.append(path('min_price/<int:product_id>', MinPriceForSizeView.as_view(),
                        name="product_min_size_view"))
urlpatterns.append(path('delivery/<int:product_id>', DeliveryForSizeView.as_view(),
                        name="delivery_for_size_view"))
urlpatterns.append(path('list', ListProductUnitView.as_view()))
urlpatterns.append(path('total_amount_list', TotalPriceForListProductUnitView.as_view()))
