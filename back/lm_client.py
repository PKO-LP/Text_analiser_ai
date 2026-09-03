import json
import httpx
from typing import AsyncGenerator
from config import config


class LMClient:
    """
    Клиент для взаимодействия с LM Studio через OpenAI-compatible API.
    Настроен под Qwen2.5-14B-Instruct с параметрами для RAG.
    """

    SYSTEM_PROMPT = (
        "Ты — интеллектуальный ассистент для анализа документов. "
        "Твоя задача — отвечать на вопросы пользователя строго на основе предоставленного контекста из загруженных документов. "
        "Если ответ не содержится в контексте, честно скажи об этом. "
        "Не придумывай факты, не используй внешние знания. "
        "Отвечай на русском языке. Будь кратким, точным и структурированным. "
        "При анализе выделяй ключевые темы и идеи."
    )

    def init(self, base_url: str = config.LM_STUDIO_URL):
        # Убираем trailing slash, чтобы не дублировались слеши в URL
        self.base_url = base_url.rstrip("/")
        # Fallback на случай, если LM_MODEL не прописан в .env
        self.model = getattr(config, "LM_MODEL", "Qwen2.5-14B-Instruct")

    async def stream_completion(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Отправляет промпт в LM Studio и стримит токены обратно.
        При сетевой ошибке или проблеме с моделью выдаёт сообщение в поток вместо крэша.
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "stream": True,
            "temperature": 0.3,   # низкая температура для точности RAG
            "top_p": 0.9,         # стандартное значение
            "max_tokens": 2048,   # лимит ответа
        }

        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    timeout=120.0,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    # Если LM Studio вернул 4xx/5xx — сразу поймаем
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue

                        data = line[6:]
                        if data == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            token = delta.get("content", "")
                            if token:
                                yield token
                        except (json.JSONDecodeError, IndexError, KeyError):
                            # Пропускаем битые или служебные SSE-фреймы
                            continue

        except httpx.ConnectError:
            yield "[Ошибка соединения: не удалось подключиться к LM Studio. Убедитесь, что сервер запущен и API включен.]"

        except httpx.HTTPStatusError as e:
            error_body = e.response.text[:300]
            yield f"[Ошибка HTTP {e.response.status_code} от LM Studio: {error_body}]"

        except Exception as e:
            yield f"[Ошибка при обращении к модели: {str(e)}]"


# Глобальный экземпляр для использования в rag_engine
lm_client = LMClient()
