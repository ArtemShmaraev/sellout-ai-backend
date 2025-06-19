from itertools import count
from django.core.management.base import BaseCommand
import json
from django.core.exceptions import ObjectDoesNotExist
from products.models import Collab
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

        # Рекурсивная функция для перебора и вывода названий папок и файлов
        def list_folders_and_files_recursive(service, folder_id, indent=""):
            results = service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name, mimeType)").execute()
            items = results.get("files", [])

            for item in items:
                if item["mimeType"] == "application/vnd.google-apps.folder":
                    print(indent + "Folder:", item["name"])
                    list_folders_and_files_recursive(service, item["id"], indent + "  ")
                else:

                    print(indent + "File:", item["name"])
                    if item["name"].endswith(".txt"):
                        title = item["name"]
                        text = service.files().get_media(fileId=item["id"]).execute().decode("utf-8")



        def write_names_to_file(items, file, parent_folder, indent=0):
            with open(file, 'a', encoding="utf-8") as f:

                for item in items:
                    f.write(' ' * indent + item['name'] + '\n')
                    new_folder = create_folder(service, item['name'], parent_folder)
                    create_folder(service, "Фото", new_folder)
                    create_folder(service, "Текст", new_folder)
                    if 'children' in item and item['children']:
                        write_names_to_file(item['children'], file, new_folder)

        START_FOLDER_ID = ["1GHpdB1_RMZ5wKCGmY19Uf5-XFlKEY1Kn",
                           "1agXJHz-u6BMY8QZZCPr4gw6-Zu68R_gs",
                           "1o3ODdyVkuE03pWexeeJ734vhxguHb-jy",
                           "1ocpyIDeW2Ph-_KrYRyxSMqhivhj36uTR",
                           "1ALNibvb14vohPhMgh_RKKPu0WYEJrZXp"]

        for folder in START_FOLDER_ID:




            # Права доступа, которые требуются для работы с Google Диском
            SCOPES = ["https://www.googleapis.com/auth/drive.file"]

            service = authenticate_google_drive()


            with open('output.txt', 'w') as f:
                f.write('')  # Очистить файл перед записью

            data = json.load(open("line2.json", encoding="utf-8"))
            data = CollabSerializer(Collab.objects.filter(is_main_collab=True), many=True).data
            write_names_to_file(data, 'output.txt', folder)





