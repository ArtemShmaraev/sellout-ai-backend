import random
from random import randint
from urllib.parse import parse_qs

from django.core.management.base import BaseCommand
from products.models import Product, SizeTranslationRows, SizeTable
from shipping.models import Platform, ProductUnit, DeliveryType
from utils.models import Currency


class Command(BaseCommand):
    def handle(self, *args, **options):
        import csv

        # Открываем CSV файл для чтения
        with open('Ассортимент.csv', 'r', newline='') as file:
            # Создаем объект для чтения CSV файла как словаря
            reader = csv.DictReader(file, delimiter=";")
            # Читаем данные из файла по строкам
            for row in reader:
                try:
                    # Получаем значение в столбце с названием 'Название столбца'
                    spu_id = row['spu_id']
                    spu_id = spu_id if spu_id != "" else False
                    slug = row['slug']
                    slug = slug if slug != "" else False

                    is_sale = False
                    absolute = int(row['absolute_sale'] if row['absolute_sale'] != "" else 0)
                    percentage = int(row['percentage_sale'] if row['percentage_sale'] != "" else 0)
                    if absolute + percentage > 0:
                        is_sale = True

                    is_new = str(row["is_new"]) == "1"
                    is_rec = str(row["is_rec"]) == "1"
                    page = int(row['page'] if row['page'] != "" else False)
                    category_page = int(row['category_page'] if row['category_page'] != "" else False)
                    brand_page = int(row['brand_page'] if row['brand_page'] != "" else False)
                    query = row['query']
                    query = query if query != "" else False
                    query_page = int(row['query_page'] if row['query_page'] != "" else False)


                    if spu_id:
                        products = Product.objects.filter(spu_id=spu_id)
                        product = products.order_by("-score_product_page").first()
                    else:
                        product = Product.objects.get(slug=slug)


                    product.is_new = is_new
                    product.is_recommend = is_rec
                    if is_sale:
                        product.add_sale(absolute, percentage)
                    else:
                        product.del_sale()


                    if page or category_page or query_page or brand_page:
                        if page:
                            products = Product.objects.filter(available_flag=True, is_custom=False).order_by("-score_product_page")
                            n_page = page


                        if category_page:
                            category = product.categories.order_by("-id").first()
                            products = Product.objects.filter(available_flag=True, is_custom=False, categories=category).order_by("-score_product_page")
                            n_page = category_page

                        if brand_page:
                            brand = product.brands.order_by("id").first()
                            products = Product.objects.filter(available_flag=True, is_custom=False,
                                                              brands=brand).order_by("-score_product_page")
                            n_page = brand_page

                        if query:
                            params_dict = parse_qs(query)
                            params = {key: values for key, values in params_dict.items()}
                            queryset = Product.objects.filter(available_flag=True, is_custom=False)

                            # Получаем значения из словаря
                            line = params.get('line')
                            color = params.get('color')
                            category = params.get("category")
                            material = params.get("material")
                            gender = params.get("gender")
                            collab = params.get("collab")

                            if gender:
                                queryset = queryset.filter(gender__name__in=gender)
                            if collab:
                                if "all" in collab:
                                    queryset = queryset.filter(is_collab=True)
                                else:
                                    queryset = queryset.filter(collab__query_name__in=collab)
                            if material:
                                queryset = queryset.filter(materials__eng_name__in=material)

                            if line:
                                queryset = queryset.filter(lines__full_eng_name__in=line)
                            if color:
                                queryset = queryset.filter(colors__name__in=color)
                            if category:
                                queryset = queryset.filter(categories__eng_name__in=category)
                            products = queryset.order_by("-score_product_page")
                            n_page = query_page

                        first = products.first().score_product_page
                        last = products[n_page * 60].score_product_page
                        score = random.randint(last, first)
                        product.score_product_page = score
                        product.save()

                except Exception as e:
                    print(row)
                    print(e)



