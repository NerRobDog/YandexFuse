import time

from api.api_client import APIClient, FileMetadata
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
URL = os.getenv('URL')

client = APIClient(token=TOKEN, base_url=URL)

# List files in root directory

# metadata = client.list_folder('/')
# print(metadata)
# metadata = client.get_metadata('/Горы.jpg')
# print(metadata)


# Download file
# client.download_file('/Горы.jpg', "/Users/nik/Downloads/Горы.jpg")

# Error handling
# try:
#     # Получение метаданных несуществующего файла
#     metadata = client.get_metadata('/НесуществующийФайл.jpg')
#     print(metadata)
# except RuntimeError as e:
#     print(f"Произошла ошибка: {e}")
from datetime import datetime
# file = "ReVoice_Multicam - Right Render 2.mov"
start_time = time.time()
print(f"Начало загрузки: {datetime.fromtimestamp(start_time).strftime('%H:%M:%S')}")
# try:
#     client.upload_file(f"/{file}", f"/Users/nik/Downloads/{file}")
# except RuntimeError as e:
#     print(f"Произошла ошибка: {e}")
# elapsed_time = time.time() - start_time
# minutes = int(elapsed_time // 60)
# seconds = int(elapsed_time % 60)
# print(f"Время загрузки: {minutes} мин {seconds} сек")

# try:
#     client.upload_file_with_progress(f"/{file}", f"/Users/nik/Downloads/{file}")
# except RuntimeError as e:
#     print(f"Произошла ошибка: {e}")


file = "EcoUroc_02.25-720.mov"
try:
    client.upload_file_bypass(f"/{file}", f"/Users/nik/Downloads/{file}")
except RuntimeError as e:
    print(f"Произошла ошибка: {e}")

# Delete file
# try:
#     client.delete_file(f"/{file}")
# except RuntimeError as e:
#     print(f"Произошла ошибка: {e}")

# metadata = client.get_metadata(f'/{file}')
# print(metadata)

# file = "small.bin"
# file2 = "small.jpg"
# folder = "test"
# try:
#     client.create_folder(folder)
# except RuntimeError as e:
#     print(f"Произошла ошибка: {e}")
# # Rename file
# try:
#     client.move(f"/{file}", f"/{file2}")
# except RuntimeError as e:
#     print(f"Произошла ошибка: {e}")
elapsed_time = time.time() - start_time
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
print(f"Время загрузки: {minutes} мин {seconds} сек")
# Download file
# client.download_file(f'/{file}', f"/Users/nik/Downloads/{file}.mov")
