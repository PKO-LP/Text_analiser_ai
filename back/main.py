from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import files, chat
from database import init_db
from config import config


init_db()

app = FastAPI(
    title="Neuro-Dossier Backend",
    version="0.1.0",
    description="REST API для загрузки документов и AI-чата"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                # Разрешённые источники (можно заменить на список)
    allow_credentials=True,             # Разрешить куки/авторизацию
    allow_methods=["*"],                # Разрешённые HTTP-методы
    allow_headers=["*"],                # Разрешённые заголовки
)

app.include_router(files.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {"message": "Neuro-Dossier API is running"}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.RELOAD
    )