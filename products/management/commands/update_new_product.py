import math
import random
from datetime import date, timedelta
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
        def add_new():
            Product.objects.filter(is_new=True).update(is_new=False)
            s_category = ['canvas_shoes', 'high_top_sneakers', 'low_top_sneakers', 'basketball_sneakers']
            s_line = ['yeezy', 'adidas_campus', 'adidas_forum', 'adidas_gazelle', 'adidas_samba', 'adidas_stan_smith',
                      'adidas_superstar', 'adidas_ultraboost', 'adidas_human_race', 'adidas_nmd', 'adidas_zx',
                      'adidas_adilette', 'adidas_nizza', 'adidas_eqt', 'adidas_ozweego', 'adidas_4d', 'adidas_harden',
                      'adidas_trae_young', 'adidas_dame_(damian_lillard)', 'adidas_d_rose', 'asics_gel-lyte',
                      'asics_gel-flux', 'asics_gel-contend', 'asics_gel-cumulus', 'asics_gel-excite', 'asics_gel-nyc',
                      'asics_gel-nimbus', 'asics_gel-quantum', 'asics_gel-kayano', 'asics_gel-kahana', 'asics_gel-1090',
                      'asics_gel-1130', 'asics_magic_speed', 'asics_gt', 'converse_chuck_taylor',
                      'converse_chuck_taylor_run_star', 'converse_one_star', 'converse_pro_leather',
                      'converse_all_star_pro_bb', 'jordan', 'new_balance_237', 'new_balance_327', 'new_balance_530',
                      'new_balance_550', 'new_balance_650', 'new_balance_580', 'new_balance_574', 'new_balance_9060',
                      'new_balance_997', 'new_balance_990', 'new_balance_991', 'new_balance_992', 'new_balance_993',
                      'new_balance_1906r', 'new_balance_2002r', 'new_balance_57%2F40', 'nike_dunk', 'nike_air_force_1',
                      'nike_air_max', 'nike_blazer', 'nike_zoom', 'nike_vapormax', 'nike_cortez', 'nike_air_trainer',
                      'nike_react', 'nike_kyrie_irving', 'nike_lebron_james', 'nike_kd_(kevin_durant)',
                      'nike_freak_(giannis_antetokounmpo)', 'nike_kobe_bryant', 'nike_pg_(paul_george)',
                      'nike_ja_morant', 'nike_air_huarache', 'nike_air_more_uptempo', 'nike_air_presto',
                      'nike_foamposite', 'vans_old_skool', 'vans_knu', 'vans_sk8', 'vans_ward', 'vans_comfycush',
                      'vans_era', 'vans_style_36', 'vans_half_cab', 'vans_slip-on', 'vans_authentic', 'puma_mb']

            s_products = Product.objects.filter(Q(available_flag=True) & Q(is_custom=False) &
                                                (Q(gender__name='M') | Q(gender__name='F')) &
                                                Q(lines__full_eng_name__in=s_line) &
                                                Q(categories__eng_name__in=s_category)).values_list("id",
                                                                                                    flat=True).order_by(
                "-exact_date")[:1800]
            s_products = Product.objects.filter(id__in=s_products).values_list("id", flat=True).order_by("rel_num")[
                         :1000]

            current_date = date.today()

            good_cats = ['Футбольные бутсы', 'Другие кроссовки для спорта', 'Лоферы', 'Мокасины и топсайдеры',
                         'Слипоны', 'Эспадрильи', 'Сандалии и босоножки', 'Пляжные сандалии', 'Шлёпки и тапки',
                         'Мюли и сабо', 'Туфли', 'Все туфли', 'Туфли на высоком каблуке', 'Туфли на среднем каблуке',
                         'Туфли на низком каблуке', 'Туфли на танкетке', 'Мужские туфли', 'Дерби', 'Оксфорды', 'Броги',
                         'Монки', 'Ботинки', 'Все ботинки', 'Ботинки на толстой подошве', 'Высокие ботинки и ботфорты',
                         'Средние ботинки', 'Короткие ботинки и ботильоны', 'Челси', 'Мартинсы', 'Тимберленды',
                         'Дезерты', 'Казаки', 'Зимние кроссовки и ботинки', 'Футболки', 'Лонгсливы', 'Худи и толстовки',
                         'Все худи и толстовки', 'Худи с капюшоном', 'Толстовки на молнии', 'Свитшоты',
                         'Свитеры и трикотаж', 'Все свитеры и трикотаж', 'Свитеры', 'Кардиганы', 'Водолазки', 'Жилеты',
                         'Шорты', 'Треники', 'Баскетбольные джерси', 'Топы', 'Майки', 'Поло', 'Джинсы', 'Юбки',
                         'Платья', 'Рубашки', 'Брюки', 'Пиджаки', 'Костюмы', 'Деним', 'Комбинезоны и боди',
                         'Зимние штаны', 'Куртки', 'Кожаные куртки', 'Джинсовые куртки', 'Бейсбольные куртки',
                         'Жилетки', 'Ветровки', 'Плащи', 'Пальто', 'Пуховики', 'Шубы', 'Сумки через плечо',
                         'Сумки на плечо', 'Сумки с ручками', 'Сумки на грудь', 'Сумки на пояс', 'Сумки тоут',
                         'Сумки хобо', 'Сумки вёдра', 'Рюкзаки', 'Портфели', 'Клатчи', 'Кошельки', 'Кардхолдеры',
                         'Косметички', 'Спортивные сумки', 'Ремни', 'Шарфы', 'Перчатки', 'Головные уборы',
                         'Все головные уборы', 'Кепки', 'Шапки', 'Панамы', 'Шляпы', 'Береты', 'Цепочки', 'Браслеты',
                         'Кольца', 'Bearbricks и другие коллекционные предметы', 'Солнцезащитные очки']
            good_brands = ['032c', '1017 ALYX 9SM', '361°', '424', 'A BATHING APE®', 'acme de la vie', 'Acne Studios',
                           'A-COLD-WALL*', 'Acupuncture', 'Ader Error', 'adidas', 'AGL', 'Agolde', 'Aimé Leon Dore',
                           'Alaia', 'Alexander McQueen', 'alexander wang', 'Alexandre Vauthier', 'Alice + Olivia',
                           'ALLSAINTS', 'Alpha Industries', 'AMBUSH', 'AMI Paris', 'AMIRI', 'Andersson Bell',
                           'Ann Demeulemeester', 'Anta', 'Anti Social Social Club', 'A.P.C.', 'APEDE MOD', 'apm monaco',
                           'Aquazzura', "Arc'teryx", 'Aries', 'Armani', 'ASH', 'Asics', 'Axel Arigato', 'Azepam',
                           'Balenciaga', 'Ballantyne', 'Bally', 'Balmain', 'Banana Shark', 'Banditk Gangn', 'Barbour',
                           'Barrow', 'beams', 'Beaster', 'Belle', 'BE@RBRICK', 'Billionaire boys club', 'Birkenstock',
                           'BJHG', 'BLINDNOPLAN', 'Blumarine', 'BODE', 'BOGNER', 'bosieagender', 'Bottega Veneta',
                           'Brioni', 'Brunello Cucinelli', 'Buccellati', 'Burberry', 'BVLGARI', 'BY FAR', 'C2H4',
                           'Cactus Jack by Travis Scott', 'Cactus Plant Flea Market', 'Calvin Klein', 'Canada Goose',
                           'Caramella', 'Carhartt', 'Cartier', 'Casablanca', 'Casadei', 'Casio', 'CAT', 'Cav Empt',
                           'Celine', 'Champion', 'Chanel', 'CHARLES&KEITH', 'Charlotte Tilbury', 'Chiara Ferragni',
                           'Chinatown Market', 'Chinism', 'Chloe', 'Christian Louboutin', 'Chrome Hearts', "Church's",
                           'Citizen', 'Clarks', 'Clot', 'Coach', 'Cole Haan', 'Comme Des Garçons', 'Common Projects',
                           'Concepts', 'Conklab', 'Converse', 'COOLALPACA', 'Coperni', 'C.P. Company', 'Crocs', 'Cubic',
                           'Cult Gaia', 'Daisy Fellowes', 'Dangerouspeople', 'Daphne', 'DC Shoes', 'Delvaux', 'diadora',
                           'Dickies', 'Diesel', 'DIMC', 'Dime MTL', 'Dior', 'DKNY', "Doucal's", 'Drew House',
                           'Dries Van Noten', 'Dr.Martens', 'DSQUARED 2', 'EASTPAK', 'ELLE', 'EMOTIONAL WORLD',
                           'Empty Reference', 'Ermenegildo Zegna', 'ETRO', 'Études', 'Evisu', 'FARFROMWHAT',
                           'Fear of God', 'Fendi', 'Ferragamo', 'Fila', 'FIND KAPOOR', 'Fjallraven', 'Fragment Design',
                           'Frame', 'Freak’s Store', 'Fred Perry', 'FRKM', 'Furla', 'Gallery Dept.', 'Ganni', 'Gap',
                           'GCDS', 'Gianvito Rossi', 'Giuseppe Zanotti', 'Givenchy', 'Golden Goose', 'GOOD', 'Goyard',
                           'Gramicci', 'Greg Lauren', 'G-SHOCK', 'Gucci', 'GUESS', 'Guidi', 'Harsh and Cruel',
                           'helmut lang', 'HERMES', 'Heron Preston', 'Herschel', 'HLA', 'H&M', 'Hogan', 'Hoka One One',
                           'Hugo Boss', 'Human Made', 'ICONS Lab', 'IH NOM UH NIT', 'INJOYLIFE', 'IRO', 'ISABEL MARANT',
                           'ISSEY MIYAKE', 'Jack Jones', 'Jacquemus', 'JANE KLAIN', 'Jil Sander', 'Jimmy Choo',
                           'John Lobb', 'John Richmond', 'Jordan', 'JW Anderson', 'Kangol', 'Kappa', 'Karl Lagerfeld',
                           'kate spade', 'Kaws', 'Kenzo', 'Khrisjoy', 'KITH', 'Kiton', 'Kreate', 'Lacoste', 'Lanvin',
                           "Levi's", 'lilbetter', 'Lily Wei', 'Li-Ning', 'LIU·JO', 'Loake', 'Loewe', 'Longchamp',
                           'Longines', 'Loro Piana', 'Louis Vuitton', 'L&R Power', 'Mach & Mach', 'Maison Kitsune',
                           'Maison Margiela', 'MAISON MIHARA YASUHIRO', 'Maje', 'Malone Souliers', 'Manolo Blahnik',
                           'Manu Atelier', 'Marcelo Burlon', 'MARC JACOBS', 'marine serre', 'Marni', 'Martine Rose',
                           'Massimo Dutti', 'MaxMara', 'MCM', 'Michael Kors', 'MIKASA', 'MISBHV', 'Missoni',
                           'Mitchell & Ness', 'MIU MIU', 'Mizuno', 'MLB', 'Moditec', 'molten', 'Moncler',
                           'Moose Knuckles', 'Moschino', 'MostwantedLab', 'Mother', 'MSCHF R', 'MSGM', 'Mugler',
                           'Mulberry', 'N°21', 'Naked Wolfe', 'Nana Jacqueline', 'nanamica', 'Nanushka', 'NBA',
                           'Needles', 'NEIGHBORHOOD', 'Neil Barrett', 'New Balance', 'New Era', 'Nike', 'NOAH', 'NOMK',
                           'NORVINCY', 'Nothomme', 'Oakley', 'Ocai', 'Off-White', 'Old Order', 'ollieskate', 'On',
                           'Onitsuka Tiger', 'ONLY', 'Osiris', 'Our Legacy', 'Paco Rabanne', 'Palace', 'Palm Angels',
                           'Pandora', 'Paset', 'patagonia', 'Paul & Shark', 'Paul Smith', 'Peaceminusone', 'Peak',
                           'Philipp Plein', 'PINKO', 'PLEASURES', 'Polar Skate Co.', 'Polo Ralph Lauren', 'Prada',
                           'PRBLMS', 'Premiata', 'Primeet', 'Proenza Schouler', 'Profound', 'PSO Brand', 'PUMA',
                           'Raf Simons', 'Randomevent', 'Raucohouse', 'Ravenous', 'RayBan', 'RED Valentino', 'Reebok',
                           'René Caovilla', 'Represent', 'Revenge', 'Rhude', 'Rick Owens', 'Rigorer', 'Rimowa',
                           'RIPNDIP', 'Roaringwild', 'Rocawear', 'Roger Vivier', 'Russell Athletic', 'sacai',
                           'Saint Laurent', 'SAINT Mxxxxxx', 'Salomon', 'Samsonite', 'SandKnit', 'SANDRO', 'Santoni',
                           'Saucony', 'See By Chloe', 'Seiko', 'Self portrait', 'Sergio Rossi', 'Skechers', 'SKIMS',
                           'Smile Republic', 'Spalding', 'Staud', 'Stella McCartney', 'Steve Madden', 'Stone Island',
                           'Stuart Weitzman', 'Stüssy', 'Suicoke', 'Supreme', 'Swarovski', 'Swatch', 'Tagliatore',
                           'The Attico', 'The North Face', 'Theory', 'The Row', 'The Simpsons', 'Thom Browne',
                           'Thrasher', 'Tiffany & Co.', 'Timberland', 'Tissot', "Tod's", 'Tom Ford', 'Tommy Hilfiger',
                           'Tory Burch', 'Toteme', 'UGG', 'umamiism', 'umbro', 'UNDEFEATED', 'Under Armour',
                           'Undercover', 'Union', 'UNIQLO', 'UNKNOWTAL', 'UZIS', 'Valentino', 'Valextra',
                           'VANESSA HOGAN', 'Vans', 'VEJA', 'VENOF', 'Versace', 'Vetements', "Victoria's Secret",
                           'VINEY', 'vision street wear', 'Vivienne Westwood', 'VLONE', 'Waitingwave', 'WE11DONE',
                           'Weird Market', 'Wilson', 'Woolrich', 'WTAPS', 'Xotic', 'xVESSEL', 'Y-3', 'YEEZY',
                           'Yese Studio', 'Yohji Yamamoto', 'Youkeshu', 'Y/Project', 'Zara', 'Zimmermann', 'Zzegna',
                           '速写']

            # Вычисляем дату, которая находится полгода назад
            six_months_ago = current_date + timedelta(days=180)
            filtered_products = Product.objects.filter(Q(available_flag=True) & Q(is_custom=False) &
                                                       Q(exact_date__lte=six_months_ago) &
                                                       (Q(gender__name='M') | Q(gender__name='F')) & Q(
                categories__name__in=good_cats) & Q(brands__name__in=good_brands)
                                                       )
            sort_products = filtered_products.order_by("-exact_date").values_list("id", flat=True)[:1400]

            result = Product.objects.filter(Q(id__in=sort_products) | Q(id__in=s_products))
            result.update(is_new=True)

        def add_rec():
            d = {"Все кроссовки": 350, "Кеды": 200, "Туфли на высоком каблуке": 20, "Все ботинки": 350,
                 "Зимние кроссовки и ботинки": 120, "Футболки": 50, "Лонгсливы": 20, "Все худи и толстовки": 80,
                 "Все свитеры и трикотаж": 80, "Шорты": 30, "Треники": 50, "Зимние штаны": 50,
                 "Вся верхняя одежда": 160,
                 "Сумки через плечо": 60, "Сумки на плечо": 60, "Сумки с ручками": 60, "Сумки на грудь": 60,
                 "Сумки на пояс": 60,
                 "Сумки тоут": 50, "Сумки хобо": 50, "Сумки вёдра": 30, "Рюкзаки": 50, "Клатчи": 30, "Кошельки": 30,
                 "Кардхолдеры": 30, "Шарфы": 90, "Перчатки": 90, "Шапки": 90}
            ids = []
            for k, v in d.items():
                s = Product.objects.filter(available_flag=True, is_custom=False, categories__name=k).order_by(
                    "-score_product_page").values_list("id", flat=True)[:v]
                ids.extend(s)
            popular_product = Product.objects.filter(id__in=ids)
            popular_product.update(is_recommend=True)

        add_new()