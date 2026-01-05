"""
User profile API endpoints.
Handles user profile data and analysis history.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.user import User, ContractAnalysis
from app.models.auth_schema import UserResponse
from app.api.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/stats")
async def get_user_stats(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get user statistics:
    - Total contracts analyzed
    - Average fairness score
    - Account status
    """
    # Count total analyses
    total_analyses = db.query(func.count(ContractAnalysis.id)).filter(
        ContractAnalysis.user_id == current_user.id
    ).scalar() or 0
    
    # Calculate average score
    avg_score = db.query(func.avg(ContractAnalysis.fairness_score)).filter(
        ContractAnalysis.user_id == current_user.id
    ).scalar()
    avg_score = int(avg_score) if avg_score else 0
    
    return {
        "total_analyses": total_analyses,
        "average_score": avg_score,
        "account_status": "Active" if current_user.is_active else "Inactive"
    }


@router.get("/analyses")
async def get_user_analyses(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 10
):
    """
    Get user's recent contract analyses.
    Returns list of analyses ordered by most recent first.
    """
    analyses = db.query(ContractAnalysis).filter(
        ContractAnalysis.user_id == current_user.id
    ).order_by(
        ContractAnalysis.created_at.desc()
    ).limit(limit).all()
    
    return [
        {
            "id": analysis.id,
            "contract_filename": analysis.contract_filename,
            "fairness_score": analysis.fairness_score,
            "contract_type": analysis.contract_type,
            "industry": analysis.industry,
            "role": analysis.role,
            "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        }
        for analysis in analyses
    ]

