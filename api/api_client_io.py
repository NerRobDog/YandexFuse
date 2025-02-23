from http.client import responses
from typing import Optional, Dict, Any, Iterator
from urllib.parse import quote

import requests

from models.exceptions import APIError


def _encode_path(path: str) -> str:
    """Кодирует путь для использования в URL"""
    return quote(path)


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
            if response.status_code == 204:
                return {}
            if response.text:
                return response.json()
            return {}
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Ошибка при запросе к {url}: {e}") from e
        except ValueError as e:
            raise RuntimeError(f"Ошибка обработки JSON ответа от {url}: {e}") from e

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

    def upload(self, upload_url: str, file_path: str) -> None:
        """ Загрузка файла по ссылке """
        with open(file_path, 'rb') as file:
            response = requests.put(upload_url, headers=self.headers, data=file)
            if not response.ok:
                self._handle_error(response)

    def upload_chunks(self, upload_url: str, file_path: str, chunk_size: int = 1024 * 1024) -> None:
        """ Загрузка файла по частям """
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                response = requests.put(upload_url, headers=self.headers, data=chunk)
                if not response.ok:
                    self._handle_error(response)

    def upload_chunk(self, upload_url: str, chunk: bytes) -> requests.Response:
        """Загрузка одной части файла"""
        response = requests.put(upload_url, headers=self.headers, data=chunk)
        return response

    def upload_retry(self, upload_url: str, file_path: str, max_retries: int = 3) -> None:
        """ Загрузка файла по ссылке с повторными попытками """
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        session = requests.Session()
        retries = Retry(total=max_retries,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])

        session.mount('https://', HTTPAdapter(max_retries=retries))

        with open(file_path, 'rb') as file:
            response = session.put(upload_url, headers=self.headers, data=file)
            if not response.ok:
                self._handle_error(response)
