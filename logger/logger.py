import logging
import os
from logging.handlers import RotatingFileHandler

# Общий формат сообщений
LOG_FORMAT = "[%(levelname)s] [%(asctime)s] [%(name)s] %(message)s"

# Папка для логов
LOG_DIR = "/tmp/yadisk_logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Настройки логирования
LOGGING_CONFIG = {
    'DiskFS': {
        'file': f"{LOG_DIR}/fuse.log",
        'level': logging.DEBUG  # Для отладки FUSE
    },
    'APIClient': {
        'file': f"{LOG_DIR}/api.log",
        'level': logging.INFO  # Только INFO и выше
    },
    'APIClientIO': {
        'file': f"{LOG_DIR}/io.log",
        'level': logging.WARNING  # Только WARNING и выше
    },
    'ChunkManager': {
        'file': f"{LOG_DIR}/chunk.log",
        'level': logging.DEBUG  # Полный DEBUG
    },
    'CacheManager': {
        'file': f"{LOG_DIR}/cache.log",
        'level': logging.INFO  # Только кэш
    }
}

def setup_logger(name: str) -> logging.Logger:
    """
    Настройка логгера по имени. Если имя есть в LOGGING_CONFIG, то используются
    настройки оттуда (разделение по файлам и уровням).
    """
    logger = logging.getLogger(name)

    # Если логгер уже настроен, не дублируем обработчики
    if logger.hasHandlers():
        return logger

    # Получаем настройки для логгера (или по умолчанию)
    config = LOGGING_CONFIG.get(name, {})
    log_file = config.get('file', f"{LOG_DIR}/default.log")
    log_level = config.get('level', logging.DEBUG)

    logger.setLevel(log_level)

    # Формат сообщений
    formatter = logging.Formatter(LOG_FORMAT)

    # === Вывод в файл с ротацией ===
    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=2)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # === Вывод в консоль (только ошибки) ===
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
