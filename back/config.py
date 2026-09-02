import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Читаем из .env или используем значения по умолчанию
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
    DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "neuro_dossier.db"))
    
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP"))
    
    LM_STUDIO_URL = os.getenv("LM_STUDIO_URL")
    LM_MODEL = os.getenv("LM_MODEL")
    
    TOP_K = int(os.getenv("TOP_K", 5))
    
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))
    RELOAD = os.getenv("RELOAD").lower() in ("true", "1", "yes")

config = Config()