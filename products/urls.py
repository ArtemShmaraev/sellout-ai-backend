from rest_framework import routers
from .api import ProductViewSet, CategoryViewSet, LinesViewSet, ColorViewSet, BrandViewSet
from django.urls import include, path
from .views import ProductSlugView, ProductIdView

# router = routers.DefaultRouter()
# router.register("", ProductViewSet, 'product')
#
# urlpatterns = router.urls
# # urlpatterns.append(path('all/<int:page_number>', ProductsView.as_view()))
# urlpatterns.append(path('slug/<str:slug>', ProductSlugView.as_view()))
# # urlpatterns.append(path('id/<int:id>', ProductIdView.as_view()))


router_product = routers.DefaultRouter()
router_product.register("products", ProductViewSet, basename="product")

router_cat = routers.DefaultRouter()
router_cat.register("categories", CategoryViewSet, basename="category")

router_line = routers.DefaultRouter()
router_line.register("lines", LinesViewSet, basename="lines")

router_brand = routers.DefaultRouter()
router_brand.register("brands", BrandViewSet, basename="brands")

router_color = routers.DefaultRouter()
router_color.register("colors", ColorViewSet, basename="colors")

urlpatterns = [path("", include(router_product.urls)), path("", include(router_cat.urls)),
               path("", include(router_brand.urls)), path("", include(router_line.urls)),
               path("", include(router_color.urls)), path('slug/<str:slug>', ProductSlugView.as_view())]

