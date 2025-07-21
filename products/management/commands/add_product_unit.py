from random import randint
from django.core.management.base import BaseCommand
from products.models import Product, SizeTranslationRows, SizeTable
from shipping.models import Platform, ProductUnit, DeliveryType
from utils.models import Currency


class Command(BaseCommand):
    help = 'Autofill ProductUnit model'

    def handle(self, *args, **options):
        products = Product.objects.all()
        # currencies = Currency.objects.all()
        delivery_type1 = DeliveryType(name="до 10 дней", days_min=1, days_max=3)
        delivery_type2 = DeliveryType(name="до 20 дней", days_min=3, days_max=5)
        delivery_type3 = DeliveryType(name="до 30 дней", days_min=10, days_max=15)
        ds = [delivery_type1, delivery_type2, delivery_type3]
        platform = Platform(platform='poizon', site="poizon")
        delivery_type1.save()
        delivery_type2.save()
        delivery_type3.save()
        platform.save()

        for product in products:
            if len(product.product_units.all()) != 0:
                continue
            # product.save()
            # continue
            # Генерация случайного количества product_unit для каждого продукта
            num_units = randint(2, 3)

            for _ in range(num_units):
                # Создание случайного product_unit
                size = str(randint(36, 45))  # Замените на логику выбора размера
                start_price = randint(10, 200) * 500 - 10  # Замените на логику генерации старой цены
                final_price = start_price  # Замените на логику генерации новой цены
                url = ""  # Замените на логику генерации URL
                size_table = SizeTable.objects.first()
                product.size_table = size_table
                size_rows = list(size_table.rows.all())
                n = randint(1, 10)
                print(size_rows[n].row)

                product_unit = ProductUnit.objects.create(
                    product=product,
                    view_size_platform=size_rows[n].row['Европейский(EU)'],

                    # currency=currencies.first(),
                    start_price=start_price,
                    final_price=final_price,
                    delivery_type=ds[randint(0, 2)],
                    platform=platform,
                    url=url,
                    availability=((randint(1, 10) % 2) == 1),
                    warehouse=False,
                    is_multiple=False,
                    is_return=((randint(1, 10) % 3) > 0),
                    is_fast_shipping=((randint(1, 10) % 3) > 0),
                    is_sale=((randint(1, 10) % 3) > 0),


                )
                product_unit.size.add(size_rows[n])
                product_unit.save()
                self.stdout.write(self.style.SUCCESS(f'Successfully created ProductUnit: {product_unit}'))
            product.save()


