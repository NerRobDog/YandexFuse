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
#
# # Download file
client.download_file('/Горы.jpg', "/Users/nik/Downloads/Горы.jpg")
#
# # Error handling
# try:
#     # Получение метаданных несуществующего файла
#     metadata = client.get_metadata('/НесуществующийФайл.jpg')
#     print(metadata)
# except RuntimeError as e:
#     print(f"Произошла ошибка: {e}")