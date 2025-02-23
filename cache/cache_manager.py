import time


class CacheManager:
    """
    CacheManager управляет кэшем для:
      - Чанков данных
      - Метаданных (getattr, stat)
    """

    def __init__(self, ttl=1800, meta_ttl=10):
        # TTL для данных (чанков)
        self.ttl = ttl
        # TTL для метаданных (короче, чем для данных)
        self.meta_ttl = meta_ttl

        # Кэш для чанков
        self.chunk_cache = {}
        # Кэш для метаданных
        self.metadata_cache = {}

    # === Методы для кэширования метаданных ===

    def get_metadata_from_cache(self, path):
        """
        Проверяет, есть ли метаданные в кэше и не протухли ли они.
        """
        if path in self.metadata_cache:
            metadata, timestamp = self.metadata_cache[path]
            # Проверяем, что не истёк TTL
            if time.time() - timestamp < self.meta_ttl:
                return metadata
            else:
                # Если TTL истёк, удаляем из кэша
                del self.metadata_cache[path]
        return None

    def update_metadata_cache(self, path, metadata):
        """
        Обновляет метаданные в кэше с текущим timestamp.
        """
        self.metadata_cache[path] = (metadata, time.time())

    # === Методы для кэширования чанков ===

    def is_cached(self, path, chunk_index):
        """
        Проверяет, есть ли чанк в кэше и не протух ли он.
        """
        if path in self.chunk_cache:
            if chunk_index in self.chunk_cache[path]:
                timestamp = self.chunk_cache[path][chunk_index]
                if time.time() - timestamp < self.ttl:
                    return True
        return False

    def update_cache(self, path, chunk_index):
        """
        Обновляет время последнего использования чанка.
        """
        if path not in self.chunk_cache:
            self.chunk_cache[path] = {}
        self.chunk_cache[path][chunk_index] = time.time()
