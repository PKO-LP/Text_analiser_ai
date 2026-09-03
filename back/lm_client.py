import json                     # Для парсинга JSON-ответов от LM Studio
import asyncio                  # Для имитации задержек в заглушке
from typing import AsyncGenerator  # Аннотация: генератор, выдающий строки
import httpx                    # Асинхронный HTTP-клиент для реальных запросов
from config import config       # Настройки (URL, модель)

"""
Клиент для взаимодействия с LM Studio.

LM Studio предоставляет OpenAI-совместимый API.
Мы отправляем POST-запрос с prompt и получаем потоковый ответ (stream=True).
"""

class LMClient:
    """
    Клиент для общения с языковой моделью через HTTP.
    """

    def __init__(self, base_url: str = config.LM_STUDIO_URL):
        """
        Сохраняем базовый URL LM Studio (по умолчанию из конфига).
        """
        self.base_url = base_url

    async def stream_completion(self, prompt: str) -> AsyncGenerator[str, None]:
        
        async with httpx.AsyncClient() as client:
            # Отправляем POST-запрос на /chat/completions (OpenAI-совместимый эндпоинт)
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json={
                    "model": config.LM_MODEL,          # Имя модели (из конфига)
                    "messages": [{"role": "user", "content": prompt}],
                    "stream": True,                    # Включаем стриминг
                },
                timeout=60.0  # Таймаут на случай, если модель долго отвечает
            ) as response:
                # Читаем ответ построчно
                async for line in response.aiter_lines():
                    # SSE-ответы начинаются с "data: "
                    if line.startswith("data: "):
                        data = line[6:]  # Убираем префикс "data: "
                        if data == "[DONE]":  # Сигнал завершения
                            break
                        try:
                            # Парсим JSON-фрагмент
                            chunk = json.loads(data)
                            # Извлекаем текст токена из структуры ответа
                            token = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                            if token:
                                yield token  # Отдаём токен наружу
                        except json.JSONDecodeError:
                            # Если что-то пошло не так – игнорируем строку
                            continue

lm_client = LMClient()