from __future__ import annotations

import hashlib
import json
import time
from functools import lru_cache
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, File, UploadFile, Form, HTTPException

from ..logging_config import get_logger
from ..models.schemas import (
    AnalyzeResponse,
    Context,
    Timings,
    ExtractionMethod,
    ContractMetadata,
    PercentileResult,
    CohortInfo,
    NarrationResult,
    EvidenceChunk,
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
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Check actual size
    # We read the content to get the accurate size. 
    # Since FastAPI/Starlette UploadFile has already handled the upload, 
    # this does not incur extra network cost, just memory/disk IO.
    content = await file.read()
    file_size = len(content)
    await file.seek(0)
    
    # log.info(f"DEBUG: Calculated file size via read/len: {file_size}")
    
    if file_size > MAX_FILE_SIZE:
        log.error(f"File upload rejected: {file.filename} size {file_size} exceeds 10MB limit")
        raise HTTPException(
            status_code=413, 
            detail=f"File too large ({file_size} bytes). Maximum allowed is 10MB."
        )
    
    try:
        try:
            ctx_dict: Dict[str, Any] = json.loads(context)
            ctx = Context(**ctx_dict)
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Invalid context JSON: {exc}")

        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Empty file")

        file_hash = _get_file_hash(content)
        
        # Initialize services (using singletons for heavy services)
        parser = ParserService()  # Lightweight, per-request is fine
        rule_extractor = RuleExtractionService()  # Lightweight
        llm = get_llm_service()  # SINGLETON: avoids re-init
        sniper = SniperExtractionService(llm)
        benchmarker = get_benchmark_service()  # SINGLETON: market data loaded once
        scorer = PsychologicalScoringEngine()  # Lightweight
        rag = get_rag_service()  # SINGLETON: ChromaDB + embedders loaded once
        evidence_service = EvidenceService(rag)
        red_flag_service = RedFlagService()  # Lightweight
        negotiation_service = NegotiationService()  # Lightweight
        cache_service = CacheService()  # Lightweight

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
        
        # Only call LLM if SALARY is missing (the most critical field)
        # Other fields (bond, probation, non_compete) are optional and shouldn't waste API quota
        salary_missing = not (extraction.ctc_inr and extraction.ctc_inr.value)
        
        if salary_missing:
            log.info("Salary missing after regex. Using LLM extraction for comprehensive analysis...")
            
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

        t_extract = time.perf_counter() - t0

        # Build contract metadata using final extraction results
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
        else:
            log.warning("Salary extraction failed - skipping benchmarking and using fallback scoring defaults.")
            
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
                    min_n=30,
                    confidence_note=f"Cohort size ({benchmark.cohort_size}) {'exceeds' if benchmark.cohort_size >= 30 else 'below'} minimum threshold."
                )
        
        # Compute notice percentile
        if notice:
            notice_percentile = benchmarker.compute_notice_percentile(
                notice_days=int(notice),
                company_type=ctx.company_type.value
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
        # Defaulting to 24 months for bond if present but duration unknown (standard assumption)
        training_bond_months = 24 if training_bond else 0
        
        # Defaults for fields not yet in ContractExtractionResult
        # TODO: Update extraction to capture these explicitly
        has_provident_fund = False
        mentions_gratuity = False
        
        # Simple keyword search fallback for immediate "un-vagueing"
        full_text_lower = " ".join([b.lower() for b in extraction.benefits]).lower() # Search in benefits first

        for b in extraction.benefits:
            b_lower = b.lower()
            if "provident" in b_lower or "pf" in b_lower:
                has_provident_fund = True
            if "gratuity" in b_lower:
                mentions_gratuity = True
                
        # Sanitize numeric fields - extraction might return strings like "18,00,000"
        def _sanitize(val: Any) -> float:
            if val is None: return 0.0
            if isinstance(val, (int, float)): return float(val)
            if isinstance(val, str):
                clean = val.replace(',', '').replace('_', '').strip()
                # Handle "18 Lakhs" etc simply by taking first number? 
                # Assuming RuleExtractionService returns digits + punctuation mostly
                try:
                    return float(clean)
                except ValueError:
                    return 0.0
            return 0.0

        salary_val = _sanitize(salary)
        notice_val = _sanitize(notice)
        bond_val = _sanitize(extraction.bond_amount_inr.value if extraction.bond_amount_inr else 0)

        try:
            psych_result = scorer.compute_score(
                salary_percentile=benchmark.percentile_salary if benchmark else None,
                notice_percentile=notice_percentile, # Using the computed notice percentile
                benefits_count=extraction.benefits_count,
                benefits_list=extraction.benefits,
                non_compete=bool(extraction.non_compete_months and extraction.non_compete_months.value),
                non_compete_months=int(_sanitize(extraction.non_compete_months.value)) if extraction.non_compete_months else 0,
                role_level="entry" if ctx.experience_level <= 2 else "senior" if ctx.experience_level > 5 else "mid",
                industry=ctx.industry,
                # Kwargs for additional context
                salary_in_inr=salary_val,
                notice_period_days=notice_val,
                training_bond=training_bond,
                training_bond_amount=bond_val,
                training_bond_months=training_bond_months,
                has_provident_fund=has_provident_fund,
                mentions_gratuity=mentions_gratuity,
                # Defaults for others
                garden_leave=False, 
                probation_months=(extraction.probation_months.value or 0) if extraction.probation_months else 0,
                termination_without_cause=False,
                unlimited_deductions=False,
                working_hours_per_week=40, # Assume standard
                has_equity=any('equity' in b.lower() or 'esop' in b.lower() for b in extraction.benefits),
                has_legal_violations=False # Will be re-calculated inside, but we can hint if we found RedFlags in stage 4? 
                # Actually scorer calculates its own legal score now.
            )
        except Exception as e:
            print(f"CRITICAL ERROR IN SCORER: {e}")
            import traceback
            traceback.print_exc()
            raise e
        
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

        scoring = ScoreResult(
            overall_score=float(psych_result.score),
            grade=psych_result.grade,
            score_confidence=psych_result.confidence,
            score_formula=f"Psychological v3.0: {psych_result.score}/100",
            breakdown=breakdown_items,
            safety_score=100.0, # Deprecated but required
            market_fairness_score=float(psych_result.raw_score), # Using raw score as fairness proxy
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
        evidence_map, drift_results = evidence_service.collect_evidence_and_drift(extraction)
        
        # Flatten evidence for top-level display
        all_evidence: List[EvidenceChunk] = []
        for chunks in evidence_map.values():
            all_evidence.extend(chunks[:3])  # Top 3 from each clause type
        
        t_rag = time.perf_counter() - t0

        # ═══════════════════════════════════════════════════════
        # STAGE 8: NARRATION
        # ═══════════════════════════════════════════════════════
        t0 = time.perf_counter()
        narration_result = None
        
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
            narration_result = NarrationResult(
                summary=narration_text,
                confidence=0.88,
                model="gemini-1.5-flash",
                tokens=len(narration_text.split()) * 2  # Rough estimate
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
            rag={
                "evidence_by_clause_type": {k: [e.model_dump() for e in v] for k, v in evidence_map.items()},
                "drift_by_clause_type": [d.model_dump() for d in drift_results]
            },
            evidence=all_evidence[:10],  # Top 10 evidence chunks
            
            # Narration
            narration=narration_result,
            
            # Meta
        timings=timings,
        cache={"hit": False, "key": file_hash},
        determinism=DeterminismInfo(
            extraction="hybrid" if salary_missing else "deterministic",
            scoring="deterministic",
            narration="non-deterministic" if narration_result else "deterministic"
        )
    )

        return response
    
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"FATAL ERROR in analyze_contract: {str(e)}")
        # Return structured error directly or let global handler catch it
        # Letting global handler catch it ensures consistent formatting
        raise e


