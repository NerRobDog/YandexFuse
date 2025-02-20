import pytest
from api.api_client import APIClient

@pytest.fixture
def api_client():
    return APIClient(token='test_token', base_url='test_base_url')

def test_get_metadata(api_client):
    with pytest.raises(NotImplementedError):
        api_client.get_metadata('test_path')

def test_list_folder(api_client):
    with pytest.raises(NotImplementedError):
        api_client.list_folder('test_path')

def test_download_file(api_client):
    with pytest.raises(NotImplementedError):
        api_client.download_file('test_path', 'test_local_path')

def test_upload_file(api_client):
    with pytest.raises(NotImplementedError):
        api_client.upload_file('test_path', 'test_local_path')

def test_create_folder(api_client):
    with pytest.raises(NotImplementedError):
        api_client.create_folder('test_path')

def test_delete_file(api_client):
    with pytest.raises(NotImplementedError):
        api_client.delete_file('test_path')

def test_delete_folder(api_client):
    with pytest.raises(NotImplementedError):
        api_client.delete_folder('test_path')

def test_move(api_client):
    with pytest.raises(NotImplementedError):
        api_client.move('test_from_path', 'test_to_path')
