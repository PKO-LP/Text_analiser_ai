from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models import ChatRequest, ActionType
from rag_engine import rag_engine

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/analyze")
async def analyze(request: ChatRequest):
    """
    Универсальный эндпоинт для анализа документов.

    Принимает:
        - action: "summary" или "context_search"
        - query: текст запроса (обязательно для context_search)
        - file_ids: список ID файлов (опционально)

    Возвращает:
        Поток SSE с ответом от LM Studio.
    """
    # Валидация: для context_search обязателен query
    if request.action == ActionType.CONTEXT_SEARCH and not request.query:
        raise HTTPException(
            status_code=400,
            detail="For 'context_search' action, 'query' field is required"
        )

    # Для summary query не обязателен
    if request.action == ActionType.SUMMARY:
        # Если query не передан, используем заглушку
        search_query = ""
    else:
        search_query = request.query

async def generate():
    try:
        async for token in rag_engine.stream_answer(
            action=request.action,
            query=request.query,
            file_ids=request.file_ids
        ):
            # Экранируем \n и \r, чтобы не ломать SSE-протокол
            safe_token = token.replace('\n', '\n').replace('\r', '\r')
            yield f"data: {safe_token}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        yield f"data: [ERROR] {str(e)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")