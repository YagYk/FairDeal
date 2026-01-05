"""
Developer/debug API endpoints for transparency and monitoring.
Shows internal operations, RAG model activity, and data flow.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.auth_schema import UserResponse
from app.api.auth import get_current_user
from app.db.chroma_client import ChromaClient
from app.services.rag_service import RAGService
from app.services.stats_service import StatsService
from app.services.embedding_service import EmbeddingService
from app.config import settings
from loguru import logger
from typing import Dict, Any, List
from pathlib import Path
import json

router = APIRouter(prefix="/api/debug", tags=["debug"])


@router.get("/knowledge-base")
async def get_knowledge_base_info(
    current_user: UserResponse = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get comprehensive information about the knowledge base.
    Shows contracts, chunks, and statistics.
    """
    try:
        chroma_client = ChromaClient()
        stats = chroma_client.get_collection_stats()
        
        # Get processed contracts (use absolute path)
        processed_dir = settings.get_processed_contracts_path()
        contracts = []
        if processed_dir.exists():
            for metadata_file in processed_dir.glob("*_metadata.json"):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        contracts.append({
                            "filename": metadata_file.name,
                            "contract_id": data.get("contract_id", "unknown"),
                            "metadata": data.get("metadata", {}),
                            "num_chunks": data.get("num_chunks", 0),
                        })
                except Exception as e:
                    logger.error(f"Error reading {metadata_file}: {e}")
        
        return {
            "success": True,
            "chromadb": {
                "collection_name": stats.get("collection_name", "contracts"),
                "total_chunks": stats.get("total_chunks", 0),
            },
            "processed_contracts": {
                "count": len(contracts),
                "contracts": contracts[:20],  # First 20 for display
            },
            "raw_contracts": {
                "path": str(settings.get_raw_contracts_path()),
                "exists": settings.get_raw_contracts_path().exists(),
                "count": len(list(settings.get_raw_contracts_path().glob("*.pdf")) + 
                            list(settings.get_raw_contracts_path().glob("*.docx"))) if settings.get_raw_contracts_path().exists() else 0,
            },
        }
    except Exception as e:
        logger.error(f"Error getting knowledge base info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get knowledge base info: {str(e)}"
        )


@router.post("/test-rag")
async def test_rag_retrieval(
    query: str,
    n_results: int = 5,
    current_user: UserResponse = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Test RAG retrieval with detailed output.
    Shows embeddings, similarity scores, and retrieved chunks.
    """
    try:
        rag_service = RAGService()
        embedding_service = EmbeddingService()
        
        # Generate embedding
        logger.info(f"Generating embedding for query: {query}")
        query_embedding = embedding_service.generate_embedding(query)
        
        # Retrieve similar contracts
        logger.info(f"Retrieving similar contracts...")
        results = rag_service.retrieve_similar_contracts(
            query_text=query,
            n_results=n_results,
        )
        
        # Format detailed results
        detailed_results = []
        for result in results:
            detailed_results.append({
                "contract_id": result.get("contract_id", "unknown"),
                "similarity_score": round(result.get("similarity_score", 0) * 100, 2),
                "clause_type": result.get("clause_type", "general"),
                "text_preview": result.get("text", "")[:200] + "..." if len(result.get("text", "")) > 200 else result.get("text", ""),
                "metadata": result.get("metadata", {}),
            })
        
        return {
            "success": True,
            "query": query,
            "query_embedding_shape": list(query_embedding.shape),
            "n_results_requested": n_results,
            "n_results_returned": len(results),
            "results": detailed_results,
        }
    except Exception as e:
        logger.error(f"RAG test error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG test failed: {str(e)}"
        )


@router.get("/stats")
async def get_detailed_stats(
    contract_type: str = None,
    industry: str = None,
    field_name: str = "salary",
    current_user: UserResponse = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get detailed statistics for a field.
    Shows all values, percentiles, and calculations.
    """
    try:
        stats_service = StatsService()
        
        # Get all values
        all_values = stats_service._get_field_values(
            field_name=field_name,
            contract_type=contract_type,
            industry=industry,
        )
        
        # Get statistics
        stats = stats_service.get_market_statistics(
            field_name=field_name,
            contract_type=contract_type,
            industry=industry,
        )
        
        # Calculate percentiles for sample values
        sample_percentiles = {}
        if all_values and len(all_values) > 0:
            sorted_values = sorted(all_values)
            for value in [sorted_values[0], sorted_values[len(sorted_values)//4], 
                         sorted_values[len(sorted_values)//2], sorted_values[3*len(sorted_values)//4], sorted_values[-1]]:
                percentile = stats_service.compute_percentile(
                    value=value,
                    field_name=field_name,
                    contract_type=contract_type,
                    industry=industry,
                )
                sample_percentiles[f"value_{value}"] = percentile
        
        return {
            "success": True,
            "field_name": field_name,
            "filters": {
                "contract_type": contract_type,
                "industry": industry,
            },
            "data": {
                "total_values": len(all_values),
                "valid_values": len([v for v in all_values if v is not None and v > 0]),
                "all_values": sorted(all_values)[:50],  # First 50 sorted values
                "statistics": stats,
                "sample_percentiles": sample_percentiles,
            },
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stats failed: {str(e)}"
        )


@router.get("/analysis-pipeline")
async def get_analysis_pipeline_info(
    current_user: UserResponse = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get information about the analysis pipeline.
    Shows configuration and capabilities.
    """
    return {
        "success": True,
        "pipeline": {
            "steps": [
                "1. Parse uploaded file (PDF/DOCX with OCR support)",
                "2. Extract metadata using LLM",
                "3. Retrieve similar contracts using RAG",
                "4. Compute percentiles and statistics",
                "5. Generate insights using LLM",
                "6. Compute fairness score",
                "7. Generate detailed explanations",
            ],
            "config": {
                "llm_model": settings.llm_model,
                "embedding_model": settings.embedding_model,
                "chroma_db_path": settings.chroma_db_path,
                "raw_contracts_path": str(settings.get_raw_contracts_path()),
                "processed_contracts_path": str(settings.get_processed_contracts_path()),
            },
            "capabilities": {
                "ocr_support": True,
                "rotation_detection": True,
                "rag_retrieval": True,
                "statistical_analysis": True,
                "llm_explanations": True,
                "transparency": True,
            },
        },
    }


@router.get("/recent-analyses")
async def get_recent_analyses(
    limit: int = 5,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get recent analyses with detailed information.
    """
    from app.models.user import ContractAnalysis
    from sqlalchemy import desc
    
    try:
        analyses = db.query(ContractAnalysis).filter(
            ContractAnalysis.user_id == current_user.id
        ).order_by(desc(ContractAnalysis.created_at)).limit(limit).all()
        
        result = []
        for analysis in analyses:
            analysis_data = {
                "id": analysis.id,
                "filename": analysis.contract_filename,
                "fairness_score": analysis.fairness_score,
                "contract_type": analysis.contract_type,
                "industry": analysis.industry,
                "role": analysis.role,
                "location": analysis.location,
                "salary": analysis.salary,
                "notice_period_days": analysis.notice_period_days,
                "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
                "has_detailed_explanation": bool(analysis.analysis_result_json),
            }
            
            # Try to extract similar contracts count from JSON
            if analysis.analysis_result_json:
                try:
                    result_data = json.loads(analysis.analysis_result_json)
                    analysis_data["similar_contracts_count"] = result_data.get("similar_contracts_count", 0)
                    analysis_data["red_flags_count"] = len(result_data.get("red_flags", []))
                    analysis_data["favorable_terms_count"] = len(result_data.get("favorable_terms", []))
                except:
                    pass
            
            result.append(analysis_data)
        
        return {
            "success": True,
            "count": len(result),
            "analyses": result,
        }
    except Exception as e:
        logger.error(f"Error getting recent analyses: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recent analyses: {str(e)}"
        )


@router.get("/system-health")
async def get_system_health(
    current_user: UserResponse = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get system health and status.
    """
    try:
        # Check ChromaDB
        chroma_client = ChromaClient()
        chroma_stats = chroma_client.get_collection_stats()
        
        # Check processed contracts
        processed_dir = settings.get_processed_contracts_path()
        processed_count = len(list(processed_dir.glob("*_metadata.json"))) if processed_dir.exists() else 0
        
        # Check raw contracts
        raw_dir = settings.get_raw_contracts_path()
        raw_count = len(list(raw_dir.glob("*.pdf")) + list(raw_dir.glob("*.docx"))) if raw_dir.exists() else 0
        
        # Test embedding service
        embedding_ok = False
        try:
            embedding_service = EmbeddingService()
            test_embedding = embedding_service.generate_embedding("test")
            embedding_ok = test_embedding is not None
        except Exception as e:
            logger.error(f"Embedding test failed: {e}")
        
        return {
            "success": True,
            "status": "healthy",
            "components": {
                "chromadb": {
                    "status": "ok" if chroma_stats.get("total_chunks", 0) >= 0 else "empty",
                    "chunks": chroma_stats.get("total_chunks", 0),
                },
                "knowledge_base": {
                    "processed_contracts": processed_count,
                    "raw_contracts": raw_count,
                    "status": "ready" if processed_count > 0 else "needs_ingestion",
                },
                "embedding_service": {
                    "status": "ok" if embedding_ok else "error",
                },
                "llm_service": {
                    "model": settings.llm_model,
                    "status": "configured",
                },
            },
            "recommendations": [
                "Ingest contracts" if processed_count == 0 else "Knowledge base ready",
                "Add more contracts for better accuracy" if processed_count < 10 else "Good sample size",
            ],
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "success": False,
            "status": "error",
            "error": str(e),
        }

