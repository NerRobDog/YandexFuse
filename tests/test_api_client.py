import os
import pytest
from models.file_metadata import FileMetadata
from api.api_client import APIClient


def api_client_with_env():
    from dotenv import load_dotenv
    load_dotenv()

    token = os.environ.get('TOKEN')
    base_url = os.environ.get('URL')
    if not token or not base_url:
        pytest.skip('Отсутствуют переменные окружения TOKEN или URL')
    return APIClient(token=token, base_url=base_url)

@pytest.fixture
def test_file(tmp_path):
    file_path = tmp_path / 'test.txt'
    file_path.write_text('test content')
    return str(file_path)

@pytest.fixture
def api_client():
    return api_client_with_env()

def test_should_get_file_metadata(api_client):
    metadata = api_client.get_metadata('/')
    assert isinstance(metadata, FileMetadata)
    assert metadata.file_type == 'dir'

def test_should_list_folder_contents(api_client):
    items = api_client.list_folder('/')
    assert isinstance(items, list)
    assert all(isinstance(item, FileMetadata) for item in items)


def test_should_upload_and_download_file(api_client, test_file, tmp_path):
    remote_path = '/test_upload.txt'
    download_path = str(tmp_path / 'downloaded.txt')

    api_client.upload_file(remote_path, test_file)
    api_client.download_file(remote_path, download_path)

    assert open(test_file).read() == open(download_path).read()
    api_client.delete_file(remote_path)

def test_should_create_and_delete_folder(api_client):
    folder_path = '/test_folder'
    api_client.create_folder(folder_path)

    metadata = api_client.get_metadata(folder_path)
    assert metadata.file_type == 'dir'

    api_client.delete_folder(folder_path)
    with pytest.raises(Exception):
        api_client.get_metadata(folder_path)

def test_should_move_file(api_client, test_file):
    src_path = '/test_move_src.txt'
    dst_path = '/test_move_dst.txt'

    api_client.upload_file(src_path, test_file)
    api_client.move(src_path, dst_path)

    with pytest.raises(Exception):
        api_client.get_metadata(src_path)
    assert api_client.get_metadata(dst_path).file_type == 'file'

    api_client.delete_file(dst_path)

def test_should_bypass_upload_speed_limit(api_client, test_file):
    limited_path = '/test.zip'
    api_client.upload_file_bypass(limited_path, test_file)

    metadata = api_client.get_metadata(limited_path)
    assert metadata.file_type == 'file'

    api_client.delete_file(limited_path)