from dataclasses import dataclass
from typing import Optional, List
from urllib.parse import quote

import requests


@dataclass
class APIError:
    """Структура для хранения информации об ошибке от API"""
    message: str
    description: Optional[str] = None
    error: Optional[str] = None

    @staticmethod
    def from_json(data: dict) -> 'APIError':
        """Создает экземпляр APIError из JSON-ответа"""
        return APIError(
            message=data.get("message", "Ошибка без сообщения"),
            description=data.get("description"),
            error=data.get("error")
        )

    def __str__(self) -> str:
        """Форматирование для вывода"""
        return f"Ошибка: {self.message} \n Описание: {self.description} \n Код ошибки: {self.error}"


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

    @staticmethod
    def from_json(data: dict) -> 'FileMetadata':
        """Создаёт экземпляр FileMetadata из JSON-ответа"""
        return FileMetadata(
            name=data.get("name"),
            path=data.get("path"),
            file_type=data.get("type"),
            created=data.get("created"),
            modified=data.get("modified"),
            size=data.get("size"),
            mime_type=data.get("mime_type"),
            md5=data.get("md5"),
            sha256=data.get("sha256"),
            resource_id=data.get("resource_id"),
            public_url=data.get("public_url"),
            file_url=data.get("file")
        )


class APIClient:
    def __init__(self, token: str, base_url: str) -> None:
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"OAuth {self.token}",
            "Content-Type": "application/json"
        }

    def _handle_error(self, response: requests.Response) -> None:
        """Обработка ошибок от API"""
        try:
            # Пробуем распарсить JSON-ответ
            error_data = response.json()
            api_error = APIError.from_json(error_data)
            raise RuntimeError(str(api_error))
        except ValueError:
            # Если не удалось распарсить JSON, выводим текст ответа
            raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

    def _encode_path(self, path: str) -> str:
        """Кодирует путь для использования в URL"""
        return quote(path)

    def _make_request(self, method: str, endpoint: str, params: Optional[dict] = None, **kwargs) -> dict:
        """Базовый метод для отправки запросов"""
        url = f"{self.base_url}/{endpoint}"

        try:
            response = requests.request(method, url, headers=self.headers, params=params, **kwargs)
            if not response.ok:
                self._handle_error(response)

            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка при запросе к {url}: {e}") from e

    def _get(self, endpoint: str, **kwargs) -> dict:
        return self._make_request('GET', endpoint, **kwargs)

    def _post(self, endpoint: str, **kwargs) -> dict:
        return self._make_request('POST', endpoint, **kwargs)

    def _put(self, endpoint: str, **kwargs) -> dict:
        return self._make_request('PUT', endpoint, **kwargs)

    def _patch(self, endpoint: str, **kwargs) -> dict:
        return self._make_request('PATCH', endpoint, **kwargs)

    def _delete(self, endpoint: str, **kwargs) -> dict:
        return self._make_request('DELETE', endpoint, **kwargs)

    def get_metadata(self, path: str) -> FileMetadata:
        """Получение метаданных папки/файла"""
        data = self._get("resources", params={"path": path})
        return FileMetadata.from_json(data)

    def list_folder(self, path: str) -> List[FileMetadata]:
        """Получение списка файлов в папке"""
        data = self._get("resources", params={"path": path})

        if data['type'] != 'dir':
            raise ValueError(f"Path {path} is not a directory")

        items = data.get('_embedded', {}).get('items', [])
        return [FileMetadata.from_json(item) for item in items]

    def download_file(self, path: str, local_path: str) -> None:
        """Скачивание файла"""
        # Получаем ссылку на скачивание
        download_data = self._get("resources/download", params={"path": path})
        download_url = download_data.get("href")

        if not download_url:
            raise ValueError("Не удалось получить ссылку на скачивание")
        # Скачиваем файл
        response = requests.get(download_url, stream=True)
        response.raise_for_status()

        # Сохраняем файл
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

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
