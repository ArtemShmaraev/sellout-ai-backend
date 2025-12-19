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

        fid = requests.post(f"https://api.webmaster.yandex.net/v4/user/{user_id}/hosts/{host_id}/feeds/batch/add")
        products = Product.objects.filter(available_flag=True, is_custom=False).order_by("-score_product_page")
        size_page = 10_000
        count = products.count()
        # for page in range(0, count, size_page):
        #     products_page = products[page:page + size_page]
        #     fid =

        def get_fid_product(product):
            yml_catalog = {"key": {
                "@name": "@date",
                "#text": product.last_upd
            }, "shop": {}}
            fid = {}
            fid['shop'] = {}
            fid['shop']['name'] = "Sellout"
            fid['shop']['company'] = "Sellout"
            fid['shop']['url'] = "https://sellout.su"
            fid['shop']['categories'] = []
            categories = product.categories.all()
            for category in categories:
                if category.parent_category is not None:
                    fid['shop']['categories'].append({"category": {"id": category.id, 'name': category.name,
                                                                   "parentId": category.parent_category.id}})
                else:
                    fid['shop']['categories'].append({"category": {"id": category.id, 'name': category.name}})

            offer = {}
            offer['id'] = product.id
            offer['name'] = product.get_full_name()
            offer['vendor'] = product.brands.first().name if product.collab is None else product.collab.name
            offer['vendorCode'] = product.manufacturer_sku
            offer['url'] = f"https://sellout.su/products/{product.slug}"
            offer['price'] = product.min_price
            offer['currencyId'] = "RUR"
            offer['picture'] = product.bucket_link.order_by("id").first().url
            offer['categoryId'] = product.categories.order_by("-id").first().id
            offer['category'] = product.categories.order_by("-id").first().name
            offer['delivery'] = True
            offer['description'] = f"""<description>
                                <![CDATA[     
                                <h3>{product.get_full_name()}</h3>
                                <p>Оригинал {product.get_full_name()} можно заказать прямо сейчас. Выгодные цены и бонусы ждут вас. Сделайте свой шаг в мир моды.</p>
                                ]]>"""
            fid['shop']['offers'] = []
            fid['shop']['offers'].append({"offer": offer})
            yml_catalog = fid
            xml = json2xml.Json2xml(yml_catalog, wrapper="yml_catalog")
            xml.attr_type = False
            xml = xml.to_xml()
            root = ET.fromstring(xml)
            # print(xml)
            currencies = ET.Element('currencies')

            # Создание нового элемента currency
            new_currency = ET.Element('currency')
            new_currency.set('id', 'RUR')
            new_currency.set('rate', '1')

            # Добавление элемента currency в currencies
            currencies.append(new_currency)

            # Добавление currencies в корневой элемент
            shop = root.find('shop')
            shop.append(currencies)
            xml = ET.tostring(root, encoding='utf-8').decode('utf-8')

            yml_catalog = ET.Element('yml_catalog', attrib={"date": str(product.last_upd)})
            # Создаем элемент shop и добавляем его в корневой элемент
            shop = ET.Element('shop')
            yml_catalog.append(shop)

            # Создаем элементы внутри shop
            shop_name = ET.Element('name')
            shop_name.text = "Sellout"
            shop_company = ET.Element('company')
            shop_company.text = "Sellout"
            shop_url = ET.Element('url')
            shop_url.text = "https://sellout.su"
            shop_categories = ET.Element('categories')
            shop.append(shop_name)
            shop.append(shop_company)
            shop.append(shop_url)
            shop.append(shop_categories)

            # Проходимся по категориям и добавляем их в shop
            categories = product.categories.all()
            for category in categories:
                category_elem = ET.Element('category', attrib={"id": str(category.id), "name": category.name})
                if category.parent_category is not None:
                    category_elem.set("parentId", str(category.parent_category.id))
                shop_categories.append(category_elem)

            # Создаем элемент offer
            offer = ET.Element('offer', attrib={"id": str(product.id)})
            offer_name = ET.Element('name')
            offer_name.text = product.get_full_name()
            offer_vendor = ET.Element('vendor')
            offer_vendor.text = product.brands.first().name if product.collab is None else product.collab.name
            offer_vendorCode = ET.Element('vendorCode')
            offer_vendorCode.text = product.manufacturer_sku
            offer_url = ET.Element('url')
            offer_url.text = f"https://sellout.su/products/{product.slug}"
            offer_price = ET.Element('price')
            offer_price.text = str(product.min_price)
            offer_currencyId = ET.Element('currencyId')
            offer_currencyId.text = "RUR"
            offer_picture = ET.Element('picture')
            offer_picture.text = product.bucket_link.order_by("id").first().url
            offer_categoryId = ET.Element('categoryId')
            offer_categoryId.text = str(product.categories.order_by("-id").first().id)
            offer_category = ET.Element('category')
            offer_category.text = product.categories.order_by("-id").first().name
            offer_delivery = ET.Element('delivery')
            offer_delivery.text = "True"
            offer_description = ET.Element('description')
            offer_description.text = f"""
                <![CDATA[     
                <h3>{product.get_full_name()}</h3>
                <p>Оригинал {product.get_full_name()} можно заказать прямо сейчас. Выгодные цены и бонусы ждут вас. Сделайте свой шаг в мир моды.</p>
                ]]>
            """.format(product=product)

            # Добавляем элементы offer в offer и добавляем его в shop
            offer.append(offer_name)
            offer.append(offer_vendor)
            offer.append(offer_vendorCode)
            offer.append(offer_url)
            offer.append(offer_price)
            offer.append(offer_currencyId)
            offer.append(offer_picture)
            offer.append(offer_categoryId)
            offer.append(offer_category)
            offer.append(offer_delivery)
            offer.append(offer_description)
            shop_offers = ET.Element('offers')
            shop_offers.append(offer)
            shop.append(shop_offers)

            # Создаем XML-документ
            tree = ET.ElementTree(yml_catalog)
            xml_str = ET.tostring(yml_catalog, encoding='utf8', method='xml')

            # Преобразуем байтовую строку в строку unicode
            xml = xml_str.decode('utf-8')


            return xml

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
