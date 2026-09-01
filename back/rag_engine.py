# -*- coding: utf-8 -*-
import os
import pypdfium2 as pdfium          # Движок PDF от Google Chrome – быстрый и точный
from typing import List, AsyncGenerator
from config import config
from database import save_chunks, search_chunks, update_file_status
from lm_client import lm_client


class RAGEngine:

    @staticmethod
    def split_text(text: str, chunk_size: int = config.CHUNK_SIZE, overlap: int = config.CHUNK_OVERLAP) -> List[str]:

        # режем текст на чанки , стараясь не задевать слова ( работать по пробелам )

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + chunk_size, text_len)

            # если не последний кусок – ищем границу по пробелу
            if end < text_len:
                last_space = text.rfind(' ', start, end)
                if last_space > start + chunk_size // 2:
                    end = last_space + 1   # берём до пробела

            chunks.append(text[start:end].strip())

            # отступаем назад, чтобы следующий чанк захватил конец предыдущего
            if end < text_len:
                start = end - overlap
            else:
                break

        return chunks

    @staticmethod
    def parse_pdf(file_path: str) -> str:

        # извлекаем текст из PDF через pypdfium2 (PDFium).

        text = ""
        # открываем пдф документ
        doc = pdfium.PdfDocument(file_path)

        # перебераем ВСЕ страницы
        for page in doc:
            # получаем объект для работы с текстом страницы
            textpage = page.get_textpage()
            # извлекаем весь текст со страницы
            page_text = textpage.get_text_range()
            if page_text:
                text += page_text + "\n"

        return text

    @staticmethod
    def parse_txt(file_path: str) -> str:
        # читает обычный текстовый файл ( UTF-8 ) 
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    async def process_file(self, file_path: str, filename: str) -> int:

        from database import add_file, update_file_status, save_chunks

        file_id = await add_file(filename)   # создаём запись

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

    async def stream_answer(self, query: str, file_ids: List[int] = None) -> AsyncGenerator[str, None]:

        # поиск чанков
        results = await search_chunks(query, top_k=config.TOP_K)

        if not results:
            yield "не найдено релевантной информации в загруженных документах."
            return

        # собираем контекст из найденных чанков
        context_parts = []
        for r in results:
            context_parts.append(f"[Файл {r['file_id']}] {r['content']}")
        context = "\n\n".join(context_parts)

        # промпт для модели
        prompt = f"Контекст:\n{context}\n\nВопрос: {query}\nОтвет:"

        # стримим токены от LM Studio
        async for token in lm_client.stream_completion(prompt):
            yield token


# единый экземпляр для использования в других модулях
rag_engine = RAGEngine()