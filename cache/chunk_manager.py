# cache/chunk_manager.py
import os
from logger.logger import setup_logger

class ChunkManager:
    """
    ChunkManager скачивает чанки файла по Range-запросам.
    По умолчанию используется chunk_size=1МБ, но это можно менять.
    Все сетевые вызовы инкапсулированы здесь для удобства будущего перехода на асинхронность.
    """
    def __init__(self, api_client, chunk_size=1024 * 1024):
        self.logger = setup_logger(self.__class__.__name__)
        self.api_client = api_client
        self.chunk_size = chunk_size
        self.cache_dir = '/tmp/yadisk_cache'
        os.makedirs(self.cache_dir, exist_ok=True)
        self.logger.debug(f"ChunkManager инициализирован: chunk_size={chunk_size}")

    def get_chunk(self, path: str, chunk_index: int) -> bytes:
        local_chunk_path = self._make_local_chunk_path(path, chunk_index)
        if not os.path.exists(local_chunk_path):
            self.logger.debug(f"Чанк {chunk_index} для {path} не найден локально. Скачиваем...")
            self._download_chunk(path, chunk_index, local_chunk_path)
        else:
            self.logger.debug(f"Чанк {chunk_index} для {path} найден локально.")
        with open(local_chunk_path, 'rb') as f:
            data = f.read()
        self.logger.debug(f"Чанк {chunk_index} для {path} прочитан: {len(data)} байт.")
        return data

    def _download_chunk(self, path: str, chunk_index: int, local_chunk_path: str) -> None:
        start_byte = chunk_index * self.chunk_size
        end_byte = start_byte + self.chunk_size - 1
        self.logger.debug(f"Скачивание чанка для {path}: bytes={start_byte}-{end_byte}")
        response = self.api_client.download_range(path, start_byte, end_byte)
        if response.status_code != 206:
            self.logger.error(f"Ошибка загрузки чанка {chunk_index} для {path}: {response.status_code}")
            raise RuntimeError(f"Range-запрос вернул {response.status_code} для {path}")
        with open(local_chunk_path, 'wb') as f:
            f.write(response.content)
        self.logger.debug(f"Чанк {chunk_index} для {path} сохранён в {local_chunk_path} ({len(response.content)} байт).")

    def _make_local_chunk_path(self, path: str, chunk_index: int) -> str:
        filename = os.path.basename(path)
        chunk_filename = f"{filename}.chunk_{chunk_index}"
        return os.path.join(self.cache_dir, chunk_filename)