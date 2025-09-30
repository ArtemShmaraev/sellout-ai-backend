import math
import random
from itertools import count
from time import time

import requests
from django.core import signing
from django.core.management.base import BaseCommand
import json

from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import OuterRef, Subquery, F, BooleanField, Case, When, Count, Max

from orders.models import ShoppingCart, Status, OrderUnit, Order
from orders.serializers import OrderSerializer

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
        # user = User.objects.all()
        # for us in user:
        #     us.extra_contact = us.email
        #     us.save()
        users = User.objects.filter(gender__name__in=["M"]).first()
        print(users)
        print(users.gender.name)

        # alf = "qwertyuiopasdfghjklzxcvbnmйцукенгшщзхъэждлорпавыфячсмитьбю1234567890.&' "
        # brands = Line.objects.all()
        # for brand in brands:
        #     serach_name = ""
        #     for i in range(len(brand.name)):
        #         if brand.name[i].lower() not in alf:
        #             print(f"Замена для {brand.name} - [{brand.name[i]}]")
        #             buk = input()
        #             if buk == "!":
        #                 serach_name += brand.name[i]
        #             else:
        #                 serach_name += buk
        #         else:
        #             serach_name += brand.name[i]
        #     print(f"search {serach_name}")
        #     brand.search_filter_name = serach_name
        #     brand.save()




        # order = Order.objects.get(id=149)
        #
        #
        # for ou in order.order_units.all():
        #     print(ou.track_number)
        #     # ou.save()
        # order.save()
        # hps = HeaderPhoto.objects.all()
        # for h in hps:
        #     h.header_text = get_text(h, [])
        #     h.save()
        #     print(h)

        # def recursive_subcategories(sz, category):
        #     subcategories = category.subcat.all()
        #
        #     for subcategory in subcategories:
        #         # print(subcategory.name)  # Вы можете выполнить нужные действия с каждой подкатегорией здесь
        #         sz.category.add(subcategory)
        #         # print(sz.name, subcategory)
        #         recursive_subcategories(sz, subcategory)
        #
        #
        # szs = SizeTable.objects.filter(standard=True)
        # for sz in szs:
        #     last_cat = sz.category.order_by("-id").first()
        #     recursive_subcategories(sz, last_cat)
        #     # for cat in sz.category.all():
        #     #     cur_cat = cat
        #     #     while cur_cat.parent_category:
        #     #         sz.category.add(cur_cat.parent_category)
        #     #         cur_cat = cur_cat.parent_category
        #     sz.save()
        # user_s = UserStatus.objects.all()
        # print(user_s.values_list("name", flat=True).order_by("id"))
        # row = SizeTranslationRows.objects.filter(is_one_size=True, table__name="Один размер").first()
        # print(row.table.filter_name)
        # prod = Product.objects.get(id=590362)
        # print(prod.slug)
        # pr = Product.objects.filter(spu_id=1249082)
        # for product in pr:
        #     if product.bucket_link.all().count() == 0:
        #         print(product.slug)
        #         product.available_flag = False
        #         product.save()
        # print(pr.slug)
        # print(pr.available_flag)

        # print(order)
        # print(OrderSerializer(order).data)
        # product = Product.objects.get(id=46644).spu_id
        # print(product)
        # print(Product.objects.filter(available_flag=True).filter(categories__name="Другое").filter(category_id=0).count())
        # products = list(set(list(Product.objects.filter(available_flag=True).filter(categories__name="Другое").filter(category_id=0).values_list("spu_id", flat=True).order_by("-rel_num"))))
        # # # print(len(products))
        # k = 0
        # for spu in products:
        #     k += 1
        #     print(k, spu)
        #     try:
        #         data = requests.get(f"https://sellout.su/product_processing/info_for_db?spu_id={spu}").json()
        #         add_product = requests.post("https://sellout.su/api/v1/product/add_list_spu_id_products", json=data)
        #     except:
        #         continue
        # print(products)
        # print(products.count())
        #
        # # Обновляем записи в базе данных сразу для всех продуктов
        # k = 0
        # for product in products:
        #     if k % 1000 == 0:
        #         print(k)
        #     k += 1
        #     product.max_profit = product.max_profit_annotation
        #     product.save()
        # k = 89000
        # products = Product.objects.filter(available_flag=True)
        #
        # count = products.count()
        # print(count)
        #
        # for page in range(89000, products.count(), 100):
        #     page_products = products[page:page + 100].annotate(max_profit_annotation=Max('product_units__total_profit'))
        #
        #     for product in page_products:
        #         product.max_profit = product.max_profit_annotation
        #         product.save()
        #
        #         k += 1
        #         if k % 1000 == 0:
        #             print(k)

       # line_yeezy = Line.objects.get(view_name="Все Yeezy")
        # line_yeezy.full_eng_name = "adidas_yeezy"
        # line_yeezy.save()
        # duplicate_photos = Photo.objects.values('url').annotate(url_count=Count('url')).filter(url_count__gt=1)
        #
        # # Вывести дубликаты
        # for duplicate in duplicate_photos:
        #     url = duplicate['url']
        #     count = duplicate['url_count']
        #     print(f"URL: {url}, Количество: {count}")

        # def round_by_step(value, step=50):
        #     return math.ceil(value / step) * step
        # product = Product.objects.get(slug="jordan-air-jordan-1-low-laser-blue-161181")
        # bonus = 250
        # print(bonus)
        # product.max_bonus = 250
        # product.is_sale = False
        # product.min_price_without_sale = product.min_price
        # product.save()
        # products = Product.objects.filter(available_flag=True).values_list("id", flat=True)
        # products.update(actual_price=False)
        # # print(products.count())
        # # # user = User.objects.get(id=118)
        # # # cart = ShoppingCart.objects.get(user=user)
        # prus = ProductUnit.objects.filter(product__actual_price=False).values_list("id", flat=True).count()
        # print(prus)
        # products = Product.objects.order_by("-rel_num")[:1000]
        # for p in products:
        #     if p.product_units.filter(final_price=p.min_price).exists():
        #         continue
        #     else:
        #         p.available_flag = False
        #     p.save()
        # print(Product.objects.all().count())
        # products = Product.objects.all()
        # products.update(one_update=False)
        # order_status = [
        #     "В пути до международного склада",
        #     "В пути до московского склада",
        #     "Прибыл в Москву",
        #     "Передан в службу доставки по России",
        #     "Доставлен",
        #     "Отменён", "Частично передан в службу доставки по России", "Частично прибыл в Москву"
        # ]
        # for os in order_status:
        #     s = Status(name=os)
        #     s.save()
        sp = []
        # for ou in ous:
        #     ou.status = Status.objects.get_or_create(name="Принят")[0]
        #     ou.save()

        # users = User.objects.all()
        # for user in users:
        #     if user.user_status is None:
        #         user.user_status = UserStatus.objects.get(name="Amethyst")
        #         user.save()
        # Фильтруем объекты, для которых нет связанных product_units
        # products_to_update = Product.objects.all()
        # #
        # # # Обновляем флаги доступности для выбранных объектов
        # products_to_update.update(is_sale=False)
        # print(1)
        # units = ProductUnit.objects.all()
        # units.update(is_sale=False)
        # print()
        #
        # # Выводим количество обновленных записей
        # self.stdout.write(self.style.SUCCESS(f'Updated {products_to_update.count()} products.'))

        # di = DewuInfo.objects.filter(spu_id__in=ps)
        # print("го")
        #
        # k = 0
        # for page in range(0, di.values("id").count(), 5):
        #     pi = di[page:page + 5]
        #     for d in pi:
        #         if k % 100 == 0:
        #             print("*", k)
        #         k += 1
        #
        #         if d.preprocessed_data["likesCount"] != "" and "年" not in d.preprocessed_data['releaseDate']:
        #             print(d.spu_id)
        # pr = Product.objects.all()

        # pr.update(min_price_without_sale=F("min_price"))
        # print("11111")
        # pr = Product.objects.get(slug="nike-air-monarch-4-air-monarch-4-white-navy-49461")
        # pr.is_sale = True
        # for unit in pr.product_units.all():
        #     unit.start_price = unit.final_price * 1.2
        #     unit.is_sale = True
        #     unit.save()
        # pr.update_min_price()
        # pr.save()
        # print(ps.count())
        # k = 0
        # for p in ps:
        #     if k % 250 == 0:
        #         print(k)
        #     k += 1
        #     p.available_flag = False
        #     print(p.spu_id)

        # queryset = Product.objects.all()
        # queryset = queryset.filter(available_flag=True, is_custom=False).order_by("min_price")
        # queryset = queryset.values_list("id", flat=True).distinct()
        # t = time()
        # print(queryset.count())
        # print(time() - t)
        # queryset = queryset[100:150]
        # print(queryset.query)
        # queryset2 = Product.objects.filter(id__in=list(queryset))
        #
        # print()
        # print(queryset2.query)
        # t1 = time()
        # s = ProductMainPageSerializer(queryset2, many=True).data
        # t2 = time()
        # print(t2-t1)
        # print(queryset.query)
        # t = time()
        # print(queryset.count())
        # t2 = time()
        # print(t2-t)
        # print(list(queryset.values_list("id", flat=True)))
        #
        # # paginator = Paginator(queryset,
        # per_page=48)  # Инициализация Paginator с количеством объектов на странице (10 в данном случае)
        #
        # #
        # mxt = time() - time()
        # for page_number in range(2, 7000, 1000):
        #     t = time()
        #     # page = paginator.get_page(page_number)
        #
        #     start_index = (page_number - 1) * 48
        #     # print(queryset[0].id)
        #     queryset1 = queryset[start_index:start_index + 48]
        #     s = list(queryset1.values_list("id", flat=True))
        #     t1 = time()
        #     print(f"{page_number}: {t1 - t}")
        #     mxt = max(mxt, t1 - t)
        # print(f"{page_number}: {t1-t}")
        # print(mxt)
        # st = SizeRow.objects.all()
        #
        # for s in st:
        #     new_js = []
        #     js = s.sizes
        #
        #     name_t = s.size_tables.first().filter_name
        #     for siz in js:
        #         js = siz
        #         js['view_name_in_line'] = f"{name_t}: {siz['size']} {s.filter_logo if s.filter_logo not in ['SIZE', 'INT'] else ''}".strip()
        #         new_js.append(js)
        #     s.sizes = new_js
        #     s.save()

        # print()
        # product_units_to_update = ProductUnit.objects.all()
        #
        # batch_size = 100  # Размер пакета для обновления
        #
        # for start in range(0, product_units_to_update.count(), batch_size):
        #     print(start)
        #     end = start + batch_size
        #     batch = product_units_to_update[start:end]
        #
        #     for product_unit in batch:
        #         size_tables = [size.table for size in product_unit.size.all()]
        #         product_unit.size_table.set(size_tables)
        # # Получите queryset ProductUnit, для которых нужно обновить поле size_table
        # product_units_to_update = ProductUnit.objects.all()
        #
        # # Создайте подзапрос для получения id таблицы для каждого объекта Size
        # size_table_subquery = SizeTranslationRows.objects.filter(
        #     product_units__in=OuterRef('id')
        # ).values('table_id')[:1]
        #
        # # Аннотируйте queryset product_units_to_update, обновив поле size_table
        # product_units_to_update = product_units_to_update.annotate(
        #     size_table_id=Subquery(size_table_subquery)
        # )
        #
        # # Обновите поле size_table на основе подзапроса
        # product_units_to_update.update(size_table=F('size_table_id'))

        # ps = ProductUnit.objects.all()
        # # pr = ProductUnit.objects.count()
        # # print(pr)
        # k = 0
        # for p in ps:
        #     k += 1
        #     if k % 100 == 0:
        #         print(k)
        #     for s in p.size.all():
        #         if not s.is_one_size:
        #             table = s.table
        #             p.size_table.add(table)
        #     p.save()

        # phs = Photo.objects.all()
        # for p in phs:
        #     if not p.product.exists():
        #         p.delete()

        # # di = DeliveryType.objects.all()
        # # for d in di:
        # #     d.view_name = f"{d.days_min}-{d.days_max}"
        # #     d.save()
        # ps = Product.objects.all().values("brands", "spu_id", "id")
        # # ps.delete()
        # s = set()
        # # ps.delete()
        # list_id = []
        # for p in ps:
        #     if p["brands"] == None:
        #         s.add(p["spu_id"])
        #         list_id.append(p["id"])
        #
        # ps = Product.objects.filter(id__in=list_id)
        # ps.delete()
        #
        # print(sorted(s))
        # f = open("list.txt", "w")
        # f.write(str(sorted(s)))
