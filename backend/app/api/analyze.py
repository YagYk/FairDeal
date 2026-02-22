from __future__ import annotations

import hashlib
import json
import math
import re
import time
import traceback
from functools import lru_cache
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, File, UploadFile, Form, HTTPException

from ..logging_config import get_logger
from ..models.schemas import (
    AnalyzeResponse,
    CacheInfo,
    Context,
    Timings,
    ExtractionMethod,
    ContractMetadata,
    PercentileResult,
    CohortInfo,
    NarrationResult,
    EvidenceChunk,
    ClauseDriftResult,
    RAGResult,
    ScoreResult,
    ScoreBreakdownItem,
    DeterminismInfo,
)
from ..services.parser_service import ParserService
from ..services.rule_extraction_service import RuleExtractionService
from ..services.sniper_extraction_service import SniperExtractionService
from ..services.psychological_scoring import PsychologicalScoringEngine
from ..services.benchmark_service import BenchmarkService
from ..services.rag_service import RAGService
from ..services.evidence_service import EvidenceService
from ..services.llm_service import LLMService
from ..services.cache_service import CacheService
from ..services.red_flag_service import RedFlagService
from ..services.negotiation_service import NegotiationService


router = APIRouter(tags=["analyze"])
log = get_logger("api.analyze")


# ═══════════════════════════════════════════════════════════════════════════
# SINGLETON SERVICE FACTORIES - Avoid reinitializing heavy services per request
# ═══════════════════════════════════════════════════════════════════════════

@lru_cache(maxsize=1)
def get_benchmark_service() -> BenchmarkService:
    """Cached BenchmarkService - loads market data once."""
    log.info("Initializing BenchmarkService (singleton)")
    return BenchmarkService()

@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """Cached RAGService - initializes ChromaDB and embedders once."""
    log.info("Initializing RAGService (singleton)")
    return RAGService()

@lru_cache(maxsize=1)
def get_llm_service() -> LLMService:
    """Cached LLMService."""
    log.info("Initializing LLMService (singleton)")
    return LLMService()

def clear_service_caches():
    """Clear all service caches - useful for testing or after code changes."""
    get_benchmark_service.cache_clear()
    get_rag_service.cache_clear()
    get_llm_service.cache_clear()

def _get_file_hash(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()[:16]


def _interpret_percentile(value: float, lower_is_better: bool = False) -> str:
    """Convert percentile to human-readable interpretation."""
    if lower_is_better:
        if value <= 20:
            return "excellent"
        elif value <= 40:
            return "above_average"
        elif value <= 60:
            return "average"
        elif value <= 80:
            return "below_average"
        else:
            return "poor"
    else:
        if value >= 80:
            return "excellent"
        elif value >= 60:
            return "above_average"
        elif value >= 40:
            return "average"
        elif value >= 20:
            return "below_average"
        else:
            return "poor"


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_contract(
    file: UploadFile = File(...),
    context: str = Form(..., description="JSON string with role, experience_level, company_type"),
) -> AnalyzeResponse:
    """
    Analyze a contract PDF/DOCX and return comprehensive intelligence:
    - Deterministic scores with full formula transparency
    - Red flags with severity and recommendations
    - Favorable terms
    - Negotiation playbook with email scripts
    - RAG evidence from similar contracts
    - Optional AI narration
    """
    t_start = time.perf_counter()
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    try:
        try:
            ctx_dict: Dict[str, Any] = json.loads(context)
            ctx = Context(**ctx_dict)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid context JSON: {exc}")

        # Read file content once
        content = await file.read()
        file_size = len(content)
        
        # Check file size
        if file_size > MAX_FILE_SIZE:
            log.error(f"File upload rejected: {file.filename} size {file_size} exceeds 10MB limit")
            raise HTTPException(
                status_code=413, 
                detail=f"File too large ({file_size} bytes). Maximum allowed is 10MB."
            )
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")

        file_hash = _get_file_hash(content)
        
        # Build context-aware cache key: same file + different context = different analysis
        context_suffix = f"_{ctx.role}_{ctx.experience_level}_{ctx.company_type.value}"
        cache_key = file_hash + hashlib.sha256(context_suffix.encode()).hexdigest()[:8]
        
        # Initialize services (using singletons for heavy services)
        cache_service = CacheService()  # Lightweight

        # ═══════════════════════════════════════════════════════
        # CACHE CHECK: Return cached result if available
        # ═══════════════════════════════════════════════════════
        cached = cache_service.get(cache_key)
        if cached is not None:
            log.info(f"Cache HIT for cache_key={cache_key}")
            cached.cache = CacheInfo(hit=True, key=cache_key)
            return cached

        log.info(f"Cache MISS for cache_key={cache_key} - running full pipeline")

        parser = ParserService()  # Lightweight, per-request is fine
        rule_extractor = RuleExtractionService()  # Lightweight
        llm = get_llm_service()  # SINGLETON: avoids re-init
        sniper = SniperExtractionService(llm)
        benchmarker = get_benchmark_service()  # SINGLETON: market data loaded once
        scorer = PsychologicalScoringEngine()  # Lightweight
        rag = get_rag_service()  # SINGLETON: ChromaDB + embedders loaded once
        evidence_service = EvidenceService(rag)
        red_flag_service = RedFlagService(benchmarker=benchmarker)  # Share benchmarker — avoid loading market data twice
        negotiation_service = NegotiationService()  # Lightweight

        # ═══════════════════════════════════════════════════════
        # STAGE 1: PARSE (with automatic OCR for scanned PDFs)
        # ═══════════════════════════════════════════════════════
        t0 = time.perf_counter()
        # Use async parser with OCR fallback for scanned documents
        parsed = await parser.parse_with_ocr(content, filename=file.filename)
        if parsed.ocr_used:
            log.info(f"OCR was used for document extraction")
        t_parse = time.perf_counter() - t0

        # ═══════════════════════════════════════════════════════
        # STAGE 2: COMPREHENSIVE EXTRACTION (LLM-First Strategy)
        # ═══════════════════════════════════════════════════════
        t0 = time.perf_counter()
        
        # First: Try deterministic regex extraction
        extraction = rule_extractor.extract(parsed)
        log.info(f"Regex extraction results: ctc={extraction.ctc_inr.value if extraction.ctc_inr else None}, notice={extraction.notice_period_days.value if extraction.notice_period_days else None}, bond={extraction.bond_amount_inr.value if extraction.bond_amount_inr else None}, probation={extraction.probation_months.value if extraction.probation_months else None}, non_compete={extraction.non_compete_months.value if extraction.non_compete_months else None}")
        
        # Call LLM if ANY critical field is missing — extract_all extracts everything at once
        salary_missing = not (extraction.ctc_inr and extraction.ctc_inr.value)
        notice_missing = not (extraction.notice_period_days and extraction.notice_period_days.value)
        bond_missing = not (extraction.bond_amount_inr and extraction.bond_amount_inr.value is not None)
        probation_missing = not (extraction.probation_months and extraction.probation_months.value is not None)
        nc_missing = not (extraction.non_compete_months and extraction.non_compete_months.value is not None)
        
        if salary_missing or notice_missing or bond_missing or probation_missing or nc_missing:
            missing_fields = []
            if salary_missing:
                missing_fields.append("salary")
            if notice_missing:
                missing_fields.append("notice_period")
            if bond_missing:
                missing_fields.append("bond")
            if probation_missing:
                missing_fields.append("probation")
            if nc_missing:
                missing_fields.append("non_compete")
            log.info(f"Fields missing after regex: {missing_fields}. Using LLM extraction...")
            
            try:
                # Use the comprehensive extract_all method which extracts ALL fields at once
                llm_extraction = await sniper.extract_all(parsed)
                
                # Merge LLM results with regex results (LLM fills in gaps)
                if not (extraction.ctc_inr and extraction.ctc_inr.value) and llm_extraction.ctc_inr:
                    extraction.ctc_inr = llm_extraction.ctc_inr
                    log.info(f"LLM extracted salary: {extraction.ctc_inr.value}")
                
                if not (extraction.notice_period_days and extraction.notice_period_days.value) and llm_extraction.notice_period_days:
                    extraction.notice_period_days = llm_extraction.notice_period_days
                    log.info(f"LLM extracted notice: {extraction.notice_period_days.value} days")
                
                if not (extraction.bond_amount_inr and extraction.bond_amount_inr.value is not None) and llm_extraction.bond_amount_inr:
                    extraction.bond_amount_inr = llm_extraction.bond_amount_inr
                    log.info(f"LLM extracted bond: {extraction.bond_amount_inr.value}")
                
                if not (extraction.probation_months and extraction.probation_months.value is not None) and llm_extraction.probation_months:
                    extraction.probation_months = llm_extraction.probation_months
                    log.info(f"LLM extracted probation: {extraction.probation_months.value} months")
                
                if not (extraction.non_compete_months and extraction.non_compete_months.value is not None) and llm_extraction.non_compete_months:
                    extraction.non_compete_months = llm_extraction.non_compete_months
                    log.info(f"LLM extracted non-compete: {extraction.non_compete_months.value} months")
                
                if not (extraction.role and extraction.role.value) and llm_extraction.role:
                    extraction.role = llm_extraction.role
                
                if not (extraction.company_type and extraction.company_type.value) and llm_extraction.company_type:
                    extraction.company_type = llm_extraction.company_type
                    
            except Exception as exc:
                log.error(f"LLM extraction failed: {exc}")
        
        # Final extraction logging
        log.info(f"Final extraction: ctc={extraction.ctc_inr.value if extraction.ctc_inr else None}, notice={extraction.notice_period_days.value if extraction.notice_period_days else None}, bond={extraction.bond_amount_inr.value if extraction.bond_amount_inr else None}, probation={extraction.probation_months.value if extraction.probation_months else None}, non_compete={extraction.non_compete_months.value if extraction.non_compete_months else None}")

        # SANITIZATION: Ensure numeric fields are actually numbers for the UI and benchmarking
        def _sanitize_numeric(val: Any) -> float | None:
            if val is None: return None
            if isinstance(val, (int, float)):
                try:
                    f = float(val)
                    if math.isnan(f) or math.isinf(f):
                        return None
                    return f
                except (ValueError, TypeError):
                    return None
            if isinstance(val, str):
                # Handle cases like "18,00,000" or "Rs. 50000"
                clean = re.sub(r"[^\d.]", "", val)
                try:
                    f = float(clean) if clean else None
                    if f is not None and (math.isnan(f) or math.isinf(f)):
                        return None
                    return f
                except ValueError:
                    return None
            return None

        if extraction.ctc_inr and extraction.ctc_inr.value is not None:
            extraction.ctc_inr.value = _sanitize_numeric(extraction.ctc_inr.value)
        if extraction.notice_period_days and extraction.notice_period_days.value is not None:
            extraction.notice_period_days.value = _sanitize_numeric(extraction.notice_period_days.value)
        if extraction.bond_amount_inr and extraction.bond_amount_inr.value is not None:
            extraction.bond_amount_inr.value = _sanitize_numeric(extraction.bond_amount_inr.value)
        if extraction.probation_months and extraction.probation_months.value is not None:
            extraction.probation_months.value = _sanitize_numeric(extraction.probation_months.value)
        if extraction.non_compete_months and extraction.non_compete_months.value is not None:
            extraction.non_compete_months.value = _sanitize_numeric(extraction.non_compete_months.value)

        # SALARY SANITY CHECK: Catch obviously wrong values
        # Annual CTC in India ranges from ~1L (100,000) to ~10Cr (100,000,000) for most jobs
        if extraction.ctc_inr and extraction.ctc_inr.value is not None:
            sal_val = extraction.ctc_inr.value
            if sal_val < 10000:
                # Likely a monthly salary mistaken for annual, or in LPA
                if sal_val < 200:
                    # Probably in LPA (e.g., 12 means 12 LPA)
                    log.warning(f"Salary sanity: {sal_val} looks like LPA, converting to INR")
                    extraction.ctc_inr.value = sal_val * 100000
                else:
                    # Probably monthly
                    log.warning(f"Salary sanity: {sal_val} looks monthly, annualizing")
                    extraction.ctc_inr.value = sal_val * 12
            elif sal_val > 500_000_000:
                # Over 50 Crore - almost certainly garbage
                log.warning(f"Salary sanity: {sal_val} is unreasonably high, discarding")
                extraction.ctc_inr.value = None

        t_extract = time.perf_counter() - t0

        # Build contract metadata using final sanitized extraction results
        salary = extraction.ctc_inr.value if extraction.ctc_inr else None
        notice = extraction.notice_period_days.value if extraction.notice_period_days else None

        contract_metadata = ContractMetadata(
            contract_type="employment",
            industry=ctx.industry if ctx.industry else "tech",
            role_level=ctx.role,
            role_title=extraction.role.value if extraction.role and extraction.role.value else ctx.role,
            company_name=extraction.company_type.value if extraction.company_type and extraction.company_type.value else None,
            location=None,
            benefits=extraction.benefits,
            benefits_count=extraction.benefits_count
        )

        # ═══════════════════════════════════════════════════════
        # STAGE 3: BENCHMARK
        # ═══════════════════════════════════════════════════════
        t0 = time.perf_counter()
        benchmark = None
        percentiles: Dict[str, PercentileResult] = {}
        cohort_info = None
        notice_percentile = None
        
        if salary:
            # Treat "national" (default UI value) as no location constraint
            loc = ctx.location
            if loc and isinstance(loc, str) and loc.strip().lower() in {"national", "all", "any"}:
                loc = None

            benchmark = benchmarker.compare_salary(
                ctc_inr=salary,
                role=ctx.role,
                yoe=ctx.experience_level,
                company_type=ctx.company_type.value,
                location=loc,
                industry=ctx.industry
            )
            
            if benchmark and benchmark.percentile_salary is not None:
                percentiles["salary"] = PercentileResult(
                    value=benchmark.percentile_salary,
                    interpretation=_interpret_percentile(benchmark.percentile_salary),
                    field_value=salary,
                    field_display=f"₹{salary:,.0f}",
                    cohort_size=benchmark.cohort_size,
                    insight=f"Your salary is better than {benchmark.percentile_salary:.0f}% of similar contracts.",
                    market_benchmarks={
                        "p25": f"₹{benchmark.market_p25:,.0f}",
                        "p50": f"₹{benchmark.market_median:,.0f}",
                        "p75": f"₹{benchmark.market_p75:,.0f}"
                    }
                )
                
                cohort_info = CohortInfo(
                    filters_used=benchmark.filters_used,
                    filters_removed=[],
                    cohort_size=benchmark.cohort_size,
                    broaden_steps=benchmark.broaden_steps,
                    min_n=5,
                    confidence_note=f"Cohort of {benchmark.cohort_size} records ({'strong' if benchmark.cohort_size >= 30 else 'limited'} statistical confidence)."
                )
        else:
            log.warning("Salary extraction failed - skipping benchmarking and using fallback scoring defaults.")
        
        # Compute notice percentile
        if notice:
            notice_percentile = benchmarker.compute_notice_percentile(
                notice_days=int(notice),
                company_type=ctx.company_type.value,
                role=ctx.role,
                yoe=ctx.experience_level,
            )
            
            if notice_percentile is not None:
                # For notice, lower percentile means shorter notice = better
                percentiles["notice_period"] = PercentileResult(
                    value=notice_percentile,
                    interpretation=_interpret_percentile(notice_percentile, lower_is_better=True),
                    field_value=notice,
                    field_display=f"{int(notice)} days",
                    cohort_size=benchmark.cohort_size if benchmark else 0,
                    insight=f"Your notice period is SHORTER than {100 - notice_percentile:.0f}% of contracts." if notice_percentile < 50 else f"Your notice period is LONGER than {notice_percentile:.0f}% of contracts."
                )

        t_benchmark = time.perf_counter() - t0

        # ═══════════════════════════════════════════════════════
        # STAGE 4: RED FLAGS & FAVORABLE TERMS
        # ═══════════════════════════════════════════════════════
        red_flags, favorable_terms = red_flag_service.analyze(
            extraction=extraction,
            benchmark=benchmark,
            benefits_count=extraction.benefits_count,
            industry=ctx.industry,
            company_type=ctx.company_type.value,
            notice_percentile=notice_percentile,
        )

        # ═══════════════════════════════════════════════════════
        # STAGE 5: PSYCHOLOGICAL SCORING (V3.0)
        # ═══════════════════════════════════════════════════════
        t0 = time.perf_counter()
        
        # Prepare data for new engine using extracted fields or safe defaults
        # Current extraction might not capture all these details, so we default safely.
        
        # Extract training bond details if available
        training_bond = (extraction.bond_amount_inr.value is not None and extraction.bond_amount_inr.value > 0) if extraction.bond_amount_inr else False
        training_bond_amount = (extraction.bond_amount_inr.value or 0) if extraction.bond_amount_inr else 0
        # Default to 12 months for bond if present but duration unknown (reasonable mid-point)
        training_bond_months = 12 if training_bond else 0
        
        # ── Detect PF and Gratuity from both benefits list AND full contract text ──
        # Status: 'present', 'absent', or 'unknown'
        pf_found = False
        gratuity_found = False
        
        # Check benefits list first
        for b in extraction.benefits:
            b_lower = b.lower()
            if "provident" in b_lower or "pf" in b_lower or "epf" in b_lower:
                pf_found = True
            if "gratuity" in b_lower:
                gratuity_found = True
        
        # Also search the full parsed text (PF is often in salary breakdowns, not benefits)
        full_text_lower = parsed.full_text.lower() if parsed.full_text else ""
        if not pf_found and full_text_lower:
            pf_keywords = ["provident fund", "pf contribution", "epf", "employee provident", "employer pf"]
            if any(kw in full_text_lower for kw in pf_keywords):
                pf_found = True
        if not gratuity_found and full_text_lower:
            gratuity_keywords = ["gratuity", "payment of gratuity"]
            if any(kw in full_text_lower for kw in gratuity_keywords):
                gratuity_found = True
        
        # Determine status: if we searched text and didn't find it, mark as 'absent' only
        # if the text is substantial enough (>500 chars) to reasonably expect to find it
        text_is_substantial = len(full_text_lower) > 500
        pf_status = "present" if pf_found else ("absent" if text_is_substantial else "unknown")
        gratuity_status = "present" if gratuity_found else ("absent" if text_is_substantial else "unknown")
        log.info(f"PF status: {pf_status}, Gratuity status: {gratuity_status}")
                
        salary_val = (extraction.ctc_inr.value or 0.0) if extraction.ctc_inr else 0.0
        notice_val = (extraction.notice_period_days.value or 0.0) if extraction.notice_period_days else 0.0
        bond_val = (extraction.bond_amount_inr.value or 0.0) if extraction.bond_amount_inr else 0.0

        try:
            psych_result = scorer.compute_score(
                salary_percentile=benchmark.percentile_salary if benchmark else None,
                notice_percentile=notice_percentile, # Using the computed notice percentile
                benefits_count=extraction.benefits_count,
                benefits_list=extraction.benefits,
                non_compete=bool(extraction.non_compete_months and extraction.non_compete_months.value),
                non_compete_months=int(extraction.non_compete_months.value or 0) if extraction.non_compete_months else 0,
                role_level="entry" if ctx.experience_level <= 2 else "senior" if ctx.experience_level > 5 else "mid",
                industry=ctx.industry,
                # Kwargs for additional context
                salary_in_inr=salary_val,
                notice_period_days=notice_val,
                training_bond=training_bond,
                training_bond_amount=bond_val,
                training_bond_months=training_bond_months,
                pf_status=pf_status,
                gratuity_status=gratuity_status,
                # Text-based detection for clause features
                garden_leave=bool(re.search(r'garden\s*leave', full_text_lower)),
                probation_months=(extraction.probation_months.value or 0) if extraction.probation_months else 0,
                termination_without_cause=bool(re.search(r'terminat(?:e|ion)\s*(?:without\s*(?:cause|reason)|at\s*(?:its|company)\s*discretion|for\s*convenience)', full_text_lower)),
                unlimited_deductions=bool(re.search(r'(?:unlimited|uncapped|any\s*amount)\s*(?:deduction|recovery|set[- ]?off)', full_text_lower)),
                working_hours_per_week=40,  # Standard assumed unless explicitly stated
                has_equity=any('equity' in b.lower() or 'esop' in b.lower() for b in extraction.benefits),
                has_legal_violations=bool(red_flags and any(rf.severity.value == 'critical' for rf in red_flags))
            )
        except Exception as e:
            log.error(f"CRITICAL ERROR IN SCORER: {e}")
            log.error(traceback.format_exc())
            raise
        
        # Map PsychScoreResult to ScoreResult structure for response
        breakdown_items = []
        for key, val in psych_result.breakdown.items():
            # val is {"score": X, "weight": Y}
            points = val['score']
            weight = val['weight']
            # We can construct a helpful string
            breakdown_items.append(ScoreBreakdownItem(
                factor=key,
                points=float(points),
                reason=f"{key.capitalize()} Check: Scored {points:.0f}/100 (Weight: {weight*100:.0f}%)"
            ))

        # ── Compute real safety score from risk factors ──
        safety = 100.0
        # Penalise for each risk factor detected
        safety -= len(psych_result.risk_factors) * 8
        # Penalise for legal violations
        safety -= len(psych_result.legal_violations) * 12
        # Penalise for red flags by severity
        for rf in red_flags:
            if rf.severity.value == "critical":
                safety -= 12
            elif rf.severity.value == "high":
                safety -= 8
            elif rf.severity.value == "medium":
                safety -= 5
            else:
                safety -= 2
        safety = max(0.0, min(100.0, safety))

        scoring = ScoreResult(
            overall_score=float(psych_result.score),
            grade=psych_result.grade,
            score_confidence=psych_result.confidence,
            score_formula=f"Psychological v3.0: {psych_result.score}/100",
            breakdown=breakdown_items,
            safety_score=safety,
            market_fairness_score=float(psych_result.raw_score),
            badges=psych_result.badges,
            risk_factors=psych_result.risk_factors,
            legal_violations=psych_result.legal_violations
        )

        log.info(f"Psychological Score v3.0: {psych_result.score} ({psych_result.grade})")
        if psych_result.badges:
            log.info(f"Badges: {psych_result.badges}")

        t_scoring = time.perf_counter() - t0

        # ═══════════════════════════════════════════════════════
        # STAGE 6: CONTEXT-AWARE NEGOTIATION PLAYBOOK
        # ═══════════════════════════════════════════════════════
        # Determine context for negotiation based on new scoring
        negotiation_context = {
            "salary_negotiable": ctx.company_type.value != "service", # Simple check for now
            "company_type": ctx.company_type.value,
            "is_campus_hire": ctx.experience_level <= 1
        }
        negotiation_points = negotiation_service.generate_playbook(
            extraction=extraction,
            benchmark=benchmark,
            red_flags=red_flags,
            context=negotiation_context
        )

        # ═══════════════════════════════════════════════════════
        # STAGE 7: RAG EVIDENCE
        # ═══════════════════════════════════════════════════════
        t0 = time.perf_counter()
        evidence_map: Dict[str, List[EvidenceChunk]] = {}
        drift_results: List[ClauseDriftResult] = []
        all_evidence: List[EvidenceChunk] = []
        
        try:
            evidence_map, drift_results = evidence_service.collect_evidence_and_drift(extraction)
            
            # Flatten evidence for top-level display
            for chunks in evidence_map.values():
                all_evidence.extend(chunks[:3])  # Top 3 from each clause type
        except Exception as rag_error:
            log.error(f"RAG evidence collection failed (non-fatal): {rag_error}")
            log.error(f"RAG error type: {type(rag_error).__name__}")
            log.error(f"RAG traceback: {traceback.format_exc()}")
            # Continue with empty evidence - analysis can proceed without RAG
        
        t_rag = time.perf_counter() - t0

        # ═══════════════════════════════════════════════════════
        # STAGE 8: NARRATION (with deterministic fallback)
        # ═══════════════════════════════════════════════════════
        t0 = time.perf_counter()
        narration_result = None
        narration_model = "deterministic"
        
        # Try LLM narration first
        narration_text = await llm.narrate({
            "role": extraction.role.value if extraction.role and extraction.role.value else ctx.role,
            "score": scoring.overall_score,
            "grade": scoring.grade,
            "ctc": salary,
            "salary_percentile": benchmark.percentile_salary if benchmark else None,
            "notice_days": notice,
            "red_flags_count": len(red_flags),
            "favorable_count": len(favorable_terms),
            "top_red_flag": red_flags[0].rule if red_flags else None,
            "top_favorable": favorable_terms[0].term if favorable_terms else None
        })
        
        if narration_text:
            narration_model = llm.model or "gemini"
        else:
            # ── Deterministic fallback verdict ──
            log.info("LLM narration unavailable — generating deterministic verdict")
            role_name = (extraction.role.value if extraction.role and extraction.role.value else ctx.role) or "this role"
            score_val = scoring.overall_score
            grade_val = scoring.grade
            
            # Build salary context
            sal_context = ""
            if salary and benchmark and benchmark.percentile_salary is not None:
                pct = benchmark.percentile_salary
                if pct >= 75:
                    sal_context = f"The offered CTC of ₹{salary:,.0f} places you in the top quartile of comparable contracts"
                elif pct >= 40:
                    sal_context = f"The offered CTC of ₹{salary:,.0f} is within the competitive range for comparable roles"
                elif pct >= 10:
                    sal_context = f"The offered CTC of ₹{salary:,.0f} falls below the median for comparable contracts"
                else:
                    sal_context = f"The offered CTC of ₹{salary:,.0f} is significantly below market rates for similar positions"
            elif salary:
                sal_context = f"The offered CTC is ₹{salary:,.0f}"
            
            # Build risk context
            risk_context = ""
            if len(red_flags) >= 3:
                risk_context = f"with {len(red_flags)} risk factors that warrant careful review"
            elif len(red_flags) > 0:
                top_flag = red_flags[0].rule if red_flags else ""
                risk_context = f"with {len(red_flags)} flagged concern{'s' if len(red_flags) > 1 else ''} including {top_flag}"
            else:
                risk_context = "with no major risks identified"
            
            # Build favorable context
            fav_context = ""
            if len(favorable_terms) > 0:
                fav_context = f" The contract includes {len(favorable_terms)} favorable term{'s' if len(favorable_terms) > 1 else ''} working in your favor."
            
            # Build notice context
            notice_bit = ""
            if notice:
                notice_bit = f" Notice period is {int(notice)} days."
            
            # Assemble the verdict
            narration_text = f"This {role_name} offer scores {score_val:.0f}/100 ({grade_val}). {sal_context}, {risk_context}.{fav_context}{notice_bit}"
        
        narration_result = NarrationResult(
            summary=narration_text,
            confidence=0.88 if narration_model != "deterministic" else 0.95,
            model=narration_model,
            tokens=len(narration_text.split()) * 2
        )
        
        t_narration = time.perf_counter() - t0

        t_total = time.perf_counter() - t_start

        timings = Timings(
            parse_ms=t_parse * 1000,
            extract_ms=t_extract * 1000,
            benchmark_ms=t_benchmark * 1000,
            rag_ms=t_rag * 1000,
            scoring_ms=t_scoring * 1000,
            narration_ms=t_narration * 1000,
            total_ms=t_total * 1000
        )

        response = AnalyzeResponse(
            # Core
            extraction=extraction,
            contract_metadata=contract_metadata,
            
            # Scoring
            score=scoring.overall_score,
            grade=scoring.grade,
            scoring=scoring,
            
            # Percentiles
            percentiles=percentiles,
            cohort=cohort_info,
            
            # Intelligence
            red_flags=red_flags,
            favorable_terms=favorable_terms,
            negotiation_points=negotiation_points,
            
            # RAG
            benchmark=benchmark,
            rag=RAGResult(
                evidence_by_clause_type={k: [e.model_dump() for e in v] for k, v in evidence_map.items()},
                drift_by_clause_type=[d.model_dump() for d in drift_results],
            ),
            evidence=all_evidence[:10],  # Top 10 evidence chunks

            # Narration
            narration=narration_result,

            # Meta
            timings=timings,
            cache=CacheInfo(hit=False, key=file_hash),
            determinism=DeterminismInfo(
                extraction="hybrid" if salary_missing else "deterministic",
                scoring="deterministic",
                narration="non-deterministic" if narration_model != "deterministic" else "deterministic"
            )
        )

        # ═══════════════════════════════════════════════════════
        # PERSIST CACHE: Store result for future identical uploads
        # ═══════════════════════════════════════════════════════
        try:
            cache_service.set(cache_key, response)
            log.info(f"Cached analysis for cache_key={cache_key}")
        except Exception as cache_err:
            log.warning(f"Failed to cache result: {cache_err}")

        return response
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"FATAL ERROR in analyze_contract: {str(e)}")
        log.error(traceback.format_exc())
        raise


