from rest_framework import routers
from .api import ProductViewSet, CategoryViewSet, LinesViewSet, ColorViewSet, BrandViewSet, CollectionViewSet, CollabViewSet
from django.urls import include, path
from .views import ProductSlugView, ProductIdView, CategoryTreeView, LineTreeView, ProductUpdateView, LineNoChildView, \
    CategoryNoChildView, ProductSizeView, AddProductView, ListProductView

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

router_color = routers.DefaultRouter()
router_color.register("colors", ColorViewSet, basename="colors")

router_collection = routers.DefaultRouter()
router_collection.register("collections", CollectionViewSet, basename="collections")

router_collab = routers.DefaultRouter()
router_collab.register("collabs", CollabViewSet, basename="collab")

urlpatterns = [
    path("", include(router_collection.urls)),
    path("", include(router_product.urls)), path("", include(router_cat.urls)),
    path("", include(router_brand.urls)), path("", include(router_line.urls)),
    path("", include(router_color.urls)), path("", include(router_collab.urls)),
    path('slug/<str:slug>', ProductSlugView.as_view()),
    path("tree_cat", CategoryTreeView.as_view()), path("tree_line", LineTreeView.as_view()),
    path("cat_no_child", CategoryNoChildView.as_view()), path("line_no_child", LineNoChildView.as_view()),
    path("update/<int:product_id>", ProductUpdateView.as_view()), path("size", ProductSizeView.as_view()),
    path("add_product", AddProductView.as_view()), path("list_product", ListProductView.as_view())]
