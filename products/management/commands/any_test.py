import math
import random
from datetime import datetime, timedelta
from itertools import count
from time import time, sleep

import requests
from django.core import signing
from django.core.cache import cache
from django.core.management.base import BaseCommand
import json
import xml.etree.ElementTree as ET
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import OuterRef, Subquery, F, BooleanField, Case, When, Count, Max, Q, Min, Sum
from elasticsearch_dsl.connections import connections

from orders.models import ShoppingCart, Status, OrderUnit, Order
from orders.serializers import OrderSerializer
from orders.tools import send_email_confirmation_order, send_email_full_order_shipped
from products.add_product_api import add_product_v2, add_product_api, add_products_spu_id_api, add_product_hk
from products.documents import ProductDocument

from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo, DewuInfo, SizeTable, SizeTranslationRows, SGInfo, RansomRequest, FooterText
from django.core.exceptions import ObjectDoesNotExist

from products.serializers import ProductMainPageSerializer, ProductSerializer
from promotions.models import PromoCode
from sellout.settings import ELASTIC_HOST
from shipping.models import ProductUnit, DeliveryType, AddressInfo
from users.models import User, EmailConfirmation, UserStatus, Partner, SpamEmail
from products.tools import get_text
from utils.models import Currency


class Command(BaseCommand):

    def handle(self, *args, **options):
        twelve_hours_ago = datetime.now() - timedelta(hours=4.5)
        products_added = Product.objects.filter(last_upd__gt=twelve_hours_ago).count()

        print(f"Количество товаров, добавленных за последние 12 часов: {products_added}")

        a = input('d')
        def round_number(num):
            n = 2 - len(str(num))
            return round(num, n)
        def get_s(line):

            products = Product.objects.filter(lines=line, available_flag=True, is_custom=False, categories__name="Кроссовки").order_by("-score_product_page")
            url = f"https://sellout.su/products?line={line.full_eng_name}"
            if line.parent_line is None:
                title = f"Оригинальные кроссовки {line.view_name} по лучшей цене в РФ"
            else:
                title = f"Оригинальные {line.view_name} по лучшей цене в РФ"

            description = f"Выбирайте среди {round_number(products.count())}+ оригинальных моделей {line.view_name}."
            min_price = products.exclude(min_price=0).aggregate(minimal_price=Min('min_price'))['minimal_price']
            imgs = []
            products = products[:5]
            for p in products:
                imgs.append(p.bucket_link.order_by('id').first().url)

            s = [url, title, description, min_price, "RUB"]
            s.extend(imgs)
            return s


        lines = Line.objects.exclude(score=0)
        s = []
        cats = Category.objects.exclude(score=0)
        k = 0
        # for line in lines:
        #
        #     for cat in cats:
        #         if Product.objects.filter(lines=line, categories=cat, available_flag=True, is_custom=False).count() > 5:
        #             s.append(get_s(line=line, cat=cat))
        #             k += 1
        #             if k % 10 == 0:
        #                 print(k)

        for line in lines:
            if Product.objects.filter(lines=line, available_flag=True, is_custom=False, categories__name="Кроссовки").count() > 5:
                s.append(get_s(line))
                k += 1
                if k % 10 == 0:
                    print(k)

        import csv

        # Список данных для заполнения CSV файла
        data = s

        # Имя CSV файла, в который будем записывать данные
        csv_filename = "линейки_кроссовки.csv"

        # Открываем файл для записи
        with open(csv_filename, mode='w', newline='', encoding="utf-8") as file:
            writer = csv.writer(file)

            # Записываем заголовки
            writer.writerow(["Url", "Title", "Description", "Offer minimal price", "Currency",
                             "Image url 1", "Image url 2", "Image url 3", "Image url 4", "Image url 5"])

            # Записываем данные из списка в CSV файл
            for row in data:
                writer.writerow(row)

        print(f"CSV файл {csv_filename} успешно создан и заполнен данными.")
        a = input("A")
        o = Order.objects.get(number="81741")
        u = User.objects.get(email="saveliy.agabekov@mail.ru")
        o.user = u
        o.save()
        a = input("ujnjdj")
        # russia = {}
        # with open("line_text4.json", 'r', encoding='utf-8') as json_file:
        #     data = (json.load(json_file))
        # for d in data:
        #     russia[d['line']] = d['russia']
        # print(russia)
        # with open("line_text2.json", 'r', encoding='utf-8') as json_file:
        #     data = (json.load(json_file))
        #
        # for d in data:
        #     print(d['line'])
        #     line = Line.objects.get(view_name=d['line'])
        #     foot, _ = FooterText.objects.get_or_create(lines=line)
        #
        #     if d['text']['title'] != "":
        #         foot.title = d['text']['title']
        #         foot.text = " ".join(d['text']['content'].replace("\n", " ").split())
        #
        #     if d['line'].replace("Все ", "") in russia:
        #         print("да")
        #         if russia[d['line'].replace("Все ", "")] not in foot.text:
        #
        #             foot.text = foot.text.replace(f'{d["line"].replace("Все ", "")}', f'{d["line"].replace("Все ", "")} ({russia[d["line"].replace("Все ", "")]})', 1)
        #             print(foot.text)
        #     foot.save()
        #
        # a = input('отово')
        product = list(Product.objects.filter(is_sale=True, min_price=F('min_price_without_sale')).order_by("-score_product_page").values_list("id", flat=True))
        k = 0
        for p in product:
            k += 1
            Product.objects.get(id=p).del_sale()
            print(k)
        print(product.count())
        a = input("u")
        # p = list(Product.objects.filter(available_flag=True, is_custom=True).values_list("id", flat=True))
        # with open("id_pop.json", 'w', encoding='utf-8') as output_file:
        #     json.dump(p, output_file, ensure_ascii=False, indent=2)
        #
        #
        # a = input("d")
        # def custom_round(number):
        #     if number == 0:
        #         return 0
        #     elif number < 0:
        #         return -custom_round(-number)
        #     else:
        #         magnitude = 10 ** (len(str(number)) - 1)
        #         formatted_number = "{:,.0f}".format(int(str(number)[0]) * magnitude).replace(',', "'")
        #         return f"Более {formatted_number} товар{'а' if formatted_number == '1' else 'ов'}"
        # data = {}
        # lines = Line.objects.all().order_by("id")
        # cats = Category.objects.all().order_by("id")
        # urls = set()
        # k = 0
        # for line in lines:
        #     k += 1
        #     print(k)
        #     if Product.objects.filter(available_flag=True, is_custom=False, lines=line).exists():
        #         count = custom_round(Product.objects.filter(available_flag=True, is_custom=False, lines=line).count())
        #         name = line.view_name
        #         ind = 0
        #         f = False
        #         while not f:
        #             most_pop = Product.objects.filter(available_flag=True, is_custom=False, lines=line).order_by("-score_product_page")[ind].bucket_link.order_by("id")[0].url
        #             if most_pop in urls:
        #                 ind += 1
        #             else:
        #                 f = True
        #                 urls.add(most_pop)
        #
        #         data[name] = {'count': count,
        #                       'photo': most_pop}
        #
        #
        #
        # for cat in cats:
        #     k += 1
        #     print(k, "2")
        #     if Product.objects.filter(available_flag=True, is_custom=False, categories=cat).exists():
        #         count = Product.objects.filter(available_flag=True, is_custom=False, categories=cat).count()
        #         custom_count = custom_round(count)
        #         name = cat.name
        #         ind = 0
        #         f = False
        #         while not f:
        #             most_pop = Product.objects.filter(available_flag=True, is_custom=False, categories=cat).order_by("-score_product_page")[ind].bucket_link.order_by("id")[0].url
        #             if most_pop in urls:
        #                 ind += 1
        #                 if count == ind:
        #                     f = True
        #             else:
        #                 f = True
        #                 urls.add(most_pop)
        #
        #         data[name] = {'count': custom_count,
        #                       'photo': most_pop}
        #
        # for cat in cats:
        #     for line in lines:
        #         if Product.objects.filter(available_flag=True, is_custom=False, categories=cat, lines=line).exists():
        #             k += 1
        #             print(k, "3")
        #             count = Product.objects.filter(available_flag=True, is_custom=False, categories=cat, lines=line).count()
        #             custom_count = custom_round(count)
        #             name = f"{cat.name} {line.view_name}"
        #             ind = 0
        #             f = False
        #             while not f:
        #                 most_pop = \
        #                 Product.objects.filter(available_flag=True, is_custom=False, categories=cat, lines=line).order_by(
        #                     "-score_product_page")[ind].bucket_link.order_by("id")[0].url
        #                 if most_pop in urls:
        #                     ind += 1
        #                     if count == ind:
        #                         f = True
        #                 else:
        #                     f = True
        #                     urls.add(most_pop)
        #
        #             data[name] = {'count': custom_count,
        #                           'photo': most_pop}
        #
        #
        #
        # with open("most_pop.json", 'w', encoding='utf-8') as output_file:
        #     json.dump(data, output_file, ensure_ascii=False, indent=2)
        #
        # a = input("Готово")
        # f = FooterText.objects.all()
        # f.delete()
        # file_path = "line_text.json"
        # with open(file_path, 'r', encoding='utf-8') as file:
        #     json_data = json.load(file)
        # for line in json_data:
        #     if Line.objects.filter(view_name=line['line']).exists():
        #         l = Line.objects.get(view_name=line['line'])
        #         new_text = FooterText(title=line['text']['title'],
        #                               text=line['text']['description'],
        #                               )
        #         new_text.save()
        #         new_text.lines.add(l)
        #         new_text.save()
        #         print(line['line'])
        # a = input("готово")
        words_with_translations = {
            'adidas': 'Адидас',
            'Все adidas': 'Все Адидас',
            'adidas Yeezy': 'Адидас Изи',
            'Все adidas Yeezy': 'Все Адидас Изи',
            'adidas Yeezy 350': 'Адидас Изи 350',
            'adidas Yeezy 380': 'Адидас Изи 380',
            'adidas Yeezy 450': 'Адидас Изи 450',
            'adidas Yeezy 500': 'Адидас Изи 500',
            'adidas Yeezy 700': 'Адидас Изи 700',
            'adidas Yeezy 750': 'Адидас Изи 750',
            'adidas Yeezy Foam Runner': 'Адидас Изи Фоум Раннер',
            'adidas Yeezy Slide': 'Адидас Изи Слайд',
            'Другие Yeezy': 'Другие Изи',
            'adidas Campus': 'Адидас Кампус',
            'adidas Forum': 'Адидас Форум',
            'adidas Gazelle': 'Адидас Газель',
            'adidas Samba': 'Адидас Самба',
            'adidas Stan Smith': 'Адидас Стэн Смит',
            'adidas Superstar': 'Адидас Суперстар',
            'adidas Ultraboost': 'Адидас Ультрабуст',
            'adidas Human Race': 'Адидас Хьюман Рейс',
            'adidas NMD': 'Адидас Эн Эм Ди',
            'adidas ZX': 'Адидас Зет Экс',
            'adidas Adilette': 'Адидас Адилет',
            'adidas Nizza': 'Адидас Ницца',
            'adidas EQT': 'Адидас Эквити',
            'adidas Ozweego': 'Адидас Озвеего',
            'adidas 4D': 'Адидас 4D',
            'adidas Harden': 'Адидас Харден',
            'adidas Trae Young': 'Адидас Трэ Янг',
            'adidas Dame (Damian Lillard)': 'Адидас Дэйм (Дэмиан Лиллард)',
            'adidas D Rose': 'Адидас Д Роуз',
            'adidas Pro Bounce': 'Адидас Про Баунс',
            'adidas D.O.N': 'Адидас Д.О.Н',
            'Anta': 'Анта',
            'Все Anta': 'Все Анта',
            'Anta KT3': 'Анта КТ3',
            'Anta KT7': 'Анта КТ7',
            'Anta KT8': 'Анта КТ8',
            'Asics': 'Асикс',
            'Все Asics': 'Все Асикс',
            'Asics Gel-Lyte': 'Асикс Гел-Лайт',
            'Asics Gel-Flux': 'Асикс Гел-Флюкс',
            'Asics Gel-Contend': 'Асикс Гел-Контенд',
            'Asics Gel-Cumulus': 'Асикс Гел-Кумулус',
            'Asics Gel-Excite': 'Асикс Гел-Эксайт',
            'Asics Gel-NYC': 'Асикс Гел-НЙС',
            'Asics Gel-Nimbus': 'Асикс Гел-Нимбус',
            'Asics Gel-Quantum': 'Асикс Гел-Квантум',
            'Asics Gel-Kayano': 'Асикс Гел-Каяно',
            'Asics Gel-Kahana': 'Асикс Гел-Кахана',
            'Asics Gel-1090': 'Асикс Гел-1090',
            'Asics Gel-1130': 'Асикс Гел-1130',
            'Asics Magic Speed': 'Асикс Мэджик Спид',
            'Asics GT': 'Асикс ГТ',
            'Converse': 'Конверс',
            'Все Converse': 'Все Конверс',
            'Converse Chuck Taylor': 'Конверс Чак Тейлор',
            'Converse Chuck Taylor Run Star': 'Конверс Чак Тейлор Ран Стар',
            'Converse One Star': 'Конверс Ван Стар',
            'Converse Pro Leather': 'Конверс Про Ледер',
            'Converse All Star Pro BB': 'Конверс Олл Стар Про ББ',
            'Jordan': 'Джордан',
            'Все Jordan': 'Все Джордан',
            'Air Jordan 1': 'Эйр Джордан 1',
            'Все Air Jordan 1': 'Все Эйр Джордан 1',
            'Air Jordan 1 Low': 'Эйр Джордан 1 Лоу',
            'Air Jordan 1 Mid': 'Эйр Джордан 1 Мид',
            'Air Jordan 1 High': 'Эйр Джордан 1 Хай',
            'Другие Air Jordan 1': 'Другие Эйр Джордан 1',
            'Air Jordan 2': 'Эйр Джордан 2',
            'Air Jordan 3': 'Эйр Джордан 3',
            'Air Jordan 4': 'Эйр Джордан 4',
            'Air Jordan 5': 'Эйр Джордан 5',
            'Air Jordan 6': 'Эйр Джордан 6',
            'Air Jordan 7': 'Эйр Джордан 7',
            'Air Jordan 8': 'Эйр Джордан 8',
            'Air Jordan 9': 'Эйр Джордан 9',
            'Air Jordan 10': 'Эйр Джордан 10',
            'Air Jordan 11': 'Эйр Джордан 11',
            'Air Jordan 12': 'Эйр Джордан 12',
            'Air Jordan 13': 'Эйр Джордан 13',
            'Air Jordan 14': 'Эйр Джордан 14',
            'Air Jordan 15': 'Эйр Джордан 15',
            'Jordan Tatum': 'Джордан Тэйтум',
            'Jordan Legacy': 'Джордан Легаси',
            'Jordan Why Not': 'Джордан Вай Нот',
            'Jordan Luka': 'Джордан Лука',
            'Jordan Zion': 'Джордан Зайон',
            'Li-Ning': 'Ли-Нинг',
            'Все Li-Ning': 'Все Ли-Нинг',
            'Li-Ning Way Of Wade': 'Ли-Нинг Уэй Оф Уэйд',
            'Li-Ning Yushuai': 'Ли-Нинг Юшуай',
            'Li-Ning Sonic': 'Ли-Нинг Соник',
            'Li-Ning Speed': 'Ли-Нинг Спид',
            'New Balance': 'Нью Бэланс',
            'Все New Balance': 'Все Нью Бэланс',
            'New Balance 237': 'Нью Бэланс 237',
            'New Balance 327': 'Нью Бэланс 327',
            'New Balance 530': 'Нью Бэланс 530',
            'New Balance 550': 'Нью Бэланс 550',
            'New Balance 574': 'Нью Бэланс 574',
            'New Balance 580': 'Нью Бэланс 580',
            'New Balance 650': 'Нью Бэланс 650',
            'New Balance 990': 'Нью Бэланс 990',
            'New Balance 991': 'Нью Бэланс 991',
            'New Balance 992': 'Нью Бэланс 992',
            'New Balance 993': 'Нью Бэланс 993',
            'New Balance 997': 'Нью Бэланс 997',
            'New Balance 9060': 'Нью Бэланс 9060',
            'New Balance 1906R': 'Нью Бэланс 1906Р',
            'New Balance 2002R': 'Нью Бэланс 2002Р',
            'New Balance 57/40': 'Нью Бэланс 57/40',
            'Nike': 'Найк',
            'Все Nike': 'Все Найк',
            'Nike Dunk': 'Найк Данк',
            'Все Nike Dunk': 'Все Найк Данк',
            'Nike Dunk Low': 'Найк Данк Лоу',
            'Nike Dunk Mid': 'Найк Данк Мид',
            'Nike Dunk High': 'Найк Данк Хай',
            'Другие Nike Dunk': 'Другие Найк Данк',
            'Nike Air Force 1': 'Найк Эйр Форс 1',
            'Все Nike Air Force 1': 'Все Найк Эйр Форс 1',
            'Nike Air Force 1 Low': 'Найк Эйр Форс 1 Лоу',
            'Nike Air Force 1 Mid': 'Найк Эйр Форс 1 Мид',
            'Nike Air Force 1 High': 'Найк Эйр Форс 1 Хай',
            'Другие Nike Air Force 1': 'Другие Найк Эйр Форс 1',
            'Nike Air Max': 'Найк Эйр Макс',
            'Все Nike Air Max': 'Все Найк Эйр Макс',
            'Nike Air Max 1': 'Найк Эйр Макс 1',
            'Nike Air Max 90': 'Найк Эйр Макс 90',
            'Nike Air Max 95': 'Найк Эйр Макс 95',
            'Nike Air Max 97': 'Найк Эйр Макс 97',
            'Nike Air Max 98': 'Найк Эйр Макс 98',
            'Nike Air Max 270': 'Найк Эйр Макс 270',
            'Nike Air Max 720': 'Найк Эйр Макс 720',
            'Другие Nike Air Max': 'Другие Найк Эйр Макс',
            'Nike Blazer': 'Найк Блейзер',
            'Все Nike Blazer': 'Все Найк Блейзер',
            'Nike Blazer Low': 'Найк Блейзер Лоу',
            'Nike Blazer Mid': 'Найк Блейзер Мид',
            'Nike Blazer High': 'Найк Блейзер Хай',
            'Другие Nike Blazer': 'Другие Найк Блейзер',
            'Nike Zoom': 'Найк Зум',
            'Nike VaporMax': 'Найк Вапормакс',
            'Nike Cortez': 'Найк Кортез',
            'Nike Air Trainer': 'Найк Эйр Трейнер',
            'Nike React': 'Найк Реакт',
            'Nike Kyrie Irving': 'Найк Кайри Ирвинг',
            'Nike LeBron James': 'Найк Леброн Джеймс',
            'Nike KD (Kevin Durant)': 'Найк КД (Кевин Дюрант)',
            'Nike Freak (Giannis Antetokounmpo)': 'Найк Фрик (Джаннис Антетокунмпо)',
            'Nike Kobe Bryant': 'Найк Кобе Брайант',
            'Nike PG (Paul George)': 'Найк ПГ (Пол Джордж)',
            'Nike Ja Morant': 'Найк Джа Морант',
            'Nike Air Presto': 'Найк Эйр Престо',
            'Nike Air More Uptempo': 'Найк Эйр Мор Аптемпо',
            'Nike Foamposite': 'Найк Фоампозит',
            'Nike Air Huarache': 'Найк Эйр Хуарач',
            'PUMA': 'Пума',
            'Все PUMA': 'Все Пума',
            'PUMA Suede': 'Пума Суэйд',
            'PUMA RS': 'Пума РС',
            'PUMA Ignite': 'Пума Игнит',
            'PUMA Cali': 'Пума Кали',
            'PUMA Carina': 'Пума Карина',
            'PUMA Smash': 'Пума Смэш',
            'PUMA MB': 'Пума МБ',
            'PUMA Fusion': 'Пума Фьюжн',
            'PUMA Clyde': 'Пума Клайд',
            'PUMA Mirage': 'Пума Мираж',
            'PUMA Mayze': 'Пума Мэйз',
            'PUMA Roma': 'Пума Рома',
            'PUMA Future Rider': 'Пума Фьючер Райдер',
            'PUMA Ca Pro': 'Пума Ка Про',
            'PUMA Slipstream': 'Пума Слипстрим',
            'PUMA Ralph Sampson': 'Пума Ральф Сампсон',
            'Reebok': 'Рибок',
            'Все Reebok': 'Все Рибок',
            'Reebok Club': 'Рибок Клаб',
            'Reebok Classic Leather': 'Рибок Классик Ледер',
            'Reebok Instapump Fury': 'Рибок Инстапамп Фьюри',
            'Reebok Zig Kinetica': 'Рибок Зиг Кинетика',
            'Reebok Question': 'Рибок Квестшн',
            'Reebok Workout': 'Рибок Воркаут',
            'Under Armour': 'Андер Армор',
            'Все Under Armour': 'Все Андер Армор',
            'Under Armour Curry 1': 'Андер Армор Карри 1',
            'Under Armour Curry 2': 'Андер Армор Карри 2',
            'Under Armour Curry 3': 'Андер Армор Карри 3',
            'Under Armour Curry 4': 'Андер Армор Карри 4',
            'Under Armour Curry 5': 'Андер Армор Карри 5',
            'Under Armour Curry 6': 'Андер Армор Карри 6',
            'Under Armour Curry 7': 'Андер Армор Карри 7',
            'Under Armour Curry 8': 'Андер Армор Карри 8',
            'Under Armour Curry 9': 'Андер Армор Карри 9',
            'Under Armour Curry 10': 'Андер Армор Карри 10',
            'Vans': 'Ванс',
            'Все Vans': 'Все Ванс',
            'Vans Old Skool': 'Ванс Олд Скул',
            'Vans Knu': 'Ванс Кну',
            'Vans SK8': 'Ванс СК8',
            'Vans Ward': 'Ванс Вард',
            'Vans ComfyCush': 'Ванс КомфиКаш',
            'Vans Era': 'Ванс Эра',
            'Vans Authentic': 'Ванс Аутентик',
            'Vans Slip-On': 'Ванс Слип-Он',
            'Vans Ultrarange': 'Ванс Ультранж',
            'Vans Anaheim': 'Ванс Анхейм',
            'Vans Vault': 'Ванс Волт',
            'Yeezy': 'Изи',
            'Все Yeezy': 'Все Изи',
            'Yeezy Boost': 'Изи Буст',
            'Все Yeezy Boost': 'Все Изи Буст',
            'Yeezy Boost 350': 'Изи Буст 350',
            'Yeezy Boost 380': 'Изи Буст 380',
            'Yeezy Boost 450': 'Изи Буст 450',
            'Yeezy Boost 500': 'Изи Буст 500',
            'Yeezy Boost 700': 'Изи Буст 700',
            'Yeezy Boost 750': 'Изи Буст 750',
            'Yeezy Boost 950': 'Изи Буст 950',
            'Yeezy Slide': 'Изи Слайд',
            'Yeezy Foam Runner': 'Изи Фоум Раннер',
            "Vans Half Cab": "Ванс Халф Кэб",
            "Vans Style 36": "Ванс Стайл 36",
            "Y-3": "Вай-Три",
            "Timberland": "Тимберленд",
            "Supreme": "Суприм",
            "A BATHING APE®": "А Бэйтинг Эйп",
            "Off-White": "Офф-Уайт",
            "Palace": "Палас",
            "Kaws": "Кавс",
            "Champion": "Чемпион",
            "Casio": "Касио",
            "Gucci": "Гуччи",
            "NOAH": "Ноа",
            "Thrasher": "Трэшер",
            "Roaringwild": "Роарингвайлд",
            "Prada": "Прада",
            "Thom Browne": "Том Браун",
            "Kenzo": "Кензо",
            "Longines": "Лонжин",
            "Givenchy": "Живанши",
            "The North Face": "Норт Фейс",
            "Mitchell & Ness": "Митчелл энд Несс",
            "Burberry": "Бёрберри",
            "Tissot": "Тиссо",
            "Rick Owens": "Рик Оуэнс",
            "Moschino": "Москино",
            "Bottega Veneta": "Боттега Венета",
            "VLONE": "Вилон",
            "Alexander McQueen": "Александр МакКуин",
            "GCDS": "Джи Си Ди Эс",
            "Canada Goose": "Канада Гус",
            "MSGM": "Эм-Эс-Джи-Эм",
            "RIPNDIP": "Рипндип",
            "Balenciaga": "Баленсиага",
            "Chiara Ferragni": "Кьяра Ферраньи",
            "Marcelo Burlon": "Марсело Бурлон",
            "Cartier": "Картье",
            "New Era": "Нью Эра",
            "Carhartt": "Кархартт",
            "Dickies": "Дикиз",
            "Onitsuka Tiger": "Онитсука Тигер",
            "Fila": "Фила",
            "Stüssy": "Стюсси",
            "Versace": "Версаче",
            "UNIQLO": "Юникло",
            "Neil Barrett": "Нил Барретт",
            "Golden Goose": "Голден Гус",
            "VEJA": "Вежа",
            "Armani": "Армани",
            "Anti Social Social Club": "Анти Сошал Сошал Клуб",
            "Comme Des Garçons": "Ком де Гарсон",
            "Cav Empt": "Кав Эмпт",
            "WTAPS": "Дабл тапс",
            "ICONS Lab": "Айконс Лаб",
            "UNDEFEATED": "Андифитед",
            "Suicoke": "Суйкоке",
            "MostwantedLab": "Мост Вантед Лаб",
            "Peak": "Пик",
            "Fear of God": "Фир оф Год",
            "PSO Brand": "ПСО Брэнд",
            "Evisu": "Ивису",
            "Citizen": "Ситизен",
            "BE@RBRICK": "Бирбрик",
            "Clot": "Клот",
            "Coach": "Коуч",
            "ISSEY MIYAKE": "Иссей Мияке",
            "Michael Kors": "Майкл Корс",
            "HERMES": "Эрмес",
            "Dior": "Диор",
            "Chanel": "Шанель",
            "361°": "361 градус",
            "Mizuno": "Мидзуно",
            "Moncler": "Монклер",
            "Louis Vuitton": "Луи Виттон",
            "UZIS": "Юзис",
            "Clarks": "Кларкс",
            "Palm Angels": "Пальм Энджелс",
            "MLB": "Эм Эль Би",
            "Maison Margiela": "Мезон Маржела",
            "Polo Ralph Lauren": "Поло Ральф Лорен",
            "Zimmermann": "Циммерман",
            "Loewe": "Лоуве",
            "Saint Laurent": "Сен Лоран",
            "Calvin Klein": "Кельвин Кляйн",
            "patagonia": "Патагония",
            "1017 ALYX 9SM": "1017 Аликс 9СМ",
            "bosieagender": "Бозиэгендер",
            "BY FAR": "Бай Фар",
            "Maje": "Маж",
            "Stella McCartney": "Стелла Маккартни",
            "Freak’s Store": "Фрикс Стор",
            "Acupuncture": "Акупунктура",
            "Celine": "Селин",
            "Hoka One One": "Хока Онэ Онэ",
            "Bally": "Бэлли",
            "On": "Он",
            "Salomon": "Саломон",
            "Acne Studios": "Акне Студиос",
            "Alpha Industries": "Альфа Индастриз",
            "Crocs": "Кроксы",
            "Tom Ford": "Том Форд",
            "Daisy Fellowes": "Дейзи Феллоус",
            "SandKnit": "Сэнд Нит",
            "VANESSA HOGAN": "Ванесса Хоган",
            "ELLE": "Эль",
            "Marni": "Марни",
            "Dries Van Noten": "Дрис Ван Нотен",
            "PINKO": "Пинко",
            "sacai": "Сакай",
            "Paco Rabanne": "Пако Рабан",
            "Stuart Weitzman": "Стьюарт Вейтцман",
            "RED Valentino": "Ред Валентино",
            "MaxMara": "Макс Мара",
            "Human Made": "Хуман Мэйд",
            "Maison Kitsune": "Мезон Китсунэ",
            "Self portrait": "Селф портрет",
            "Hugo Boss": "Хьюго Босс",
            "Spalding": "Сполдинг",
            "AMIRI": "Амири",
            "UGG": "Уги",
            "AMI Paris": "Ами Пари",
            "Levi's": "Левайс",
            "Stone Island": "Стон Айленд",
            "Ferragamo": "Феррагамо",
            "Jimmy Choo": "Джимми Чу",
            "Tod's": "Тодс",
            "Hogan": "Хоган",
            "Chloe": "Клоэ",
            "JW Anderson": "Джей Дабл Ю Эндерсон",
            "Needles": "Нидлс",
            "Skechers": "Скетчерс",
            "RayBan": "Рэй Бэн",
            "Arc'teryx": "Арктерикс",
            "BJHG": "Би Джейч Ги",
            "BVLGARI": "Бвлгари",
            "Fendi": "Фенди",
            "Swarovski": "Сваровски",
            "Pandora": "Пандора",
            "Zzegna": "Цегна",
            "Moose Knuckles": "Мус Наклес",
            "Herschel": "Хершель",
            "Mother": "Мазер",
            "Vetements": "Ветман",
            "A.P.C.": "А Пи Си",
            "WE11DONE": "Велл Дон",
            "Nanushka": "Нанушка",
            "Tagliatore": "Тальятур",
            "MARC JACOBS": "Марк Джейкобс",
            "Oakley": "Оукли",
            "NORVINCY": "Норвинси",
            "Paset": "Пасет",
            "Rocawear": "Рокавеар",
            "Yohji Yamamoto": "Йодзи Ямамото",
            "acme de la vie": "Акме де ла ви",
            "DSQUARED 2": "Ди Скверед 2",
            "ollieskate": "Оллискейт",
            "Valentino": "Валентино",
            "Tory Burch": "Тори Бёрч",
            "Moditec": "Модитек",
            "Kreate": "Креат",
            "COOLALPACA": "Кулалпака",
            "marine serre": "марин сер",
            "xVESSEL": "эксВэссел",
            "Tommy Hilfiger": "Томми Хилфигер",
            "VINEY": "Виней",
            "MIU MIU": "Миу Миу",
            "Balmain": "Бальман",
            "vision street wear": "вижн стрит веар",
            "PRBLMS": "Проблемс",
            "Ganni": "Ганни",
            "Fjallraven": "Фьяллрэвен",
            "Paul Smith": "Пол Смит",
            "Jacquemus": "Жакемю",
            "MISBHV": "Мисбхв",
            "A-COLD-WALL*": "А-Колд-Уолл",
            "ETRO": "Этро",
            "424": "Фортуфор",
            "IRO": "Айро",
            "C.P. Company": "Си Пи Компани",
            "Lanvin": "Ланвин",
            "Khrisjoy": "Крисджой",
            "Alexandre Vauthier": "Александр Вотье",
            "Jil Sander": "Жиль Сандер",
            "Y/Project": "Уай Проджект",
            "Lacoste": "Лакост",
            "ISABEL MARANT": "Изабель Маран",
            "Diesel": "Дизель",
            "Karl Lagerfeld": "Карл Лагерфельд",
            "YEEZY": "Изи",
            "速写": "Суша",
            "Rhude": "Рюд",
            "Lily Wei": "Лили Вэй",
            "Ermenegildo Zegna": "Эрменеджильдо Цегна",
            "Gianvito Rossi": "Джанвито Росси",
            "Santoni": "Сантони",
            "Philimarket": "Филимаркет",
            "Theory": "Теория",
            "Études": "Этюд",
            "Missoni": "Миссони",
            "ASH": "Эш",
            "Daphne": "Дафне",
            "kate spade": "кейт спейд",
            "Goyard": "Гояр",
            "Charlotte Tilbury": "Шарлотта Тилбури",
            "GUESS": "Гесс",
            "molten": "молтен",
            "Manolo Blahnik": "Маноло Бланик",
            "umbro": "умбро",
            "Staud": "Стауд",
            "Banana Shark": "Банана Шарк",
            "Belle": "Белл",
            "FRKM": "Фркм",
            "Ballantyne": "Баллантайн",
            "Gap": "Гэп",
            "René Caovilla": "Рене Кавилла",
            "Undercover": "Андеркавер",
            "N°21": "Номер 21",
            "Proenza Schouler": "Проэнза Шулер",
            "KITH": "Кит",
            "JANE KLAIN": "Джейн Клейн",
            "Zara": "Зара",
            "Andersson Bell": "Андерсон Белл",
            "Steve Madden": "Стив Мэдден",
            "beams": "бимс",
            "Polar Skate Co.": "Полар Скейт Ко",
            "PLEASURES": "Плезур",
            "Buccellati": "Бучеллати",
            "Church's": "Чёрчес",
            "Naked Wolfe": "Нейкд Вулф",
            "Nana Jacqueline": "Нана Жаклин",
            "Banditk Gangn": "Бандитк Гангн",
            "Guidi": "Гуиди",
            "Empty Reference": "Эмпти Референс",
            "umamiism": "умамиизм",
            "Axel Arigato": "Аксель Аригато",
            "EMOTIONAL WORLD": "Эмоушнл Ворлд",
            "DIMC": "ДИМК",
            "Revenge": "Ревендж",
            "Raucohouse": "Раукохаус",
            "Delvaux": "Делво",
            "Valextra": "Валекстра",
            "John Richmond": "Джон Ричмонд",
            "SANDRO": "Сандро",
            "Waitingwave": "Вейтингуэйв",
            "APEDE MOD": "Эпеде Мод",
            "FARFROMWHAT": "Фарфромуот",
            "Yese Studio": "Йес Студио",
            "Youkeshu": "Юкешу",
            "Ocai": "Окай",
            "DC Shoes": "Ди Си Шуз",
            "nan": "нан",
            "UNKNOWTAL": "Анноутоул",
            "AGL": "Эджил",
            "SKIMS": "Скимс",
            "Fred Perry": "Фред Перри",
            "Osiris": "Осирис",
            "Mach & Mach": "Мач энд Мач",
            "Birkenstock": "Биркеншток",
            "Fragment Design": "Фрагмент Дизайн",
            "Gramicci": "Грамиччи",
            "Weird Market": "Вирд Маркет",
            "Caramella": "Карамелла",
            "Old Order": "Олд Ордер",
            "Russell Athletic": "Расселл Атлетик",
            "EASTPAK": "Истпак",
            "Greg Lauren": "Грег Лорен",
            "Alaia": "Алайя",
            "BODE": "Боде",
            "DKNY": "Ди Кей Эн Уай",
            "Aries": "Арис",
            "Profound": "Профаунд",
            "Paul & Shark": "Пол энд Шарк",
            "Cult Gaia": "Калт Гаиа",
            "H&M": "ХэндМ",
            "diadora": "диадора",
            "Premiata": "Прэмиата",
            "Brioni": "Бриони",
            "Loake": "Лоаке",
            "ALLSAINTS": "Оллсэйнтс",
            "Union": "Юнион",
            "Massimo Dutti": "Массимо Дутти",
            "MIKASA": "Микаса",
            "Coperni": "Коперни",
            "Mugler": "Муглер",
            "Dime MTL": "Дайм МТЛ",
            "Concepts": "Концептс",
            "Peaceminusone": "Писминасон",
            "Cactus Plant Flea Market": "Кактус Плант Фли Маркет",
            "Aimé Leon Dore": "Айме Леон Дор",
            "MSCHF R": "МСЧФ Эр",
            "Jack Jones": "Джек Джонс",
            "ONLY": "Онли",
            "Samsonite": "Сэмсонайт",
            "Swatch": "Свотч",
            "G-SHOCK": "Джи-Шок",
            "Teenie Weenie": "Тини Уини",
            "Unifree": "Юнифри",
            "33TH": "Тридцать Третий",
            "Camel": "Камел",
            "F426": "Эф Фо Фоу Сикс",
            "Fido Dido": "Фидо Дидо",
            "HUF": "Хаф",
            "Brain Dead": "Брейн Дед",
            "lululemon": "лулулемон",
            "CEEC LA": "Сиси ЛА",
            "Killwinner": "Киллвиннер",
            "Khaite": "Кхайт",
            "Omega": "Омега",
            "Boy London": "Бой Лондон",
            "Golfcross": "Гольфкросс",
            "palladium": "палладиум",
            "Chaumet": "Шоме",
            "GOLF": "Гольф",
            "Dark Circle": "Дарк Серкл",
            "Van Cleef & Arpels": "Ван Клиф энд Арпель",
            "Rolex": "Ролекс",
            "Vacheron Constantin": "Вашерон Константин",
            "Native": "Нэйтив",
            "Patek Philippe": "Патек Филип",
            "Discover Mental Club": "Дискавер Ментал Клуб",
            "Audemars Piguet": "Одемар Пиге",
            "Harry Winston": "Гарри Уинстон",
            "Wandler": "Вандлер",
            "Berluti": "Берлути",
            "UFZ": "ЮФЗ",
            "Ermanno Scervino": "Эрманно Счервино",
            "Atry": "Этри",
            "Arket": "Аркет",
            "Moon Boot": "Мун Бут",
            "Aquascutum": "Акваскутум",
            "Free world order": "Фри Ворлд Ордер",
            "The Salvages Fashion Club": "Зе Сальваджес Фэшн Клаб",
            "Boucheron": "Бушерон",
            "Barker": "Баркер"
        }

        # lines = Line.objects.all().order_by("id")
        # categories = Category.objects.exclude(name__icontains='Все').exclude(
        #     name__contains='Другие').exclude(name__icontains='Вся').exclude(parent_category=None).order_by("id")
        #
        # data = []
        # file_path = "wordstat_sum.json"
        # with open(file_path, 'r', encoding='utf-8') as file:
        #     json_data = json.load(file)
        # popular = {}
        # for line in json_data:
        #     key = []
        #     for pop in line['popular'][:10]:
        #
        #         key.append(list(dict(pop).keys())[0])
        #     popular[line['search']] = ", ".join(key)
        #
        #
        # # Для каждой линии создаем запись в данных
        # k = 0
        # for line in lines:
        #     k += 1
        #     print(k)
        #     top5 = (
        #         Product.objects
        #         # Фильтруем продукты по текущей линии и категории
        #         .filter(lines=line, categories__in=categories)
        #         # Группируем продукты по категориям и подсчитываем количество для каждой категории
        #         .values('categories__name')
        #         .annotate(category_count=Count('categories__name'))
        #         # Сортируем категории по убыванию количества продуктов
        #         .order_by('-category_count')
        #         # Выбираем только топ-5 категорий
        #         .annotate(category_name=F('categories__name'))
        #         .values_list('category_name', flat=True)[:10]
        #     )
        #
        #     data.append({
        #         'line': line.view_name,
        #         'top5': ", ".join(list(top5)),
        #         'key_words': popular.get(line.view_name, "пропуск"),
        #         'russia': words_with_translations.get(line.view_name, "пропуск"),
        #         'text': {"title": "", "description": ""}
        #     })
        # with open("line_text4.json", 'w', encoding='utf-8') as output_file:
        #     json.dump(data, output_file, ensure_ascii=False, indent=2)
        # a = input("Стоп")
        # print(Product.objects.get(manufacturer_sku="DD8959-113").slug)

        # # p = add_product_hk([])
        # p = list(set(Product.objects.values_list("spu_id", flat=True)))
        #
        # s = 0
        # ps = Product.objects.filter(in_search=True)
        #
        #
        #
        #
        #
        # print(ps.count())
        # a = input()

        # k = 0
        # for p in ps:
        #     # if p.min_price == p.min_price_without_sale:
        #     #     p.del_sale()
        #     #     k += 1
        #     p.delete()
        #     k += 1
        #     if k % 10 == 0:
        #         print(k)
        # # print(10)
        # a = input()
        # for prod in p:
        #     r = random.randint(1, 3)
        #     if r != 1:
        #         s += 1
        #         prod.del_sale()
        #     if s % 10 == 0:
        #         print(s)
        # a = input()

        # cache.clear()

        # prod = Product.objects.filter(bucket_link=None, lines=Line.objects.get(view_name="adidas"))
        # prod.delete()
        # prod = Product.objects.filter(bucket_link=None, lines=Line.objects.get(view_name="adidas"))
        # # prod = Product.objects.filter(bucket_link=None)
        # print(prod.count())
        # lines = Line.objects.filter(full_eng_name="")
        # for l in lines:
        #     l.save()
        # print(lines.count())
        # p = Product.objects.filter(bucket_link=None)
        # p.delete()
        # print(len(p), len(set(p)))

        # p = Product.objects.all()
        # # p = Product.objects.all()
        # print(p.count())
        # # print("\n".join(list(p)))
        # # print(p.count())
        # # # p = Product.objects.get(spu_id=2267001)
        # # # print(p.slug)
        # a = input()
        # d = DeliveryType.objects.get(id=32887789)
        # print(d)
        # order = Order.objects.get(number="77934")
        # order = OrderSerializer(order).data
        # with open("order.json", 'w', encoding='utf-8') as output_file:
        #     json.dump(order, output_file, ensure_ascii=False, indent=2)

        # order.order_in_progress = False
        # order.status = Status.objects.get(name="В пути до московского склада")
        # order.save()
        # s = ProductUnit.objects.all()
        # print(s.count())

        # ou.final_price = 13090
        # ou.save()
        # ou = order.order_units.first()
        # print(ou.product.platform_info)
        # # ou.final_price = 26990
        # # ou.start_price = 26990
        # # ou.save()
        # print(ou.original_price)
        # ou.update_status(cancel=False)
        # print(ou.status)
        # order.status = Status.objects.get(name="Заказ принят")
        # order.save()
        # order.update_order_status()

        # order.fact_of_payment = True
        # order.save()
        # cart = ShoppingCart.objects.get(user=order.user)
        # send_email_confirmation_order(OrderSerializer(order).data, order.email)
        # cart.clear()

        # order.start_order()
        # order.fz54()

        # order.fact_of_payment = True
        # order.save()
        # cart = ShoppingCart.objects.get(user=order.user)
        # cart.clear()
        # send_email_confirmation_order(OrderSerializer(order).data, order.email)

        # file_path = "test_product.json"
        # with open(file_path, 'r', encoding='utf-8') as file:
        #     json_data = json.load(file)
        # s = add_products_spu_id_api(json_data)
        # s = input("s")
        # ids = ['36039']
        # for id in ids:
        #     order = Order.objects.get(number=id)
        #     order.order_in_progress = True
        #     send_email_full_order_shipped(OrderSerializer(order).data, order.email)
        # ou = order.order_units.all()
        # for u in ou:
        #     u.update_status(on_way_to_client=True)
        # order.update_order_status()
        #
        # order = Order.objects.get(number="74939")
        # order.status = Status.objects.get(name="Передан в службу доставки по России")
        # order.save()
        # a = input()
        # ou = order.order_units.all()
        # send_email_full_order_shipped(OrderSerializer(order).data, order.email)
        # send_email_full_order_shipped(OrderSerializer(order).data, "shmaraev18@mail.ru")
        # for u in ou:
        #     print(u.product.get_full_name())
        #     u.update_status(on_way_to_client=True)
        #     # u.add_track_number("AIA311098440")
        #
        # s = input()

        # order = Order.objects.get(number="49233")
        # print(order)
        # # order.start_order()
        # user_status = order.user.user_status
        # product = Product.objects.get(slug="coach-lane-20-455999")
        # pus = product.product_units.all()
        # for pu in pus:
        #     print(pu.view_size_platform, pu.final_price)
        #     a = input()
        #     if a == "1":
        #         order.add_order_unit(pu, user_status=user_status)
        # order.save()

        # print(order.status.name)
        # # a = input('s')
        # order.fact_of_payment = True
        # order.save()
        # cart = ShoppingCart.objects.get(user=order.user)
        # send_email_confirmation_order(OrderSerializer(order).data, order.email)
        #
        # # send_email_confirmation_order(OrderSerializer(order).data, "markenson888inst@gmail.com")
        # send_email_confirmation_order(OrderSerializer(order).data, "shmaraev18@mail.ru")
        # # send_email_confirmation_order(OrderSerializer(order).data, "wiwkw23@yandex.ru")
        # cart.clear()


        # a = input('d')
        # def round_number(num):
        #     n = 2 - len(str(num))
        #     return round(num, n)
        # def get_s(line=False, cat=False):
        #     imgs = []
        #     if line and cat:
        #         products = Product.objects.filter(lines=line, categories=cat, available_flag=True, is_custom=False).order_by("-score_product_page")
        #         url = f"https://sellout.su/products?line={line.full_eng_name}&category={cat.eng_name}"
        #         title = f"{cat.name} {line.view_name} по лучшей цене в РФ"
        #         description = f"Выбирайте среди {round_number(products.count())}+ оригинальных моделей {line.view_name}."
        #
        #     elif line:
        #         products = Product.objects.filter(lines=line, available_flag=True, is_custom=False).order_by("-score_product_page")
        #         url = f"https://sellout.su/products?line={line.full_eng_name}"
        #         title = f"{line.view_name} по лучшей цене в РФ на Sellout"
        #         description = f"Выбирайте среди {round_number(products.count())}+ оригинальных моделей {line.view_name}."
        #
        #
        #     else:
        #         products = Product.objects.filter(categories=cat, available_flag=True,
        #                                          is_custom=False).order_by("-score_product_page")
        #         url = f"https://sellout.su/products?category={cat.eng_name}"
        #         title = f"{cat.name} по лучшей цене в РФ на Sellout"
        #         description = f"Выбирайте среди {round_number(products.count())}+ моделей в категории {cat.name}."
        #     min_price = products.exclude(min_price=0).aggregate(minimal_price=Min('min_price'))['minimal_price']
        #     products = products[:5]
        #     for p in products:
        #         imgs.append(p.bucket_link.order_by('id').first().url)
        #
        #     s = [url, title, description, min_price, "RUB"]
        #     s.extend(imgs)
        #     return s

        #
        # lines = Line.objects.exclude(score=0)
        # s = []
        # cats = Category.objects.exclude(score=0)
        # k = 0
        # for line in lines:
        #
        #     for cat in cats:
        #         if Product.objects.filter(lines=line, categories=cat, available_flag=True, is_custom=False).count() > 5:
        #             s.append(get_s(line=line, cat=cat))
        #             k += 1
        #             if k % 10 == 0:
        #                 print(k)
        # for cat in cats:
        #     if Product.objects.filter(categories=cat, available_flag=True, is_custom=False).count() > 5:
        #         s.append(get_s(cat=cat))
        #         k += 1
        #         if k % 10 == 0:
        #             print(k)
        # for line in lines:
        #     if Product.objects.filter(lines=line, available_flag=True, is_custom=False).count() > 5:
        #         s.append(get_s(line=line))
        #         k += 1
        #         if k % 10 == 0:
        #             print(k)
        #
        # import csv
        #
        # # Список данных для заполнения CSV файла
        # data = s
        #
        # # Имя CSV файла, в который будем записывать данные
        # csv_filename = "data.csv"
        #
        # # Открываем файл для записи
        # with open(csv_filename, mode='w', newline='', encoding="utf-8") as file:
        #     writer = csv.writer(file)
        #
        #     # Записываем заголовки
        #     writer.writerow(["Url", "Title", "Description", "Offer minimal price", "Currency",
        #                      "Image url 1", "Image url 2", "Image url 3", "Image url 4", "Image url 5"])
        #
        #     # Записываем данные из списка в CSV файл
        #     for row in data:
        #         writer.writerow(row)
        #
        # print(f"CSV файл {csv_filename} успешно создан и заполнен данными.")
        # a = input("A")

        # def round_number(num):
        #     n = 2 - len(str(num))
        #     return round(num, n)
        # lines = Line.objects.order_by("id")
        # d = {}
        # for l in lines:
        #     d[l.view_name] = round_number(Product.objects.filter(lines=l).count())
        #
        # file_path = 'line_count.json'
        # with open(file_path, 'w', encoding='utf-8') as output_file:
        #     json.dump(d, output_file, ensure_ascii=False, indent=2)
        #
        #
        # a = input('s')

        # order = Order.objects.order_by("-id").first()
        # order.update_order_status()
        # order.total_bonus = 1500
        # order.total_bonus_and_promo_bonus = 1500
        # order.promo_bonus = 0
        # order.save()

        # user = User.objects.get(id=140)
        # cart = ShoppingCart.objects.get(user=user)

        # order.user = new_user
        # print(OrderSerializer(order).data)
        # send_email_confirmation_order(OrderSerializer(order).data, "shmaraev18@mail.ru")
        # order.save()
        # new_cart = ShoppingCart.objects.filter(user=new_user).order_by("id").first()
        # new_cart = cart
        # new_cart.user = new_user
        # new_user.save()
        # # new_cart.delete()
        # print(new_cart)
        # new_cart.save()
        # new_cart = cart
        # new_cart.user = new_user
        # new_cart.save()

        # new_user =

        # print(cart.user)
        # p = Product.objects.get(slug="nike-off-white-dunk-low-the-50-no28-811648")
        # pu = p.product_units.filter(availability=True)
        # for u in pu:
        #     print(u.view_size_platform, u.original_price)
        # ps = Product.objects.filter(is_sale=True)
        # for p in ps:
        #     if p.min_price == p.min_price_without_sale:
        #         p.del_sale()
        # prod = Product.objects.filter(available_flag=True, is_custom=False).order_by("-score_product_page")[:600]
        # sale = 0
        # for p in prod:
        #     if p.is_sale and random.randint(1, 12) % 4 == 0:
        #         p.del_sale()
        #
        #     # sale += p.is_sale
        #
        #     sale += p.is_sale
        # print(sale)
        # order = Order.objects.get(number="")
        # order.finish_order()


        # p.update(is_sale=False)
        # d = DeliveryType.objects.all()
        # print(d.count())
        # d.update(currency=13.15)
        # p = Product.objects.get(slug='nike-air-force-1-low-color-of-the-month-light-smoke-790148')
        # pu = p.product_units.filter(availability=True)
        # for u in pu:
        #     sizes = u.size.all()
        #     print(sizes.values_list("row", flat=True))
        #     a = input()
        #     if a == "1":
        #         print(u.history_price)
        # for category in Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие'):
        #     for line in Line.objects.filter(parent_line=None):
        #         s = Product.objects.filter(categories=category, lines=line).count()
        #         print(s)

        # order = Order.objects.get(number="42039")
        # order.update_order_status()
        #
        # zs = SpamEmail.objects.all()
        # for z in zs:
        #     print(z.email)
        # a = input("d")
        # s = [248104, 373903, 435663, 244333]
        # for t in s:
        #     print(Product.objects.get(id=t).slug)

        #

        # # print(s.slug)
        # p = Product.objects.get(slug="new-balance-550-blue-groove-558550")
        # print(p.spu_id)
        # s = p.sizes.all()
        # for size in s:
        #     print(size.row)

        # product = Product.objects.filter(available_flag=True, is_custom=False).order_by('-score_product_page')[:1]
        # for p in product:
        #     p.score_product_page = 1000
        #     p.save()
        # cache.clear()
        # product.update(score_product_page=1000)
        # pu = ProductUnit.objects.filter(availability=False)
        # print(pu.count())

        # cats = Category.objects.all().order_by("id")
        # json_data = {}
        # for cat in cats:
        #     json_data[cat.name] = ""
        # file_path = 'all_cat.json'
        # with open(file_path, 'w', encoding='utf-8') as output_file:
        #     json.dump(json_data, output_file, ensure_ascii=False, indent=2)
        # a = input()
        # p = Product.objects.get(spu_id=1523942)
        # print(p.slug)
        # a = input()
        # product = Product.objects.filter(min_price=0, is_custom=False).order_by("-score_product_page")[1000:2000]
        # k = 0
        # for p in product:
        #     sleep(2)
        #     k += 1
        #     print(k, p.spu_id, p.slug)
        #     s = requests.get(f"https://sellout.su/intermediate_parser/process_spu_id?spu_id={p.spu_id}")

        # a = input()

        # cache.clear()
        # order = Order.objects.get(number="42433")
        # print(OrderSerializer(order).data)
        # a = input()

        # header_photos = HeaderPhoto.objects.all().values_list("photo", flat=True)
        # s = []
        # for p in header_photos:
        #     s.append(p.replace("https://sellout.su/sellout-photos", ""))
        #
        # with open("output.txt", "w", encoding="utf-8") as file:
        #     file.write("\n".join(s))
        #
        # a = input()
        # product = Product.objects.filter(min_price=0, is_custom=False).order_by("-score_product_page")[:1000]
        # k = 0
        # for p in product:
        #     sleep(2)
        #     k += 1
        #     print(k, p.spu_id, p.slug)
        #     s = requests.get(f"https://sellout.su/intermediate_parser/process_spu_id?spu_id={p.spu_id}")
        # print(product.count())
        # order = Order.objects.get(number='42039')
        # ou = order.order_units.all()
        # for o in ou:
        #     print(o.product.slug)
        # order.save()
        # a = input()
        #
        #
        # for block in json_data:
        #     if block['type'] == "collection":
        #         print(block)
        #         col, _ = Collection.objects.get_or_create(query_name=block['url'].replace("collection=", ""))
        #
        #         col.subtitle = block['subTitle']
        #         col.title = block['title']
        #         col.save()
        #         print(col.subtitle)
        # prod = block['products'].split("\n")
        # for p in prod:
        #     try:
        #         print(p.replace("https://sellout.su/products/", ""))
        #         product = Product.objects.get(slug=p.replace("https://sellout.su/products/", ""))
        #         product.collections.add(col)
        #     except:
        #         pass

        # if block['type'] == 'complexMainPageBlock':
        #     for row in block['imagesInRow']:
        #         if f'gender={gender}' not in row['url']:
        #             row['url'] += f"&gender={gender}"
        #     if 'url' in block['fullWidthImage']:
        #         if f"&gender={gender}" not in  block['fullWidthImage']['url']:
        #             block['fullWidthImage']['url'] += f"&gender={gender}"
        #
        # if block['type'] == 'photo':
        #     if f'gender={gender}' not in block['desktop']['url']:
        #         block['desktop']['url'] += f"&gender={gender}"
        #     if f'gender={gender}' not in block['mobile']['url']:
        #         block['mobile']['url'] += f"&gender={gender}"
        # if block['type'] == 'selection':
        #     block['products'] = block['products'][:10]
        # if f'gender={gender}' not in block['url']:
        #     block['url'] += f"&gender={gender}"

        #
        # if block['type'] == "selection":
        #     print(block['url'])
        #     try:
        #         count = requests.get(f"https://sellout.su/api/v1/product/products_count?{block['url']}").json()['count']
        #     except:
        #         count = 60

        # print(count)
        # if count == 0:
        #     collection, _ = Collection.objects.get_or_create(name=block['title'])
        #
        #     collection.save()
        #     for prod in block['products']:
        #         pr = Product.objects.get(slug=prod)
        #         pr.collections.add(collection)
        #     count = 1
        #     block['url'] = f"collections={collection.query_name}"
        # if type(block['products']) == type(""):
        #     block['products'] = block['products'].split("\n")
        # s = []
        # for product in block['products']:
        #     slug = product.replace("https://sellout.su/products/", "")
        #     if Product.objects.filter(slug=slug).exists():
        #         s.append(ProductMainPageSerializer(Product.objects.get(slug=slug)).data)
        # block['products'] = s
        # block['productsAmount'] = count * 60

        # if block['type'] == 'photo':
        #
        #     title = block['desktop']['title']
        #     line = Line.objects.filter(view_name=title).exists()
        #     if line:
        #         line = Line.objects.get(view_name=title)
        #         header = HeaderPhoto.objects.filter(lines=line)
        #         block['desktop']['url'] = f"line={line.full_eng_name}".strip("_")
        #         block['mobile']['url'] = f"line={line.full_eng_name}".strip("_")
        #         block['desktop']['photo'] = header.filter(type='desktop').first().photo
        #         block['mobile']['photo'] = header.filter(type='mobile').first().photo
        #         text = HeaderText.objects.get(lines=line)
        #         block['mobile']['content'] = text.text
        #         block['desktop']['content'] = text.text
        #     collab = Collab.objects.filter(name=title)
        #     if collab:
        #         collab = Collab.objects.get(name=title)
        #         header = HeaderPhoto.objects.filter(collabs=collab)
        #         block['desktop']['url'] = f"collab={collab.query_name}".strip("_")
        #         block['mobile']['url'] = f"collab={collab.query_name}".strip("_")
        #         block['desktop']['photo'] = header.filter(type='desktop').first().photo
        #         block['mobile']['photo'] = header.filter(type='mobile').first().photo
        #         text = HeaderText.objects.get(collabs=collab)
        #         block['mobile']['content'] = text.text
        #         block['desktop']['content'] = text.text
        #     block['mobile']['button'] = "Посмотреть все"
        #     block['desktop']['button'] = "Посмотреть все"
        # a = input("cerf")
        # file_path = 'temp_main_men_withproducts.json'
        # with open(file_path, 'w', encoding='utf-8') as output_file:
        #     json.dump(json_data, output_file, ensure_ascii=False, indent=2)
        # print("сука")

        # product = Product.objects.filter(is_sale=True)
        # for pr in product:
        #     if pr.min_price == pr.min_price_without_sale:
        #         print(pr)
        #         pr.del_sale()
        # product.update(available_flag=False)

        # order = Order.objects.order_by("-id").first()
        # ou = order.order_units.all()
        # for o in ou:
        #     print(o.product.slug)
        # a = input()
        #
        # order.fact_of_payment = True
        # send_email_confirmation_order(OrderSerializer(order).data, "tb.sum@yandex.ru")
        # order.save()
        # product = Product.objects.get(slug="vivienne-westwood-new-tiny-orb-811232")
        # product.add_sale(5500, 0)
        # pu = product.product_units.filter(availability=True)
        # # product.add_sale()
        # for u in pu:
        #     u.start_price = 41490
        #     u.final_price = 35990
        #     u.is_sale = True
        #     product.is_sale = True
        #     u.save()
        #
        # product.actual_price = True
        # print("a", product.min_price_without_sale)
        #
        # product.save()
        # product.actual_price = True
        # product.min_price_without_sale = 41490
        #
        # product.save()
        # # product.update_min_price()
        # for u in pu:
        #     print(u.start_price)
        # # product.add_sale(5500, 0)
        # product.del_sale()
        # print(product.size_table_platform)
        # a1 = input()
        file_path = 'picture.json'

        # Откройте файл и загрузите его содержимое в словарь

        # order = Order.objects.get(number="36039")
        # order.fact_of_payment = True
        # order.save()
        # cart = ShoppingCart.objects.get(user=order.user)
        # send_email_confirmation_order(OrderSerializer(order).data, order.email)
        # send_email_confirmation_order(OrderSerializer(order).data, "shmaraev18@mail.ru")
        # cart.clear()
        # order = Order.objects.get(number="35938")
        # ou = order.order_units.all()
        # pu = ProductUnit.objects.filter(final_price__lt=0)

        # for o in ou:
        #     print(o.product.slug, o.final_price, o.start_price, o.view_size_platform, o.original_price)

        # file_path = 'поисковые фразы15-60.txt'
        # with open(file_path, 'w', encoding="utf-8") as file:
        #     lines = Line.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие').order_by("id")
        #     # print(lines.count())
        #     s = []
        #     for line in lines:
        #         count = Product.objects.filter(lines=line).count()
        #         if count >= 15 and count < 60:
        #             file.write("%s\n" % f"{line.view_name}")
        #     print(len(s))
        #     cats = Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Вся').exclude(
        #         name__icontains='Другие').order_by('id')
        #     # for cat in cats:
        #     #     count = Product.objects.filter(categories=cat).count()
        #     #     if count >= 15 and count < 60:
        #     #         file.write("%s\n" % f"{cat.name} {count}")
        #     # print(len(s))
        #
        #     for cat in cats:
        #         for line in lines:
        #             if Product.objects.filter(categories=cat, lines=line).exists():
        #                 count = Product.objects.filter(categories=cat, lines=line).count()
        #                 if count >= 15 and count < 60:
        #                     file.write("%s\n" % f"{cat.name} {line.view_name}")
        #     print(len(s))
        #
        # print(f"Список сохранен в файл: {file_path}")
        # a = input("s")
        # cur = Currency.objects.all()
        # for c in cur:
        #     print(c.name)
        # print(ProductUnit.objects.get(id=7663797).platform_info)

        # user = User.objects.get(email="iesm@mail.ru")
        # cart = ShoppingCart.objects.get(user=user)
        # cart.clear()

        # print(0)
        # print(o.start_price)
        # h = HeaderText.objects.order_by("-id").first()
        # h.text = "Собрали товары, которые упали в цене, при этом все так же востребованы. Успей купить желанные лоты по самым лучшим ценам!"
        # h.save()
        # products = Product.objects.filter(is_sale=True)
        # for product in products:
        #     f = False
        #     pus = ProductUnit.objects.filter(product=product, availability=True)
        #     for pu in pus:
        #         if pu.start_price > pu.final_price:
        #             f = True
        #     product.is_sale = f
        #     product.save()
        # print(Product.objects.all().first())
        # orders = Order.objects.filter(order_in_progress=True)
        # for order in orders:
        #     order.update_order_status()
        #     print(order.status, order.user)
        # d = {
        #     "Обувь": {"count": "178'000", "RP": "Обуви"},
        #     "Вся обувь": {"count": "178'000", "RP": "Всей обуви"},
        #     "Кроссовки": {"count": "145'000", "RP": "Кроссовок"},
        #     "Все кроссовки": {"count": "145'000", "RP": "Всех кроссовок"},
        #     "Высокие кроссовки": {"count": "17'000", "RP": "Высоких кроссовок"},
        #     "Низкие кроссовки": {"count": "110'000", "RP": "Низких кроссовок"},
        #     "Баскетбольные кроссовки": {"count": "11'000", "RP": "Баскетбольных кроссовок"},
        #     "Футбольные бутсы": {"count": "2'400", "RP": "Футбольных бутс"},
        #     "Другие кроссовки для спорта": {"count": "6'000", "RP": "Других кроссовок для спорта"},
        #     "Кеды": {"count": "4'000", "RP": "Кед"},
        #     "Лоферы": {"count": "1'400", "RP": "Лоферов"},
        #     "Мокасины и топсайдеры": {"count": "80", "RP": "Мокасин и топсайдеров"},
        #     "Слипоны": {"count": "1'000", "RP": "Слипонов"},
        #     "Эспадрильи": {"count": "100", "RP": "Эспадрильей"},
        #     "Сандалии и босоножки": {"count": "7'000", "RP": "Сандалей и босоножек"},
        #     "Пляжные сандалии": {"count": "2'200", "RP": "Пляжных сандалий"},
        #     "Шлёпки и тапки": {"count": "3'600", "RP": "Шлёпок и тапок"},
        #     "Мюли и сабо": {"count": "700", "RP": "Мюлей и сабо"},
        #     "Туфли": {"count": "8'300", "RP": "Туфель"},
        #     "Все туфли": {"count": "8'300", "RP": "Всех туфель"},
        #     "Туфли на высоком каблуке": {"count": "3'400", "RP": "Туфель на высоком каблуке"},
        #     "Туфли на среднем каблуке": {"count": "1'500", "RP": "Туфель на среднем каблуке"},
        #     "Туфли на низком каблуке": {"count": "5'400", "RP": "Туфель на низком каблуке"},
        #     "Туфли на танкетке": {"count": "20", "RP": "Туфель на танкетке"},
        #     "Мужские туфли": {"count": "2'200", "RP": "Мужских туфель"},
        #     "Дерби": {"count": "100", "RP": "Дерби"},
        #     "Оксфорды": {"count": "50", "RP": "Оксфордов"},
        #     "Броги": {"count": "40", "RP": "Брог"},
        #     "Монки": {"count": "5", "RP": "Монков"},
        #     "Ботинки": {"count": "5'500", "RP": "Ботинок"},
        #     "Все ботинки": {"count": "5'500", "RP": "Всех ботинок"},
        #     "Ботинки на толстой подошве": {"count": "600", "RP": "Ботинок на толстой подошве"},
        #     "Высокие ботинки и ботфорты": {"count": "600", "RP": "Высоких ботинок и ботфортов"},
        #     "Средние ботинки": {"count": "60", "RP": "Средних ботинок"},
        #     "Короткие ботинки и ботильоны": {"count": "2'400", "RP": "Коротких ботинок и ботильонов"},
        #     "Челси": {"count": "780", "RP": "Челси"},
        #     "Мартинсы": {"count": "1'100", "RP": "Мартинсов"},
        #     "Тимберленды": {"count": "440", "RP": "Тимберлендов"},
        #     "Дезерты": {"count": "0", "RP": "Дезертов"},
        #     "Казаки": {"count": "0", "RP": "Казаков"},
        #     "Зимние кроссовки и ботинки": {"count": "3'000", "RP": "Зимних кроссовок и ботинок"},
        #     "Одежда": {"count": "246'000", "RP": "Одежды"},
        #     "Вся одежда": {"count": "246'000", "RP": "Всей одежды"},
        #     "Футболки": {"count": "52'000", "RP": "Футболок"},
        #     "Лонгсливы": {"count": "6'700", "RP": "Лонгсливов"},
        #     "Худи и толстовки": {"count": "38'000", "RP": "Худи и толстовок"},
        #     "Все худи и толстовки": {"count": "38'000", "RP": "Всех худи и толстовок"},
        #     "Худи с капюшоном": {"count": "20'000", "RP": "Худи с капюшоном"},
        #     "Толстовки на молнии": {"count": "3'900", "RP": "Толстовок на молнии"},
        #     "Свитшоты": {"count": "16'000", "RP": "Свитшотов"},
        #     "Свитеры и трикотаж": {"count": "10'000", "RP": "Свитеров и трикотажа"},
        #     "Все свитеры и трикотаж": {"count": "10'000", "RP": "Всех свитеров и трикотажа"},
        #     "Свитеры": {"count": "6'500", "RP": "Свитеров"},
        #     "Кардиганы": {"count": "2'300", "RP": "Кардиганов"},
        #     "Водолазки": {"count": "1'400", "RP": "Водолазок"},
        #     "Жилеты": {"count": "140", "RP": "Жилетов"},
        #     "Шорты": {"count": "12'000", "RP": "Шортов"},
        #     "Треники": {"count": "25'000", "RP": "Треников"},
        #     "Спортивная одежда": {"count": "9'700", "RP": "Спортивной одежды"},
        #     "Вся спортивная одежда": {"count": "9'700", "RP": "Всей спортивной одежды"},
        #     "Баскетбольные джерси": {"count": "2'100", "RP": "Баскетбольных джерси"},
        #     "Баскетбольные шорты": {"count": "1'100", "RP": "Баскетбольных шортов"},
        #     "Футбольные майки": {"count": "600", "RP": "Футбольных маек"},
        #     "Футбольные шорты": {"count": "50", "RP": "Футбольных шортов"},
        #     "Спортивные майки": {"count": "1'100", "RP": "Спортивных маек"},
        #     "Спортивные шорты": {"count": "700", "RP": "Спортивных шортов"},
        #     "Спортивные топы": {"count": "1'700", "RP": "Спортивных топов"},
        #     "Спортивные костюмы": {"count": "0", "RP": "Спортивных костюмов"},
        #     "Легинсы и термобелье": {"count": "1'300", "RP": "Леггинсов и термобелья"},
        #     "Топы": {"count": "600", "RP": "Топов"},
        #     "Майки": {"count": "4'200", "RP": "Маек"},
        #     "Поло": {"count": "5'800", "RP": "Поло"},
        #     "Джинсы": {"count": "6'000", "RP": "Джинсов"},
        #     "Юбки": {"count": "3'800", "RP": "Юбок"},
        #     "Платья": {"count": "7'300", "RP": "Платьев"},
        #     "Рубашки": {"count": "10'500", "RP": "Рубашек"},
        #     "Брюки": {"count": "4'500", "RP": "Брюк"},
        #     "Пиджаки": {"count": "2'000", "RP": "Пиджаков"},
        #     "Костюмы": {"count": "200", "RP": "Костюмов"},
        #     "Деним": {"count": "8'200", "RP": "Денима"},
        #     "Комбинезоны и боди": {"count": "500", "RP": "Комбинезонов и боди"},
        #     "Зимние штаны": {"count": "100", "RP": "Зимних штанов"},
        #     "Верхняя одежда": {"count": "42'700", "RP": "Верхней одежды"},
        #     "Вся верхняя одежда": {"count": "42'700", "RP": "Всей верхней одежды"},
        #     "Куртки": {"count": "26'600", "RP": "Курток"},
        #     "Кожаные куртки": {"count": "200", "RP": "Кожаных курток"},
        #     "Жилетки": {"count": "2'338", "RP": "Жилеток"},
        #     "Плащи": {"count": "117", "RP": "Плащей"},
        #     "Пальто": {"count": "2'384", "RP": "Пальто"},
        #     "Пуховики": {"count": "7'299", "RP": "Пуховиков"},
        #     "Шубы": {"count": "10", "RP": "Шуб"},
        #     "Лыжные костюмы": {"count": "38", "RP": "Лыжных костюмов"},
        #     "Пляжная одежда": {"count": "1'588", "RP": "Пляжной одежды"},
        #     "Мужские плавки": {"count": "413", "RP": "Мужских плавок"},
        #     "Женские купальники": {"count": "206", "RP": "Женских купальников"},
        #     "Сплошные купальники": {"count": "505", "RP": "Сплошных купальников"},
        #     "Нижнее бельё и домашняя одежда": {"count": "9'526", "RP": "Нижнего белья и домашней одежды"},
        #     "Домашняя одежда": {"count": "124", "RP": "Домашней одежды"},
        #     "Носки": {"count": "6'508", "RP": "Носков"},
        #     "Бюстгальтеры": {"count": "377", "RP": "Бюстгальтеров"},
        #     "Трусы": {"count": "2'008", "RP": "Трусов"},
        #     "Сумки": {"count": "57'137", "RP": "Сумок"},
        #     "Сумки через плечо": {"count": "28'811", "RP": "Сумок через плечо"},
        #     "Сумки на плечо": {"count": "34'138", "RP": "Сумок на плечо"},
        #     "Сумки с ручками": {"count": "21'106", "RP": "Сумок с ручками"},
        #     "Сумки на грудь": {"count": "1'303", "RP": "Сумок на грудь"},
        #     "Сумки на пояс": {"count": "2'778", "RP": "Сумок на пояс"},
        #     "Сумки тоут": {"count": "5'678", "RP": "Сумок тоут"},
        #     "Сумки хобо": {"count": "369", "RP": "Сумок хобо"},
        #     "Сумки вёдра": {"count": "2'079", "RP": "Сумок вёдра"},
        #     "Рюкзаки": {"count": "6'453", "RP": "Рюкзаков"},
        #     "Портфели": {"count": "385", "RP": "Портфелей"},
        #     "Клатчи": {"count": "3'718", "RP": "Клатчей"},
        #     "Кошельки": {"count": "5'380", "RP": "Кошельков"},
        #     "Кардхолдеры": {"count": "2'013", "RP": "Кардхолдеров"},
        #     "Обложки на паспорт": {"count": "32", "RP": "Обложек на паспорт"},
        #     "Косметички": {"count": "443", "RP": "Косметичек"},
        #     "Спортивные сумки": {"count": "573", "RP": "Спортивных сумок"},
        #     "Чемоданы и дорожные сумки": {"count": "663", "RP": "Чемоданов и дорожных сумок"},
        #     "Аксессуары для сумок": {"count": "128", "RP": "Аксессуаров для сумок"},
        #     "Аксессуары": {"count": "113'927", "RP": "Аксессуаров"},
        #     "Ремни": {"count": "4'328", "RP": "Ремней"},
        #     "Шарфы": {"count": "6'077", "RP": "Шарфов"},
        #     "Перчатки": {"count": "269", "RP": "Перчаток"},
        #     "Головные уборы": {"count": "11'993", "RP": "Головных уборов"},
        #     "Кепки": {"count": "6'727", "RP": "Кепок"},
        #     "Шапки": {"count": "2'475", "RP": "Шапок"},
        #     "Панамы": {"count": "2'450", "RP": "Панам"},
        #     "Шляпы": {"count": "78", "RP": "Шляп"},
        #     "Береты": {"count": "263", "RP": "Беретов"},
        #     "Спортивные товары": {"count": "9'231", "RP": "Спортивных товаров"},
        #     "Баскетбольные мячи": {"count": "5'178", "RP": "Баскетбольных мячей"},
        #     "Футбольные мячи": {"count": "587", "RP": "Футбольных мячей"},
        #     "Волейбольные мячи": {"count": "98", "RP": "Волейбольных мячей"},
        #     "Спортивные перчатки": {"count": "177", "RP": "Спортивных перчаток"},
        #     "Спортивная экипировка": {"count": "1'185", "RP": "Спортивной экипировки"},
        #     "Другие спортивные товары": {"count": "2'006", "RP": "Других спортивных товаров"},
        #     "Украшения": {"count": "18'606", "RP": "Украшений"},
        #     "Цепочки": {"count": "6'538", "RP": "Цепочек"},
        #     "Браслеты": {"count": "4'206", "RP": "Браслетов"},
        #     "Кольца": {"count": "2'212", "RP": "Колец"},
        #     "Серьги": {"count": "3'981", "RP": "Серёг"},
        #     "Кулоны": {"count": "1'122", "RP": "Кулонов"},
        #     "Брошь": {"count": "238", "RP": "Брошей"},
        #     "Другие украшения": {"count": "309", "RP": "Других украшений"},
        #     "Bearbricks и другие коллекционные предметы": {"count": "2'066",
        #                                                    "RP": "Bearbricks и других коллекционных предметов"},
        #     "Солнцезащитные очки": {"count": "5'193", "RP": "Солнцезащитных очков"},
        #     "Оправы для очков": {"count": "2'042", "RP": "Оправ для очков"},
        #     "Очешники": {"count": "11", "RP": "Очешников"},
        #     "Галстуки": {"count": "616", "RP": "Галстуков"},
        #     "Часы": {"count": "14'564", "RP": "Часов"},
        #     "Духи": {"count": "5'627", "RP": "Духов"},
        #     "Косметика": {"count": "23'438", "RP": "Косметики"},
        #     "Брелоки": {"count": "481", "RP": "Брелоков"},
        #     "Чехлы для телефона": {"count": "284", "RP": "Чехлов для телефона"},
        #     "Аксессуары для техники": {"count": "150", "RP": "Аксессуаров для техники"},
        #     "Другие аксессуары": {"count": "8'951", "RP": "Других аксессуаров"},
        #     "Джинсовые куртки": {"count": "1'231", "RP": "Джинсовых курток"},
        #     "Бейсбольные куртки": {"count": "732", "RP": "Бейсбольных курток"},
        #     "Ветровки": {"count": "1'729", "RP": "Ветровок"},
        #     "Вся пляжная одежда": {"count": "1'588", "RP": "Всей пляжной одежды"},
        #     "Все нижнее бельё и домашняя одежда": {"count": "9'526", "RP": "Всей нижней белья и домашней одежды"},
        #     "Все сумки": {"count": "57'137", "RP": "Всех сумок"},
        #     "Все аксессуары": {"count": "113'927", "RP": "Всех аксессуаров"},
        #     "Все головные уборы": {"count": "11'993", "RP": "Всех головных уборов"},
        #     "Все спортивные товары": {"count": "9'231", "RP": "Всех спортивных товаров"},
        #     "Все украшения": {"count": "18'606", "RP": "Всех украшений"}
        # }
        #
        # description = {}
        #
        # def format_count(count):
        #     formatted_count = "{:,}".format(count).replace(",", "'")
        #     return formatted_count
        #
        # import pymorphy2
        #
        # def get_rp_category(category):
        #     # Создаем объект pymorphy2
        #     morph = pymorphy2.MorphAnalyzer()
        #
        #     # Приводим категорию к нормальной форме и получаем родительный падеж
        #     normal_form = morph.parse(category)[0].normal_form
        #     rp_category = morph.parse(normal_form)[0].inflect({'gent'}).word
        #
        #     return rp_category
        #
        # rp_cat = {}
        # for cat in Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие').exclude(name__icontains='Вся').order_by("id"):
        #     if cat.name not in d:
        #         print(cat.name)
        #     else:
        #         rp_cat[cat.name] = d[cat.name]['RP']
        #
        # print(rp_cat)
        # for cat in Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие').exclude(name__icontains='Вся').order_by("id"):
        #     description[cat.name] = {"title": f"Купить {cat.name.lower()} по лучшим ценам в РФ на Sellout",
        #                              "description": f"Нашли дешевле? Мы предложим более выгодную цену! Выберите среди {format_count(Product.objects.filter(categories=cat).count())}+ оригинальных {rp_cat[cat.name].lower()} от 400+ мировых брендов. 3-ёх этапная проверка на оригинальность"}
        #
        # # for k, v in d.items():
        # #     description[k] = {"title": f"Купить {k} по лучшим ценам в РФ на Sellout",
        # #                       "description": f"Нашли дешевле? Мы предложим более выгодную цену! Выберите среди {v['count']}+ ориганльных {v['RP']} от 400+ мировых брендов. 3-ёх этапная проверка на оригинальность"}
        #
        # description["Новинки"] = {"title": "Новинки на платформе Sellout",
        #                           "description": "Собрали самые актуальные и трендовые модели и коллекции на сегодняшний день. Погрузитесь в захватывающий мир новинок и обновите свой гардероб сегодня"}
        # description['Скидки — еще больше выгоды'] = {"title": "Скидки на платформе Sellout — еще больше выгоды",
        #                                              "description": "Собрали товары, которые упали в цене, при этом все так же востребованы. Успей купить желанные лоты по самым лучшим ценам"}
        # description['Рекоммендации'] = {'title': "Рекомендации от экспертов на платформе Sellout",
        #                                 "description": "Наши стилисты ежедневно следят за стремительно трансформирующейся модой и подбирают для Вас модели, пользующиеся наибольшим спросом во всем мире"}
        #
        # for brand in Brand.objects.all():
        #     description[brand.name] = {"title": f"Купить лучшие позиции от {brand.name} на платформе Sellout",
        #                                "description": f"Нашли дешевле? Мы предложим более выгодную цену! Выберите среди {format_count(Product.objects.filter(brands=brand).count())}+ оригинальных лотов от {brand.name}. 3-ёх этапная проверка на оригинальность"}
        # # print(description)

        # for line in Line.objects.exclude(parent_line=None):
        #     description[line.view_name] = {"title": f"Купите {line.view_name} по лучшей цене в РФ на Sellout",
        #                          'description': f"Нашли дешевле? Мы предложим более выгодную цену! Выберите среди {format_count(Product.objects.filter(lines=line).count())}+ оригинальных моделей {line.view_name}. 3-ёх этапная проверка на оригинальность"}
        #
        # k = 0
        # for cat in Category.objects.exclude(name__icontains='Все').exclude(name__icontains='Другие').exclude(name__icontains='Вся'):
        #     for brand in Brand.objects.all():
        #         k += 1
        #         if k % 100 == 0:
        #             print(k)
        #         if Product.objects.filter(brands=brand, categories=cat).exists():
        #             print(1)
        #             description[f"{cat.name} {brand.name}"] = {"title": f"Купите {f'{cat.name.lower()} {brand.name}'} по лучшей цене в РФ на Sellout",
        #                                          "description": f"Нашли дешевле? Мы предложим более выгодную цену! Выберите среди {format_count(Product.objects.filter(brands=brand, categories=cat).count())}+ оригинальных моделей {rp_cat[cat.name].lower()} {brand.name}. 3-ёх этапная проверка на оригинальность"}
        # with open("seo_title_description.json", 'w', encoding='utf-8') as json_file:
        #     json.dump(description, json_file, ensure_ascii=False, indent=4)
        # # product = Product.objects.get(slug="jordan-air-jordan-4-retro-thunder-28734")
        # unit = ProductUnit.objects.filter(product=product, is_sale=True)
        # # unit.update(is_sale=False)
        # # product.is_sale = False
        # product.save()
        # for u in unit:
        #     print(u.view_size_platform, u.start_price, u.final_price)

        # product = Product.objects.get(manufacturer_sku="FN3421-104")
        # print(product.parameters)
        # product.parameters["parameters"]["Прыжок"] = ["+100"]
        # # product.parameters['parameters_order'].append("Прыжок")
        # print(product.parameters)
        # product.save()
        # order = Order.objects.order_by("-id").first()
        # print(order.status)
        # order.update_order_status()
        # print(order.status)
        # order.start_order()

        # ou = order.order_units.all()
        # for o in ou:
        #
        #     print(ProductSerializer(o.product).data)
        #     print(o.product.spu_id)
        # print(str(OrderSerializer(order).data).replace("'", '"'))
        # p = Product.objects.get(slug="gucci-g-4cm-31810")
        # print(p.spu_id)

        # order.finish_order()
        # s = ProductUnit.objects.get(id=7663797)
        # print(s.platform_info)
        # s = []
        # line = Line.objects.all()
        # for l in line:
        #     prc = Product.objects.filter(categories__name="Обувь", lines=l).count()
        #     s.append([prc, l.name])
        # s.sort()
        # for _ in s:
        #     print(f"{_[1]}: {_[0]}")
        # product = Product.objects.get(slug="li-ning-sonic-10-v1-543617")
        # pu = product.product_units.all()
        # for u in pu:
        #     u.original_price = u.original_price + 100
        #     u.save()
        # product.actual_price = False
        # product.update_price()
        # texts = HeaderText.objects.order_by("id")
        # for text in texts:
        #     if text.lines.exists():
        #         line = text.lines.order_by("-id").first()
        #         print(line)
        #         product = Product.objects.filter(lines=line)
        #         product.update(description=text.text)
        # products = Product.objects.order_by("id")
        # count = products.count()
        # for page in range(0, count, 100):
        #     page_prod = products[page:page + 100]
        #     for product in page_prod:
        #         line = product.lines.order_by("-id").first()
        #         texts = HeaderText.objects.filter(line=line)
        #         if texts.exists():
        #             text = texts.first()
        #             product.description = text.text
        #             product.save()

        # sp = SpamEmail.objects.all()
        # for s in sp:
        #     print(s.email)
        # product = Product.objects.filter(available_flag=True, is_custom=False).order_by("-score_product_page").first()
        # product.description = "Nike Dunk Low - это смешение стиля и удобства в мире кроссовок. Эта модель предоставляет низкий силуэт и минималистичный дизайн, отражая дух уличной моды и комфорта. Nike Dunk Low отличается разнообразием цветовых вариантов и материалов, позволяя создавать стильные и выразительные образы."
        # # product.description = ""
        # product.save()
        # print(product.description)
        # print(product.slug)
        # products = Product.objects.filter(available_flag=True, is_custom=False).order_by("-score_product_page").values_list("slug", flat=True)[:2000]
        #
        # s = []
        #
        # for p in products:
        #     s.append(f"https://sellout.su/products/{p}")
        #     print(s[-1])
        #
        # with open('url_list.txt', 'w') as file:
        #     # Записываем каждый элемент списка в отдельной строке файла
        #     for item in s:
        #         file.write("%s\n" % item)
        # # order =
        # order = Order.objects.get(id=270)
        # user = order.user
        # order.accrue_bonuses()
        # print(user.bonuses.total_amount)
        # # order.get_total_bonus()
        # # order.start_order()
        # print(order.total_bonus_and_promo_bonus)
        # print(order.status)
        # pu = order.order_units.all()
        # for u in pu:
        #     print(u.original_price)
        #     print(u.total_profit)
        #     print(u.weight)
        # collabs = Collab.objects.all()
        # for collab in collabs:
        #     collab.order = collab.id
        #     if collab.id == 198:
        #         collab.order = 1000
        #     collab.save()
        # order = Order.objects.order_by("-id").first()
        # order.fact_of_payment = True
        # order.save()
        # order.start_order()
        # order.accrue_bonuses()
        # order.save()
        # print(order.id)
        # total_min_price_sum = Product.objects.aggregate(total_sum=Sum('min_price'))['total_sum']
        #
        # # Вывод результата
        # print(f"Сумма min_price для всех продуктов: {total_min_price_sum}")
        # product = Product.objects.order_by("-min_price")
        # sm =
        # for p in product:
        #     pu = p.product_units.all()
        #     for u in pu:
        #         print(f"{u.original_price} {u.size_platform}")
        #     print(p.slug)

        # def default_referral_data(id):
        #     return {
        #         "order_amounts": [3000, 35000],
        #         "partner_bonus_amounts": [500, 1000],
        #         "client_sale_amounts": None,
        #         "client_bonus_amounts": [100, 1000],
        #         "promo_text": None,
        #         "promo_link": f"https://sellout.su?referral_id={id}",
        #     }
        # users = User.objects.all()
        # for u in users:
        #     promo = u.referral_promo.string_representation
        #     u.referral_data = default_referral_data(promo)
        #     print(u.referral_data)
        #     u.save()
        # data = "SMARAEVARTEM53"
        # referral_promo = PromoCode.objects.get(string_representation=data.upper())
        #
        # ref_user = referral_promo.owner
        # print(ref_user)
        # cart = ShoppingCart.objects.get(user=User.objects.get(email="felta2506@inbox.ru"))
        # product = cart.product_units.all()
        # for p in product:
        #     print(f"https://sellout.su/products/{p.product.slug}")
        # last_ous = OrderUnit.objects.order_by("-id").first()
        # last_ous.add_track_number("123")
        # p = Product.objects.order_by("-id").first()
        # print(p.slug)
        # order = Order.objects.order_by("-id").first()
        # order.fact_of_payment = True
        # order.accrue_bonuses()
        # order.save()
        # s = RansomRequest.objects.order_by("-id").first()
        # print(s.photo)
        # with open('lines_temp.json', 'r') as file:
        #     data = json.load(file)
        # #
        # # # Вывод словаря
        # # s = []
        # for line in data:
        #     if line['id'] < 490 and "другие" not in line["view_name"].lower() and line["full_eng_name"][-1] != "_":
        #         s.append(line["full_eng_name"])
        # print(s)
        k = 1
        root = ET.Element('urlset')
        lines = Line.objects.all().exclude(name__icontains='Все').exclude(name__icontains='Другие').exclude(
            name__icontains='Вся').order_by("id")
        cats = Category.objects.all().exclude(name__icontains='Все').exclude(name__icontains='Другие').exclude(
            name__icontains='Вся').order_by("id")
        for line in lines:
            url_element = ET.SubElement(root, 'url')
            loc_element = ET.SubElement(url_element, 'loc')
            loc_element.text = f"https://sellout.su/products?line={line.full_eng_name}"
        for cat in cats:
            url_element = ET.SubElement(root, 'url')
            loc_element = ET.SubElement(url_element, 'loc')
            loc_element.text = f"https://sellout.su/products?category={cat.eng_name}"
        for cat in cats:
            for line in lines:
                k += 1
                print(k)
                if Product.objects.filter(available_flag=True, is_custom=False, lines=line, categories=cat).exists():
                    url_element = ET.SubElement(root, 'url')
                    loc_element = ET.SubElement(url_element, 'loc')
                    loc_element.text = f"https://sellout.su/products?category={cat.eng_name}&line={line.full_eng_name}"

        # Создание объекта ElementTree
        tree = ET.ElementTree(root)

        # Запись XML в файл
        tree.write('sitemap_line.xml', encoding='utf-8', xml_declaration=True)
        a = input("Ujnjdj")
        # print("cerf")

        # prs = Product.objects.all()
        # prs.update(actual_price=False)
        # product = Product.objects.get(slug="nike-dunk-low-sb-michael-lau-gardener-wood-41367")
        # product.model = "Dunk Low"
        # sleep(80)
        # product.save()

        # rr = RansomRequest.objects.all()
        # for r in rr:
        #     print(r.photo)
        #     sleep(20)

        # texts = HeaderText.objects.filter(title='sellout')
        # texts.update(type='desktop')
        #
        # texts = HeaderPhoto.objects.all()
        # for text in texts:
        #     s = text.lines.all()
        #     for curent_line in s:
        #         if Line.objects.filter(name=f"Все {curent_line.name}").exists():
        #             line_db = Line.objects.get(name=f"Все {curent_line.name}")
        #             text.lines.add(line_db)
        #         text.save()
        #         print(text.lines.all())

        #     line = s.order_by("-id").first()
        #     text.lines.clear()
        #     text.lines.add(line)
        #     text.save()
        #     curent_line = s.first()

        #     while curent_line.parent_line is not None:
        #         curent_line = curent_line.parent_line
        #         text.lines.add(curent_line)
        #         if Line.objects.filter(name=f"Все {curent_line.name}").exists():
        #             line_db = Line.objects.get(name=f"Все {curent_line.name}")
        #             text.lines.add(line_db)
        # text.save()

        # if "yeezy" in line_name.lower():
        # product = Product.objects.get(slug="timberland-field-780538")
        # pus = product.product_units.all()
        # for pu in pus:
        #     if "43" in pu.view_size_platform:
        #         print(pu.original_price, pu.weight_kg, pu.weight, pu.delivery_type.decimal_insurance)

        # pus = ProductUnit.objects.filter(update_w=False)
        # count = pus.count()
        # k = 0
        # for page in range(0, count, 100):
        #     pus_page = pus[page:page + 100]
        #     for pu in pus_page:
        #         pu.weight_kg = pu.weight
        #         pu.update_w = True
        #         pu.save()
        #     k += 100
        #     if k % 1000 == 0:
        #         print(k, count)

        # ps = Product.objects.filter(min_price=0)
        # # ps.update(score_product_page=-10000)
        # ps.update(available_flag=False)
        # order = Order.objects.filter(user=User.objects.get(email="dolgirev_lev2003@mail.ru"), fact_of_payment=True).order_by("-id").first()
        # order.update_order_status()

        # for ord in order:
        #     print(ord.id)
        #     ord.update_order_status()

        # ProductUnit.objects.update(weight=F('weight') * 1000)
        # ps = Product.objects.filter(is_recommend=True)
        # print(ps.count())
        # print("готово")
        # products = ProductUnit.objects.all()
        # ck = products.count()
        # k = 0
        # for unit in products:
        #     k += 1
        #     if k % 100 == 0:
        #         print(k, ck)
        #     w = unit.weight
        #     unit.weight_kg = w
        # p = Product.objects.get(slug="nike-dunk-low-chicago-split-262086")
        # p.available_flag = True
        # p.save()
        # pr = Product.objects.all()
        # pr.update(actual_price=False)
        # ds = DewuInfo.objects.all()
        # print(ds.count())
        # cart = ShoppingCart.objects.get(user=User.objects.get(email="Lesnoy.enotik@mail.ru"))
        # p1 = Product.objects.get(slug="balenciaga-cagole-279820")
        # for unit in p1.product_units.filter(availability=True):
        #     if "40" in unit.view_size_platform:
        #         print(unit.delivery_type.days_min, unit.delivery_type.days_max, unit.view_size_platform, unit.final_price)
        #         s = input()
        #         if s == "1":
        #             cart.product_units.add(unit)
        # cart.save()
        # p1 = Product.objects.get(id=279820)
        # for unit in p1.product_units.all():
        #     print(unit.delivery_type.days_min, unit.delivery_type.days_max, unit.view_size_platform)
        #     s = input()
        #     if s == "1":
        #         cart.product_units.add(unit)

        # su = cart.product_units.all()
        # print(cart.final_amount)
        # for pu in su:
        #     if pu.availability == False:
        #         cart.product_units.remove(pu)
        #         cart.save()
        #     print(f"https://sellout.su/products/{pu.product.slug}")
        #     print("Цена Р:", pu.final_price, "Цена Y:", pu.original_price, pu.url, pu.product.manufacturer_sku, pu.view_size_platform,"Доставка",  pu.delivery_type.days_min, pu.delivery_type.days_max, pu.availability)
        # order = Order.objects.filter(fact_of_payment=True, user__first_name="Лев").order_by("-id").first()
        # order.update_order_status()

        #     print(f"{o.product.platform_info['poizon']['title']} Артикул: {o.product.manufacturer_sku} Цена: {o.final_price}Р {o.original_price}Y Размер: {o.view_size_platform} {o.size_platform}")

        # ps.update(available_flag=False)

        # p = Product.objects.get(slug="nike-dunk-low-chicago-split-262086")
        # p.is_sale = True
        # pu = p.product_units.all()
        # for u in pu:
        #     u.is_sale = True
        #     u.start_price = (math.ceil((u.final_price * 1.33) / 100) * 100) - 10
        #     u.save()
        #     print(u.original_price)
        # pum = pu.order_by("final_price").first()
        # p.min_price_without_sale = pum.start_price
        # p.save()

        # lines = Line.objects.all()
        # for line in lines:
        #     if "&" in line.full_eng_name:
        #         line.full_eng_name = line.full_eng_name.replace("&", "and")
        #         print(line.full_eng_name)
        #         line.save()

        # lines = Product.objects.get(id=455655).lines.all().exclude(name__icontains='Все').exclude(name__icontains='Другие').exclude(parent_line=None).values_list("name", flat=True)
        # print(list(lines))

        # es = Elasticsearch(['http://130.193.53.215:9200'])
        #
        # # Имя индекса, для которого вы хотите узнать количество документов
        # index_name = 'product_index_3'
        #
        # # Отправка запроса для получения количества документов в индексе
        # response = es.count(index=index_name)
        #
        # # Получение количества документов из ответа
        # document_count = response['count']
        # print(f'Количество документов в индексе {index_name}: {document_count}')

        # p = Product.objects.get(slug="nike-zoom-court-vapor-cage-4-rafa-161294")
        # print(p.categories.all())
        # pr = Product.objects.get(id=245490)
        # print(pr.slug)
        # prs = Product.objects.filter(available_flag=True, min_price=0)
        # prs.update(available_flag=False)

        #
        # line = Line.objects.get(name="adidas Yeezy")
        # line2 = Line.objects.get(name="Все adidas Yeezy")
        # products = Product.objects.filter(lines=line)
        # k = 0
        # for p in products:
        #     k += 1
        #     p.lines.add(line2)
        #     p.save()
        #     print(k)

        # products = Product.objects.filter(available_flag=True, is_custom=False, likes_month=-1)
        #
        # # print(products)
        # ck = products.count()
        # print(ck)

        # prs = Product.objects.filter(likes_month=303333, rel_num=129654).values_list("slug", flat=True)
        # print(prs)

        # products = Product.objects.exclude(categories__name__in=["Обувь", "Одежда"]).filter(available_flag=True, is_custom=False)
        # products = Product.objects.filter(spu_id=1011766)
        # ck = products.count()
        # for page in range(0, ck, 100):
        #     products_p = products[page:page+100]
        #     print(page)
        #     for product in products_p:
        #         likes_month = product.likes_month
        #         rel_num = product.rel_num
        #         if likes_month > rel_num:
        #             new = rel_num + likes_month
        #             old = rel_num // 0.3
        #             product.rel_num = old
        #             product.likes_month = new - old
        #             product.save()
        # # lc = list(Product.objects.filter(available_flag=True).exclude(likes_month=-1).values_list("likes_month", "rel_num"))
        # json_string = json.dumps(lc, ensure_ascii=False)
        #
        # with open("dynamic_likes.json", "w", encoding="utf-8") as file:
        #     file.write(json_string)
        #
        # brands = Brand.objects.all()

        # cats = Category.objects.filter(Q(name__icontains='Все') | Q(name__icontains='Вся'))
        # for cat in cats:
        #     cat.save()
        #
        # lines = Category.objects.filter(Q(name__icontains='Все') | Q(name__icontains="Вся"))
        # for line in lines:
        #     line.save()

        # d = []
        # for brand in brands:
        #     for cat in cats:
        #         d.append({"category": cat.name, "brand": brand.name, "score": 0})
        #
        # print()
        #
        # json_string = json.dumps(d, ensure_ascii=False)
        #
        #     # Запись JSON-строки в файл
        # with open("brand_and_category_score.json", "w", encoding="utf-8") as file:
        #     file.write(json_string)

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
        #
        # # min_ids = Product.objects.values('spu_id', 'property_id').annotate(min_id=Min('id'))
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
        #     # products_to_delete.delete()
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

        # def recursive_subcategories(sz, category):
        #     print(category)
        #     subcategories = category.subcat.all()
        #
        #     for subcategory in subcategories:
        #         # print(subcategory.name)  # Вы можете выполнить нужные действия с каждой подкатегорией здесь
        #         sz.category.add(subcategory)
        #         # print(sz.name, subcategory)
        #         recursive_subcategories(sz, subcategory)

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
        # sz.save()
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
