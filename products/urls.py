from rest_framework import routers
from .api import ProductViewSet

router = routers.DefaultRouter()
router.register("", ProductViewSet, 'product')

urlpatterns = router.urls

