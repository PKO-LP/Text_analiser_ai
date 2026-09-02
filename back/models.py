# шедевро Dto для записи ответов в бд 
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

# === Модель ответа при загрузке файла ===
class FileUploadResponse(BaseModel):
    file_id: int                 # ID файла, присвоенный БД
    filename: str                # Оригинальное имя файла
    status: str                  # Текущий статус (PROCESSING/READY/ERROR)

# === Модель информации о файле (для списка / детального просмотра) ===
class FileInfo(BaseModel):
    id: int                      # ID файла
    filename: str                # Имя файла
    status: str                  # Статус обработки
    chunks_count: Optional[int] = 0  # Количество чанков (пока не используется)

# === Модель запроса к чату ===
class ChatRequest(BaseModel):
    query: str                   # Вопрос пользователя
    file_ids: Optional[List[int]] = []  # Фильтр по ID файлов (пока не реализован)

# === Модель ошибки (заготовка) ===
class ErrorResponse(BaseModel):
    detail: str                  # Текст ошибки


# === Enum для типов действий ===
class ActionType(str, Enum):
    SUMMARY = "summary"                    # Краткий анализ
    CONTEXT_SEARCH = "context_search"      # Поиск по контексту
    # В будущем можно добавить:
    # COMPARE = "compare"                  # Сравнение документов
    # TRANSLATE = "translate"              # Перевод

# === Модель запроса к чату (обновлённая) ===
class ChatRequest(BaseModel):
    action: ActionType                    # Тип действия (от кнопки)
    query: Optional[str] = None           # Текст поиска (для context_search)
    file_ids: Optional[List[int]] = []    # ID файлов (можно искать по всем)

# === Остальные модели остаются без изменений ===
class FileUploadResponse(BaseModel):
    file_id: int
    filename: str
    status: str

class FileInfo(BaseModel):
    id: int
    filename: str
    status: str
    chunks_count: Optional[int] = 0

class ErrorResponse(BaseModel):
    detail: str