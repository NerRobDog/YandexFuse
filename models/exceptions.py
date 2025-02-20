from dataclasses import dataclass
from typing import Optional


@dataclass
class APIError:
    """Структура для хранения информации об ошибке от API"""
    message: str
    description: Optional[str] = None
    error: Optional[str] = None

    @staticmethod
    def from_json(data: dict) -> 'APIError':
        """Создает экземпляр APIError из JSON-ответа"""
        return APIError(
            message=data.get("message", "Ошибка без сообщения"),
            description=data.get("description"),
            error=data.get("error")
        )

    def __str__(self) -> str:
        """Форматирование для вывода"""
        return f"Ошибка: {self.message} \n Описание: {self.description} \n Код ошибки: {self.error}"
