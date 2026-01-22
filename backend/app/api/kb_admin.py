from __future__ import annotations

from typing import List

from fastapi import APIRouter, Query

from ..logging_config import get_logger
from ..models.schemas import (
    KBStats,
    KBContractMetadata,
    KBContractsResponse,
    KBChunkPreview,
    ClauseType,
)
from ..services.ingestion_service import IngestionService
from ..services.rag_service import RAGService


router = APIRouter(tags=["kb"])
log = get_logger("api.kb")


@router.get("/stats", response_model=KBStats)
def get_stats() -> KBStats:
    rag = RAGService()
    return rag.get_kb_stats()


@router.get("/contracts", response_model=KBContractsResponse)
def list_contracts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> KBContractsResponse:
    rag = RAGService()
    return rag.list_contracts(limit=limit, offset=offset)


@router.get("/contracts/{contract_id}", response_model=KBContractMetadata)
def get_contract(contract_id: str) -> KBContractMetadata:
    rag = RAGService()
    return rag.get_contract(contract_id)


@router.get("/contracts/{contract_id}/chunks", response_model=List[KBChunkPreview])
def get_contract_chunks(contract_id: str) -> List[KBChunkPreview]:
    rag = RAGService()
    return rag.get_contract_chunks(contract_id)


@router.get("/health")
def health() -> dict:
    ingestion = IngestionService()
    rag = RAGService()
    return {
        "chroma_path": str(ingestion.settings.chroma_dir),
        "processed_count": ingestion.count_processed_contracts(),
        "collection_count": rag.collection_count(),
    }


@router.get("/search", response_model=List[KBChunkPreview])
def kb_search(
    query: str = Query(..., min_length=1),
    clause_type: ClauseType | None = Query(None),
    top_k: int = Query(5, ge=1, le=20),
) -> List[KBChunkPreview]:
    rag = RAGService()
    return rag.search_chunks(
        query=query,
        clause_type=clause_type,
        top_k=top_k,
    )

