import random
from itertools import count
from django.core.management.base import BaseCommand
import json
import os
import json
from datetime import datetime, date
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, Collab, Photo
from products.tools import add_product

class Command(BaseCommand):
    def handle(self, *args, **options):


        for count in range(1, 2):
            # folder_path = f'dewu/{count}m'
            folder_path = f'processed_for_db'  # Укажите путь к папке, содержащей JSON-файлы
            k = 37900
            k = 0
            ek = 0
            t0 = datetime.now()
            # Перебор всех файлов в папке
            for filename in os.listdir(folder_path)[k:]:
                if filename.endswith('json'):  # Проверка, что файл имеет расширение .json
                    file_path = os.path.join(folder_path, filename)  # Полный путь к файлу
                    k += 1
                    if k % 100 == 0:
                        t1 = datetime.now()
                        print(f"{k}: эта сотка за {(t1 - t0).seconds} сек")
                        t0 = t1
                    # Открытие файла и чтение его содержимого
                    with open(file_path, 'r') as file:
                        json_content = file.read()

                    # data = json.loads(json_content)
                    # print(data)
                    # add_product(data)


                    # Преобразование содержимого файла в словарь
                    try:
                        data = json.loads(json_content)
                        add_product(data)
                    except Exception as e:
                        print(data)
                        print(e)

        print('finished')
