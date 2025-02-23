# cache/cache_manager.py
import os
import time
from logger.logger import setup_logger

class CacheManager:
    """
    CacheManager управляет кэшем для:
      - Чанков данных
      - Метаданных (getattr, stat)
      - Содержимого каталогов (readdir)
    """

    def __init__(self, ttl=1800, meta_ttl=1800, dir_ttl=1800):
        self.logger = setup_logger(self.__class__.__name__)
        self.ttl = ttl  # TTL для данных (чанков)
        self.meta_ttl = meta_ttl  # TTL для метаданных
        self.dir_ttl = dir_ttl  # TTL для содержимого каталогов

        # Кэш для чанков: { path: { chunk_index: (data, timestamp) } }
        self.chunk_cache = {}
        # Кэш для метаданных: { path: (metadata, timestamp) }
        self.metadata_cache = {}
        # Кэш для содержимого каталогов: { path: (dir_content, timestamp) }
        self.directory_cache = {}

        self.logger.info(f"CacheManager инициализирован: ttl={ttl}, meta_ttl={meta_ttl}, dir_ttl={dir_ttl}")

    # --- Методы для кэширования метаданных ---
    def get_metadata_from_cache(self, path):
        if path in self.metadata_cache:
            metadata, timestamp = self.metadata_cache[path]
            if time.time() - timestamp < self.meta_ttl:
                self.logger.debug(f"Метаданные для {path} найдены в кэше (ещё валидны).")
                return metadata
            else:
                self.logger.debug(f"Метаданные для {path} устарели. Удаляем из кэша.")
                del self.metadata_cache[path]
        return None

    def update_metadata_cache(self, path, metadata):
        self.metadata_cache[path] = (metadata, time.time())
        self.logger.debug(f"Метаданные обновлены в кэше для {path}.")

    # --- Методы для кэширования содержимого каталогов ---
    def get_directory_cache(self, path):
        if path in self.directory_cache:
            dir_content, timestamp = self.directory_cache[path]
            if time.time() - timestamp < self.dir_ttl:
                self.logger.debug(f"Содержимое каталога {path} найдено в кэше (ещё валидно).")
                return dir_content
            else:
                self.logger.debug(f"Содержимое каталога {path} устарело. Удаляем из кэша.")
                del self.directory_cache[path]
        return None

    def set_directory_cache(self, path, dir_content):
        self.directory_cache[path] = (dir_content, time.time())
        self.logger.debug(f"Кэш обновлён для каталога {path}.")

    # --- Методы для кэширования чанков ---
    def is_chunk_cached(self, path, chunk_index):
        if path in self.chunk_cache and chunk_index in self.chunk_cache[path]:
            data, timestamp = self.chunk_cache[path][chunk_index]
            if time.time() - timestamp < self.ttl:
                self.logger.debug(f"Чанк {chunk_index} для {path} найден в кэше (актуален).")
                return True
            else:
                self.logger.debug(f"Чанк {chunk_index} для {path} устарел. Удаляем из кэша.")
                del self.chunk_cache[path][chunk_index]
        return False

    def get_chunk_from_cache(self, path, chunk_index):
        if self.is_chunk_cached(path, chunk_index):
            return self.chunk_cache[path][chunk_index][0]
        return None

    def update_chunk_cache(self, path, chunk_index, data):
        if path not in self.chunk_cache:
            self.chunk_cache[path] = {}
        self.chunk_cache[path][chunk_index] = (data, time.time())
        self.logger.debug(f"Чанк {chunk_index} для {path} обновлён в кэше.")

    def remove_chunk(self, path, chunk_index, chunk_manager):
        if path in self.chunk_cache and chunk_index in self.chunk_cache[path]:
            del self.chunk_cache[path][chunk_index]
        local_path = chunk_manager._make_local_chunk_path(path, chunk_index)
        try:
            if os.path.exists(local_path):
                os.remove(local_path)
                self.logger.debug(f"Локальный файл чанка {local_path} удалён.")
        except Exception as e:
            self.logger.error(f"Ошибка при удалении файла {local_path}: {e}")