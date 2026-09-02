import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from models import FileUploadResponse, FileInfo
from database import get_files, get_file
from rag_engine import rag_engine
from config import config


router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    os.makedirs(config.UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(config.UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

    try:
        file_id = await rag_engine.process_file(file_path, file.filename)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Processing failed: {str(e)}")

    return FileUploadResponse(file_id=file_id, filename=file.filename, status="READY")


@router.get("/", response_model=List[FileInfo])
async def list_files():
    files = await get_files()
    return [FileInfo(**f) for f in files]


@router.get("/{file_id}", response_model=FileInfo)
async def get_file_info(file_id: int):

    f = await get_file(file_id)
    if not f:
        raise HTTPException(status_code=404, detail="File not found")
    return FileInfo(**f)