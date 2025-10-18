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
from django.db.models import OuterRef, Subquery, F, BooleanField, Case, When, Count, Max, Q, Min

from orders.models import ShoppingCart, Status, OrderUnit, Order
from orders.serializers import OrderSerializer

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo, SizeTable, SizeTranslationRows, SGInfo
from django.core.exceptions import ObjectDoesNotExist

from products.serializers import ProductMainPageSerializer
from promotions.models import PromoCode
from shipping.models import ProductUnit, DeliveryType, AddressInfo
from users.models import User, EmailConfirmation, UserStatus
from products.tools import get_text
import matplotlib.pyplot as plt
from collections import Counter

class Command(BaseCommand):

    def handle(self, *args, **options):
        # lc = list(Product.objects.filter(available_flag=True).values_list("rel_num", flat=True))
        # json_string = json.dumps(lc, ensure_ascii=False)
        #
        brands = Brand.objects.all()
        cats = Category.objects.all().order_by("id").exclude(name__icontains='Все').exclude(name__icontains='Вся')
        d = []
        for brand in brands:
            for cat in cats:
                d.append({"category": cat.name, "brand": brand.name, "score": 0})

        print()

        json_string = json.dumps(d, ensure_ascii=False)

            # Запись JSON-строки в файл
        with open("brand_and_category_score.json", "w", encoding="utf-8") as file:
            file.write(json_string)


        # prs = Product.objects.filter(categories__name="Кроссовки")
        # print(prs.count())
        # print(Product.objects.all().count())
        #     # Запись JSON-строки в файл
        # with open("lc.json", "w", encoding="utf-8") as file:
        #     file.write(json_string)
        # sgs = SGInfo.objects.filter(Q(formatted_manufacturer_sku=""))
        # sg = SGInfo.objects.all()
        # print(sg.count() - sgs.count())
        # print(sgs)

        # product = Product.objects.filter(product_units=None)
        # print(product.count())
        # for p in product:
        #     print(p)
        # print(lc)
        # Используйте Counter для подсчета уникальных значений параметра rel_num
        # rel_num_counts = Counter(lc)
        # rel_nums = list(rel_num_counts.keys())
        # counts = list(rel_num_counts.values())
        # plt.figure(figsize=(10, 6))
        # plt.bar(rel_nums, counts, width=0.8, align='center')
        # plt.xlabel('rel_num')
        # plt.ylabel('Количество')
        # plt.title('Распределение параметра rel_num')
        # plt.xticks(rotation=45)  # Поворачиваем подписи оси X для лучшей читаемости
        # plt.tight_layout()
        # plt.show()

        # pr = Product.objects.get(manufacturer_sku="dh7722-001")
        # print(pr.slug)
        # # product = Product.objects.filter(available_flag=False)
        # product.delete()
        # print('cerf')
        # duplicates = Product.objects.values('spu_id', 'property_id').annotate(count=Count('id')).filter(count__gt=1)
        # print(duplicates.count())
        # k = 0

        # min_ids = Product.objects.values('spu_id', 'property_id').annotate(min_id=Min('id'))
        # print(duplicates)
        # for duplicate in duplicates:
        #     k += 1
        #     # products_to_delete = Product.objects.filter(spu_id=duplicate['spu_id'],
        #     #                                             property_id=duplicate['property_id'],
        #     #                                             id__gt=duplicate['min_id'])
        #     prs = Product.objects.filter(spu_id=duplicate['spu_id'], property_id=duplicate['property_id'], available_flag=False)
        #     prs.delete()
        #     prs2 = Product.objects.filter(spu_id=duplicate['spu_id'], property_id=duplicate['property_id']).order_by("id")[1:].values_list("id", flat=True)
        #     prs_d = Product.objects.filter(id__in=prs2)
        #     prs_d.delete()
        #     print(k, Product.objects.filter(spu_id=duplicate['spu_id'], property_id=duplicate['property_id']).values_list("id", flat=True))
            # products_to_delete.delete()
        # Проходимся по дубликатам и удаляем лишние записи
        # for duplicate in duplicates:
        #     products_to_delete = Product.objects.filter(spu_id=duplicate['spu_id'],
        #                                                 property_id=duplicate['property_id'])[1:]
        #     # print(Product.objects.get(spu_id=duplicate['spu_id'], property_id=duplicate['property_id']))
        #     print(products_to_delete)

        #     order = Order.objects.all().order_by("-id").first()
    #     print(order.invoice_data)
    #     print(order.surname)
    #     # pro = Product.objects.filter(colors__name="gray")
    #     # print(pro.count())
    #     # # pro.available_flag = False
    #     # # pro.save()
    #     # products = Product.objects.filter(available_flag=True, min_price=0)
    #     # products.update(available_flag=False)
    #
    #
    #     brands = list(Brand.objects.all().order_by("name").values_list("name", flat=True))
    #     d = []
    #     for brand in brands:
    #         d.append({"name": brand, "score": 0})

    #
    #     lines = list(Line.objects.all().order_by("name").values_list("name", flat=True))
    #     d = []
    #     for line in lines:
    #         d.append({"name": line, "score": 0})
    #     json_string = json.dumps(d, ensure_ascii=False)
    #
    #     # Запись JSON-строки в файл
    #     with open("lines_score.json", "w", encoding="utf-8") as file:
    #         file.write(json_string)
    #
    #     collabs = list(Collab.objects.all().order_by("id").values_list("name", flat=True))
    #     d = []
    #     for collab in collabs:
    #         d.append({"name": collab, "score": 0})
    #     json_string = json.dumps(d, ensure_ascii=False)
    #
    #     # Запись JSON-строки в файл
    #     with open("collabs_score.json", "w", encoding="utf-8") as file:
    #         file.write(json_string)
    #
    #     cats = list(Category.objects.all().order_by("id").values_list("name", flat=True))
    #     d = []
    #     for cat in cats:
    #         d.append({"name": cat, "score": 0})
    #     json_string = json.dumps(d, ensure_ascii=False)
    #
    #     # Запись JSON-строки в файл
    #     with open("categories_score.json", "w", encoding="utf-8") as file:
    #         file.write(json_string)
    #
    #     print(len(brands))
    #     print(len(cats))
    #     print(len(collabs))
    #     print(len(lines))
    #
    #     print(len(lines) + len(cats) + len(collabs) + len(brands))


        # print(products.count())
        # # s = (res["manufacturer_sku"].replace(" ", "").replace("-", "")).lower()
        # # product = Product.objects.get(slug="")
        # # product.slug = "1"
        # # product.save()
        # products = list(set(list(Product.objects.filter(available_flag=False, min_price__gt=0).values_list("spu_id", flat=True))))
        # # # print(len(products))
        # k = 0
        # st = []
        # f = open("bags.txt", "w")
        # for spu in products:
        #     k += 1
        #     print(k, spu)
        #     try:
        #         data = requests.get(f"https://sellout.su/product_processing/info_for_db?spu_id={spu}").json()
        #         # print(data)
        #         add_product = requests.post("https://sellout.su/api/v1/product/add_list_spu_id_products", json=data)
        #         if add_product.status_code == 500:
        #             products_spu = Product.objects.filter(spu_id=spu)
        #             products_spu.delete()
        #             add_product = requests.post("https://sellout.su/api/v1/product/add_list_spu_id_products", json=data)
        #             if add_product.status_code == 500:
        #                 f.write(f"{spu}\n")
        #                 print("cerf")
        #
        #         # print(";f")
        #         # print(add_product.json())
        #     except:
        #         continue



        # user = User.objects.all()
        # for us in user:
        #     us.extra_contact = us.email
        #     us.save()
        # users = User.objects.filter(gender__name__in=["M"]).first()
        # print(users)
        # print(users.gender.name)



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

        def recursive_subcategories(sz, category):
            print(category)
            subcategories = category.subcat.all()

            for subcategory in subcategories:
                # print(subcategory.name)  # Вы можете выполнить нужные действия с каждой подкатегорией здесь
                sz.category.add(subcategory)
                # print(sz.name, subcategory)
                recursive_subcategories(sz, subcategory)


        # szs = SizeTable.objects.filter(standard=True)
        # for sz in szs:
        #     print(sz)
        #     c = input()
        #     if c != "0":
        #         last_cat = Category.objects.get(name=c)
        #         sz.category.add(last_cat)
            # for cat in sz.category.all():
            #     cur_cat = cat
            #     while cur_cat.parent_category:
            #         sz.category.add(cur_cat.parent_category)
            #         cur_cat = cur_cat.parent_category
            sz.save()
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
