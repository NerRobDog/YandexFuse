import os
from tqdm import tqdm
from api.api_client import APIClient

class APIClientWithProgress(APIClient):
    def upload_file_with_progress(self, path: str, local_path: str) -> None:
        """Загрузка файла с отображением прогресса"""
        # Получаем ссылку на загрузку
        upload_data = self.io.get(endpoint="resources/upload", params={"path": path})
        upload_url = upload_data.get("href")

        if not upload_url:
            raise ValueError("Не удалось получить ссылку на загрузку")

        # Получаем размер файла
        file_size = os.path.getsize(local_path)

        # Загружаем файл с прогресс-баром
        with open(local_path, 'rb') as file, tqdm(total=file_size, unit='B', unit_scale=True, desc=local_path) as pbar:
            while True:
                chunk = file.read(1024 * 1024)
                if not chunk:
                    break
                response = self.io.upload_chunk(upload_url, chunk)
                if not response.ok:
                    self.io._handle_error(response)
                pbar.update(len(chunk))

    def download_file_with_progress(self, path: str, local_path: str) -> None:
        """Скачивание файла с отображением прогресса"""
        # Получаем ссылку на скачивание
        download_data = self.io.get("resources/download", params={"path": path})
        download_url = download_data.get("href")

        if not download_url:
            raise ValueError("Не удалось получить ссылку на скачивание")

        # Получаем размер файла
        file_size = int(download_data.get("size", 0))

        # Скачиваем файл с прогресс-баром
        with open(local_path, 'wb') as file, tqdm(total=file_size, unit='B', unit_scale=True, desc=local_path) as pbar:
            for chunk in self.io.download(download_url):
                file.write(chunk)
                pbar.update(len(chunk))

# Пример использования
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    URL = os.getenv('URL')

    client = APIClientWithProgress(token=TOKEN, base_url=URL)
    file = "Oxygen_Not_Included_v651155_Incl_DLC.dmg"
    try:
        # client.upload_file_with_progress(f"/{file}", f"/Users/nik/Downloads/{file}")
        client.download_file_with_progress(f"/{file}", f"/Users/nik/Downloads/{file}")
    except RuntimeError as e:
        print(f"Произошла ошибка: {e}")