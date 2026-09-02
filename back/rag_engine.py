import os
import pypdfium2 as pdfium
from typing import List, AsyncGenerator
from config import config
from database import save_chunks, search_chunks, update_file_status
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

            chunks.append(text[start:end].strip())

            if end < text_len:
                start = end - overlap
            else:
                break

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
        from database import add_file, update_file_status, save_chunks

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
        # Шаг 1: ищем релевантные чанки
        search_query = query if query else ""
        results = await search_chunks(search_query, top_k=config.TOP_K)

        if not results:
            yield "Не найдено релевантной информации в загруженных документах."
            return

        # Шаг 2: собираем контекст
        context_parts = []
        for r in results:
            context_parts.append(f"[Файл {r['file_id']}] {r['content']}")
        context = "\n\n".join(context_parts)

        # Шаг 3: формируем минимальный промт в зависимости от действия
        if action == "summary":
            # Краткий анализ всего документа
            prompt = f"Файл:\n{context}\n\nЗадача: сделай краткий анализ этого текста. Выдели основные темы и ключевые идеи."

        elif action == "context_search":
            # Поиск по контексту с конкретным запросом
            if not query:
                yield "Для поиска по контексту укажите текст запроса."
                return
            prompt = f"Файл:\n{context}\n\nЗадача: найди в тексте информацию, связанную с запросом: '{query}'. Ответь кратко и по делу, используя только содержимое файла."

        else:
            # На всякий случай (если пришёл неизвестный action)
            prompt = f"Файл:\n{context}\n\nВопрос: {query if query else 'сделай анализ'}"

        # Шаг 4: отправляем в LM Studio (системный промт уже настроен в LM Studio)
        async for token in lm_client.stream_completion(prompt):
            yield token


# Единый экземпляр
rag_engine = RAGEngine()