import logging

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from core.config import settings
from core.sessions import get_vectordb, set_vectordb
from models.mistral_runner import generate_answer
from services.pdf_utils import extract_text_from_pdf, split_text_to_chunks

logger = logging.getLogger(__name__)

# Shared embedding model — loaded once at startup
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def embed_document(file_path: str, file_id: str) -> Chroma:
    """
    Extract text from PDF, chunk it, embed with HuggingFace, and store in
    a per-document Chroma collection identified by file_id.
    """
    text = extract_text_from_pdf(file_path)
    chunks = split_text_to_chunks(text)
    metadatas = [{"source": file_path, "chunk": i} for i in range(len(chunks))]

    vectordb = Chroma.from_texts(
        texts=chunks,
        embedding=embedding_model,
        collection_name=file_id,
        persist_directory=settings.chroma_persist_dir,
        metadatas=metadatas,
    )
    vectordb.persist()
    set_vectordb(file_id, vectordb)

    logger.info("Embedded %d chunks for file_id=%s", len(chunks), file_id)
    return vectordb


def _load_vectordb(file_id: str) -> Chroma:
    """Return the in-memory vectordb or reload it from disk."""
    vectordb = get_vectordb(file_id)
    if vectordb is None:
        vectordb = Chroma(
            collection_name=file_id,
            embedding_function=embedding_model,
            persist_directory=settings.chroma_persist_dir,
        )
        set_vectordb(file_id, vectordb)
    return vectordb


def search_document(query: str, file_id: str, k: int = 4, history: list[dict] = None) -> str:
    """
    Retrieve top-k relevant chunks and answer the question.
    Includes conversation history so follow-up questions work correctly.
    """
    vectordb = _load_vectordb(file_id)
    docs = vectordb.similarity_search(query, k=k)

    if not docs:
        return "No relevant information found in the document."

    context = "\n---\n".join(doc.page_content for doc in docs)

    # Build conversation history block for follow-up awareness
    history_block = ""
    if history:
        turns = (history or [])[-6:]  # last 6 turns max
        history_block = "Conversation so far:\n"
        for turn in turns:
            role = "User" if turn.get("role") == "user" else "Assistant"
            history_block += f"{role}: {turn.get('text', '')}\n"
        history_block += "\n"

    prompt = (
        "You are a document Q&A assistant. You have been given excerpts from a document.\n"
        "STRICT RULES:\n"
        "- Answer using ONLY the facts in the document excerpts below.\n"
        "- The document excerpts ARE the document — never say 'please provide the document'.\n"
        "- If a fact is in the excerpts, state it clearly and confidently.\n"
        "- If a fact is NOT in the excerpts, say exactly: 'This is not mentioned in the document.'\n"
        "- Never invent, guess, or use outside knowledge.\n"
        "- For follow-up questions, use the conversation history to understand context.\n\n"
        f"Document excerpts:\n{context}\n\n"
        f"{history_block}"
        f"Current question: {query}\n\n"
        "Answer:"
    )
    return generate_answer(prompt)


def get_document_summary(file_id: str) -> str:
    """Retrieve broad overview chunks and generate a summary using the local LLM."""
    vectordb = _load_vectordb(file_id)
    docs = vectordb.similarity_search(
        "main topic overview introduction conclusion key findings", k=5
    )

    if not docs:
        return "Could not generate summary — document appears to be empty."

    context = "\n---\n".join(doc.page_content for doc in docs)
    prompt = (
        "You are a document assistant. Read the excerpts below and write a clear, "
        "well-structured summary. Cover the main topic, key facts, and important details. "
        "Base the summary ONLY on the excerpts. Do not add outside knowledge.\n\n"
        f"Document excerpts:\n{context}\n\n"
        "Summary:"
    )
    return generate_answer(prompt)


def get_suggested_questions(file_id: str) -> list[str]:
    """
    Generate 4 document-specific questions from actual document content.
    Used to populate the hint pills in the chat UI.
    """
    vectordb = _load_vectordb(file_id)
    docs = vectordb.similarity_search(
        "overview main content key information summary profile", k=3
    )

    fallback = [
        "What is this document about?",
        "What are the key skills or qualifications mentioned?",
        "What experience or background is described?",
        "What are the main achievements listed?",
    ]

    if not docs:
        return fallback

    context = "\n".join(doc.page_content for doc in docs)
    prompt = (
        "Read the document excerpt below and write exactly 4 specific questions "
        "that someone reading this document would want to ask.\n"
        "Each question must be directly answerable from the document.\n"
        "Write one question per line. No numbers, no bullets, no extra text.\n\n"
        f"Document:\n{context}\n\n"
        "4 questions:"
    )

    raw = generate_answer(prompt)

    questions = []
    for line in raw.strip().split("\n"):
        line = line.strip().lstrip("-*•123456789.)").strip()
        if line and "?" in line and len(line) > 10:
            questions.append(line)
        if len(questions) == 4:
            break

    # Pad with fallbacks if the model didn't give enough
    for fb in fallback:
        if len(questions) >= 4:
            break
        questions.append(fb)

    return questions[:4]
