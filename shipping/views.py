from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductUnitSerializer
from .models import ProductUnit
from wishlist.models import Wishlist, WishlistUnit
from products.models import Product
from products.serializers import ProductSerializer
import json
from sellout.permissions import IsOwnerOrReadOnly


class ProductUnitProductView(APIView):
    def get(self, request, product_id):
        s = ProductUnit.objects.filter(product_id=product_id)
        return Response(ProductUnitSerializer(s, many=True).data)


class ProductUnitProductMainView(APIView):
    def get(self, request, product_id, user_id):
        s = ProductUnit.objects.filter(product_id=product_id)
        data = ProductUnitSerializer(s, many=True).data
        if len(data) == 0:
            return Response([])
        ans = ProductSerializer(Product.objects.get(id=product_id)).data
        min_price = data[0]["final_price"]
        for d in data:
            min_price = min(min_price, d["final_price"])
        ans['min_price'] = min_price

        if request.user.id == user_id or request.user.is_staff:
            wishlist = Wishlist.objects.get(user_id=user_id)
            data = WishlistUnit.objects.filter(wishlist=wishlist, product_id=product_id)
            ans['in_wishlist'] = len(data) > 0
        else:
            return Response(ans)

# Create your views here.

