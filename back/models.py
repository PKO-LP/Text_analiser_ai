# шедевро Dto для записи ответов в бд 
from pydantic import BaseModel   # Базовый класс для всех моделей данных
from typing import List, Optional

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