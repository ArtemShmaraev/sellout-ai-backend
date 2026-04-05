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

from orders.models import ShoppingCart, Status, OrderUnit, Order

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo, SizeTable, SizeTranslationRows
from django.core.exceptions import ObjectDoesNotExist

from products.serializers import ProductMainPageSerializer
from promotions.models import PromoCode
from shipping.models import ProductUnit, DeliveryType, AddressInfo
from users.models import User, EmailConfirmation, UserStatus
from products.tools import get_text


class Command(BaseCommand):

    def handle(self, *args, **options):

        import json

        # Открываем файл JSON
        file_path = "temp_main_men_withproducts.json"
        with open(file_path, "r", encoding="utf-8") as json_file:
            # Загружаем данные из файла в словарь
            data = json.load(json_file)

        # Теперь переменная data содержит данные из JSON-файла в виде словаря
        for block in data:
            if block['type'] == 'selection':
                products = []
                for p in block['products']:
                    id_p = p['slug']
                    if Product.objects.filter(slug=id_p).exists():
                        prod = Product.objects.get(slug=id_p)
                        if prod.min_price != 0 and prod.available_flag:
                            products.append(ProductMainPageSerializer(prod).data)
                block['products'] = products


        # Запись списка в JSON-файл
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False)

# # Обработка результатов запроса
# for row in results:
#     print(row[0], row[1])
