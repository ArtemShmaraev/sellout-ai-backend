from django.urls import path, re_path
from .views import UserWishlist


urlpatterns = [path('<int:user_id>', UserWishlist.as_view()),  # инфа о вл
               path('<user_id>/<int:wishlist_unit_id>', UserWishlist.as_view()),  # удалить юнит
               # path('change_size/<int:user_id>/<int:wishlist_unit_id>/<int:size_id>', UserChangeSizeWishlist.as_view())   # изменить размер
               ]
