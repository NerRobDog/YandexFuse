import requests
from logger.logger import setup_logger
from models.exceptions import APIError

class APIClientIO:
    @staticmethod
    def download(download_url: str, chunk_size: int = 8192):
        """
        Выполняет запрос для скачивания файла по download_url (потоковый).
        """
        logger = setup_logger("APIClientIO")
        logger.warning(f"download() - Запрос к {download_url} (stream, chunk_size={chunk_size})")

        response = requests.get(download_url, stream=True)
        response.raise_for_status()  # Обработка 4xx/5xx

        for chunk in response.iter_content(chunk_size=chunk_size):
            yield chunk

    def __init__(self, token: str, base_url: str) -> None:
        self.logger = setup_logger("APIClientIO")

        self.token = token
        self.base_url = base_url
        self.headers = {
            "Authorization": f"OAuth {self.token}",
            "Content-Type": "application/json"
        }
        self.logger.warning(f"APIClientIO init: base_url={base_url}")

    def _handle_error(self, response: requests.Response) -> None:
        """Обработка ошибок от API"""
        try:
            error_data = response.json()
            api_error = APIError.from_json(error_data)
            raise RuntimeError(str(api_error))
        except ValueError:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text}")

    def _make_request(self, method: str, endpoint: str, params=None, **kwargs):
        url = f"{self.base_url}/{endpoint}"
        self.logger.warning(f"{method} {url} params={params} kwargs={kwargs}")
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

    def get(self, endpoint: str, **kwargs):
        return self._make_request('GET', endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs):
        return self._make_request('POST', endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs):
        return self._make_request('PUT', endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        return self._make_request('DELETE', endpoint, **kwargs)

    def upload(self, upload_url: str, file_path: str) -> None:
        self.logger.warning(f"upload() - {file_path} -> {upload_url}")
        with open(file_path, 'rb') as file:
            response = requests.put(upload_url, headers=self.headers, data=file)
            if not response.ok:
                self._handle_error(response)

    def upload_chunks(self, upload_url: str, file_path: str, chunk_size: int = 1024 * 1024) -> None:
        self.logger.warning(f"upload_chunks() - {file_path} -> {upload_url}, chunk_size={chunk_size}")
        with open(file_path, 'rb') as file:
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break
                response = requests.put(upload_url, headers=self.headers, data=chunk)
                if not response.ok:
                    self._handle_error(response)

    def upload_chunk(self, upload_url: str, chunk: bytes):
        self.logger.warning(f"upload_chunk() -> {upload_url}, {len(chunk)} bytes")
        response = requests.put(upload_url, headers=self.headers, data=chunk)
        return response

    def upload_retry(self, upload_url: str, file_path: str, max_retries: int = 3) -> None:
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        self.logger.warning(f"upload_retry() - {file_path} -> {upload_url}, max_retries={max_retries}")
        session = requests.Session()
        retries = Retry(total=max_retries,
                        backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])

        session.mount('https://', HTTPAdapter(max_retries=retries))

        with open(file_path, 'rb') as file:
            response = session.put(upload_url, headers=self.headers, data=file)
            if not response.ok:
                self._handle_error(response)

    def download_range(self, path: str, start_byte: int, end_byte: int):
        """
        Делаем частичный GET (Range).
        """
        self.logger.warning(f"download_range() - {path} bytes={start_byte}-{end_byte}")

        # Сначала получаем download_url
        download_data = self.get("resources/download", params={"path": path})
        download_url = download_data.get("href")
        if not download_url:
            raise ValueError("Не удалось получить ссылку на скачивание (range).")

        headers = {"Range": f"bytes={start_byte}-{end_byte}"}
        response = requests.get(download_url, headers=headers)
        return response
