from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
from app.db.database import get_db
from app.models import models, schemas

router = APIRouter()

UPLOAD_DIR = "data/raw_contracts"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/contracts/upload", response_model=schemas.ContractResponse)
async def upload_contract(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    db_contract = models.Contract(
        title=title,
        filename=file.filename,
        file_path=file_path
    )
    db.add(db_contract)
    db.commit()
    db.refresh(db_contract)
    return db_contract

@router.get("/contracts", response_model=List[schemas.ContractResponse])
def read_contracts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contracts = db.query(models.Contract).offset(skip).limit(limit).all()
    return contracts

@router.get("/contracts/{contract_id}", response_model=schemas.ContractResponse)
def read_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.post("/contracts/{contract_id}/analyze")
async def analyze_contract(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    
    if not os.path.exists(contract.file_path):
        raise HTTPException(status_code=404, detail="Contract file not found on disk")
        
    try:
        # Read file content
        with open(contract.file_path, "rb") as f:
            file_content = f.read()
            
        # Initialize service (lazy load)
        from app.services.analysis_service import AnalysisService
        analysis_service = AnalysisService()
        
        # Run analysis
        result = analysis_service.analyze_contract(file_content, contract.filename)
        
        # Update DB
        import json
        contract.summary = result.get("narration", "")
        contract.risk_score = 100 - result.get("fairness_score", 50)
        # Store full result if needed, explicitly or in a separate table
        # For now, just these fields to match current model
        db.commit()
        db.refresh(contract)
        
        return {
            "message": "Analysis complete",
            "summary": contract.summary,
            "risk_score": contract.risk_score,
            "details": result # Return full details to frontend
        }
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
