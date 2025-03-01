from rest_framework import routers
from .api import ProductViewSet
from django.urls import path
from .views import ProductsView

router = routers.DefaultRouter()
router.register("", ProductViewSet, 'product')

urlpatterns = router.urls
urlpatterns.append(path('all/<int:page_number>', ProductsView.as_view()))
