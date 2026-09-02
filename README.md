# 📝 Neuro-Dossier - AI-Powered Document Analysis Platform

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green.svg)
![React](https://img.shields.io/badge/React-Vite-blue.svg)
![SQLite](https://img.shields.io/badge/SQLite-FTS5-lightgrey.svg)
![LM Studio](https://img.shields.io/badge/LM_Studio-AI_Integration-orange.svg)

**Веб-платформа для интеллектуального анализа документов с интеграцией локальной ИИ-модели**

## 📋 О проекте

Neuro-Dossier - это инновационная веб-платформа, сочетающая в себе интерфейс для загрузки документов и интеллектуального AI-помощника на базе LM Studio с моделью 14B. Проект предоставляет уникальную возможность загружать файлы (PDF, TXT) и получать точные ответы на вопросы, основываясь исключительно на загруженном контексте.

## 🚀 Основные возможности

- 📄 **Загрузка и парсинг документов** (PDF, TXT) с автоматической нарезкой на чанки
- 🤖 **AI-анализ документов** с ответами строго по контексту загруженных файлов
- 🔍 **Полнотекстовый поиск (FTS5)** для быстрого поиска релевантных фрагментов
- 💬 **Потоковый вывод ответов** (SSE) для мгновенного отображения генерации ИИ
- 📚 **Отслеживание источников** — указание, из какого документа взят ответ
- 💾 **История чатов** и управление загруженными файлами

## 🏗 Архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Client    │◄──►│   FastAPI        │◄──►│   LM Studio     │
│   (React Vite)  │    │   Backend Core  │    │   (14B Model)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │   SQLite FTS5   │
                        │ (Docs/Chunks)   │
                        └─────────────────┘
```

## ⚡ Быстрый старт

```bash
# Клонирование репозитория
git clone https://github.com/yourusername/Neuro-Dossier.git
cd Neuro-Dossier

# --- Настройка Backend ---
cd backend
pip install -r requirements.txt
cp .env.example .env
# Настройте URL до LM Studio в .env

# Запуск backend
uvicorn main:app --host 0.0.0.0 --port 8000

# --- Настройка Frontend ---
cd ../frontend
npm install
npm run dev
```

## 📖 Документация

Полная документация проекта доступна в папке [docs/](./docs/):

- [Бизнес-требования](./documentation/br01.md)
- [Системный анализ](./documentation/sa02.md)
- [План архитектуры](./documentation/ap03.md)
- [Техническое задание](./documentation/tt04.md)
- [План тестирования](./documentation/tp05.md)

## 🛠 Технологический стек

- **Frontend**: React, Vite, TailwindCSS
- **Backend**: Python 3.10+, FastAPI, PyPDF2
- **AI Integration**: LM Studio (Qwen 14B / Llama 3)
- **Database**: SQLite + FTS5 (Полнотекстовый поиск)
- **Architecture**: Async/await, SSE Streaming, Custom RAG

## 👥 Команда разработки

| Роль | Разработчик | 
|------|-------------|
| Team Lead & Backend | Чернаков Денис |
| AI/ML Engineer | Татаринов Вячеслав |
| Frontend Developer | Бобин Вадим |
| DevOps & Integration | Шелков Данила |

---

*Документация подготовлена командой Neuro-Dossier*

---
