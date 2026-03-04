from django.core.cache import cache
from django.db import models

from sellout.settings import CACHE_TIME


# class WishlistUnit(models.Model):
#     product = models.ForeignKey("products.Product", on_delete=models.CASCADE, null=False, blank=False,
#                                 related_name="wishlist_units")
#     # size = models.ForeignKey("products.SizeTranslationRows", on_delete=models.PROTECT, null=True, blank=True,
#     #                          related_name="wishlist_units")
#     wishlist = models.ForeignKey("Wishlist", on_delete=models.CASCADE, null=False, blank=False,
#                                  related_name="wishlist_units")
#
#     def __str__(self):
#         return f'{self.product}  in wishlist'


class Wishlist(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=False, blank=False,
                             related_name="wishlist")
    products = models.ManyToManyField("products.Product", blank=True)

    def __str__(self):
        return f'{self.user}'

    def get_wishlist_product_ids(self, clear=False):
        cache_header_key = f"wishlist_id:{self.id}"  # Уникальный ключ для каждой URL
        cached_header = cache.get(cache_header_key)
        if cached_header is not None and not clear:
            wl = cached_header
        else:
            wl = set(self.products.all().values_list("id", flat=True))
            cache.set(cache_header_key, wl, CACHE_TIME * 5)
        return wl
