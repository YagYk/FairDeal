"""
Pydantic schemas for contract metadata extraction.
Ensures type safety and validation for LLM-extracted data with strict confidence tracking.
"""
from typing import Optional, List, Generic, TypeVar, Any, Union
from pydantic import BaseModel, Field, field_validator

T = TypeVar('T')

class ExtractedField(BaseModel, Generic[T]):
    """
    Wrapper for any extracted field to ensure auditability.
    """
    value: Optional[T] = Field(default=None, description="The extracted value")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    source_text: Optional[str] = Field(default=None, description="Exact substring from contract proving this value")
    explanation: Optional[str] = Field(default=None, description="Reasoning if value is inferred or ambiguous")
    
    class Config:
        # Allow validation of generic types
        arbitrary_types_allowed = True

class ContractMetadata(BaseModel):
    """
    Structured metadata extracted from a contract.
    All fields are now audit-ready with confidence scores.
    """
    
    contract_type: ExtractedField[str] = Field(
        description="Type of contract (e.g., 'employment', 'consulting')"
    )
    industry: ExtractedField[str] = Field(
        description="Industry sector (e.g., 'technology', 'finance')"
    )
    role: ExtractedField[Optional[str]] = Field(
        description="Job role or position"
    )
    location: ExtractedField[str] = Field(
        description="Geographic location"
    )
    salary: ExtractedField[Optional[float]] = Field(
        description="Salary amount in INR"
    )
    notice_period_days: ExtractedField[Optional[int]] = Field(
        description="Notice period in days"
    )
    non_compete: ExtractedField[bool] = Field(
        description="Whether contract contains non-compete clause"
    )
    termination_clauses: ExtractedField[List[str]] = Field(
        description="List of termination-related clauses found"
    )
    benefits: ExtractedField[List[str]] = Field(
        description="List of benefits mentioned"
    )
    risky_clauses: ExtractedField[List[str]] = Field(
        description="List of potentially risky or unfavorable clauses"
    )
    

    
    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "contract_type": {
                    "value": "employment", 
                    "confidence": 0.95, 
                    "source_text": "Employment Agreement"
                },
                "industry": {
                    "value": "technology", 
                    "confidence": 0.8, 
                    "source_text": "software development services"
                },
                "role": {
                    "value": "Software Engineer", 
                    "confidence": 0.9, 
                    "source_text": "Position: Software Engineer"
                },
                "salary": {
                    "value": 1500000.0, 
                    "confidence": 0.95, 
                    "source_text": "INR 15,00,000 per annum"
                },
                "notice_period_days": {
                    "value": 90, 
                    "confidence": 0.99, 
                    "source_text": "90 days notice"
                }
            }
        }

