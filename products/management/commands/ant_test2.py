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
        try:
            # Измеряем время выполнения запроса к базе данных
            t_db = time()
            products = Product.objects.all()[:200]
            db_time = time() - t_db

            # Измеряем время выполнения сериализации
            t_serialization = time()
            serialized = ProductMainPageSerializer(products, many=True)
            serialization_time = time() - t_serialization

            new_time = time()
            serialized_data = serialized.data
            from django.db import connection
            print(connection.queries)


            # Выводим информацию о времени выполнения каждого процесса
            self.stdout.write(self.style.SUCCESS(f'Time taken for database query: {db_time:.6f} seconds'))
            self.stdout.write(self.style.SUCCESS(f'Time taken for serialization: {serialization_time:.6f} seconds'))
            self.stdout.write(self.style.SUCCESS(f'Time taken for data: {time() - new_time:.6f} seconds'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {str(e)}'))

# # Обработка результатов запроса
# for row in results:
#     print(row[0], row[1])
