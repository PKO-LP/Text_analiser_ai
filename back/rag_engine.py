import os
import pypdfium2 as pdfium
from typing import List, AsyncGenerator
from config import config
from database import save_chunks, search_chunks, update_file_status, add_file
from lm_client import lm_client


class RAGEngine:
    """Ядро RAG: парсинг, нарезка, поиск, генерация ответа."""

    @staticmethod
    def split_text(text: str, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> List[str]:
        """Разбивает текст на чанки с перекрытием."""
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)

            if end < text_len:
                last_space = text.rfind(' ', start, end)
                if last_space > start + chunk_size // 2:
                    end = last_space + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            if end >= text_len:
                break
            start = end - overlap

        return chunks

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Извлекает текст из PDF через pypdfium2."""
        text = ""
        doc = pdfium.PdfDocument(file_path)
        for page in doc:
            textpage = page.get_textpage()
            page_text = textpage.get_text_range()
            if page_text:
                text += page_text + "\n"
        return text

    @staticmethod
    def parse_txt(file_path: str) -> str:
        """Читает текстовый файл."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    async def process_file(self, file_path: str, filename: str) -> int:
        """Полный цикл обработки файла."""
        file_id = await add_file(filename)

        try:
            ext = os.path.splitext(filename)[1].lower()

            if ext == '.pdf':
                text = self.parse_pdf(file_path)
            elif ext == '.txt':
                text = self.parse_txt(file_path)
            else:
                raise ValueError(f"Unsupported format: {ext}")

            if not text.strip():
                raise ValueError("Empty text extracted (maybe scanned PDF?)")

            chunks = self.split_text(text)
            if not chunks:
                raise ValueError("No chunks produced")

            await save_chunks(file_id, chunks)
            await update_file_status(file_id, "READY")

        except Exception as e:
            await update_file_status(file_id, "ERROR")
            raise e

        return file_id

    async def stream_answer(self, action: str, query: str = None, file_ids: List[int] = None) -> AsyncGenerator[str, None]:
        """
        Генерация ответа в зависимости от действия.
        action: "summary" или "context_search"
        query: текст поиска (для context_search)
        file_ids: список ID файлов (если None — ищем по всем)
        """
        # Валидация
        if action == "context_search" and not query:
            yield "Для поиска по контексту укажите текст запроса."
            return

        # Шаг 1: выбираем чанки
        if action == "summary":
            # Для сводки берем первые top_k чанков из всех документов
            # (пустой MATCH в FTS5 ломается, поэтому ищем по букве "а" — она есть в любом тексте)
            results = await search_chunks("а", top_k=config.TOP_K)
        else:
            results = await search_chunks(query, top_k=config.TOP_K)

        if not results:
            yield "Не найдено релевантной информации в загруженных документах."
            return

        # Шаг 2: собираем контекст
        context_parts = []
        for r in results:
            context_parts.append(f"[Файл {r['file_id']}, фрагмент {r['chunk_index']}] {r['content']}")
        context = "\n\n".join(context_parts)

        # Шаг 3: формируем промпт
        if action == "summary":
            prompt = f"Проанализируй следующий текст и выдели основные темы и ключевые идеи:\n\n{context}"
        elif action == "context_search":
            prompt = (
                f"Контекст из документов:\n{context}\n\n"
                f"Вопрос: {query}\n\n"
                f"Ответь кратко и точно, используя только предоставленный контекст. "
                f"Если ответа нет в контексте, скажи об этом."
            )
        else:
            prompt = f"Контекст:\n{context}\n\nВопрос: {query if query else 'Сделай анализ текста.'}"

        # Шаг 4: отправляем в LM Studio
        async for token in lm_client.stream_completion(prompt):
            yield token


rag_engine = RAGEngine()
