# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Читаем из .env или используем значения по умолчанию
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
    DB_PATH = os.getenv("DB_PATH", os.path.join(BASE_DIR, "neuro_dossier.db"))
    
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    
    LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://26.55.161.146:1234/")
    LM_MODEL = os.getenv("LM_MODEL", "qwen2.5-14b-instruct")
    
    TOP_K = int(os.getenv("TOP_K", 5))
    
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    RELOAD = os.getenv("RELOAD", "True").lower() in ("true", "1", "yes")

config = Config()