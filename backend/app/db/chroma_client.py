from __future__ import annotations

import sys
import time
import threading
from pathlib import Path
from typing import Any, Dict

from ..config import settings
from ..logging_config import get_logger


log = get_logger("chroma")

ClientAPI = Any  # avoid hard import-time dependency

_client: ClientAPI | None = None
_collection = None
_client_lock = threading.Lock()


def get_chroma_client(max_retries: int = 3) -> ClientAPI:
    global _client
    if _client is not None:
        return _client

    with _client_lock:
        # Double-check inside lock (another thread may have initialised it)
        if _client is not None:
            return _client

        try:
            import chromadb
            from chromadb.config import Settings as ChromaSettings
        except Exception as exc:  # noqa: BLE001
            # Log the real exception so the operator can tell ImportError from
            # a DLL load failure or a chroma-hnswlib build error.
            log.error(
                "ChromaDB import failed under interpreter %s (%s): %r",
                sys.executable,
                sys.version.split()[0],
                exc,
            )
            raise RuntimeError(
                f"ChromaDB is not available under {sys.executable} "
                f"({sys.version.split()[0]}). Underlying error: {exc!r}. "
                "Install with `python -m pip install chromadb` using the same "
                "interpreter, or on Windows/Python 3.12 install Microsoft C++ "
                "Build Tools to build chroma-hnswlib."
            ) from exc

        persist_dir: Path = settings.chroma_dir
        persist_dir.mkdir(parents=True, exist_ok=True)

        last_exc: Exception | None = None
        for attempt in range(1, max_retries + 1):
            try:
                client = chromadb.PersistentClient(
                    path=str(persist_dir),
                    settings=ChromaSettings(allow_reset=False),
                )
                _client = client
                log.info(f"Initialized Chroma client at {persist_dir} (attempt {attempt})")
                return _client
            except Exception as exc:
                last_exc = exc
                log.warning(f"Chroma init attempt {attempt}/{max_retries} failed: {exc}")
                if attempt < max_retries:
                    time.sleep(0.5 * attempt)  # back off before retry

        raise RuntimeError(
            f"Failed to initialise ChromaDB after {max_retries} attempts: {last_exc}"
        ) from last_exc


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

