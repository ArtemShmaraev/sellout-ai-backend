
from django.core.management.base import BaseCommand

from products.models import (
    Category,
    Gender,
    Product,
    SizeTranslationRows,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        def update_gender_size(product):
            sizes = []
            genders = list(product.gender.values_list('name', flat=True))
            for unit in product.product_units.filter(availability=True):
                for s in unit.size.all():
                    if 'Европейский(EU)' in s.row and not ("M" in genders and "F" in genders):
                        size_eu = float(s.row['Европейский(EU)'])
                        if size_eu <= 41:
                            product.gender.add(Gender.objects.get(name="F"))
                        if size_eu >= 40:
                            product.gender.add(Gender.objects.get(name="M"))
                    sizes.append(s.id)

            product.sizes.clear()
            product.sizes.add(*SizeTranslationRows.objects.filter(id__in=sizes))


        product = Product.objects.filter(is_custom=False, categories__in=Category.objects.filter(name__in=["Кроссовки", "Кеды", "Зимние кроссовки и ботинки"]))
        count = product.count()
        for page in range(0, count, 100):
            page_product = Product.objects.filter(is_custom=False, categories__in=Category.objects.filter(name__in=["Кроссовки", "Кеды", "Зимние кроссовки и ботинки"])).order_by("id")[page: page + 100]
            for product in page_product:
                update_gender_size(product)
            print(page, count)

