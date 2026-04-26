import threading

from django.core.management.base import BaseCommand
from django.db import transaction

from products.models import (
    Product,
)
from users.models import UserStatus


class Command(BaseCommand):



    def handle(self, *args, **options):
        def update_prices(products, user_status, start, end):
            for product_id in products[start:end]:
                product = Product.objects.get(id=product_id)
                with transaction.atomic():
                    product.update_price(in_sale=False)


        # Получите все продукты, которые вы хотите обновить
        products = Product.objects.filter(available_flag=True).filter(actual_price=False).order_by(
            "-rel_num").values_list("id", flat=True)

        # part = 1
        # num_part = products.count() // 4
        # products = products[num_part * (part - 1):num_part * part]
        # products = products[105000:210000]
        # products = products[210000:315000]
        # products = products[315000:429000]
        user_status = UserStatus.objects.get(name="Amethyst")

        # Укажите количество потоков
        num_threads = 8
        count_products = products.count()

        # Разделите список продуктов на равные части для каждого потока
        batch_size = count_products // num_threads

        # Создайте потоки и запустите их
        threads = []
        for i in range(num_threads):
            start = i * batch_size
            end = start + batch_size if i < num_threads - 1 else count_products
            thread = threading.Thread(target=update_prices, args=(products, user_status, start, end))
            thread.start()
            threads.append(thread)

        # Дождитесь завершения всех потоков
        for thread in threads:
            thread.join()

        print("Цены успешно обновлены.")


    # def handle(self, *args, **options):
    #     from multiprocessing import Pool
    #
    #     def process_product(product):
    #         user_status = UserStatus.objects.get(name="Amethyst")
    #         product = Product.objects.get(id=product)
    #         for unit in product.product_units.all():
    #             price = formula_price(product, unit, user_status)
    #             unit.start_price = price['start_price']
    #             unit.final_price = price['final_price']
    #             unit.save()
    #         product.update_min_price()
    #
    #     products = Product.objects.filter(available_flag=True).values_list("id")
    #     pool = Pool(processes=8)  # указываем количество потоков
    #     pool.map(process_product, products)
    #     pool.close()
    #     pool.join()
    #
    #
    #
    #     #
    #     #
    #     #
    #     ps = ProductUnit.objects.filter(start_price=0)
    #     print(ps.count())

        # products = Product.objects.filter(available_flag=True)
        # user_status = UserStatus.objects.get(name="Amethyst")
        # for page in range(0, products.count(), 100):
        #     products_page = products[page:page + 100]
        #     print(page)
        #     for product in products_page:
        #         for unit in product.product_units.all():
        #             price = formula_price(product, unit, user_status)
        #             unit.start_price = price['start_price']
        #             unit.final_price = price['final_price']
        #             unit.save()
        #         product.update_min_price()


