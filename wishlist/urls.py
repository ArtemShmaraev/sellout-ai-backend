from django.urls import path, re_path
from .views import UserWishlist, UserAddWishlist, UserDeleteWishlist, UserAddWishlistNoSize, UserChangeSizeWishlist


urlpatterns = [path('<int:user_id>', UserWishlist.as_view()),  # инфа о вл
               path('add/<int:user_id>/<int:product_id>/<int:size_id>', UserAddWishlist.as_view()),  # добавить с размером
               path('delete/<int:wishlist_unit_id>', UserDeleteWishlist.as_view()),  # удалить юнит
               path('add_no_size/<int:user_id>/<int:product_id>', UserAddWishlistNoSize.as_view()),  # добавить без размера
               path('change_size/<int:user_id>/<int:wishlist_unit_id>/<int:size_id>', UserChangeSizeWishlist.as_view())   # изменить размер
               ]
