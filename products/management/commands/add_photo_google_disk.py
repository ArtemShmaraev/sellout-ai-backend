from itertools import count
from django.core.management.base import BaseCommand
import json
from django.core.exceptions import ObjectDoesNotExist
from products.models import Collab, Line, Category, Gender, HeaderPhoto, HeaderText, Photo
from products.serializers import CollabSerializer
from users.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        from googleapiclient.discovery import build
        from google.oauth2.credentials import Credentials

        # ID папки, из которой вы хотите начать перебор


        # Аутентификация и создание API клиента
        def authenticate_google_drive():
            creds = Credentials.from_authorized_user_file("googleAPI.json", SCOPES)

            service = build("drive", "v3", credentials=creds)
            return service

        # Рекурсивная функция для перебора и вывода названий папок

        def create_folder(service, folder_name, parent_folder_id=None):
            folder_metadata = {
                "name": folder_name,
                "mimeType": "application/vnd.google-apps.folder"
            }

            if parent_folder_id:
                folder_metadata["parents"] = [parent_folder_id]

            folder = service.files().create(body=folder_metadata, fields="id").execute()
            return folder.get("id")

        def get_parent_folder_name(file_id):
            service = authenticate_google_drive()
            file = service.files().get(fileId=file_id, fields="id, name, parents").execute()

            if "parents" in file:
                parent_id = file["parents"][0]
                parent = service.files().get(fileId=parent_id, fields="id, name").execute()
                return parent
            else:
                return "No Parent Folder"

        def add_collab_photo(service, folder_id, type, where):
            results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name, mimeType)").execute()
            items = results.get("files", [])

            for item in items:
                if item["mimeType"] == "application/vnd.google-apps.folder":
                    # print("Folder:", item["name"])
                    add_collab_photo(service, item["id"], type, where)
                else:
                    print(item['name'])
                    # Действия для файлов
                    name = get_parent_folder_name(get_parent_folder_name(item['id'])['id'])['name']
                    try:
                        collab = Collab.objects.get(name=name)
                        category = Category.objects.get(name="Обувь")
                        gender_m = Gender.objects.get(id=1)
                        gender_f = Gender.objects.get(id=2)
                        gender_k = Gender.objects.get(id=3)
                        if item["name"].endswith(".txt"):
                            title = item["name"]
                            text = service.files().get_media(fileId=item["id"]).execute().decode("utf-8")
                        else:
                            url = f"http://drive.google.com/uc?export=view&id={item['id']}"
                            photo = Photo(url=url)
                            photo.save()
                            header_photo = HeaderPhoto(photo=photo, type=type, where=where)
                            header_photo.save()
                            header_photo.collabs.add(collab)
                            header_photo.genders.add(gender_m)
                            header_photo.genders.add(gender_f)
                            header_photo.genders.add(gender_k)
                            header_photo.categories.add(category)
                            header_photo.save()
                            print(url)
                    except:
                        print(name, "EERRRROOOORRR")
                        continue


        def add_headers_photo(service, folder_id, type, where):
            results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name, mimeType)").execute()
            items = results.get("files", [])

            for item in items:
                if item["mimeType"] == "application/vnd.google-apps.folder":
                    # print("Folder:", item["name"])
                    add_headers_photo(service, item["id"], type, where)
                else:
                    print(item['name'])
                    # Действия для файлов
                    name = get_parent_folder_name(item['id'])['name']
                    try:
                        category = Category.objects.get(name=name)
                        gender_m = Gender.objects.get(id=1)
                        gender_f = Gender.objects.get(id=2)
                        gender_k = Gender.objects.get(id=3)
                        if item["name"].endswith(".txt"):
                            title = item["name"]
                            text = service.files().get_media(fileId=item["id"]).execute().decode("utf-8")
                        else:
                            url = f"http://drive.google.com/uc?export=view&id={item['id']}"
                            photo = Photo(url=url)
                            photo.save()
                            header_photo = HeaderPhoto(photo=photo, type=type, where=where)
                            header_photo.save()

                            header_photo.genders.add(gender_m)
                            header_photo.genders.add(gender_f)
                            header_photo.genders.add(gender_k)
                            header_photo.categories.add(category)
                            header_photo.save()
                            print(url)
                    except:
                        print(name, "EERRRROOOORRR")
                        continue

        # Рекурсивная функция для перебора и вывода названий папок и файлов
        def add_lines_photo(service, folder_id, type, where):
            results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name, mimeType)").execute()
            items = results.get("files", [])


            for item in items:
                if item["mimeType"] == "application/vnd.google-apps.folder":
                    # print("Folder:", item["name"])
                    add_lines_photo(service, item["id"], type, where)
                else:
                    print(item['name'])
                    # Действия для файлов
                    name = get_parent_folder_name(get_parent_folder_name(item['id'])['id'])['name']
                    try:
                        line = Line.objects.get(name=name)
                        category = Category.objects.get(name="Обувь")
                        gender_m = Gender.objects.get(id=1)
                        gender_f = Gender.objects.get(id=2)
                        gender_k = Gender.objects.get(id=3)
                        if item["name"].endswith(".txt"):
                            title = item["name"]
                            text = service.files().get_media(fileId=item["id"]).execute().decode("utf-8")
                        else:
                            url = f"http://drive.google.com/uc?export=view&id={item['id']}"
                            photo = Photo(url=url)
                            photo.save()
                            header_photo = HeaderPhoto(photo=photo, type=type, where=where)
                            header_photo.save()
                            header_photo.lines.add(line)
                            curent_line = line
                            while curent_line.parent_line is not None:
                                curent_line = curent_line.parent_line
                                header_photo.lines.add(curent_line)
                            header_photo.genders.add(gender_m)
                            header_photo.genders.add(gender_f)
                            header_photo.genders.add(gender_k)
                            header_photo.categories.add(category)
                            header_photo.save()
                            line_yzy = Line.objects.get(name="adidas Yeezy")
                            if line_yzy in header_photo.lines.all():
                                header_photo.collabs.add(Collab.objects.get(name="adidas Yeezy"))
                            # print(url)
                    except Exception as e:
                        print(e)
                        print(name, "EERRRROOOORRR")
                        continue

        # def list_files_and_folders_recursive(service, folder_id):
        #     results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name, mimeType)").execute()
        #     items = results.get("files", [])
        #
        #     for item in items:
        #         if item["mimeType"] == "application/vnd.google-apps.folder":
        #             print("Folder:", item["name"])
        #             list_files_and_folders_recursive(service, item["id"])
        #         else:
        #             print("File:", item["name"])

        SCOPES = ["https://www.googleapis.com/auth/drive"]

        # Аутентификация и создание сервиса

        #
        # START_FOLDER_ID = [
        #     ["1903_YQpzTnMAW-jB_FWdkBnQhLfUQG38", "mobile", "product_page"],
        #     ["1baj3nS9S6pzu44-T3b2b7otn_KjfgQop", "desktop", "product_page"]
        # ]
        #
        service = authenticate_google_drive()
        #
        # for folder in START_FOLDER_ID:
        #     # Права доступа, которые требуются для работы с Google Диско
        #
        #     add_lines_photo(service, folder[0], folder[1], folder[2])
        #
        #
        # START_FOLDER_ID = [
        #     ["1agXJHz-u6BMY8QZZCPr4gw6-Zu68R_gs", "mobile", "product_page"],
        #     ["1o3ODdyVkuE03pWexeeJ734vhxguHb-jy", "desktop", "product_page"]
        # ]
        #
        # for folder in START_FOLDER_ID:
        #     # Права доступа, которые требуются для работы с Google Диско
        #
        #     add_collab_photo(service, folder[0], folder[1], folder[2])

        START_FOLDER_ID = [
            ["1Po9LmSlM3PnfE5A3WAR5FURy8M9NyOEi", "mobile", "header"],
            ["1TT_vGRLGRAwsrzbirIwk_CbWgw1OyBOq", "desktop", "header"]
        ]

        for folder in START_FOLDER_ID:
            # Права доступа, которые требуются для работы с Google Диско

            add_headers_photo(service, folder[0], folder[1], folder[2])





