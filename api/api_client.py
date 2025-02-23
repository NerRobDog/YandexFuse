from typing import List
from logger.logger import setup_logger
from api.api_client_io import APIClientIO
from models.file_metadata import FileMetadata

class APIClient:
    def __init__(self, token: str, base_url: str) -> None:
        self.logger = setup_logger(self.__class__.__name__)
        self.io = APIClientIO(token, base_url)
        self.logger.info(f"APIClient инициализирован: base_url={base_url}")

    def get_metadata(self, path: str) -> FileMetadata:
        """Получение метаданных папки/файла"""
        self.logger.info(f"get_metadata для path={path}")
        data = self.io.get("resources", params={"path": path})
        return FileMetadata.from_json(data)

    def list_folder(self, path: str) -> List[FileMetadata]:
        """Получение списка файлов в папке"""
        self.logger.info(f"list_folder для path={path}")
        data = self.io.get("resources", params={"path": path})

        if data['type'] != 'dir':
            self.logger.warning(f"list_folder: {path} не является директорией.")
            raise ValueError(f"Path {path} is not a directory")

        items = data.get('_embedded', {}).get('items', [])
        self.logger.debug(f"list_folder: найдено {len(items)} элементов в {path}")
        return [FileMetadata.from_json(item) for item in items]

    def download_file(self, path: str, local_path: str) -> None:
        """Скачивание файла"""
        self.logger.info(f"download_file path={path} -> local={local_path}")
        download_data = self.io.get("resources/download", params={"path": path})
        download_url = download_data.get("href")

        if not download_url:
            self.logger.error("Не удалось получить ссылку на скачивание.")
            raise ValueError("Не удалось получить ссылку на скачивание")

        with open(local_path, 'wb') as f:
            for chunk in self.io.download(download_url):
                f.write(chunk)
        self.logger.debug(f"Файл {path} скачан в {local_path}")

    def upload_file(self, path: str, local_path: str) -> None:
        """Загрузка файла"""
        self.logger.info(f"upload_file local={local_path} -> path={path}")
        upload_data = self.io.get(endpoint="resources/upload", params={"path": path})
        upload_url = upload_data.get("href")

        if not upload_url:
            self.logger.error("Не удалось получить ссылку на загрузку.")
            raise ValueError("Не удалось получить ссылку на загрузку")

        self.io.upload_retry(upload_url, local_path)
        self.logger.debug(f"Файл {local_path} загружен в {path} (через upload_retry).")

    def upload_file_bypass(self, path: str, local_path: str) -> None:
        """Загрузка файла с обходом ограничения скорости"""
        import os
        self.logger.info(f"upload_file_bypass local={local_path} -> path={path}")
        original_path = path
        file_name, ext = os.path.splitext(path)

        limited_extensions = {'.db', '.dat', '.zip', '.gz', '.rar', '.mp4', '.avi', '.mov'}
        if ext.lower() in limited_extensions:
            path = f"{file_name}.tmp"
            self.logger.debug(f"Переименовываем {original_path} -> {path} для обхода лимита.")

        upload_data = self.io.get(endpoint="resources/upload", params={"path": path})
        upload_url = upload_data.get("href")
        if not upload_url:
            self.logger.error("Не удалось получить ссылку на загрузку (bypass).")
            raise ValueError("Не удалось получить ссылку на загрузку")

        self.io.upload(upload_url, local_path)
        self.logger.debug("Файл загружен (bypass).")

        if path != original_path:
            self.logger.debug(f"Переименовываем {path} обратно в {original_path}.")
            self.move(path, original_path)

    def create_folder(self, path: str) -> None:
        self.logger.info(f"create_folder path={path}")
        self.io.put("resources", params={"path": path})

    def delete_file(self, path: str) -> None:
        self.logger.info(f"delete_file path={path}")
        self.io.delete("resources", params={"path": path})

    def delete_folder(self, path: str) -> None:
        self.logger.info(f"delete_folder path={path}")
        self.io.delete("resources", params={"path": path})

    def move(self, from_path: str, to_path: str) -> None:
        self.logger.info(f"move from={from_path} to={to_path}")
        self.io.post("resources/move", params={"from": from_path, "path": to_path})

    def download_range(self, path: str, start_byte: int, end_byte: int):
        """
        Предположим, мы добавили этот метод для чанкового скачивания (Range).
        Фактически, он будет дергать self.io.download_range(...)
        """
        self.logger.debug(f"download_range path={path}, bytes={start_byte}-{end_byte}")
        return self.io.download_range(path, start_byte, end_byte)
