
from rest_framework import routers
from .api import UserViewSet
from django.urls import path, re_path, include
from .views import SizeTableInLK, UserSizeInfo, AddFavoriteBrands, UserLastSeenView, UserRegister, UserInfoView, \
    UserAddressView, UserChangePassword, UserLoginView, TokenVerifyView, TokenRefreshView,GoogleAuth, initiate_google_auth


router = routers.DefaultRouter()
router.register("", UserViewSet, 'user')

urlpatterns = router.urls
urlpatterns.append(path('last_seen/<int:user_id>', UserLastSeenView.as_view()))
urlpatterns.append(path('user_info/<int:user_id>', UserInfoView.as_view(), name='user_info'))
urlpatterns.append(path('address/<int:user_id>', UserAddressView.as_view()))
urlpatterns.append(path('address/<int:user_id>/<int:address_id>', UserAddressView.as_view()))
urlpatterns.append(path('register', UserRegister.as_view(), name='register'))


urlpatterns.append(path('change_psw', UserChangePassword.as_view()))

urlpatterns.append(path('login', UserLoginView.as_view(), name='token_obtain_pair'))
urlpatterns.append(path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')) #кастом
urlpatterns.append(path('token/verify/', TokenVerifyView.as_view(), name='token_verify')) #кастом
urlpatterns.append(path('favorite_brand/<int:user_id>/<int:brand_id>', AddFavoriteBrands.as_view())) #кастом
urlpatterns.append(path('size_info', UserSizeInfo.as_view()))
urlpatterns.append(path('get_size_table', SizeTableInLK.as_view()))


urlpatterns.append(path('auth/complete/google-oauth2/', GoogleAuth.as_view(), name='google-auth-callback'))
urlpatterns.append(path('auth/google/', initiate_google_auth))