"""
Knowledge Base Admin API endpoints.

Provides visibility into the ingested knowledge base:
- GET /kb/contracts - List ingested contracts with metadata
- GET /kb/contracts/{id} - Full metadata for a contract
- GET /kb/contracts/{id}/chunks - Chunk previews and metadata
- GET /kb/stats - Available cohorts and counts
- GET /kb/health - ChromaDB status
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List, Optional
from loguru import logger
import json
from pathlib import Path

from app.config import settings
from app.db.chroma_client import ChromaClient
from app.models.schemas import KBContractSummary, KBStats

router = APIRouter(prefix="/api/kb", tags=["knowledge-base"])


def get_chroma_client() -> ChromaClient:
    """Dependency to get ChromaDB client."""
    return ChromaClient()


@router.get("/contracts", response_model=Dict[str, Any])
async def list_contracts(
    contract_type: Optional[str] = Query(None, description="Filter by contract type"),
    industry: Optional[str] = Query(None, description="Filter by industry"),
    role_level: Optional[str] = Query(None, description="Filter by role level"),
    location: Optional[str] = Query(None, description="Filter by location"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
) -> Dict[str, Any]:
    """
    List ingested contracts with metadata.
    Returns contract summaries without raw text.
    """
    logger.info(f"Listing contracts: type={contract_type}, industry={industry}, limit={limit}")
    
    # Load from processed metadata files
    processed_dir = settings.get_processed_contracts_path()
    
    if not processed_dir.exists():
        return {
            "contracts": [],
            "total": 0,
            "offset": offset,
            "limit": limit,
            "filters_applied": {},
        }
    
    contracts = []
    filters_applied = {}
    
    for metadata_file in processed_dir.glob("*_metadata.json"):
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Get metadata (handle both old and new formats)
            meta = data.get("contract_metadata") or data.get("metadata", {})
            
            # Helper to extract value
            def get_val(field):
                if isinstance(field, dict):
                    return field.get("value")
                return field
            
            # Apply filters
            ct = get_val(meta.get("contract_type")) or ""
            if contract_type and ct.lower() != contract_type.lower():
                continue
            
            ind = get_val(meta.get("industry")) or ""
            if industry and ind.lower() != industry.lower():
                continue
            
            rl = get_val(meta.get("role_level")) or get_val(meta.get("role")) or ""
            if role_level and rl.lower() != role_level.lower():
                continue
            
            loc = get_val(meta.get("location")) or ""
            if location and loc.lower() != location.lower():
                continue
            
            # Build summary
            summary = KBContractSummary(
                contract_id=data.get("contract_id", metadata_file.stem.replace("_metadata", "")),
                contract_type=ct,
                industry=ind,
                role_level=rl,
                location=loc,
                salary_in_inr=get_val(meta.get("salary_in_inr")) or get_val(meta.get("salary")),
                notice_period_days=get_val(meta.get("notice_period_days")),
                non_compete=get_val(meta.get("non_compete")),
                num_chunks=data.get("num_chunks", 0),
                processed_date=data.get("processed_date") or meta.get("processed_date"),
            )
            
            contracts.append(summary)
            
        except Exception as e:
            logger.warning(f"Error reading {metadata_file}: {e}")
            continue
    
    # Track filters
    if contract_type:
        filters_applied["contract_type"] = contract_type
    if industry:
        filters_applied["industry"] = industry
    if role_level:
        filters_applied["role_level"] = role_level
    if location:
        filters_applied["location"] = location
    
    # Apply pagination
    total = len(contracts)
    contracts = contracts[offset:offset + limit]
    
    return {
        "contracts": [c.model_dump() for c in contracts],
        "total": total,
        "offset": offset,
        "limit": limit,
        "filters_applied": filters_applied,
    }


@router.get("/contracts/{contract_id}", response_model=Dict[str, Any])
async def get_contract(contract_id: str) -> Dict[str, Any]:
    """
    Get full metadata for a specific contract.
    """
    logger.info(f"Getting contract: {contract_id}")
    
    processed_dir = settings.get_processed_contracts_path()
    metadata_file = processed_dir / f"{contract_id}_metadata.json"
    
    if not metadata_file.exists():
        raise HTTPException(status_code=404, detail=f"Contract not found: {contract_id}")
    
    try:
        with open(metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        return {
            "contract_id": contract_id,
            "metadata": data.get("contract_metadata") or data.get("metadata", {}),
            "num_chunks": data.get("num_chunks", 0),
            "text_hash": data.get("text_hash"),
            "processed_date": data.get("processed_date"),
        }
    except Exception as e:
        logger.error(f"Error reading contract {contract_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading contract: {e}")


@router.get("/contracts/{contract_id}/chunks", response_model=Dict[str, Any])
async def get_contract_chunks(
    contract_id: str,
    chroma_client: ChromaClient = Depends(get_chroma_client),
) -> Dict[str, Any]:
    """
    Get chunk previews and metadata for a contract.
    """
    logger.info(f"Getting chunks for contract: {contract_id}")
    
    try:
        # Query ChromaDB for chunks belonging to this contract
        results = chroma_client.collection.get(
            where={"contract_id": {"$eq": contract_id}},
            include=["documents", "metadatas"],
            limit=100,
        )
        
        chunks = []
        ids = results.get("ids", [])
        documents = results.get("documents", [])
        metadatas = results.get("metadatas", [])
        
        for i in range(len(ids)):
            chunk_text = documents[i] if documents else ""
            chunk_meta = metadatas[i] if metadatas else {}
            
            chunks.append({
                "id": ids[i],
                "preview": chunk_text[:200] + "..." if len(chunk_text) > 200 else chunk_text,
                "chunk_index": chunk_meta.get("chunk_index", i),
                "clause_type": chunk_meta.get("clause_type", "general"),
                "char_count": len(chunk_text),
            })
        
        # Sort by chunk index
        chunks.sort(key=lambda x: x.get("chunk_index", 0))
        
        return {
            "contract_id": contract_id,
            "total_chunks": len(chunks),
            "chunks": chunks,
        }
    
    except Exception as e:
        logger.error(f"Error getting chunks for {contract_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving chunks: {e}")


@router.get("/stats", response_model=Dict[str, Any])
async def get_kb_stats(
    chroma_client: ChromaClient = Depends(get_chroma_client),
) -> Dict[str, Any]:
    """
    Get knowledge base statistics.
    Shows available cohorts and counts for each.
    """
    logger.info("Getting KB stats")
    
    # Get ChromaDB stats
    try:
        chroma_stats = chroma_client.get_collection_stats()
    except Exception as e:
        chroma_stats = {"error": str(e)}
    
    # Load contract metadata and compute stats
    processed_dir = settings.get_processed_contracts_path()
    
    stats = KBStats(
        total_contracts=0,
        total_chunks=chroma_stats.get("total_chunks", 0),
        chroma_status="healthy" if "error" not in chroma_stats else "error",
    )
    
    type_counts: Dict[str, int] = {}
    industry_counts: Dict[str, int] = {}
    role_counts: Dict[str, int] = {}
    
    if processed_dir.exists():
        for metadata_file in processed_dir.glob("*_metadata.json"):
            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                stats.total_contracts += 1
                
                meta = data.get("contract_metadata") or data.get("metadata", {})
                
                # Helper to extract value
                def get_val(field):
                    if isinstance(field, dict):
                        return field.get("value")
                    return field
                
                ct = get_val(meta.get("contract_type")) or "unknown"
                type_counts[ct] = type_counts.get(ct, 0) + 1
                
                ind = get_val(meta.get("industry")) or "unknown"
                industry_counts[ind] = industry_counts.get(ind, 0) + 1
                
                rl = get_val(meta.get("role_level")) or get_val(meta.get("role")) or "unknown"
                role_counts[rl] = role_counts.get(rl, 0) + 1
                
            except Exception:
                continue
    
    stats.contracts_by_type = type_counts
    stats.contracts_by_industry = industry_counts
    stats.contracts_by_role_level = role_counts
    
    # Compute cohort counts (combinations)
    cohort_counts = {}
    for ct, ct_count in type_counts.items():
        cohort_counts[f"type:{ct}"] = ct_count
    for ind, ind_count in industry_counts.items():
        cohort_counts[f"industry:{ind}"] = ind_count
    
    stats.cohort_counts = cohort_counts
    
    return {
        "stats": stats.model_dump(),
        "chroma": chroma_stats,
    }


@router.get("/health", response_model=Dict[str, Any])
async def check_kb_health(
    chroma_client: ChromaClient = Depends(get_chroma_client),
) -> Dict[str, Any]:
    """
    Health check for the knowledge base.
    Returns ChromaDB status, collection info, and counts.
    """
    logger.info("Checking KB health")
    
    health = {
        "status": "healthy",
        "chroma": {},
        "metadata_dir": {},
        "issues": [],
    }
    
    # Check ChromaDB
    try:
        chroma_stats = chroma_client.get_collection_stats()
        health["chroma"] = {
            "status": "connected",
            "collection_name": chroma_stats.get("collection_name"),
            "total_chunks": chroma_stats.get("total_chunks", 0),
        }
    except Exception as e:
        health["chroma"] = {
            "status": "error",
            "error": str(e),
        }
        health["status"] = "degraded"
        health["issues"].append(f"ChromaDB error: {e}")
    
    # Check metadata directory
    processed_dir = settings.get_processed_contracts_path()
    if processed_dir.exists():
        metadata_files = list(processed_dir.glob("*_metadata.json"))
        health["metadata_dir"] = {
            "status": "accessible",
            "path": str(processed_dir),
            "file_count": len(metadata_files),
        }
    else:
        health["metadata_dir"] = {
            "status": "not_found",
            "path": str(processed_dir),
            "file_count": 0,
        }
        health["issues"].append(f"Metadata directory not found: {processed_dir}")
    
    # Check consistency
    chroma_chunks = health["chroma"].get("total_chunks", 0)
    metadata_count = health["metadata_dir"].get("file_count", 0)
    
    if chroma_chunks == 0 and metadata_count == 0:
        health["issues"].append("Knowledge base is empty - run ingestion first")
    elif chroma_chunks == 0 and metadata_count > 0:
        health["issues"].append("Metadata exists but ChromaDB is empty - re-run ingestion")
    
    if health["issues"]:
        health["status"] = "warning" if health["status"] == "healthy" else health["status"]
    
    return health


@router.delete("/contracts/{contract_id}", response_model=Dict[str, Any])
async def delete_contract(
    contract_id: str,
    chroma_client: ChromaClient = Depends(get_chroma_client),
) -> Dict[str, Any]:
    """
    Delete a contract from the knowledge base.
    Removes both metadata file and ChromaDB chunks.
    """
    logger.info(f"Deleting contract: {contract_id}")
    
    deleted = {
        "contract_id": contract_id,
        "metadata_deleted": False,
        "chunks_deleted": 0,
    }
    
    # Delete metadata file
    processed_dir = settings.get_processed_contracts_path()
    metadata_file = processed_dir / f"{contract_id}_metadata.json"
    
    if metadata_file.exists():
        try:
            metadata_file.unlink()
            deleted["metadata_deleted"] = True
        except Exception as e:
            logger.error(f"Failed to delete metadata file: {e}")
    
    # Delete ChromaDB chunks
    try:
        # Get chunk IDs for this contract
        results = chroma_client.collection.get(
            where={"contract_id": {"$eq": contract_id}},
            include=[],
        )
        
        chunk_ids = results.get("ids", [])
        
        if chunk_ids:
            chroma_client.collection.delete(ids=chunk_ids)
            deleted["chunks_deleted"] = len(chunk_ids)
            
    except Exception as e:
        logger.error(f"Failed to delete ChromaDB chunks: {e}")
    
    return deleted
