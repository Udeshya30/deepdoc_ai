import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.rag_engine import get_suggested_questions

router = APIRouter()
logger = logging.getLogger(__name__)


class QuestionsResponse(BaseModel):
    questions: list[str]


@router.get("/questions/{file_id}", response_model=QuestionsResponse)
async def suggested_questions(file_id: str):
    if not file_id.strip():
        raise HTTPException(status_code=400, detail="file_id is required.")
    try:
        questions = get_suggested_questions(file_id)
    except Exception as exc:
        logger.exception("Failed to generate questions for file_id=%s", file_id)
        raise HTTPException(status_code=500, detail=str(exc))
    return QuestionsResponse(questions=questions)
