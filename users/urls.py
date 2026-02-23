from rest_framework import routers
from .api import UserViewSet
from django.urls import path, re_path, include
from .views import SizeTableInLK, UserSizeInfo, AddFavoriteBrands, FavoriteBrands, UserLastSeenView, UserRegister, UserInfoView, \
    UserAddressView, UserChangePassword, UserLoginView, TokenVerifyView, TokenRefreshView, GoogleAuth, \
    initiate_google_auth, UserForSpamEmail, confirm_email, ReferralProgram, SendSetPassword, UserChangePasswordLK, SendVerifyEmail, WaitList, LoyaltyProgram, UserReferalPromo, AddMailingList,  AddPartnerList, ValidCaptcha

router = routers.DefaultRouter()
# router.register("", UserViewSet, 'user')

urlpatterns = router.urls
urlpatterns.append(path('last_seen/<int:user_id>', UserLastSeenView.as_view()))
urlpatterns.append(path('user_info/<int:user_id>', UserInfoView.as_view(), name='user_info'))
urlpatterns.append(path('address/<int:user_id>', UserAddressView.as_view()))
urlpatterns.append(path('address/<int:user_id>/<int:address_id>', UserAddressView.as_view()))
urlpatterns.append(path('register', UserRegister.as_view(), name='register'))

urlpatterns.append(path('change_pwd/<str:uidb64>/<str:token>', UserChangePassword.as_view()))
urlpatterns.append(path('change_pwd_lk/<int:user_id>', UserChangePasswordLK.as_view()))

urlpatterns.append(path('login', UserLoginView.as_view(), name='token_obtain_pair'))
urlpatterns.append(path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'))  # кастом
urlpatterns.append(path('token/verify/', TokenVerifyView.as_view(), name='token_verify'))  # кастом
urlpatterns.append(path('favorite_brand/<int:user_id>/<int:brand_id>', AddFavoriteBrands.as_view()))  # кастом
urlpatterns.append(path('favorite_brand/<int:user_id>', FavoriteBrands.as_view()))  # кастом
urlpatterns.append(path('size_info', UserSizeInfo.as_view()))
urlpatterns.append(path('get_size_table', SizeTableInLK.as_view()))
urlpatterns.append(path('loyalty_program', LoyaltyProgram.as_view()))
urlpatterns.append(path('referral_program', ReferralProgram.as_view()))


urlpatterns.append(path('auth/complete/google/', GoogleAuth.as_view(), name='google-auth-callback'))
urlpatterns.append(path('mailing_list', UserForSpamEmail.as_view()))
urlpatterns.append(path('send_set_pwd/<str:email>', SendSetPassword.as_view()))
urlpatterns.append(path('send_verify_email/<int:user_id>', SendVerifyEmail.as_view()))
urlpatterns.append(path('auth/google/', initiate_google_auth))
urlpatterns.append(path('waiting_list/<int:product_id>', WaitList.as_view()))
urlpatterns.append(path('referral_promo', UserReferalPromo.as_view()))
urlpatterns.append(path('add_mailing', AddMailingList.as_view()))
urlpatterns.append(path('add_partner', AddPartnerList.as_view()))
urlpatterns.append(path('valid_captcha/<str:captcha_token>', ValidCaptcha.as_view()))
