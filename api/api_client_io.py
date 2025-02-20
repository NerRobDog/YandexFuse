from typing import Optional, Dict, Any, Iterator
from urllib.parse import quote

import requests

from models.exceptions import APIError


class APIClientIO:
    @staticmethod
    def download(download_url: str, chunk_size: int = 8192) -> Iterator[bytes]:
        """
        Выполняет запрос для скачивания файла по download_url.
        Возвращает поток данных по частям (chunks).
        """
        response = requests.get(download_url, stream=True)
        response.raise_for_status()  # Обработка 4xx/5xx

        for chunk in response.iter_content(chunk_size=chunk_size):
            yield chunk

    def __init__(self, token: str, base_url: str) -> None:
        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"OAuth {self.token}",
            "Content-Type": "application/json"
        }

    def _encode_path(self, path: str) -> str:
        """Кодирует путь для использования в URL"""
        return quote(path)

    def _handle_error(self, response: requests.Response) -> None:
        """Обработка ошибок от API"""
        try:
            error_data = response.json()
            api_error = APIError.from_json(error_data)
            raise RuntimeError(str(api_error))
        except ValueError:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, str]] = None, **kwargs) -> Dict[
        str, Any]:
        """Универсальный метод для выполнения запросов"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.request(method, url, headers=self.headers, params=params, **kwargs)
            if not response.ok:
                self._handle_error(response)
            return response.json()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка при запросе к {url}: {e}") from e

    def get(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """GET-запрос"""
        return self._make_request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """POST-запрос"""
        return self._make_request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """PUT-запрос"""
        return self._make_request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """DELETE-запрос"""
        return self._make_request('DELETE', endpoint, **kwargs)
