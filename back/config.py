import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    #пути
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
    DB_PATH = os.path.join(BASE_DIR, "neuro_dossier.db")

    #настройка нарезки чанков
    CHUNK_SIZE = 1000          #символы
    CHUNK_OVERLAP = 200

    # LMstudio 
    LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://localhost:1234/v1")
    LM_MODEL = os.getenv("LM_MODEL", "local-model")

    # макс количество чанков для контекста
    TOP_K = 5

config = Config()