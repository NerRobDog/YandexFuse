import os

class ChunkManager:
    """
    ChunkManager умеет скачивать куски (чанки) файла по Range-запросам.
    По умолчанию мы берём chunk_size=1MB, но это можно менять.
    """
    def __init__(self, api_client, chunk_size=1024 * 1024):
        self.api_client = api_client
        self.chunk_size = chunk_size

        # Локальная папка, где будем складывать чанки
        self.cache_dir = '/tmp/yadisk_cache'
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_chunk(self, path: str, chunk_index: int) -> bytes:
        """
        Вернёт данные конкретного чанка (chunk_index) файла `path`.
        Если чанк уже скачан, то просто прочитаем его локально.
        Если нет, скачаем с Я.Диска (Range-запрос), сохраним и вернём.
        """
        local_chunk_path = self._make_local_chunk_path(path, chunk_index)

        if not os.path.exists(local_chunk_path):
            # Надо скачать
            self._download_chunk(path, chunk_index, local_chunk_path)

        # Читаем файл с диска и возвращаем байты
        with open(local_chunk_path, 'rb') as f:
            return f.read()

    def _download_chunk(self, path: str, chunk_index: int, local_chunk_path: str) -> None:
        """
        Скачивает нужные байты и сохраняет их.
        """
        start_byte = chunk_index * self.chunk_size
        end_byte = start_byte + self.chunk_size - 1

        # Допустим, мы добавили в api_client метод download_range
        # который делает GET запрос с заголовком Range
        response = self.api_client.download_range(path, start_byte, end_byte)
        if response.status_code != 206:
            raise RuntimeError(f"Range-запрос вернул {response.status_code}")

        # Сохраняем ответ в файл
        with open(local_chunk_path, 'wb') as f:
            f.write(response.content)

    def _make_local_chunk_path(self, path: str, chunk_index: int) -> str:
        """
        Создаём "уникальное" имя для файла-чанка, чтобы хранить его в /tmp/yadisk_cache
        """
        filename = os.path.basename(path)   # только имя файла
        chunk_filename = f"{filename}.chunk_{chunk_index}"
        return os.path.join(self.cache_dir, chunk_filename)
