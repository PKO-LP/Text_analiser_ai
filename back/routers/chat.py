from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models import ChatRequest
from rag_engine import rag_engine

"""
Роутер для работы с чатом.
Принимает вопросы пользователя и возвращает потоковый ответ (SSE) от ИИ.
"""

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Эндпоинт для потоковой генерации ответа.

    Принимает:
        - query: текст вопроса
        - file_ids: (опционально) список ID файлов для ограничения поиска

    Возвращает:
        Поток Server-Sent Events (SSE) с токенами ответа.
        Каждое событие имеет вид: data: токен\n\n
        По окончании отправляется data: [DONE]\n\n
    """
    # Валидация: вопрос не должен быть пустым
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Внутренний генератор, который будет выдавать SSE-события
    async def generate():
        # Запускаем RAG-пайплайн и получаем токены
        async for token in rag_engine.stream_answer(
            request.query,
            request.file_ids
        ):
            # Формируем SSE-строку
            yield f"data: {token}\n\n"
        # Сигнал завершения потока
        yield "data: [DONE]\n\n"

    # Возвращаем StreamingResponse с типом text/event-stream
    return StreamingResponse(generate(), media_type="text/event-stream")