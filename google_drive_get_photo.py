from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

# ID папки, из которой вы хотите начать перебор
START_FOLDER_ID = "1m8d5tTwtDUJteqymT3IvZ4tpsBYnVEqz"

# Права доступа, которые требуются для работы с Google Диском
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
# Права доступа, которые требуются для работы с Google Диском


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


if __name__ == "__main__":
    service = authenticate_google_drive()
    print("Folders and Files:")
    list_folders_and_files_recursive(service, START_FOLDER_ID)