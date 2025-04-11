from random import randint
from django.core.management.base import BaseCommand
from products.models import Product, SizeTranslationRows
from shipping.models import Platform, ProductUnit, DeliveryType
from utils.models import Currency


class Command(BaseCommand):
    help = 'Autofill ProductUnit model'

    def handle(self, *args, **options):
        products = Product.objects.all()
        # currencies = Currency.objects.all()
        delivery_type1 = DeliveryType(name="до 10 дней")
        delivery_type2 = DeliveryType(name="до 30 дней")
        platform = Platform(platform='poizon', site="poizon")
        delivery_type1.save()
        delivery_type2.save()
        platform.save()

        for product in products:
            # Генерация случайного количества product_unit для каждого продукта
            num_units = randint(5, 10)

            for _ in range(num_units):
                # Создание случайного product_unit
                size = SizeTranslationRows.objects.all()[randint(1, 100)]  # Замените на логику выбора размера
                start_price = randint(10, 200) * 500 - 10  # Замените на логику генерации старой цены
                final_price = start_price  # Замените на логику генерации новой цены
                url = ""  # Замените на логику генерации URL

                product_unit = ProductUnit.objects.create(
                    product=product,
                    size=size,
                    # currency=currencies.first(),
                    start_price=start_price,
                    final_price=final_price,
                    delivery_type=delivery_type1 if randint(1, 100) % 2 == 0 else delivery_type2,
                    platform=platform,
                    url=url,
                    availability=((randint(1, 10) % 2) == 1),
                    warehouse=False,
                    is_multiple=False,
                    is_return=((randint(1, 10) % 3) > 0),
                    is_fast_shipping=((randint(1, 10) % 3) > 0),
                    is_sale=((randint(1, 10) % 3) > 0)
                )

                self.stdout.write(self.style.SUCCESS(f'Successfully created ProductUnit: {product_unit}'))
