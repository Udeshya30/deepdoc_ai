import logging

from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from agent.graph import agent_graph
from agent.state import AgentState

router = APIRouter()
logger = logging.getLogger(__name__)


class ConversationTurn(BaseModel):
    role: str   # "user" or "ai"
    text: str


class AskRequest(BaseModel):
    question: str
    file_id: str
    history: list[ConversationTurn] = []


class AskResponse(BaseModel):
    answer: str
    intent: str


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if not request.file_id.strip():
        raise HTTPException(status_code=400, detail="file_id is required.")

    initial_state: AgentState = {
        "messages": [HumanMessage(content=request.question)],
        "file_id": request.file_id,
        "intent": "",
        "context": "",
        "answer": "",
        "history": [t.model_dump() for t in request.history],
    }

    try:
        result = agent_graph.invoke(initial_state)
    except Exception as exc:
        logger.exception("Agent failed for file_id=%s", request.file_id)
        raise HTTPException(status_code=500, detail=str(exc))

    return AskResponse(answer=result["answer"], intent=result["intent"])
