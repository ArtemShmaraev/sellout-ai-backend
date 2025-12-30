# {"requestId":"504514a0-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"505a9870-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"50757370-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"508d6840-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"50ab5080-b079-11ee-95b5-2b5dc98ce3ba"}
# {"requestId":"50c54120-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"50df31c0-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"50fb4540-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"5115d220-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"512d9fe0-b079-11ee-a826-cf891f5fc84f"}
# {"requestId":"514371d0-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"515af170-b079-11ee-a826-cf891f5fc84f"}
# {"requestId":"51799d00-b079-11ee-95b5-2b5dc98ce3ba"}
# {"requestId":"5194ed30-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"51ace200-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"51c795f0-b079-11ee-a826-cf891f5fc84f"}
# {"requestId":"51e1fbc0-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"51ff47c0-b079-11ee-95b5-2b5dc98ce3ba"}
# {"requestId":"521ba960-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"5231f080-b079-11ee-a826-cf891f5fc84f"}
# {"requestId":"524be120-b079-11ee-a826-cf891f5fc84f"}
# {"requestId":"5269a250-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"528ba940-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"52a572d0-b079-11ee-a826-cf891f5fc84f"}
# {"requestId":"52bccb60-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"52d0efa0-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"52e70fb0-b079-11ee-95b5-2b5dc98ce3ba"}
# {"requestId":"52fe6840-b079-11ee-a826-cf891f5fc84f"}
# {"requestId":"531b1800-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"5333d020-b079-11ee-95b5-2b5dc98ce3ba"}
# {"requestId":"534b28b0-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"53656770-b079-11ee-95b5-2b5dc98ce3ba"}
# {"requestId":"537b3960-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"5391f5b0-b079-11ee-95b5-2b5dc98ce3ba"}
# {"requestId":"53abbf40-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"53c7abb0-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"53e03cc0-b079-11ee-a826-cf891f5fc84f"}
# {"requestId":"53fc7750-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"541619d0-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"54342920-b079-11ee-95b5-2b5dc98ce3ba"}
# {"requestId":"544d7d80-b079-11ee-b2c7-bd0e42e02359"}
# {"requestId":"546b8cd0-b079-11ee-95b5-2b5dc98ce3ba"}
# {"requestId":"5483a8b0-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"549a16e0-b079-11ee-90ba-ebc17f8e26ef"}
# {"requestId":"54b7b100-b079-11ee-95b5-2b5dc98ce3ba"}
# {"requestId":"54cdf820-b079-11ee-b2c7-bd0e42e02359"}



import math
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
from products.tools import get_text
from json2xml import json2xml
import xml.etree.ElementTree as ET

class Command(BaseCommand):

    def handle(self, *args, **options):
        token = "y0_AgAAAAAn9wHCAAryqAAAAADz-xd2E4U3tlycQPKRrTiKMAMK33VNv84"
        headers = {
            "Authorization": f"OAuth {token}"
        }
        user_id = requests.get("https://api.webmaster.yandex.net/v4/user", headers=headers).json()['user_id']
        host_id = \
            requests.get(f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts", headers=headers).json()["hosts"][
                0][
                'host_id']

        print(host_id)
        print(user_id)
        for i in range(50):
            fid = {
                "feed": {
                    "url": f"https://sellout.su/api/v1/product/yml_fid/{i + 1}.xml?size=1000",
                    "type": "GOODS",
                    "regionIds": [
                        225
                    ]
                }
            }
            post = requests.post(f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{host_id}/feeds/add/start", headers=headers, json=fid)
            print(post.text)

        # # fid = requests.post(f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{host_id}/feeds/batch/add")
        # fid = requests.get(f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{host_id}/feeds/list", headers=headers)
        # print(fid)
        # products = Product.objects.filter(available_flag=True, is_custom=False).order_by("-score_product_page")
        # size_page = 10_000
        # count = products.count()
        # # for page in range(0, count, size_page):
        # #     products_page = products[page:page + size_page]
        # #     fid =



        print(get_fid_product(products[0]))


s = """
<?xml version="1.0" encoding="UTF-8"?>
<yml_catalog date="2020-11-22T14:37:38+03:00">
    <shop>
        <name>Sellout</name>
        <company>Sellout</company>
        <url>https://sellout.su</url>
        <currencies>
            <currency id="RUR" rate="1"/>
        </currencies>
        <categories>
            <category id="1">Бытовая техника</category>
            <category id="10" parentId="1">Мелкая техника для кухни</category>
        </categories>
        <delivery-options>
            <option cost="200" days="1"/>
        </delivery-options>
        <offers>
            <offer id="9012">
                <name>Мороженица Brand 3811</name>
                <url>http://best.seller.ru/product_page.asp?pid=12345</url>
                <price>8990</price>
                <currencyId>RUR</currencyId>
                <categoryId>10</categoryId>
                <delivery>true</delivery>
                <delivery-options>
                    <option cost="300" days="1" order-before="18"/>
                </delivery-options>
                <param name="Цвет">белый</param>
                <weight>3.6</weight>
                <dimensions>20.1/20.551/22.5</dimensions>
            </offer>
        </offers>
    </shop>
</yml_catalog>
"""
