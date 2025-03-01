from rest_framework import routers
from django.urls import path, re_path
from .views import UserWishlist, UserAddWishlist, UserDeleteWishlist

urlpatterns = []
urlpatterns.append(path('<int:user_id>', UserWishlist.as_view()))
urlpatterns.append(path('add/<int:user_id>/<int:product_id>/<int:size_id>', UserAddWishlist.as_view()))
urlpatterns.append(path('delete/<int:user_id>/<int:product_id>/<int:size_id>', UserDeleteWishlist.as_view()))