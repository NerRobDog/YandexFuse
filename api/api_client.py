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
        # self.io.upload(upload_url, local_path)
        # self.io.upload_chunks(upload_url, local_path)
        self.io.upload_retry(upload_url, local_path)

    def upload_file_bypass(self, path: str, local_path: str) -> None:
        """Загрузка файла с обходом ограничения скорости"""
        import os
        original_path = path
        file_name, ext = os.path.splitext(path)

        # Список расширений с ограничением скорости
        limited_extensions = {'.db', '.dat', '.zip', '.gz', '.rar', '.mp4', '.avi', '.mov'}

        # Если расширение в списке ограниченных, меняем его
        if ext.lower() in limited_extensions:
            path = f"{file_name}.tmp"

        # Получаем ссылку на загрузку с временным расширением
        upload_data = self.io.get(endpoint="resources/upload", params={"path": path})
        upload_url = upload_data.get("href")

        if not upload_url:
            raise ValueError("Не удалось получить ссылку на загрузку")

        # Загружаем файл
        self.io.upload(upload_url, local_path)

        # # Если расширение было изменено, переименовываем обратно
        if path != original_path:
            self.move(path, original_path)

    def create_folder(self, path: str) -> None:
        """Создание папки"""
        self.io.put("resources", params={"path": path})

    def delete_file(self, path: str) -> None:
        """Удаление файла"""
        self.io.delete("resources", params={"path": path})

    def delete_folder(self, path: str) -> None:
        """Удаление папки"""
        self.io.delete("resources", params={"path": path})

    def move(self, from_path: str, to_path: str) -> None:
        """Перемещение файла/папки"""
        self.io.post("resources/move", params={"from": from_path, "path": to_path})
