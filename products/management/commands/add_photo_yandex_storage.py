import shutil
from itertools import count

import botocore
from PIL import Image
from django.core import signing
from django.core.management.base import BaseCommand
import json
from products.models import Product, Category, Line, Gender, Brand, Tag, Collection, Color, SizeRow, Collab, \
    HeaderPhoto, HeaderText, Photo
from django.core.exceptions import ObjectDoesNotExist
from shipping.models import ProductUnit
from users.models import User, EmailConfirmation


class Command(BaseCommand):

    def handle(self, *args, **options):

        def add_photo(url, type, where, collab_name="", category_name="", line_name=""):

            gender_m = Gender.objects.get(id=1)
            gender_f = Gender.objects.get(id=2)
            gender_k = Gender.objects.get(id=3)

            photo = Photo(url=url)
            photo.save()
            header_photo = HeaderPhoto(photo=photo, type=type, where=where)
            header_photo.save()

            header_photo.genders.add(gender_m)
            header_photo.genders.add(gender_f)
            header_photo.genders.add(gender_k)
            if category_name != "":
                category = Category.objects.get(name=category_name)
                header_photo.categories.add(category)
            if collab_name != "":
                collab = Collab.objects.filter(name__icontains=collab_name).first()
                header_photo.collabs.add(collab)
            if line_name != "":
                line = Line.objects.get(name=line_name)
                header_photo.lines.add(line)
                curent_line = line
                while curent_line.parent_line is not None:
                    curent_line = curent_line.parent_line
                    header_photo.lines.add(curent_line)
                if "yeezy" in line_name.lower():
                    collab = Collab.objects.get(query_name="adidas_yeezy")
                    header_photo.collabs.add(collab)
            header_photo.save()

        import boto3

        import os

        access_id = 'YCAJE0F2sIDFNPfcTqknCFtoY'
        access_key = 'YCNRvyqXPhlTbZ8vdAhDA6wAhxZCZ8KlRKjTPIDV'
        bucket_name = 'sellout-photos'  # Укажите название бакета

        # Создание сессии
        # session = botocore.session.get_session()
        #
        # # Получение подписанной ссылки на объект
        # client = session.create_client('s3', region_name=region_name, endpoint_url='https://storage.yandexcloud.net',
        #                                aws_access_key_id=access_id, aws_secret_access_key=access_key)
        #
        s3_client = boto3.client(
            service_name='s3',
            endpoint_url='https://storage.yandexcloud.net',
            aws_access_key_id=access_id,
            aws_secret_access_key=access_key
        )

        # bucket = s3.Bucket(bucket_name)
        # print(bucket)
        k = 0

        # Цикл для перебора файлов в папке
        def upload_files_to_cloud(local_path, cloud_path):
            global k
            destination_folder = r"C:\Users\artem\OneDrive\Рабочий стол\Мусор2"
            for item in os.listdir(local_path):
                full_local_path = os.path.join(local_path, item)
                full_cloud_path = os.path.join(cloud_path, item)


                if os.path.isfile(full_local_path):
                    # Если это файл, отправляем его на облако
                    path = full_cloud_path.replace("\\", "/")




                    url = f'https://storage.yandexcloud.net/sellout-photos/{path}'
                    # print(url)
                    if not HeaderPhoto.objects.filter(photo__url=url).exists():
                        content_type = 'image/png'
                        s3_client.upload_file(
                            full_local_path,
                            bucket_name,
                            path,
                            ExtraArgs={'ContentType': content_type}
                        )

                        try:
                            if "Mobile" in path:
                                type = "mobile"
                            else:
                                type = "desktop"

                            if "коллаборации" in path:
                                where = "product_page"
                                paths = path.split("/")
                                collab_name = paths[-2]
                                # print(collab_name)
                                add_photo(url, type, where, collab_name=collab_name, category_name="Обувь")

                            elif "линейки" in path:
                                where = "product_page"
                                paths = path.split("/")
                                line_name = paths[-2]
                                if "new" in line_name.lower():
                                    line_name = line_name.replace("-", "/")
                                # print(line_name)
                                add_photo(url, type, where, line_name=line_name, category_name="Обувь")
                            else:
                                where = "header"
                                paths = path.split("/")
                                category_name = paths[-2]
                                type = "any"
                                add_photo(url, type, where, category_name=category_name)
                        except Exception as e:
                            print(e)
                            print(path)
                            print("ERRRRRRRROOORRR")

                    # Формирование подписи
                    # print(f'Uploaded {full_local_path}')
                elif os.path.isdir(full_local_path):
                    upload_files_to_cloud(full_local_path, full_cloud_path)


        # Запускаем загрузку из корневой локальной папки в корневую папку на облаке

        local_folder = r'C:\Users\artem\OneDrive\Рабочий стол\Desktop'  # Путь до вашей локальной папки в файловой системе
        cloud_folder = 'Desktop'  # Подпапка в облаке
        upload_files_to_cloud(local_folder, cloud_folder)
        print(1)
        local_folder = r'C:\Users\artem\OneDrive\Рабочий стол\Mobile'  # Путь до вашей локальной папки в файловой системе
        cloud_folder = 'Mobile'  # Подпапка в облаке
        upload_files_to_cloud(local_folder, cloud_folder)
