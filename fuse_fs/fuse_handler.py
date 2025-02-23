import errno
import os
import stat
from datetime import datetime
from fuse import FUSE, Operations, FuseOSError
from api.api_client import APIClient
from cache.chunk_manager import ChunkManager
from cache.cache_manager import CacheManager

class DiskFS(Operations):
    """
    Класс DiskFS отвечает за связь с FUSE. Он реализует методы, которые
    FUSE вызывает при доступе к файлам и папкам. Внутри каждого метода
    мы будем вызывать логику, которая работает с Яндекс-Диском.
    """
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.chunk_manager = ChunkManager(api_client)
        self.cache_manager = CacheManager()

        self.open_files = {}  # fh -> path
        self._next_fh = 1

    def getattr(self, path, fh=None):
        """
        Возвращает словарь атрибутов (аналог `stat()`).
        FUSE вызывает этот метод, когда ему нужно узнать,
        что это за файл, какой у него размер, время модификации и т.д.
        """
        # === Проверяем кэш метаданных ===
        cached_metadata = self.cache_manager.get_metadata_from_cache(path)
        if cached_metadata:
            return cached_metadata

        # === Специальная обработка корня "/" ===
        if path == "/":
            root_stat = {
                'st_mode': stat.S_IFDIR | 0o755,  # S_IFDIR для каталога
                'st_nlink': 2,
                'st_size': 0,
                'st_ctime': 0,
                'st_mtime': 0,
                'st_atime': 0,
                'st_uid': os.getuid(),
                'st_gid': os.getgid(),
            }
            self.cache_manager.update_metadata_cache(path, root_stat)
            return root_stat

        # === Запрашиваем метаданные через API ===
        try:
            metadata = self.api_client.get_metadata(path)

            # Определяем режим: папка (S_IFDIR) или файл (S_IFREG)
            if metadata.file_type == 'dir':
                mode = stat.S_IFDIR | 0o755  # drwxr-xr-x
                nlink = 2
            else:
                mode = stat.S_IFREG | 0o644  # -rw-r--r--
                nlink = 1

            # Преобразуем время в Unix timestamp
            created = int(datetime.fromisoformat(metadata.created.replace('Z', '+00:00')).timestamp())
            modified = int(datetime.fromisoformat(metadata.modified.replace('Z', '+00:00')).timestamp())

            result = {
                'st_mode': mode,
                'st_size': metadata.size or 0,
                'st_ctime': created,
                'st_mtime': modified,
                'st_atime': modified,
                'st_nlink': nlink,
                'st_uid': os.getuid(),
                'st_gid': os.getgid(),
            }

            # === Обновляем кэш метаданных ===
            self.cache_manager.update_metadata_cache(path, result)
            return result

        except RuntimeError as e:
            # Если API вернул ошибку 404 — файл не найден
            if "404" in str(e):
                raise FuseOSError(errno.ENOENT)
            # Иначе поднимаем общее исключение
            raise FuseOSError(errno.EIO)

    def readdir(self, path, fh):
        """
        Список содержимого папки (ls). Нужно вернуть
        хотя бы ['.', '..'] и дальше все имена файлов и папок внутри.
        """
        print(f"readdir called for path={path}")

        try:
            items = self.api_client.list_folder(path)
            print(f"list_folder returned {len(items)} items")
            yield '.'
            yield '..'
            for item in items:
                yield item.name
        except Exception as e:
            print(f"readdir EXCEPTION for path={path}: {e}")
            # Если нет доступа или папка не существует
            raise FuseOSError(errno.ENOENT)

    def open(self, path, flags):
        # Если файл не существует или это папка, бросим ошибку
        metadata = self.api_client.get_metadata(path)
        if metadata.file_type != 'file':
            raise FuseOSError(errno.ENOENT)

        # Создаём "уникальный" дескриптор и запоминаем, какой путь ему соответствует
        fh = self._next_fh
        self.open_files[fh] = path
        self._next_fh += 1
        return fh

    def read(self, path, size, offset, fh):
        """
        Здесь мы переходим к «гибридному» подходу:
        - Делим файл на чанки по self.chunk_manager.chunk_size (например, 1 МБ).
        - При чтении циклами получаем нужные чанки.
        - Возвращаем только тот фрагмент, который запросили (size, offset).
        """
        # Предположим, мы не опираемся на path, а берём его из open_files.
        path = self.open_files[fh]

        chunk_size = self.chunk_manager.chunk_size
        result = bytearray()

        # Мы хотим прочитать [offset, offset+size)
        end_offset = offset + size
        current_offset = offset

        while current_offset < end_offset:
            chunk_index = current_offset // chunk_size
            chunk_start_byte = chunk_index * chunk_size
            chunk_end_byte = chunk_start_byte + chunk_size

            # Скачиваем чанк (или берём из кэша)
            chunk_data = self.chunk_manager.get_chunk(path, chunk_index)

            # (Если используем CacheManager, можно mark: self.cache_manager.add_chunk(...))

            # Определяем диапазон внутри chunk_data, который нам нужен
            # Пример: если current_offset=512, chunk_start_byte=0, тогда local_offset=512
            local_offset = current_offset - chunk_start_byte
            # А максимальное количество байт, которое нам ещё нужно:
            bytes_we_still_need = end_offset - current_offset
            # Возьмём подотрезок
            slice_data = chunk_data[local_offset : local_offset + bytes_we_still_need]

            result.extend(slice_data)
            current_offset += len(slice_data)

        return bytes(result)

    # Остальные методы – mkdir, unlink, rmdir и т.д. – пока пропустим или оставим пустыми.
