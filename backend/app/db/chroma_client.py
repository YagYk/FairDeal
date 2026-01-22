from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..config import settings
from ..logging_config import get_logger


log = get_logger("chroma")

ClientAPI = Any  # avoid hard import-time dependency

_client: ClientAPI | None = None
_collection = None


def get_chroma_client() -> ClientAPI:
    global _client
    if _client is None:
        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                "ChromaDB is not available. On Windows/Python 3.12 you may need "
                "Microsoft C++ Build Tools to build chroma-hnswlib, or use Python 3.11."
            ) from exc

        persist_dir: Path = settings.chroma_dir
        persist_dir.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(allow_reset=False),
        )
        log.info(f"Initialized Chroma client at {persist_dir}")
    return _client


def get_collection():
    global _collection
    if _collection is None:
        client = get_chroma_client()
        _collection = client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        log.info(
            f"Using Chroma collection {settings.chroma_collection_name}",
        )
    return _collection


def collection_stats() -> Dict[str, Any]:
    col = get_collection()
    return {"count": col.count()}

