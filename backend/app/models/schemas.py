from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class CompanyType(str, Enum):
    service = "service"
    product = "product"
    startup = "startup"


class ExtractionMethod(str, Enum):
    regex = "regex"
    sniper_llm = "sniper_llm"
    llm_fallback = "llm_fallback"
    missing = "missing"


class ExtractedField(BaseModel):
    value: Any | None
    confidence: float = Field(ge=0, le=1)
    source_text: Optional[str] = None
    page_number: Optional[int] = None
    method: ExtractionMethod


class ClauseType(str, Enum):
    termination = "termination"
    ip = "ip"
    non_compete = "non_compete"
    confidentiality = "confidentiality"
    compensation = "compensation"
    general = "general"


class ExtractedClause(BaseModel):
    text: Optional[str] = None
    evidence: Optional[ExtractedField] = None


class ContractExtractionResult(BaseModel):
    role: Optional[ExtractedField] = None
    company_type: Optional[ExtractedField] = None
    experience_level: Optional[ExtractedField] = None
    ctc_inr: Optional[ExtractedField] = None
    notice_period_days: Optional[ExtractedField] = None
    bond_amount_inr: Optional[ExtractedField] = None
    non_compete_months: Optional[ExtractedField] = None
    probation_months: Optional[ExtractedField] = None
    benefits: List[str] = []
    benefits_count: int = 0
    extracted_clauses: Dict[str, ExtractedClause] = {}


class EvidenceChunk(BaseModel):
    contract_id: str
    chunk_id: str
    clause_type: ClauseType
    similarity: float
    text_preview: str
    metadata: Dict[str, Any] = {}


class ClauseDriftResult(BaseModel):
    clause_type: ClauseType
    similarity_to_gold: float
    status: str  # "standard" | "anomalous"
    matched_gold_clause_preview: str
    retrieved_examples: List["EvidenceChunk"] = []


class ScoreBreakdownItem(BaseModel):
    factor: str
    points: float  # Can be positive (bonus) or negative (penalty)
    reason: str
    source_text: Optional[str] = None


class Severity(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class RedFlag(BaseModel):
    id: str
    severity: Severity
    rule: str
    explanation: str
    source_text: Optional[str] = None
    impact_score: float
    market_context: Optional[str] = None
    recommendation: str


class FavorableTerm(BaseModel):
    id: str
    term: str
    explanation: str
    source_text: Optional[str] = None
    value: str
    impact_score: float
    market_context: Optional[str] = None


class NegotiationPoint(BaseModel):
    id: str
    priority: int
    topic: str
    current_term: str
    target_term: str
    rationale: str
    success_probability: str
    script: str
    fallback: Optional[str] = None
    evidence: List[str] = []


class PercentileResult(BaseModel):
    value: float
    interpretation: str  # "excellent", "above_average", "average", "below_average", "poor"
    field_value: Any
    field_display: str
    cohort_size: int
    insight: str
    market_benchmarks: Optional[Dict[str, str]] = None


class CohortInfo(BaseModel):
    filters_used: Dict[str, Any]
    filters_removed: List[str] = []
    cohort_size: int
    broaden_steps: List[str] = []
    min_n: int = 30
    confidence_note: str


class ScoreResult(BaseModel):
    overall_score: float
    grade: str  # "EXCELLENT", "GOOD", "FAIR", "POOR", "CRITICAL", "EXCEPTIONAL"
    score_confidence: float
    score_formula: str
    breakdown: List[ScoreBreakdownItem]
    # Legacy fields for backward compatibility
    safety_score: float
    market_fairness_score: float
    # New V3.0 fields
    badges: List[str] = []
    risk_factors: List[str] = []
    legal_violations: List[str] = []


class BenchmarkResult(BaseModel):
    percentile_salary: Optional[float] = None
    percentile_notice: Optional[float] = None
    cohort_size: int
    filters_used: Dict[str, Any]
    broaden_steps: List[str]
    market_mean: float
    market_median: float
    market_p25: float
    market_p75: float
    warning: Optional[str] = None
    # Enhanced fields
    notice_mean: Optional[float] = None
    notice_median: Optional[float] = None


class ContractMetadata(BaseModel):
    contract_type: Optional[str] = None
    industry: Optional[str] = None
    role_level: Optional[str] = None
    role_title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    benefits: List[str] = []
    benefits_count: int = 0


class NarrationResult(BaseModel):
    summary: str
    confidence: float
    model: str
    tokens: int


class Timings(BaseModel):
    parse_ms: float
    extract_ms: float
    benchmark_ms: float
    rag_ms: float
    scoring_ms: float = 0.0
    narration_ms: float = 0.0
    total_ms: float


class DeterminismInfo(BaseModel):
    scoring: str = "deterministic"
    extraction: str = "hybrid" # hybrid, deterministic, or stochastic
    narration: str = "non-deterministic"
class AnalyzeResponse(BaseModel):
    # Core
    extraction: ContractExtractionResult
    contract_metadata: ContractMetadata = ContractMetadata()
    
    # Scoring
    score: float
    grade: str
    scoring: ScoreResult
    
    # Percentiles
    percentiles: Dict[str, PercentileResult] = {}
    cohort: Optional[CohortInfo] = None
    
    # Intelligence
    red_flags: List[RedFlag] = []
    favorable_terms: List[FavorableTerm] = []
    negotiation_points: List[NegotiationPoint] = []
    
    # RAG Evidence
    benchmark: Optional[BenchmarkResult] = None
    rag: Dict[str, Any] = {}
    evidence: List[EvidenceChunk] = []
    
    # Narration
    narration: Optional[NarrationResult] = None
    
    # Meta
    timings: Timings
    cache: Dict[str, Any] = {}
    determinism: DeterminismInfo = DeterminismInfo() # Default to optimistic


# KB Admin Models
class KBContractMetadata(BaseModel):
    contract_id: str
    filename: str
    company_type: Optional[CompanyType] = None
    role: Optional[str] = None
    extra: Dict[str, Any] = {}


class KBStats(BaseModel):
    num_contracts: int
    num_chunks: int
    clause_type_counts: Dict[str, int]


class KBChunkPreview(BaseModel):
    contract_id: str
    chunk_id: str
    clause_type: ClauseType
    text_preview: str
    similarity: Optional[float] = None


class KBContractsResponse(BaseModel):
    contracts: List[KBContractMetadata]
    total: int
    offset: int
    limit: int
    filters_applied: Dict[str, Any] = {}


class Context(BaseModel):
    role: str
    experience_level: float = Field(..., description="Years of experience / YOE")
    company_type: CompanyType
    location: Optional[str] = "national"
    industry: Optional[str] = "tech"


# Error Handling Models
class ErrorDetail(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: Optional[List[ErrorDetail]] = None

