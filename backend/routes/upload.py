import os
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from core.config import settings
from services.rag_engine import embed_document

router = APIRouter()

os.makedirs(settings.upload_dir, exist_ok=True)


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    message: str


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    if file.size and file.size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds the {settings.max_file_size_mb}MB size limit.",
        )

    file_id = str(uuid.uuid4())
    safe_name = Path(file.filename).name  # strips any directory traversal attempts
    file_location = os.path.join(settings.upload_dir, f"{file_id}_{safe_name}")

    content = await file.read()
    with open(file_location, "wb") as f:
        f.write(content)

    try:
        embed_document(file_location, file_id)
    except Exception as exc:
        os.remove(file_location)
        raise HTTPException(
            status_code=500, detail=f"Failed to process document: {exc}"
        )

    return UploadResponse(
        file_id=file_id,
        filename=safe_name,
        message="Upload and indexing successful",
    )
