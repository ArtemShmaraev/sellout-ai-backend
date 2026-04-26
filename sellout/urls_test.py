"""URLConf для тестов: только модуль ЛК и заказов.

products/views.py содержит SyntaxError (строка 96) и импорт его роутов
ломает любой HTTP-запрос в тестах. Поэтому в тестах используется
этот минимальный URLConf, включающий только зону ВКР.
"""
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('api/v1/user/', include('users.urls')),
    path('api/v1/promo/', include('promotions.urls')),
    path('api/v1/order/', include('orders.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
