from dataclasses import dataclass
from typing import Optional


@dataclass
class FileMetadata:
    """Класс для хранения метаданных файла/папки"""
    name: str
    path: str
    file_type: str
    created: str
    modified: str
    size: Optional[int] = None
    mime_type: Optional[str] = None
    md5: Optional[str] = None
    sha256: Optional[str] = None
    resource_id: Optional[str] = None
    public_url: Optional[str] = None
    file_url: Optional[str] = None

    @staticmethod
    def from_json(data: dict) -> 'FileMetadata':
        """Создаёт экземпляр FileMetadata из JSON-ответа"""
        return FileMetadata(
            name=data.get("name"),
            path=data.get("path"),
            file_type=data.get("type"),
            created=data.get("created"),
            modified=data.get("modified"),
            size=data.get("size"),
            mime_type=data.get("mime_type"),
            md5=data.get("md5"),
            sha256=data.get("sha256"),
            resource_id=data.get("resource_id"),
            public_url=data.get("public_url"),
            file_url=data.get("file")
        )
