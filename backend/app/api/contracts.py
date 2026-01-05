"""
Contract analysis API endpoints.
Handles file upload, analysis, and ingestion.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.models.auth_schema import UserResponse
from app.api.auth import get_current_user
from app.services.analysis_service import AnalysisService
from app.services.ingestion_service import IngestionService
from app.services.chatbot_service import ChatbotService
from app.models.user import ContractAnalysis
from loguru import logger
from typing import Dict, Any
import json

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

analysis_service = AnalysisService()
ingestion_service = IngestionService()
chatbot_service = ChatbotService()


class ChatRequest(BaseModel):
    """Request model for chatbot endpoint."""
    question: str
    analysis_id: str


@router.post("/analyze")
async def analyze_contract(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Analyze a user-uploaded contract.
    
    Steps:
    1. Parse uploaded file
    2. Extract metadata using LLM
    3. Retrieve similar contracts using RAG
    4. Compute percentiles and statistics
    5. Generate insights and negotiation scripts
    6. Store analysis result in database
    
    Returns:
        Complete analysis result with fairness score, insights, etc.
    """
    logger.info(f"Analysis request from user {current_user.id} for file: {file.filename}")
    
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    suffix = file.filename.lower().split('.')[-1]
    if suffix not in ['pdf', 'docx', 'doc']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {suffix}. Supported: PDF, DOCX, DOC"
        )
    
    # Read file content
    try:
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file"
            )
        
        # Limit file size (10MB)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large. Maximum size: 10MB"
            )
        
        logger.info(f"File size: {len(file_content)} bytes")
        
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Analyze contract
    try:
        analysis_result = analysis_service.analyze_contract(
            file_content=file_content,
            filename=file.filename,
        )
        
        # Store analysis in database
        contract_metadata = analysis_result.get("contract_metadata", {})
        
        # Helper to safely extract value from ExtractedField
        def extract_value(field):
            """Extract actual value from ExtractedField dict or object."""
            if field is None:
                return None
            # If it's a dict (ExtractedField serialized)
            if isinstance(field, dict):
                val = field.get("value")
                # Handle nested dicts
                while isinstance(val, dict) and "value" in val:
                    val = val.get("value")
                return val
            # If it's an object with .value attribute
            if hasattr(field, 'value'):
                val = field.value
                while isinstance(val, dict) and "value" in val:
                    val = val.get("value")
                return val
            return field
        
        # Extract values safely
        salary_val = extract_value(contract_metadata.get("salary"))
        notice_period_val = extract_value(contract_metadata.get("notice_period_days"))
        contract_type_val = extract_value(contract_metadata.get("contract_type"))
        industry_val = extract_value(contract_metadata.get("industry"))
        role_val = extract_value(contract_metadata.get("role"))
        location_val = extract_value(contract_metadata.get("location"))
        
        # Convert salary to int safely
        salary_int = None
        if salary_val is not None:
            try:
                if isinstance(salary_val, (int, float)):
                    salary_int = int(salary_val)
                elif isinstance(salary_val, str) and salary_val.replace('.', '', 1).isdigit():
                    salary_int = int(float(salary_val))
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not convert salary to int: {salary_val}, error: {e}")
                salary_int = None
        
        # Convert notice_period_days to int safely
        notice_period_int = None
        if notice_period_val is not None:
            try:
                if isinstance(notice_period_val, (int, float)):
                    notice_period_int = int(notice_period_val)
                elif isinstance(notice_period_val, str) and notice_period_val.isdigit():
                    notice_period_int = int(notice_period_val)
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not convert notice_period_days to int: {notice_period_val}, error: {e}")
                notice_period_int = None
        
        db_analysis = ContractAnalysis(
            user_id=current_user.id,
            contract_filename=file.filename,
            fairness_score=analysis_result.get("fairness_score", 0),
            contract_type=str(contract_type_val) if contract_type_val else None,
            industry=str(industry_val) if industry_val else None,
            role=str(role_val) if role_val else None,
            location=str(location_val) if location_val else None,
            salary=salary_int,
            notice_period_days=notice_period_int,
            analysis_result_json=json.dumps(analysis_result),  # Store full result as JSON
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        logger.info(f"Analysis complete. Score: {analysis_result.get('fairness_score')}")
        
        return {
            "success": True,
            "analysis_id": db_analysis.id,
            **analysis_result,
        }
        
    except ValueError as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis failed: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.post("/ingest")
async def ingest_contracts(
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Ingest a contract into the knowledge base.
    
    This endpoint is for adding contracts to the RAG database.
    Typically used by admins to build the knowledge base.
    
    Steps:
    1. Parse file
    2. Extract metadata
    3. Chunk text
    4. Generate embeddings
    5. Store in ChromaDB
    
    Returns:
        Ingestion result with contract ID and status
    """
    logger.info(f"Ingestion request from user {current_user.id} for file: {file.filename}")
    
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    suffix = file.filename.lower().split('.')[-1]
    if suffix not in ['pdf', 'docx', 'doc']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {suffix}"
        )
    
    # Read file content
    try:
        file_content = await file.read()
        
        # Save to temporary file for ingestion
        from pathlib import Path
        import tempfile
        import os
        
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        try:
            # Ingest contract
            result = ingestion_service.ingest_contract(Path(tmp_path))
            
            logger.info(f"Ingestion complete: {result.get('contract_id')}")
            
            return {
                "success": True,
                **result,
            }
        finally:
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ingestion failed: {str(e)}"
        )


@router.post("/chat")
async def chat_about_analysis(
    request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Chat with AI about a specific contract analysis.
    
    Args:
        request: Chat request with question and analysis_id
        
    Returns:
        Chatbot response
    """
    logger.info(f"Chat request from user {current_user.id} for analysis {request.analysis_id}")
    
    # Get analysis from database
    analysis = db.query(ContractAnalysis).filter(
        ContractAnalysis.id == request.analysis_id,
        ContractAnalysis.user_id == current_user.id,  # Ensure user owns this analysis
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Load analysis result from JSON
    if not analysis.analysis_result_json:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis result not available"
        )
    
    try:
        analysis_data = json.loads(analysis.analysis_result_json)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse analysis data"
        )
    
    # Generate chatbot response
    try:
        response = chatbot_service.generate_response(
            question=request.question,
            analysis_data=analysis_data,
        )
        
        return {
            "success": True,
            "response": response,
            "analysis_id": request.analysis_id,
        }
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )


@router.get("/stats")
async def get_knowledge_base_stats(
    current_user: UserResponse = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get statistics about the knowledge base.
    
    Returns:
        Statistics about contracts in the database
    """
    from app.db.chroma_client import ChromaClient
    
    try:
        chroma_client = ChromaClient()
        stats = chroma_client.get_collection_stats()
        
        return {
            "success": True,
            **stats,
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

