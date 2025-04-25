from django.db import models


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
    user = models.ForeignKey("users.User", on_delete=models.PROTECT, null=False, blank=False,
                             related_name="wishlist")
    products = models.ManyToManyField("products.Product", blank=True)

    def __str__(self):
        return f'{self.user}'
