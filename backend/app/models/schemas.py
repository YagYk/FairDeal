"""
Comprehensive Pydantic schemas for the deterministic contract analysis system.
All extracted values include provenance (source_text, confidence, explanation).
"""
from typing import Optional, List, Generic, TypeVar, Any, Dict, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from datetime import datetime
import hashlib

T = TypeVar('T')


# ============================================================================
# ENUMS - Strict type safety
# ============================================================================

class ContractType(str, Enum):
    """Strict enum for contract types."""
    EMPLOYMENT = "employment"
    FIXED_TERM = "fixed_term"
    INTERNSHIP = "internship"
    CONSULTANCY = "consultancy"
    FREELANCE = "freelance"
    SERVICE_AGREEMENT = "service_agreement"
    NDA = "nda"
    UNKNOWN = "unknown"


class Industry(str, Enum):
    """Strict enum for industries."""
    TECH = "tech"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    RETAIL = "retail"
    EDUCATION = "education"
    LEGAL = "legal"
    CONSULTING = "consulting"
    OTHER = "other"


class RoleLevel(str, Enum):
    """Strict enum for role levels."""
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"
    UNKNOWN = "unknown"


class SalaryType(str, Enum):
    """Strict enum for salary types."""
    CTC = "ctc"
    BASE = "base"
    MONTHLY = "monthly"
    FEE = "fee"
    EQUITY = "equity"
    HOURLY = "hourly"
    UNKNOWN = "unknown"


class RedFlagSeverity(str, Enum):
    """Severity levels for red flags."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ============================================================================
# EXTRACTED FIELD - Provenance wrapper for all extracted values
# ============================================================================

class ExtractedField(BaseModel, Generic[T]):
    """
    Wrapper for any extracted field to ensure auditability and provenance.
    Every field that comes from extraction MUST include this metadata.
    """
    value: Optional[T] = Field(default=None, description="The extracted value")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    source_text: Optional[str] = Field(default=None, description="Exact substring from contract proving this value")
    explanation: Optional[str] = Field(default=None, description="Reasoning if value is inferred or ambiguous")
    
    class Config:
        arbitrary_types_allowed = True
    
    def __bool__(self) -> bool:
        """Allow truthy check on value."""
        return self.value is not None
    
    @classmethod
    def empty(cls) -> "ExtractedField":
        """Create an empty ExtractedField."""
        return cls(value=None, confidence=0.0)
    
    @classmethod
    def from_value(cls, value: T, confidence: float = 0.5, source_text: str = None) -> "ExtractedField[T]":
        """Create ExtractedField from a value with optional metadata."""
        return cls(value=value, confidence=confidence, source_text=source_text)


# ============================================================================
# CONTRACT METADATA - Full contract metadata with provenance
# ============================================================================

class ContractMetadataV2(BaseModel):
    """
    Complete contract metadata extracted from a document.
    All fields include provenance information for auditability.
    """
    # Identifiers
    contract_id: str = Field(description="UUID for this contract")
    source: Optional[str] = Field(default=None, description="Source URL or 'manual'")
    
    # Classification
    contract_type: ExtractedField[str] = Field(description="Type: employment, internship, consultancy, etc.")
    industry: ExtractedField[str] = Field(description="Industry sector")
    role_level: ExtractedField[str] = Field(description="Role level: junior, mid, senior, etc.")
    role_title: ExtractedField[Optional[str]] = Field(default=None, description="Job title")
    location: ExtractedField[Optional[str]] = Field(default=None, description="Geographic location")
    
    # Compensation
    salary_in_inr: ExtractedField[Optional[int]] = Field(default=None, description="Salary in INR")
    salary_type: ExtractedField[str] = Field(default=None, description="CTC, base, monthly, etc.")
    
    # Terms
    notice_period_days: ExtractedField[Optional[int]] = Field(default=None, description="Notice period in days")
    non_compete: ExtractedField[bool] = Field(default=None, description="Has non-compete clause")
    non_compete_duration_months: ExtractedField[Optional[int]] = Field(default=None, description="Non-compete duration")
    
    # Benefits
    benefits: ExtractedField[List[str]] = Field(default=None, description="List of benefits")
    
    # Quality metrics
    extraction_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall extraction confidence")
    processed_date: str = Field(default="", description="YYYY-MM-DD when processed")
    raw_file_path: str = Field(default="", description="Path to raw file")
    text_hash: str = Field(default="", description="SHA256 of extracted text for caching")
    
    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
    
    @classmethod
    def compute_text_hash(cls, text: str) -> str:
        """Compute SHA256 hash of text for caching."""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()


# ============================================================================
# CHUNK RECORD - Metadata stored with each chunk in ChromaDB
# ============================================================================

class ChunkRecord(BaseModel):
    """
    Metadata stored with each chunk in ChromaDB.
    Enables efficient filtering and provenance tracking.
    """
    contract_id: str
    chunk_index: int
    clause_type: str = "general"
    page_no: Optional[int] = None
    char_start: Optional[int] = None
    char_end: Optional[int] = None
    
    # Denormalized filters for efficient querying
    contract_type: Optional[str] = None
    industry: Optional[str] = None
    role_level: Optional[str] = None
    location: Optional[str] = None
    
    # Denormalized values for statistics
    salary_in_inr: Optional[int] = None
    notice_period_days: Optional[int] = None
    non_compete: Optional[bool] = None


# ============================================================================
# RED FLAG - Deterministic rule-based flag
# ============================================================================

class RedFlag(BaseModel):
    """A red flag identified by deterministic rules."""
    id: str = Field(description="Rule ID that triggered this flag")
    severity: RedFlagSeverity = Field(description="Severity level")
    rule: str = Field(description="Human-readable rule description")
    explanation: str = Field(description="Detailed explanation")
    source_text: Optional[str] = Field(default=None, description="Contract text that triggered this")
    threshold: Optional[str] = Field(default=None, description="The threshold used")
    actual_value: Optional[str] = Field(default=None, description="The actual value found")


class FavorableTerm(BaseModel):
    """A favorable term identified by deterministic rules."""
    id: str = Field(description="Rule ID")
    term: str = Field(description="Term description")
    explanation: str = Field(description="Why this is favorable")
    source_text: Optional[str] = Field(default=None, description="Contract text")
    value: Optional[str] = Field(default=None, description="The favorable value")


class NegotiationPoint(BaseModel):
    """A negotiation point generated from deterministic templates."""
    id: str = Field(description="Point ID")
    topic: str = Field(description="Negotiation topic")
    script: str = Field(description="Template script")
    reason: str = Field(description="Why negotiate this")
    priority: int = Field(default=1, ge=1, le=5, description="Priority 1-5")


# ============================================================================
# EVIDENCE - RAG retrieval result
# ============================================================================

class EvidenceChunk(BaseModel):
    """Evidence chunk retrieved from RAG."""
    contract_id: str
    chunk_index: int
    clause_type: str
    similarity: float = Field(ge=0.0, le=1.0)
    chunk_text_preview: str = Field(description="First 200 chars of chunk")
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============================================================================
# COHORT INFO - Statistics cohort details
# ============================================================================

class CohortInfo(BaseModel):
    """Information about the cohort used for percentile computation."""
    filters_used: Dict[str, str] = Field(description="Filters applied")
    cohort_size: int = Field(description="Number of contracts in cohort")
    broaden_steps: List[str] = Field(default_factory=list, description="Steps taken to broaden cohort")
    min_n: int = Field(default=30, description="Minimum cohort size target")
    confidence_note: Optional[str] = Field(default=None, description="Note if cohort is small")


class PercentileInfo(BaseModel):
    """Percentile information for a field."""
    value: Optional[float] = Field(default=None, description="The percentile 0-100")
    field_value: Optional[Any] = Field(default=None, description="The actual field value")
    cohort_size: int = Field(default=0, description="Size of cohort used")
    comparable_values_range: Optional[str] = Field(default=None, description="Range of values in cohort")


# ============================================================================
# TIMINGS - Performance metrics
# ============================================================================

class AnalysisTimings(BaseModel):
    """Timing metrics for analysis stages."""
    parse_ms: int = 0
    extract_ms: int = 0
    stats_ms: int = 0
    rag_ms: int = 0
    score_ms: int = 0
    total_ms: int = 0


# ============================================================================
# ANALYSIS RESULT - Complete API response
# ============================================================================

class AnalysisResult(BaseModel):
    """
    Complete analysis result returned by the API.
    All values are traceable and deterministically computed.
    """
    # Core scores (deterministic)
    score: int = Field(ge=0, le=100, description="Fairness score 0-100")
    score_confidence: float = Field(ge=0.0, le=1.0, description="Confidence in the score")
    score_formula: str = Field(default="", description="Formula used to compute score")
    
    # Percentiles
    percentiles: Dict[str, PercentileInfo] = Field(default_factory=dict)
    
    # Cohort info
    cohort: CohortInfo = Field(description="Cohort used for comparison")
    
    # Deterministic findings
    red_flags: List[RedFlag] = Field(default_factory=list)
    favorable_terms: List[FavorableTerm] = Field(default_factory=list)
    negotiation_points: List[NegotiationPoint] = Field(default_factory=list)
    
    # RAG evidence
    evidence: List[EvidenceChunk] = Field(default_factory=list)
    
    # Optional narration (LLM, strictly constrained)
    narration: Optional[str] = Field(default=None, description="Optional LLM narration")
    
    # Metadata
    contract_metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Performance
    timings: AnalysisTimings = Field(default_factory=AnalysisTimings)
    
    # Caching
    text_hash: str = Field(default="", description="For cache lookup")
    cached: bool = Field(default=False, description="Whether result was cached")


# ============================================================================
# KNOWLEDGE BASE STATS - For admin endpoints
# ============================================================================

class KBContractSummary(BaseModel):
    """Summary of a contract in the knowledge base."""
    contract_id: str
    contract_type: Optional[str] = None
    industry: Optional[str] = None
    role_level: Optional[str] = None
    location: Optional[str] = None
    salary_in_inr: Optional[int] = None
    notice_period_days: Optional[int] = None
    non_compete: Optional[bool] = None
    num_chunks: int = 0
    processed_date: Optional[str] = None


class KBStats(BaseModel):
    """Knowledge base statistics."""
    total_contracts: int = 0
    total_chunks: int = 0
    contracts_by_type: Dict[str, int] = Field(default_factory=dict)
    contracts_by_industry: Dict[str, int] = Field(default_factory=dict)
    contracts_by_role_level: Dict[str, int] = Field(default_factory=dict)
    cohort_counts: Dict[str, int] = Field(default_factory=dict)
    chroma_status: str = "unknown"


# ============================================================================
# GOLD SET - For evaluation
# ============================================================================

class GoldAnnotation(BaseModel):
    """Gold standard annotation for evaluation."""
    file: str = Field(description="Path to file")
    salary_in_inr: Optional[int] = None
    notice_period_days: Optional[int] = None
    non_compete: Optional[bool] = None
    contract_type: Optional[str] = None
    role_level: Optional[str] = None


class EvaluationResult(BaseModel):
    """Result of evaluation against gold set."""
    total_samples: int = 0
    salary_exact_match_pct: float = 0.0
    salary_within_5pct: float = 0.0
    notice_exact_match: float = 0.0
    non_compete_precision: float = 0.0
    non_compete_recall: float = 0.0
    non_compete_f1: float = 0.0
    confusion_examples: List[Dict[str, Any]] = Field(default_factory=list)
