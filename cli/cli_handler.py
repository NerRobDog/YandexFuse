import argparse
from api.api_client import APIClient
from dotenv import load_dotenv
import os
import shlex

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TOKEN')
URL = os.getenv('URL')

client = APIClient(token=TOKEN, base_url=URL)

def list_folder(path):
    try:
        items = client.list_folder(path)
        for item in items:
            print(item.name)
    except Exception as e:
        print(f"Ошибка: {e}")

def get_metadata(path):
    try:
        metadata = client.get_metadata(path)
        print(metadata)
    except Exception as e:
        print(f"Ошибка: {e}")

def download_file(remote_path, local_path):
    try:
        client.download_file(remote_path, local_path)
        print(f"Файл {remote_path} скачан в {local_path}")
    except Exception as e:
        print(f"Ошибка: {e}")

def upload_file(local_path, remote_path):
    try:
        client.upload_file(remote_path, local_path)
        print(f"Файл {local_path} загружен в {remote_path}")
    except Exception as e:
        print(f"Ошибка: {e}")

def delete_file(path):
    try:
        client.delete_file(path)
        print(f"Файл {path} удален")
    except Exception as e:
        print(f"Ошибка: {e}")

def move_file(from_path, to_path):
    try:
        client.move(from_path, to_path)
        print(f"Файл перемещен из {from_path} в {to_path}")
    except Exception as e:
        print(f"Ошибка: {e}")

def main():
    parser = argparse.ArgumentParser(description="CLI для работы с API Яндекс.Диска")
    subparsers = parser.add_subparsers(dest="command")

    # Команда ls
    parser_ls = subparsers.add_parser("ls", help="Список файлов в папке")
    parser_ls.add_argument("path", help="Путь к папке")

    # Команда get
    parser_get = subparsers.add_parser("get", help="Получение метаданных файла/папки")
    parser_get.add_argument("path", help="Путь к файлу/папке")

    # Команда download
    parser_download = subparsers.add_parser("download", help="Скачивание файла")
    parser_download.add_argument("remote_path", help="Удаленный путь к файлу")
    parser_download.add_argument("local_path", help="Локальный путь для сохранения файла")

    # Команда upload
    parser_upload = subparsers.add_parser("upload", help="Загрузка файла")
    parser_upload.add_argument("local_path", help="Локальный путь к файлу")
    parser_upload.add_argument("remote_path", help="Удаленный путь для сохранения файла")

    # Команда rm
    parser_rm = subparsers.add_parser("rm", help="Удаление файла")
    parser_rm.add_argument("path", help="Путь к файлу")

    # Команда mv
    parser_mv = subparsers.add_parser("mv", help="Перемещение файла")
    parser_mv.add_argument("from_path", help="Исходный путь к файлу")
    parser_mv.add_argument("to_path", help="Новый путь к файлу")

    while True:
        try:
            user_input = input("Введите команду: ")
            args = parser.parse_args(shlex.split(user_input))

            if args.command == "ls":
                list_folder(args.path)
            elif args.command == "get":
                get_metadata(args.path)
            elif args.command == "download":
                download_file(args.remote_path, args.local_path)
            elif args.command == "upload":
                upload_file(args.local_path, args.remote_path)
            elif args.command == "rm":
                delete_file(args.path)
            elif args.command == "mv":
                move_file(args.from_path, args.to_path)
            else:
                parser.print_help()
        except (KeyboardInterrupt, EOFError):
            print("\nЗавершение работы.")
            break

if __name__ == "__main__":
    main()