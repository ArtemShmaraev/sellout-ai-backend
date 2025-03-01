from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from products.serializers import ProductSerializer, SizeSerializer
from .models import User
from products.models import Product
from products.models import Size
from sellout.settings import url

import requests


class UserLastSeenView(APIView):
    def get(self, request, id):
        def s_id(product):
            return requests.get(f"{url}/api/v1/product_unit/product_main/{product['id']}/{id}").json()

        s = list(map(s_id, list(ProductSerializer(User.objects.filter(id=id)[0].last_viewed_products, many=True).data[-7:])))
        return Response(s)



