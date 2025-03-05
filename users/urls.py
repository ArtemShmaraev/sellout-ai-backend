from rest_framework import routers
from .api import UserViewSet
from django.urls import path, re_path
from .views import UserLastSeenView, RegisterUser, LoginUser, UserInfoView, AddressUserView

router = routers.DefaultRouter()
router.register("", UserViewSet, 'user')

urlpatterns = router.urls
urlpatterns.append(path('last_seen/<int:user_id>', UserLastSeenView.as_view()))
urlpatterns.append(path('user_info/<int:user_id>', UserInfoView.as_view()))
urlpatterns.append(path('address/<int:user_id>', AddressUserView.as_view()))
urlpatterns.append(path('register', RegisterUser.as_view()))
urlpatterns.append(path('login', LoginUser.as_view()))