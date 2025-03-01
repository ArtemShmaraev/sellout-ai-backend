from django.shortcuts import render
from .models import Wishlist, WishlistUnit
# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from products.serializers import ProductSerializer, SizeSerializer
from users.models import User
from .serializers import WishlistSerializer, WishlistUnitSerializer
from products.models import Product
from products.models import Size
from sellout.settings import url

import requests


class UserWishlist(APIView):
    def get(self, request, user_id):

        wishlist_id = WishlistSerializer(Wishlist.objects.get(user_id=user_id)).data['id']
        data = WishlistUnitSerializer(WishlistUnit.objects.filter(wishlist_id=wishlist_id), many=True).data

        ans = []
        for el in data:
            main = requests.get(f"{url}/api/v1/product_unit/product_main/{el['product']}").json()
            ans.append({'product': main, "size": SizeSerializer(Size.objects.filter(id=el['size'])[0]).data,
                        'product_unit': requests.get(f"{url}/api/v1/product_unit/product/{el['product']}").json()[0]})
        return Response(ans)


class UserAddWishlist(APIView):
    def post(self, request, user_id, product_id, size_id):
        wishlist_id = WishlistSerializer(Wishlist.objects.get(user=user_id)).data['id']
        wishlist = Wishlist.objects.get(id=wishlist_id)
        product = Product.objects.get(id=product_id)
        size = Size.objects.get(id=size_id)
        wl = WishlistUnit(product=product, size=size, wishlist=wishlist)
        wl.save()
        return Response('Ok')


class UserDeleteWishlist(APIView):
    def delete(self, request, user_id, product_id, size_id):
        wishlist = Wishlist.objects.get(user_id=user_id)
        wishlist_unit = WishlistUnit.objects.get(wishlist=wishlist, product_id=product_id, size_id=size_id)
        wishlist_unit.delete()
        return Response('Ok')