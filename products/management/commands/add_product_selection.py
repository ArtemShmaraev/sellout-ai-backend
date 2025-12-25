from random import randint
from django.core.management.base import BaseCommand
from products.models import Product, SizeTranslationRows, SizeTable
from shipping.models import Platform, ProductUnit, DeliveryType
from utils.models import Currency


class Command(BaseCommand):
    def handle(self, *args, **options):
        import csv

        # Открываем CSV файл для чтения
        with open('example.csv', 'r', newline='') as file:
            # Создаем объект для чтения CSV файла как словаря
            reader = csv.DictReader(file)

            # Читаем данные из файла по строкам
            for row in reader:
                # Получаем значение в столбце с названием 'Название столбца'
                spu_id = row['spu_id']
                spu_id = spu_id if spu_id != "" else False
                slug = row['slug']
                slug = slug if slug != "" else False
                is_sale = str(row["is_sale"]) == "1"
                if is_sale:
                    absolute = int(row['absolute_sale'] if row['absolute_sale'] != "" else 0)
                    percentage = int(row['percentage_sale'] if row['percentage_sale'] != "" else 0)
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

                if page:
                    products = Product.objects.filter(available_flag=True, is_custom=False).order_by("-score_product_page")
                    try:
                        first = products.first().score_product_page
                        last = products[page * 60].score_product_page
                    except:
                        continue


