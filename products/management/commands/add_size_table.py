from django.core.management.base import BaseCommand
from promotions.models import Bonuses
import json
from products.models import Product, Category, Brand, SizeTable, SizeTranslationRows, Gender
from django.core.exceptions import ObjectDoesNotExist



import json
from django.core.management.base import BaseCommand
from products.models import SizeTable, Category, Gender, SizeTranslationRows

data = {
    # Вставьте предоставленную структуру данных здесь
}

class Command(BaseCommand):
    help = 'Populate SizeTable with data'

    def handle(self, *args, **options):
        file_path = 'size_table_2.json'  # Замените на путь к вашему JSON файлу
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        for table in data:

            size_table = SizeTable.objects.create(
                name=table['name'],
                filter_name=table['filter_name'],
                standard=False
            )

            category_objects = [Category.objects.get_or_create(name=name)[0] for name in table['category']]
            size_table.category.add(*category_objects)

            gender_objects = [Gender.objects.get_or_create(name=name)[0] for name in table['gender']]
            size_table.gender.add(*gender_objects)

            size_table.size_rows = table['all_sizes']
            keys = list(dict(table['all_sizes']).keys())
            first_key = keys[0] if len(keys) > 0 else None
            len_table = len(table['all_sizes'][first_key]['sizes'])
            size_table.save()

            for i in range(len_table):
                d = dict()
                for key in keys:
                    d[key] = table['all_sizes'][key]['sizes'][i]

                is_one_size = table['all_sizes'][first_key]['sizes'][i].lower() == "один размер"
                if SizeTranslationRows.objects.filter(table=size_table, row=d, is_one_size=is_one_size).exists():
                    continue
                else:
                    size_row = SizeTranslationRows(table=size_table, row=d, is_one_size=is_one_size)
                    size_row.save()
        self.stdout.write(self.style.SUCCESS('Successfully populated SizeTable'))





# class Command(BaseCommand):
#
#     def handle(self, *args, **options):
#
#         s = SizeTable.objects.all()
#         s.delete()
#         s = SizeTranslationRows.objects.all()
#         s.delete()
#
#         all_data = json.load(open("size_table.json", encoding="utf-8"))
#         for data in all_data:
#
#             brand, created = Brand.objects.get_or_create(name=data['brand'])
#             brand.save()
#             category = Category.objects.get(name=data['category'])
#             name = f"{data['brand']} | {data['category']} | {data['gender']}"
#             if SizeTable.objects.filter(brand=brand, category=category,
#                                    name=name,
#                                    gender=data['gender']).exists():
#                 size_table = SizeTable.objects.get(brand=brand, category=category,
#                                        name=name,
#                                        gender=data['gender'])
#                 size_table.delete()
#             size_table = SizeTable(brand=brand, category=category,
#                                                name=name,
#                                                gender=data['gender'])
#             size_table.save()
#             for row in data['rows']:
#                 size_row = SizeTranslationRows(table=size_table)
#                 if "US" in row:
#                     size_row.US = row['US']
#                 if "UK" in row:
#                     size_row.UK = row['UK']
#                 if "EU" in row:
#                     size_row.EU = row['EU']
#                 if "RU" in row:
#                     size_row.RU = row['RU']
#                 if "CM" in row:
#                     size_row.SM = row['CM']
#                 size_row.table = size_table
#
#                 size_row.save()
#                 size_table.size_row.add(size_row)
#             print(str(size_table))
#         print('finished')