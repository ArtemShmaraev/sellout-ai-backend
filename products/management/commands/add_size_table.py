from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Brand, SizeTable, SizeTranslationRows, Gender
from django.core.exceptions import ObjectDoesNotExist


class Command(BaseCommand):

    def handle(self, *args, **options):
        s = SizeTable.objects.all()
        s.delete()
        s = SizeTranslationRows.objects.all()
        s.delete()

        all_data = json.load(open("size_table.json", encoding="utf-8"))
        for data in all_data:

            brand, created = Brand.objects.get_or_create(name=data['brand'])
            brand.save()
            category = Category.objects.get(name=data['category'])
            name = f"{data['brand']} | {data['category']} | {data['gender']}"
            if SizeTable.objects.filter(brand=brand, category=category,
                                   name=name,
                                   gender=data['gender']).exists():
                size_table = SizeTable.objects.get(brand=brand, category=category,
                                       name=name,
                                       gender=data['gender'])
                size_table.delete()
            size_table = SizeTable(brand=brand, category=category,
                                               name=name,
                                               gender=data['gender'])
            size_table.save()
            for row in data['rows']:
                size_row = SizeTranslationRows(table=size_table)
                if "US" in row:
                    size_row.US = row['US']
                if "UK" in row:
                    size_row.UK = row['UK']
                if "EU" in row:
                    size_row.EU = row['EU']
                if "RU" in row:
                    size_row.RU = row['RU']
                if "CM" in row:
                    size_row.SM = row['CM']
                size_row.table = size_table

                size_row.save()
                size_table.size_row.add(size_row)
            print(str(size_table))
        print('finished')