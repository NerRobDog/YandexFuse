import os
import signal
import subprocess
import sys

from dotenv import load_dotenv
from api.api_client import APIClient
from fuse import FUSE
from fuse_fs.fuse_handler import DiskFS


def cleanup(mount_point, signum=None, frame=None):
    print("\nРазмонтирование файловой системы...")
    try:
        subprocess.run(['umount', mount_point], check=True)
        print("Файловая система успешно размонтирована")
    except subprocess.CalledProcessError:
        print("Ошибка при размонтировании")
    sys.exit(0)


# Load environment variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
URL = os.getenv('URL')
MOUNT_POINT = "/Users/nik/Downloads/fuse"

client = APIClient(token=TOKEN, base_url=URL)
fs = DiskFS(api_client=client)

# Регистрируем обработчик сигналов
signal.signal(signal.SIGINT, lambda s, f: cleanup(MOUNT_POINT, s, f))
signal.signal(signal.SIGTERM, lambda s, f: cleanup(MOUNT_POINT, s, f))

# Монтируем файловую систему
FUSE(fs, MOUNT_POINT, nothreads=True, foreground=True, debug=True)