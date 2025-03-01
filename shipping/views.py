from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductUnitSerializer
from .models import ProductUnit
from wishlist.models import Wishlist, WishlistUnit
import json


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
        ans = dict()
        ans["id"] = data[0]['product']['id']
        ans['brands'] = data[0]['product']['brands']
        ans['name'] = data[0]['product']['name']
        ans['bucket_link'] = data[0]['product']['bucket_link']

        min_price = data[0]["final_price"]
        for d in data:
            min_price = min(min_price, d["final_price"])
        ans['min_price'] = min_price
        wishlist = Wishlist.objects.get(user_id=user_id)
        data = WishlistUnit.objects.filter(wishlist=wishlist, product_id=product_id)
        ans['in_wishlist'] = len(data) > 0
        return Response(ans)
# Create your views here.

