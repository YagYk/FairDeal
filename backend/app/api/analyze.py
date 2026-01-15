"""
Deterministic Contract Analysis API endpoint.
Uses the new AnalysisServiceV2 for deterministic scoring.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from loguru import logger
import json

from app.db.database import get_db
from app.models.auth_schema import UserResponse
from app.api.auth import get_current_user
from app.services.analysis_service_v2 import AnalysisServiceV2
from app.models.user import ContractAnalysis


router = APIRouter(prefix="/api/v2", tags=["analysis-v2"])

# Create a singleton analysis service
_analysis_service: Optional[AnalysisServiceV2] = None


def get_analysis_service() -> AnalysisServiceV2:
    """Get or create the analysis service singleton."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisServiceV2(enable_narration=False)
    return _analysis_service


@router.post("/analyze")
async def analyze_contract_v2(
    file: UploadFile = File(...),
    enable_narration: bool = Query(False, description="Enable LLM narration (adds latency)"),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Analyze a user-uploaded contract using deterministic scoring.
    
    This endpoint uses the new deterministic analysis pipeline:
    1. Parse document locally (no LLM)
    2. Extract metadata using regex patterns
    3. Compute percentiles from knowledge base
    4. Apply rule-based red flags
    5. Calculate score using exact formula
    6. Retrieve RAG evidence for provenance
    7. Optionally generate LLM narration
    
    Target latencies:
    - Without narration: ~2-3 seconds
    - With narration: ~5-6 seconds
    
    Returns:
        Complete analysis result with:
        - score (0-100)
        - score_confidence (0-1)
        - score_formula (traceable formula)
        - percentiles with cohort info
        - red_flags with rule IDs and source text
        - favorable_terms
        - negotiation_points
        - evidence chunks from RAG
        - timing metrics
    """
    logger.info(f"V2 Analysis request from user {current_user.id} for file: {file.filename}")
    
    # Validate file type
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    suffix = file.filename.lower().split('.')[-1]
    if suffix not in ['pdf', 'docx', 'doc', 'txt']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {suffix}. Supported: PDF, DOCX, DOC, TXT"
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
    
    # Get or create analysis service with appropriate narration setting
    if enable_narration:
        analysis_service = AnalysisServiceV2(enable_narration=True)
    else:
        analysis_service = get_analysis_service()
    
    # Analyze contract
    try:
        analysis_result = analysis_service.analyze_contract(
            file_content=file_content,
            filename=file.filename,
            skip_narration=not enable_narration,
        )
        
        # Store analysis in database
        contract_metadata = analysis_result.get("contract_metadata", {})
        
        db_analysis = ContractAnalysis(
            user_id=current_user.id,
            contract_filename=file.filename,
            fairness_score=analysis_result.get("score", 0),
            contract_type=contract_metadata.get("contract_type"),
            industry=contract_metadata.get("industry"),
            role=contract_metadata.get("role_level"),
            location=contract_metadata.get("location"),
            salary=contract_metadata.get("salary_in_inr"),
            notice_period_days=contract_metadata.get("notice_period_days"),
            analysis_result_json=json.dumps(analysis_result, default=str),
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        
        logger.info(f"V2 Analysis complete. Score: {analysis_result.get('score')}")
        
        return {
            "success": True,
            "analysis_id": db_analysis.id,
            "version": "v2",
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


@router.get("/scoring-info")
async def get_scoring_info() -> Dict[str, Any]:
    """
    Get information about the deterministic scoring system.
    
    Returns:
        Documentation of the scoring formula and rules.
    """
    return {
        "version": "v2",
        "type": "deterministic",
        "formula": "S = 50 + 0.4*(P_salary - 50) + 0.3*(50 - P_notice) - 0.3*(N_flags*5) + bonuses - penalties",
        "components": {
            "base_score": 50,
            "salary_weight": 0.4,
            "notice_weight": 0.3,
            "flag_weight": 0.3,
            "flag_penalty": 5,
            "favorable_bonus": 3,
            "non_compete_penalty": 10,
        },
        "percentile_calculation": "count_below_or_equal / cohort_size * 100",
        "cohort_broadening": {
            "order": ["location", "industry", "role_level"],
            "min_n_target": 30,
            "min_n_minimum": 10,
            "always_keep": "contract_type",
        },
        "red_flag_rules": {
            "SALARY_CRITICAL_LOW": "salary < 10th percentile → critical",
            "SALARY_HIGH_LOW": "salary < 25th percentile → high",
            "NOTICE_EXCESSIVE": "notice > 90th percentile → high",
            "NOTICE_LONG": "notice > 75th percentile → medium",
            "NON_COMPETE_PRESENT": "non_compete = true → medium",
            "BENEFITS_LIMITED": "benefits_count < 3 → low",
        },
        "llm_usage": {
            "extraction": "NO - uses regex patterns",
            "scoring": "NO - uses exact formula",
            "red_flags": "NO - uses deterministic rules",
            "narration": "OPTIONAL - single constrained call, must not invent facts",
        },
        "target_latencies": {
            "deterministic_ms": 3000,
            "with_narration_ms": 6000,
        },
    }
