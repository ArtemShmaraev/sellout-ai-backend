from rest_framework import routers
from .api import UserViewSet
from django.urls import path, re_path
from .views import UserLastSeenView

router = routers.DefaultRouter()
router.register("", UserViewSet, 'user')

urlpatterns = router.urls
urlpatterns.append(path('last_seen/<int:id>', UserLastSeenView.as_view()))