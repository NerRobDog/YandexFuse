# fuse_fs/fuse_handler.py
import os
import stat
import errno
from datetime import datetime
from os.path import basename

from fuse import FUSE, Operations, FuseOSError
from api.api_client import APIClient
from cache.cache_manager import CacheManager
from cache.chunk_manager import ChunkManager

class DiskFS(Operations):
    """
    DiskFS – FUSE-обработчик, реализующий методы для работы с файловой системой.
    Использует ChunkManager и CacheManager для оптимизации запросов и кэширования.
    """
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.chunk_manager = ChunkManager(api_client)
        self.cache_manager = CacheManager()
        self.open_files = {}  # mapping: file handle -> path
        self._next_fh = 1

    def _build_stat(self, metadata) -> dict:
        """Формирует словарь атрибутов (stat) на основе метаданных."""
        if metadata.file_type == 'dir':
            mode = stat.S_IFDIR | 0o755
            nlink = 2
        else:
            mode = stat.S_IFREG | 0o644
            nlink = 1
        created = int(datetime.fromisoformat(metadata.created.replace('Z', '+00:00')).timestamp())
        modified = int(datetime.fromisoformat(metadata.modified.replace('Z', '+00:00')).timestamp())
        return {
            'st_mode': mode,
            'st_size': metadata.size or 0,
            'st_ctime': created,
            'st_mtime': modified,
            'st_atime': modified,
            'st_nlink': nlink,
            'st_uid': os.getuid(),
            'st_gid': os.getgid(),
        }

    def getattr(self, path, fh=None):
        """Возвращает атрибуты файла или каталога (аналог stat)."""
        # Сначала пытаемся получить данные из кэша метаданных
        if os.path.basename(path).startswith('.'):
            # print(f"Попытка обратиться к {path}")
            raise FuseOSError(errno.ENOENT)
        # else:
        #     print(f"Попытка обратиться к {path}")
        cached = self.cache_manager.get_metadata_from_cache(path)
        if cached:
            return cached

        if path == "/":
            root_stat = {
                'st_mode': stat.S_IFDIR | 0o755,
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

        try:
            print(f"Получение метаданных для {path}")
            metadata = self.api_client.get_metadata(path)
            stat_data = self._build_stat(metadata)
            self.cache_manager.update_metadata_cache(path, stat_data)
            return stat_data
        except RuntimeError as e:
            if "404" in str(e):
                raise FuseOSError(errno.ENOENT)
            raise FuseOSError(errno.EIO)

    def readdir(self, path, fh):
        """Возвращает список содержимого каталога, обновляя кэш метаданных и фильтруя скрытые файлы."""
        try:
            # Если содержимое каталога уже в кэше, используем его
            cached_entries = self.cache_manager.get_directory_cache(path)
            if cached_entries is not None:
                return cached_entries

            # Получаем список объектов каталога через API (list_folder возвращает FileMetadata)
            items = self.api_client.list_folder(path)
            filtered_entries = []
            for item in items:
                filtered_entries.append(item.name)
                # Формируем полный путь объекта (учитывая, что для корня он выглядит как "/имя")
                full_path = os.path.join(path, item.name) if path != "/" else "/" + item.name
                # Обновляем кэш метаданных для объекта
                self.cache_manager.update_metadata_cache(full_path, self._build_stat(item))
            self.cache_manager.set_directory_cache(path, filtered_entries)
            return filtered_entries
        except Exception as e:
            raise FuseOSError(errno.ENOENT)

    def open(self, path, flags):
        # Сначала пытаемся получить метаданные из кэша
        cached_metadata = self.cache_manager.get_metadata_from_cache(path)
        if cached_metadata is not None:
            metadata = cached_metadata
        else:
            # Если в кэше нет, запрашиваем через API и обновляем кэш
            metadata_obj = self.api_client.get_metadata(path)
            metadata = self._build_stat(metadata_obj)
            self.cache_manager.update_metadata_cache(path, metadata)
        # Проверяем, что это файл (а не, например, каталог)
        if not (metadata['st_mode'] & stat.S_IFREG):
            raise FuseOSError(errno.ENOENT)
        fh = self._next_fh
        self.open_files[fh] = path
        self._next_fh += 1
        return fh

    def _read_from_chunks(self, path: str, offset: int, size: int) -> bytes:
        """Собирает данные файла из чанков с учётом offset и size."""
        chunk_size = self.chunk_manager.chunk_size
        end_offset = offset + size
        result = bytearray()
        current_offset = offset

        while current_offset < end_offset:
            chunk_index = current_offset // chunk_size
            chunk_data = self.chunk_manager.get_chunk(path, chunk_index)
            local_offset = current_offset - (chunk_index * chunk_size)
            bytes_needed = end_offset - current_offset
            slice_data = chunk_data[local_offset:local_offset + bytes_needed]
            result.extend(slice_data)
            current_offset += len(slice_data)
            if len(slice_data) == 0:
                break  # предохранитель на случай непредвиденного завершения данных
        return bytes(result)

    def read(self, path, size, offset, fh):
        """Чтение файла, реализованное через сбор данных из чанков."""
        actual_path = self.open_files.get(fh, path)
        return self._read_from_chunks(actual_path, offset, size)

    # Заглушки для остальных методов
    def write(self, path, buf, offset, fh):
        return len(buf)

    def flush(self, path, fh):
        return 0

    def unlink(self, path):
        raise FuseOSError(errno.ENOENT)

    def mkdir(self, path, mode):
        pass

    def rmdir(self, path):
        pass

    def rename(self, old, new):
        pass

    def create(self, path, mode, fi=None):
        return 0

    def truncate(self, path, length, fh=None):
        pass