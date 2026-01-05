from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ContractBase(BaseModel):
    title: str

class ContractCreate(ContractBase):
    pass

class ContractResponse(ContractBase):
    id: int
    filename: str
    uploaded_at: datetime
    summary: Optional[str] = None
    risk_score: Optional[int] = None

    class Config:
        from_attributes = True

class AnalysisRequest(BaseModel):
    contract_id: int
    query: Optional[str] = None
