# Yandex Disk FUSE Filesystem

## Описание проекта:
Проект предоставляет FUSE-файловую систему для macOS, позволяющую работать с данными Яндекс.Диска через REST API. Система поддерживает базовые операции (чтение, запись, создание, удаление, переименование), динамическое кэширование и может работать в синхронном и асинхронном режимах. В будущем возможна контейнеризация через Docker.

## Структура проекта

```
project/
├── api/
│   ├── api_client.py       # Основной класс для работы с REST API
│   └── api_client_io.py    # Низкоуровневые HTTP-запросы (requests / aiohttp)
├── fuse/
│   └── fuse_handler.py     # Обработчик FUSE-вызовов (getattr, readdir, open, read, write, mkdir, rename, unlink)
├── cache/
│   ├── cache_manager.py    # Модуль кэширования (TTL, LRU)
│   └── download_listener.py# (Опционально) Отслеживание прогресса загрузок
├── models/
│   └── disk_info.py        # Информация о состоянии диска
├── main.py                 # Инициализация и запуск FUSE-системы
└── Dockerfile              # (Опционально) Докеризация приложения
```
### Как начать
	1.Установка зависимостей:
Установите необходимые библиотеки (например, fusepy, requests, aiohttp) через pip:

`pip install -r requirements.txt`


	2. Настройка API:
Отредактируйте конфигурационный файл или переменные окружения, чтобы задать токен доступа и параметры API Яндекс.Диска.
	
	3. Запуск приложения:
Для запуска базовой (синхронной) версии:

`python main.py`

Для асинхронной версии убедитесь, что настроены соответствующие параметры в конфигурации.

	4.	Монтаж FUSE-системы:
После запуска приложение смонтирует файловую систему в указанную точку монтирования (укажите путь в конфигурации).

## Основные компоненты
- **APIClient:**
Отвечает за взаимодействие с REST API Яндекс.Диска (получение метаданных, загрузка, скачивание файлов, создание папок и т.д.).
- **FUSEHandler:**
Реализует обработку системных вызовов FUSE, используя APIClient для работы с данными. Поддерживает основные операции: getattr, readdir, open, read, write, mkdir, rename, unlink.
- **CacheManager:**
Модуль для кэширования метаданных и содержимого файлов с поддержкой TTL и политики LRU. Позволяет уменьшить задержки при повторных запросах.
- **DownloadListener (опционально):**
Абстрактный класс для обработки событий загрузки (прогресс, отмена).
- **DiskInfo:**
Модель для представления информации о состоянии диска (общий объем, использованное пространство и др.).

## Разработка и вклад
- Стиль и архитектура:
Проект построен на модульной архитектуре. Каждый компонент отвечает за свою задачу: API клиент, обработка FUSE вызовов, кэширование. При добавлении нового функционала следуйте принципу единой ответственности.
- Порядок разработки:
  * Реализация и тестирование APIClient (синхронно и асинхронно).
  * Разработка FUSEHandler с интеграцией APIClient.
  * Внедрение кэширования и обработки событий загрузки.
  * Тестирование и сравнение синхронной и асинхронной реализации.
  * Докеризация (опционально).

- Как внести вклад:
Если вы хотите улучшить проект, отправьте pull request с подробным описанием изменений. Рекомендуется сначала обсудить изменения через Issues.
