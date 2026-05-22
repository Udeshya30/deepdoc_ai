"""
LangGraph agent graph for DeepDocAI.

Flow:
  classify_intent → (conditional) → rag_search | summarize | extract
                                           ↓
                                   format_response → END

The LLM is used twice:
  1. To classify intent (cheap, ~50 tokens)
  2. To format the final answer using retrieved context
"""
import logging

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph

from agent.state import AgentState
from models.mistral_runner import generate_answer
from services.rag_engine import get_document_summary, search_document

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Node 1: Classify what the user wants
# ---------------------------------------------------------------------------
def classify_intent(state: AgentState) -> AgentState:
    question = state["messages"][-1].content

    prompt = (
        "Classify the user's question into exactly one category.\n\n"
        "Categories:\n"
        "- summarize: user wants an overview or summary of the document\n"
        "- extract: user wants specific items like skills, dates, names, numbers, or lists\n"
        "- search: user wants to find information or get an answer to a question\n\n"
        f"User question: {question}\n\n"
        "Reply with ONE word only (summarize / extract / search):"
    )

    raw = generate_answer(prompt).strip().lower()

    if "summarize" in raw:
        intent = "summarize"
    elif "extract" in raw:
        intent = "extract"
    else:
        intent = "search"

    logger.info("Intent classified as: %s for question: %s", intent, question[:60])
    return {**state, "intent": intent}


def route_by_intent(state: AgentState) -> str:
    return state.get("intent", "search")


# ---------------------------------------------------------------------------
# Node 2a: RAG search — answer a specific question
# ---------------------------------------------------------------------------
def rag_search_node(state: AgentState) -> AgentState:
    query = state["messages"][-1].content
    file_id = state["file_id"]
    history = state.get("history", [])
    context = search_document(query, file_id, history=history)
    return {**state, "context": context}


# ---------------------------------------------------------------------------
# Node 2b: Summarize the full document
# ---------------------------------------------------------------------------
def summarize_node(state: AgentState) -> AgentState:
    file_id = state["file_id"]
    context = get_document_summary(file_id)
    return {**state, "context": context}


# ---------------------------------------------------------------------------
# Node 2c: Extract specific entities / structured data
# ---------------------------------------------------------------------------
def extract_node(state: AgentState) -> AgentState:
    query = state["messages"][-1].content
    file_id = state["file_id"]
    history = state.get("history", [])
    context = search_document(query, file_id, history=history)
    return {**state, "context": context}


# ---------------------------------------------------------------------------
# Node 3: Format final response and append to message history
# ---------------------------------------------------------------------------
def format_response_node(state: AgentState) -> AgentState:
    question = state["messages"][-1].content
    context = state["context"]
    intent = state["intent"]

    if intent == "summarize":
        # For summaries the context IS already the answer from the LLM
        answer = context
    else:
        # For search/extract, do a final formatting pass
        prompt = (
            f"Using the following information from the document, answer the question clearly.\n\n"
            f"Document information:\n{context}\n\n"
            f"Question: {question}\n\n"
            f"Answer:"
        )
        answer = generate_answer(prompt)

    updated_messages = list(state["messages"]) + [AIMessage(content=answer)]
    return {**state, "messages": updated_messages, "answer": answer}


# ---------------------------------------------------------------------------
# Build and compile the graph (singleton)
# ---------------------------------------------------------------------------
def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify", classify_intent)
    graph.add_node("rag_search", rag_search_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("extract", extract_node)
    graph.add_node("format_response", format_response_node)

    graph.set_entry_point("classify")

    graph.add_conditional_edges(
        "classify",
        route_by_intent,
        {
            "summarize": "summarize",
            "extract": "extract",
            "search": "rag_search",
        },
    )

    graph.add_edge("rag_search", "format_response")
    graph.add_edge("summarize", "format_response")
    graph.add_edge("extract", "format_response")
    graph.add_edge("format_response", END)

    return graph.compile()


# Compile once at import time — reused across all requests
agent_graph = build_agent_graph()
