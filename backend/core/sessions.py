"""
In-memory session store for per-document vector DB instances.
Each uploaded file gets a unique file_id and its own Chroma collection.
"""
from typing import Dict, Optional

from langchain_community.vectorstores import Chroma

_store: Dict[str, Chroma] = {}


def get_vectordb(file_id: str) -> Optional[Chroma]:
    return _store.get(file_id)


def set_vectordb(file_id: str, vectordb: Chroma) -> None:
    _store[file_id] = vectordb


def remove_vectordb(file_id: str) -> None:
    _store.pop(file_id, None)


def has_vectordb(file_id: str) -> bool:
    return file_id in _store
