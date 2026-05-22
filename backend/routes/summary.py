from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.rag_engine import get_document_summary

router = APIRouter()


class SummaryResponse(BaseModel):
    summary: str
    file_id: str


@router.get("/summary/{file_id}", response_model=SummaryResponse)
async def get_summary(file_id: str):
    if not file_id.strip():
        raise HTTPException(status_code=400, detail="file_id is required.")

    summary = get_document_summary(file_id)
    return SummaryResponse(summary=summary, file_id=file_id)
