from dataclasses import dataclass
from typing import Optional, List

@dataclass
class FileMetadata:
    """Класс для хранения метаданных файла/папки"""
    name: str
    path: str
    file_type: str
    created: str
    modified: str
    size: Optional[int] = None
    mime_type: Optional[str] = None
    md5: Optional[str] = None
    sha256: Optional[str] = None
    resource_id: Optional[str] = None
    public_url: Optional[str] = None
    file_url: Optional[str] = None


class APIClient:
    def __init__(self, token: str, base_url: str) -> None:
        self.token = token
        self.base_url = base_url

    def get_metadata(self, path: str) -> FileMetadata:
        """Получение метаданных папки/файла"""
        raise NotImplementedError

    def list_folder(self, path: str) -> List[FileMetadata]:
        """Получение списка файлов в папке"""
        raise NotImplementedError

    def download_file(self, path: str, local_path: str) -> None:
        """Скачивание файла"""
        raise NotImplementedError

    def upload_file(self, path: str, local_path: str) -> None:
        """Загрузка файла"""
        raise NotImplementedError

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

