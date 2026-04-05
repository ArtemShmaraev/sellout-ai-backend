# {"requestId":"86c89fe0-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"86d8cc80-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"86f10f70-b481-11ee-bcfc-a16e0e850f4a"}
# {"requestId":"870a63d0-b481-11ee-a0c0-2b5dc98ce3ba"}
# {"requestId":"871c1710-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"873173d0-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"87491a80-b481-11ee-bcfc-a16e0e850f4a"}
# {"requestId":"8763ce70-b481-11ee-bcfc-a16e0e850f4a"}
# {"requestId":"877cada0-b481-11ee-a0c0-2b5dc98ce3ba"}
# {"requestId":"87947b60-b481-11ee-bcfc-a16e0e850f4a"}
# {"requestId":"87ac4920-b481-11ee-bcfc-a16e0e850f4a"}
# {"requestId":"87c2b750-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"87d86230-b481-11ee-a0c0-2b5dc98ce3ba"}
# {"requestId":"87f3b260-b481-11ee-bcfc-a16e0e850f4a"}
# {"requestId":"880da300-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"8820dce0-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"8859c730-b481-11ee-a0c0-2b5dc98ce3ba"}
# {"requestId":"886deb70-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"89f10900-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"8a083a80-b481-11ee-a0c0-2b5dc98ce3ba"}
# {"requestId":"8a21b5f0-b481-11ee-bcfc-a16e0e850f4a"}
# {"requestId":"8a37d600-b481-11ee-a0c0-2b5dc98ce3ba"}
# {"requestId":"8a4c9680-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"8a648b50-b481-11ee-bcfc-a16e0e850f4a"}
# {"requestId":"8a78fdb0-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"8a91dce0-b481-11ee-a0c0-2b5dc98ce3ba"}
# {"requestId":"8aa82400-b481-11ee-bcfc-a16e0e850f4a"}
# {"requestId":"8abb84f0-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"8acfa930-b481-11ee-b3bf-bd0e42e02359"}
# {"requestId":"8aecce20-b481-11ee-bcfc-a16e0e850f4a"}
# {"requestId":"8b053820-b481-11ee-a0c0-2b5dc98ce3ba"}
# {"requestId":"8b1823e0-b481-11ee-b3bf-bd0e42e02359"}


import math
import os
import random
from itertools import count
from time import time

import requests
from django.core import signing
from django.core.management.base import BaseCommand
import json

from django.core.paginator import Paginator
from django.db import transaction, connection
from django.db.models import OuterRef, Subquery, F, BooleanField, Case, When, Count, Max
from json2xml.utils import readfromstring

from orders.models import ShoppingCart, Status, OrderUnit, Order

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo, SizeTable, SizeTranslationRows
from django.core.exceptions import ObjectDoesNotExist

from products.serializers import ProductMainPageSerializer
from promotions.models import PromoCode
from shipping.models import ProductUnit, DeliveryType, AddressInfo
from users.models import User, EmailConfirmation, UserStatus
from products.tools import get_text, get_fid_product_all
from json2xml import json2xml
import xml.etree.ElementTree as ET


class Command(BaseCommand):

    def handle(self, *args, **options):
        k = 8
        page = 1000
        file_name = f"fids/Кроссовки_до_20000_1{k}.xml"

        lines = list(Line.objects.exclude(score=0).values_list("view_name", flat=True))
        products_id = Product.objects.filter(available_flag=True, is_custom=False, min_price__lt=20000, categories__name="Кроссовки", lines__view_name__in=lines).values_list("id", flat=True).distinct()

        products = Product.objects.filter(id__in=products_id).order_by("-score_product_page")[(k-1)*page:k*page]
        print(products.count())
        print(products.first().min_price)


        fid = get_fid_product_all(products)

        with open(file_name, 'wb') as f:
            f.write(fid)

        # Возвращение файла XML в ответе
        # with open(file_name, 'rb') as f:
        #     response = HttpResponse(f, content_type='application/xml')
        #     response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        #     return response
        # return HttpResponse(fid, content_type="application/xml")

        # token = "y0_AgAAAAAn9wHCAAryqAAAAADz-xd2E4U3tlycQPKRrTiKMAMK33VNv84"
        # headers = {
        #     "Authorization": f"OAuth {token}"
        # }
        # user_id = requests.get("https://api.webmaster.yandex.net/v4/user", headers=headers).json()['user_id']
        # host_id = \
        #     requests.get(f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts", headers=headers).json()["hosts"][
        #         0][
        #         'host_id']
        #
        # print(host_id)
        # print(user_id)
        # s = requests.get(f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{host_id}/feeds/add/info", json={
        #     "requestId": "8b1823e0-b481-11ee-b3bf-bd0e42e02359"
        # }, headers=headers)
        # print(s.text)
        # for i in range(50):
        #     fid = {
        #         "feed": {
        #             "url": f"https://sellout.su/api/v1/product/yml_fid/{i + 1}.xml?size=1000",
        #             "type": "GOODS",
        #             "regionIds": [
        #                 225
        #             ]
        #         }
        #     }
        #     post = requests.post(f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{host_id}/feeds/add/start", headers=headers, json=fid)
        #     print(post.text)

        # # fid = requests.post(f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{host_id}/feeds/batch/add")
        # fid = requests.get(f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{host_id}/feeds/list", headers=headers)
        # print(fid)
        # products = Product.objects.filter(available_flag=True, is_custom=False).order_by("-score_product_page")
        # size_page = 10_000
        # count = products.count()
        # # for page in range(0, count, size_page):
        # #     products_page = products[page:page + size_page]
        # #     fid =

        # print(get_fid_product(products[0]))



