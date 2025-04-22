from rest_framework import routers
from .api import UserViewSet
from django.urls import path, re_path
from .views import UserLastSeenView, UserRegister, UserInfoView, UserAddressView, UserChangePassword, UserLoginView, TokenVerifyView, TokenRefreshView

router = routers.DefaultRouter()
router.register("", UserViewSet, 'user')

urlpatterns = router.urls
urlpatterns.append(path('last_seen/<int:user_id>', UserLastSeenView.as_view()))
urlpatterns.append(path('user_info/<int:user_id>', UserInfoView.as_view(), name='user_info'))
urlpatterns.append(path('address/<int:user_id>', UserAddressView.as_view()))
urlpatterns.append(path('address/<int:user_id>/<int:address_id>', UserAddressView.as_view()))
urlpatterns.append(path('register', UserRegister.as_view(), name='register'))
urlpatterns.append(path('change_psw', UserChangePassword.as_view()))
# urlpatterns.append(path('login', LoginUser.as_view()))

urlpatterns.append(path('login', UserLoginView.as_view(), name='token_obtain_pair'))
urlpatterns.append(path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')) #кастом
urlpatterns.append(path('token/verify/', TokenVerifyView.as_view(), name='token_verify')) #кастом