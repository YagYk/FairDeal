"""
Deterministic Contract Analysis Service.

This service implements the core analysis pipeline:
1. Parse upload → extract text locally
2. Run deterministic extraction (FastExtractionService)
3. Cohort selection with broadening (StatsServiceV2)
4. Compute percentiles
5. Red flags (ClauseMatcherV2) - deterministic rules only
6. Fairness score (ScoringEngine) - exact formula
7. RAG evidence retrieval (Chroma) - for provenance only
8. Deterministic explanation builder
9. Optional LLM narration (single short call, must not invent facts)

Target latencies:
- Deterministic path (no LLM): <= 3 seconds
- With narration: <= 6 seconds
"""
import time
import hashlib
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import tempfile
import os
from loguru import logger

from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.services.fast_extraction_service import FastExtractionService
from app.services.stats_service_v2 import StatsServiceV2
from app.services.scoring_engine import ScoringEngine
from app.services.clause_matcher_v2 import ClauseMatcherV2
from app.services.rag_service import RAGService
from app.models.schemas import (
    AnalysisResult, AnalysisTimings, CohortInfo, PercentileInfo,
    RedFlag, FavorableTerm, NegotiationPoint, EvidenceChunk
)
from app.config import settings


class AnalysisServiceV2:
    """
    Deterministic-first contract analysis service.
    
    Key principles:
    1. NO LLM for scoring - purely mathematical
    2. All outputs traceable to source text
    3. RAG for evidence only, not for scoring
    4. Optional narration must not invent facts
    """
    
    def __init__(self, enable_narration: bool = False, cache_enabled: bool = True):
        """
        Initialize the analysis service.
        
        Args:
            enable_narration: Whether to enable LLM narration (adds ~3s latency)
            cache_enabled: Whether to cache analysis results by text hash
        """
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.fast_extraction = FastExtractionService()
        self.stats_service = StatsServiceV2()
        self.scoring_engine = ScoringEngine()
        self.clause_matcher = ClauseMatcherV2()
        self.rag_service = RAGService()
        
        self.enable_narration = enable_narration
        self.cache_enabled = cache_enabled
        self._analysis_cache: Dict[str, AnalysisResult] = {}
        
        # LLM service for optional narration only
        self._llm_service = None
        if enable_narration:
            try:
                from app.services.llm_service import LLMService
                self._llm_service = LLMService()
            except Exception as e:
                logger.warning(f"LLM service not available for narration: {e}")
    
    def analyze_contract(
        self,
        file_content: bytes,
        filename: str,
        skip_narration: bool = False,
    ) -> Dict[str, Any]:
        """
        Analyze a user-uploaded contract.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            skip_narration: Force skip LLM narration even if enabled
            
        Returns:
            Complete AnalysisResult as dictionary
        """
        total_start = time.time()
        timings = AnalysisTimings()
        
        logger.info(f"Starting deterministic analysis for: {filename}")
        
        # === STEP 1: Parse document ===
        step_start = time.time()
        text = self._parse_file(file_content, filename)
        
        if not text or len(text.strip()) < 100:
            raise ValueError(f"Failed to extract meaningful text from {filename}")
        
        timings.parse_ms = int((time.time() - step_start) * 1000)
        logger.info(f"Step 1 (Parse): {timings.parse_ms}ms - Extracted {len(text)} characters")
        
        # Compute text hash for caching
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        # Check cache
        if self.cache_enabled and text_hash in self._analysis_cache:
            logger.info(f"Cache hit for text_hash: {text_hash[:16]}...")
            cached_result = self._analysis_cache[text_hash]
            return self._to_dict(cached_result, cached=True)
        
        # === STEP 2: Fast extraction (deterministic) ===
        step_start = time.time()
        metadata = self.fast_extraction.extract_metadata(text)
        timings.extract_ms = int((time.time() - step_start) * 1000)
        
        # Extract values with provenance
        salary_val = self._get_val(metadata.salary)
        salary_source = self._get_source(metadata.salary)
        notice_val = self._get_val(metadata.notice_period_days)
        notice_source = self._get_source(metadata.notice_period_days)
        non_compete = self._get_val(metadata.non_compete) or False
        non_compete_source = self._get_source(metadata.non_compete)
        benefits = self._get_val(metadata.benefits) or []
        contract_type = self._get_val(metadata.contract_type) or "employment"
        industry = self._get_val(metadata.industry) or "other"
        role_level = self._get_val(metadata.role) or "mid"
        location = self._get_val(metadata.location) or "India"
        
        # Compute extraction confidence
        extraction_confidence = min(
            self._get_confidence(metadata.salary),
            self._get_confidence(metadata.notice_period_days),
            self._get_confidence(metadata.contract_type),
        )
        
        logger.info(f"Step 2 (Extract): {timings.extract_ms}ms - Type={contract_type}, Salary={salary_val}, Notice={notice_val}d")
        
        # === STEP 3: Cohort selection and percentiles ===
        step_start = time.time()
        
        salary_percentile = None
        notice_percentile = None
        cohort_info = None
        
        # Compute salary percentile with cohort broadening
        if salary_val and salary_val > 0:
            salary_pct_info, cohort_info = self.stats_service.compute_percentile_with_cohort(
                value=float(salary_val),
                field_name="salary_in_inr",
                contract_type=contract_type,
                industry=industry,
                role_level=role_level,
                location=location,
            )
            salary_percentile = salary_pct_info.value
        
        # Compute notice percentile
        if notice_val and notice_val > 0:
            notice_pct_info, notice_cohort = self.stats_service.compute_percentile_with_cohort(
                value=float(notice_val),
                field_name="notice_period_days",
                contract_type=contract_type,
                industry=industry,
                role_level=role_level,
                location=location,
            )
            notice_percentile = notice_pct_info.value
            
            # Use the cohort with more data if we don't have one yet
            if cohort_info is None or notice_cohort.cohort_size > cohort_info.cohort_size:
                cohort_info = notice_cohort
        
        # Default cohort info if none computed
        if cohort_info is None:
            cohort_info = CohortInfo(
                filters_used={"contract_type": contract_type},
                cohort_size=0,
                confidence_note="No comparable data available"
            )
        
        timings.stats_ms = int((time.time() - step_start) * 1000)
        logger.info(f"Step 3 (Stats): {timings.stats_ms}ms - Salary: {salary_percentile}%, Notice: {notice_percentile}%, Cohort: {cohort_info.cohort_size}")
        
        # === STEP 4: Red flags and favorable terms (deterministic rules) ===
        step_start = time.time()
        
        source_texts = {
            "salary": salary_source,
            "notice_period": notice_source,
            "non_compete": non_compete_source,
        }
        
        red_flags, favorable_terms, negotiation_points = self.clause_matcher.match_clauses(
            salary_percentile=salary_percentile,
            notice_percentile=notice_percentile,
            salary_value=salary_val,
            notice_value=notice_val,
            non_compete=non_compete,
            benefits=benefits,
            source_texts=source_texts,
            cohort_size=cohort_info.cohort_size,
        )
        
        match_ms = int((time.time() - step_start) * 1000)
        logger.info(f"Step 4 (Clause Match): {match_ms}ms - {len(red_flags)} flags, {len(favorable_terms)} favorable")
        
        # === STEP 5: Compute fairness score (deterministic formula) ===
        step_start = time.time()
        
        score, score_confidence, score_formula = self.scoring_engine.compute_score(
            salary_percentile=salary_percentile,
            notice_percentile=notice_percentile,
            red_flags_count=len(red_flags),
            favorable_terms_count=len(favorable_terms),
            non_compete=non_compete,
            cohort_size=cohort_info.cohort_size,
            extraction_confidence=extraction_confidence,
            benefits_count=len(benefits),
        )
        
        timings.score_ms = int((time.time() - step_start) * 1000)
        logger.info(f"Step 5 (Score): {timings.score_ms}ms - Score: {score}/100 (confidence: {score_confidence})")
        
        # === STEP 6: RAG evidence retrieval (for provenance only) ===
        step_start = time.time()
        
        evidence: List[EvidenceChunk] = []
        try:
            query_text = f"{contract_type} contract {role_level} {industry}"
            similar_chunks = self.rag_service.retrieve_similar_contracts(
                query_text=query_text,
                n_results=10,
                filters={"contract_type": contract_type} if contract_type != "unknown" else None,
            )
            
            for chunk in similar_chunks[:10]:
                evidence.append(EvidenceChunk(
                    contract_id=chunk.get("contract_id", "unknown"),
                    chunk_index=chunk.get("metadata", {}).get("chunk_index", 0),
                    clause_type=chunk.get("clause_type", "general"),
                    similarity=chunk.get("similarity_score", 0.0),
                    chunk_text_preview=chunk.get("text", "")[:200] if chunk.get("text") else "",
                    metadata=chunk.get("metadata", {}),
                ))
        except Exception as e:
            logger.warning(f"RAG retrieval failed: {e}")
        
        timings.rag_ms = int((time.time() - step_start) * 1000)
        logger.info(f"Step 6 (RAG): {timings.rag_ms}ms - Retrieved {len(evidence)} evidence chunks")
        
        # === STEP 7: Build percentile info ===
        percentiles: Dict[str, PercentileInfo] = {}
        
        if salary_percentile is not None:
            percentiles["salary"] = PercentileInfo(
                value=salary_percentile,
                field_value=salary_val,
                cohort_size=cohort_info.cohort_size,
            )
        
        if notice_percentile is not None:
            percentiles["notice_period"] = PercentileInfo(
                value=notice_percentile,
                field_value=notice_val,
                cohort_size=cohort_info.cohort_size,
            )
        
        # === STEP 8: Optional narration (LLM, strictly constrained) ===
        narration = None
        if self.enable_narration and not skip_narration and self._llm_service:
            try:
                narration = self._generate_constrained_narration(
                    score=score,
                    salary_percentile=salary_percentile,
                    notice_percentile=notice_percentile,
                    red_flags_count=len(red_flags),
                    favorable_count=len(favorable_terms),
                    cohort_size=cohort_info.cohort_size,
                    contract_type=contract_type,
                )
            except Exception as e:
                logger.warning(f"Narration generation failed: {e}")
                narration = None
        
        # Build final result
        timings.total_ms = int((time.time() - total_start) * 1000)
        
        # Contract metadata dict for response
        contract_metadata_dict = {
            "contract_type": contract_type,
            "industry": industry,
            "role_level": role_level,
            "location": location,
            "salary_in_inr": salary_val,
            "salary_source_text": salary_source,
            "notice_period_days": notice_val,
            "notice_source_text": notice_source,
            "non_compete": non_compete,
            "benefits": benefits,
            "extraction_confidence": extraction_confidence,
        }
        
        result = AnalysisResult(
            score=score,
            score_confidence=score_confidence,
            score_formula=score_formula,
            percentiles=percentiles,
            cohort=cohort_info,
            red_flags=red_flags,
            favorable_terms=favorable_terms,
            negotiation_points=negotiation_points,
            evidence=evidence,
            narration=narration,
            contract_metadata=contract_metadata_dict,
            timings=timings,
            text_hash=text_hash,
            cached=False,
        )
        
        # Cache the result
        if self.cache_enabled:
            self._analysis_cache[text_hash] = result
        
        logger.info(f"Analysis complete in {timings.total_ms}ms. Score: {score}/100")
        
        return self._to_dict(result)
    
    def _parse_file(self, file_content: bytes, filename: str) -> str:
        """Parse file content and extract text."""
        suffix = Path(filename).suffix.lower()
        
        if suffix == ".txt":
            try:
                return file_content.decode('utf-8')
            except UnicodeDecodeError:
                return file_content.decode('latin-1')
        
        # Save to temporary file for parsing
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        try:
            if suffix == ".pdf":
                text = self.pdf_parser.extract_text(Path(tmp_path))
            elif suffix in [".docx", ".doc"]:
                text = self.docx_parser.extract_text(Path(tmp_path))
            else:
                raise ValueError(f"Unsupported file type: {suffix}")
            
            return text
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _get_val(self, field) -> Any:
        """Extract value from ExtractedField or dict."""
        if field is None:
            return None
        if hasattr(field, 'value'):
            return field.value
        if isinstance(field, dict):
            return field.get('value')
        return field
    
    def _get_source(self, field) -> Optional[str]:
        """Extract source_text from ExtractedField or dict."""
        if field is None:
            return None
        if hasattr(field, 'source_text'):
            return field.source_text
        if isinstance(field, dict):
            return field.get('source_text')
        return None
    
    def _get_confidence(self, field) -> float:
        """Extract confidence from ExtractedField or dict."""
        if field is None:
            return 0.0
        if hasattr(field, 'confidence'):
            return field.confidence
        if isinstance(field, dict):
            return field.get('confidence', 0.0)
        return 0.5
    
    def _generate_constrained_narration(
        self,
        score: int,
        salary_percentile: Optional[float],
        notice_percentile: Optional[float],
        red_flags_count: int,
        favorable_count: int,
        cohort_size: int,
        contract_type: str,
    ) -> Optional[str]:
        """
        Generate LLM narration with strict constraints.
        The LLM MUST NOT invent facts - only rephrase provided data.
        """
        if not self._llm_service:
            return None
        
        # Build facts-only prompt
        facts = f"""
Score: {score}/100
Salary percentile: {salary_percentile}%
Notice percentile: {notice_percentile}%
Red flags: {red_flags_count}
Favorable terms: {favorable_count}
Cohort size: {cohort_size}
Contract type: {contract_type}
"""
        
        prompt = f"""You are summarizing a contract analysis. 
ONLY use the facts below. Do NOT add any information not provided.
Do NOT make claims about market data, industry standards, or comparisons unless the data is given.
Keep it to 2-3 sentences maximum.

FACTS:
{facts}

Generate a brief, professional summary:"""
        
        try:
            response = self._llm_service._call_llm(prompt, max_tokens=150)
            return response.strip() if response else None
        except Exception as e:
            logger.warning(f"Narration failed: {e}")
            return None
    
    def _to_dict(self, result: AnalysisResult, cached: bool = False) -> Dict[str, Any]:
        """Convert AnalysisResult to dictionary for API response.
        
        Ensures backwards compatibility with the frontend which expects:
        - fairness_score (not score)
        - contract_metadata with specific camelCase friendly keys
        - percentile_rankings with salary and notice_period
        - negotiation_scripts array with clause, script, successProbability
        """
        # Use model_dump for Pydantic v2
        if hasattr(result, 'model_dump'):
            data = result.model_dump()
        else:
            data = result.dict()
        
        data['cached'] = cached
        
        # === Legacy field mappings for backwards compatibility ===
        
        # Score mapping
        data['fairness_score'] = data['score']
        
        # Percentile rankings mapping
        percentiles = data.get('percentiles', {}) or {}
        data['percentile_rankings'] = {
            'salary': percentiles.get('salary', {}).get('value') if percentiles.get('salary') else None,
            'notice_period': percentiles.get('notice_period', {}).get('value') if percentiles.get('notice_period') else None,
        }
        
        # Similar contracts count
        cohort = data.get('cohort') or {}
        data['similar_contracts_count'] = cohort.get('cohort_size', 0)
        
        # Transform red flags to frontend format
        raw_red_flags = data.get('red_flags', []) or []
        data['red_flags'] = [
            {
                'issue': flag.get('rule') or flag.get('id', ''),
                'title': flag.get('rule') or flag.get('id', ''),
                'explanation': flag.get('explanation', ''),
                'severity': flag.get('severity', 'medium'),
                'source_text': flag.get('source_text'),
            } if isinstance(flag, dict) else str(flag)
            for flag in raw_red_flags
        ]
        
        # Transform favorable terms to frontend format
        raw_favorable = data.get('favorable_terms', []) or []
        data['favorable_terms'] = [
            {
                'term': term.get('term') or term.get('id', ''),
                'title': term.get('term') or term.get('id', ''),
                'explanation': term.get('explanation', ''),
                'value': term.get('value'),
            } if isinstance(term, dict) else str(term)
            for term in raw_favorable
        ]
        
        # Generate negotiation scripts from negotiation points
        raw_negotiations = data.get('negotiation_points', []) or []
        negotiation_scripts = []
        for point in raw_negotiations:
            if isinstance(point, dict):
                # Calculate success probability based on priority
                priority = point.get('priority', 2)
                success_prob = max(0.4, min(0.8, 0.9 - priority * 0.15))
                
                negotiation_scripts.append({
                    'clause': point.get('topic', 'Negotiation Point'),
                    'script': point.get('script', ''),
                    'successProbability': success_prob,
                })
        
        # Add default script if none generated
        if not negotiation_scripts:
            score = data.get('score', 50)
            if score >= 75:
                negotiation_scripts.append({
                    'clause': '✅ Excellent Contract',
                    'script': f'This contract has a good fairness score of {score}/100. The terms appear competitive and fair.',
                    'successProbability': 1.0,
                })
            elif score >= 50:
                negotiation_scripts.append({
                    'clause': '📝 Review Complete',
                    'script': f'This contract has a fairness score of {score}/100. Consider reviewing the terms with a legal professional.',
                    'successProbability': 0.8,
                })
            else:
                negotiation_scripts.append({
                    'clause': '⚠️ Needs Attention',
                    'script': f'This contract has a fairness score of {score}/100. Consider negotiating key terms before signing.',
                    'successProbability': 0.6,
                })
        
        data['negotiation_scripts'] = negotiation_scripts
        
        # Negotiation priorities (simplified from negotiation points)
        data['negotiation_priorities'] = [
            point.get('topic', '') if isinstance(point, dict) else str(point)
            for point in raw_negotiations
        ]
        
        # Similar contracts details (from evidence)
        evidence = data.get('evidence', []) or []
        data['similar_contracts_details'] = [
            {
                'contract_id': e.get('contract_id', ''),
                'similarity_score': e.get('similarity', 0),
                'contract_type': e.get('metadata', {}).get('contract_type'),
                'industry': e.get('metadata', {}).get('industry'),
            }
            for e in evidence[:5]
        ]
        
        # Detailed explanation for frontend
        contract_metadata = data.get('contract_metadata', {}) or {}
        data['detailed_explanation'] = {
            'data_sources': {
                'knowledge_base_contracts_used': len(evidence),
                'total_contracts_in_knowledge_base': cohort.get('cohort_size', 0),
                'data_quality': {
                    'sample_size': cohort.get('cohort_size', 0),
                    'coverage': 'good' if cohort.get('cohort_size', 0) >= 10 else 'limited',
                    'relevance': 'high' if cohort.get('cohort_size', 0) >= 5 else 'medium',
                },
            },
            'explanations': {
                'fairness_score_explanation': {
                    'score': data['score'],
                    'category': 'Excellent' if data['score'] >= 75 else 'Good' if data['score'] >= 50 else 'Needs Improvement',
                    'explanation': data.get('score_formula', ''),
                    'factors': ['Salary percentile', 'Notice period', 'Red flags', 'Favorable terms'],
                    'calculation_method': 'Deterministic formula based on market percentiles',
                },
            },
            'confidence_metrics': {
                'confidence_level': 'High' if data.get('score_confidence', 0) >= 0.7 else 'Medium',
                'sample_size': cohort.get('cohort_size', 0),
                'data_quality': 'Good' if cohort.get('cohort_size', 0) >= 10 else 'Limited',
                'explanation': f"Based on {cohort.get('cohort_size', 0)} similar contracts",
            },
        }
        
        return data


# Backwards-compatible alias
def create_analysis_service(enable_narration: bool = False) -> AnalysisServiceV2:
    """Factory function to create analysis service."""
    return AnalysisServiceV2(enable_narration=enable_narration)
