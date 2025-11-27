from django.contrib.sitemaps.views import sitemap
from rest_framework import routers
from .api import ProductViewSet, CategoryViewSet, LinesViewSet, ColorViewSet, BrandViewSet, CollectionViewSet, \
    CollabViewSet, MaterialViewSet
from django.urls import include, path
from .product_site_map import ProductSitemap
from .views import SizeTableForFilter, DewuInfoListView, DewuInfoView, ProductSearchView, ProductSlugView, \
    ProductIdView, CategoryTreeView, \
    LineTreeView, ProductUpdateView, LineNoChildView, \
    CategoryNoChildView, ProductSizeView, AddProductView, ListProductView, ProductView, CollabView, \
    DewuInfoListSpuIdView, SuggestSearch, ProductSimilarView, MainPageBlocks, GetHeaderPhoto, MakeRansomRequest, \
    SGInfoListSkuView, SGInfoListView, SGInfoView, BrandSearchView, AddFilterSearch, AvailableSize, UpdatePrice, \
    PopularSpuIdView, HideProductView, DewuInfoCount, HideProductSpiIdView, AddPhotoBlackList, ProductSlugAndPhoto, \
    PhotoWhiteList, AddListProductsView, ProductsCountView, view_photo_for_rate, rate_photo, SearchBySkuView, MaterialView, MyScoreForProduct, ProductFullSlugView

# router = routers.DefaultRouter()
# router.register("", ProductViewSet, 'product')
#
# urlpatterns = router.urls
# # urlpatterns.append(path('all/<int:page_number>', ProductsView.as_view()))
# urlpatterns.append(path('slug/<str:slug>', ProductSlugView.as_view()))
# # urlpatterns.append(path('id/<int:id>', ProductIdView.as_view()))


router_product = routers.DefaultRouter()
router_product.register("products2", ProductViewSet, basename="product")

router_cat = routers.DefaultRouter()
router_cat.register("categories", CategoryViewSet, basename="category")

router_line = routers.DefaultRouter()
router_line.register("lines", LinesViewSet, basename="lines")

router_brand = routers.DefaultRouter()
router_brand.register("brands", BrandViewSet, basename="brands")

router_color = routers.DefaultRouter()
router_color.register("colors", ColorViewSet, basename="colors")

router_collection = routers.DefaultRouter()
router_collection.register("collections", CollectionViewSet, basename="collections")

# router_material = routers.DefaultRouter()
# router_material.register("materials", MaterialViewSet, basename="materials")

sitemaps = {
    'products': ProductSitemap
}

urlpatterns = [
    path("products/", ProductView.as_view(), name="home"),
    path("", include(router_collection.urls)),
    path("materials/", MaterialView.as_view()),
    path("", include(router_product.urls)), path("", include(router_cat.urls)),
    path("", include(router_brand.urls)), path("", include(router_line.urls)),
    path("", include(router_color.urls)),
    path('slug/<str:slug>', ProductSlugView.as_view(), name='product_detail'), path('similar/<int:product_id>', ProductSimilarView.as_view()),
    path('slug_full/<str:slug>', ProductFullSlugView.as_view()),
    path("tree_cat", CategoryTreeView.as_view()), path("tree_line", LineTreeView.as_view()),
    path("cat_no_child", CategoryNoChildView.as_view()), path("line_no_child", LineNoChildView.as_view()),
    path("update/<int:product_id>", ProductUpdateView.as_view()), path("size", ProductSizeView.as_view()),
    path("add_product", AddProductView.as_view()), path("list_product", ListProductView.as_view()),
    path("product_search", ProductSearchView.as_view()),
    path("dewu_info/<int:spu_id>", DewuInfoView.as_view()), path("dewu_info", DewuInfoListView.as_view()),
    path("size_table", SizeTableForFilter.as_view()), path("collabs", CollabView.as_view()),
    path("dewu_info_list", DewuInfoListSpuIdView.as_view()), path("suggest_search", SuggestSearch.as_view()),
    path("main_page", MainPageBlocks.as_view()), path("header_photo", GetHeaderPhoto.as_view()),
    path("ransom_request", MakeRansomRequest.as_view()), path("sg_info_list", SGInfoListSkuView.as_view()),
    path("sg_info", SGInfoListView.as_view()), path("sg_info/<str:sku>", SGInfoView.as_view()),
    path("search_brands", BrandSearchView.as_view()), path("add_filter_search", AddFilterSearch.as_view()),
    path("sizes_info/<int:product_id>", AvailableSize.as_view()), path("update_price", UpdatePrice.as_view()),
    path("popular_spu_id", PopularSpuIdView.as_view()),
    path("hide_product/<int:spu_id>/<int:property_id>", HideProductView.as_view()),
    path("hide_product/<int:spu_id>", HideProductSpiIdView.as_view()),
    path("dewu_info_count", DewuInfoCount.as_view()),
    path("add_photo_black_list/<int:product_id>/<int:photo_id>", AddPhotoBlackList.as_view()),
    path("photo_white_list/<int:product_id>", PhotoWhiteList.as_view()),
    path("product_photo_and_slug", ProductSlugAndPhoto.as_view()),
    path("add_list_spu_id_products", AddListProductsView.as_view()), path("products_count", ProductsCountView.as_view()),
    path('pict', view_photo_for_rate, name='view_photo'),
    path("my_score_for_product/<int:id>", MyScoreForProduct.as_view()),
    path('rate_pict', rate_photo, name='rate_photo'), path("search_bu_sku", SearchBySkuView.as_view()), path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]



