from typing import List

from api.api_client_io import APIClientIO
from models.file_metadata import FileMetadata


class APIClient:
    def __init__(self, token: str, base_url: str) -> None:
        self.io = APIClientIO(token, base_url)

    def get_metadata(self, path: str) -> FileMetadata:
        """Получение метаданных папки/файла"""
        data = self.io.get("resources", params={"path": path})
        return FileMetadata.from_json(data)

    def list_folder(self, path: str) -> List[FileMetadata]:
        """Получение списка файлов в папке"""
        data = self.io.get("resources", params={"path": path})

        if data['type'] != 'dir':
            raise ValueError(f"Path {path} is not a directory")

        items = data.get('_embedded', {}).get('items', [])
        return [FileMetadata.from_json(item) for item in items]

    def download_file(self, path: str, local_path: str) -> None:
        """Скачивание файла"""
        # 1. Получаем ссылку на скачивание
        download_data = self.io.get("resources/download", params={"path": path})
        download_url = download_data.get("href")

        if not download_url:
            raise ValueError("Не удалось получить ссылку на скачивание")

        # 2. Скачиваем файл по ссылке через APIClientIO
        with open(local_path, 'wb') as f:
            for chunk in self.io.download(download_url):
                f.write(chunk)

    def upload_file(self, path: str, local_path: str) -> None:
        """Загрузка файла"""
        # 1. Получаем ссылку на загрузку
        upload_data = self.io.get(endpoint="resources/upload", params={"path": path})

        upload_url = upload_data.get("href")

        if not upload_url:
            raise ValueError("Не удалось получить ссылку на загрузку")

        # 2. Загружаем файл по ссылке через APIClientIO
        self.io.upload(upload_url, local_path)

    def create_folder(self, path: str) -> None:
        """Создание папки"""
        raise NotImplementedError

    def delete_file(self, path: str) -> None:
        """Удаление файла"""
        raise NotImplementedError

    def delete_folder(self, path: str) -> None:
        """Удаление папки"""
        raise NotImplementedError

    def move(self, from_path: str, to_path: str) -> None:
        """Перемещение файла/папки"""
        raise NotImplementedError
