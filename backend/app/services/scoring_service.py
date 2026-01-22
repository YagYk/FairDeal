from __future__ import annotations

from typing import List, Optional

from ..logging_config import get_logger
from ..models.schemas import (
    ContractExtractionResult,
    BenchmarkResult,
    ScoreResult,
    ScoreBreakdownItem,
    RedFlag,
    FavorableTerm,
)


log = get_logger("service.scoring")


class ScoringService:
    """
    Deterministic, auditable scoring for contract analysis.
    
    Formula:
    S = 50 + W_salary*(P_salary - 50) + W_notice*(50 - P_notice) 
           - Σ(flag_penalties) + Σ(favorable_bonuses)
    
    Where:
      W_salary = 0.4  (salary percentile weight)
      W_notice = 0.3  (notice percentile weight - lower is better)
    """

    W_SALARY = 0.4
    W_NOTICE = 0.3

    def compute_scores(
        self, 
        extraction: ContractExtractionResult, 
        benchmark: Optional[BenchmarkResult],
        red_flags: List[RedFlag],
        favorable_terms: List[FavorableTerm],
        notice_percentile: Optional[float] = None
    ) -> ScoreResult:
        """
        Compute holistic health score:
        S = Base(50) 
            + Salary_Impact(±20) 
            + Notice_Impact(±10) 
            + Sum(RedFlag_Impacts) 
            + Sum(Favorable_Impacts)
        """
        breakdown: List[ScoreBreakdownItem] = []
        formula_parts: List[str] = ["50.0 (Base)"]
        
        # 1. Base Score
        score = 50.0
        breakdown.append(ScoreBreakdownItem(
            factor="base_baseline",
            points=50.0,
            reason="Starting point for a standard contract."
        ))

        # 2. Salary Market Positioning (Max ±20)
        p_sal = benchmark.percentile_salary if benchmark and benchmark.percentile_salary is not None else 50.0
        # Map 0-100 percentile to -20 to +20 points
        sal_impact = (p_sal - 50.0) * 0.4
        score += sal_impact
        breakdown.append(ScoreBreakdownItem(
            factor="salary_benchmarking",
            points=round(sal_impact, 1),
            reason=f"Compensation is at the {p_sal:.0f}th percentile compared to peers."
        ))
        formula_parts.append(f"{sal_impact:+.1f} (Salary)")

        # 3. Notice Period Mobility (Max ±10)
        p_not = notice_percentile if notice_percentile is not None else 50.0
        # Lower notice is better. Map 0-100 percentile to +10 to -10 points.
        not_impact = (50.0 - p_not) * 0.2
        score += not_impact
        breakdown.append(ScoreBreakdownItem(
            factor="notice_mobility",
            points=round(not_impact, 1),
            reason=f"Notice period mobility score based on the {p_not:.0f}th percentile."
        ))
        formula_parts.append(f"{not_impact:+.1f} (Notice)")

        # 4. Critical Red Flag Penalties
        flag_total = 0.0
        for flag in red_flags:
            # Red flag impact scores are already negative (e.g., -15.0)
            impact = flag.impact_score
            # We scale the impact score to ensure overall score stays sane
            # Scaling factor: total red flag impact shouldn't easily kill the whole score unless critical
            scaled_impact = impact * 0.8 
            flag_total += scaled_impact
            breakdown.append(ScoreBreakdownItem(
                factor=f"risk_{flag.id.lower()}",
                points=round(scaled_impact, 1),
                reason=flag.rule,
                source_text=flag.source_text
            ))
        
        score += flag_total
        if flag_total != 0:
            formula_parts.append(f"{flag_total:+.1f} (Risks)")

        # 5. Favorable Terms Bonuses
        term_total = 0.0
        for term in favorable_terms:
            impact = term.impact_score * 0.5 # Subtler bonus
            term_total += impact
            breakdown.append(ScoreBreakdownItem(
                factor=f"benefit_{term.id.lower()}",
                points=round(impact, 1),
                reason=term.term,
                source_text=term.source_text
            ))
            
        score += term_total
        if term_total != 0:
            formula_parts.append(f"{term_total:+.1f} (Benefits)")

        # Final Clamp & Grade
        score = max(0.0, min(100.0, score))
        grade = self._compute_grade(score)
        confidence = self._compute_confidence(extraction, benchmark)
        
        formula_str = " ".join(formula_parts) + f" = {score:.1f}"

        # Logic for legacy fields
        safety_score = self._compute_safety_score(extraction)
        market_fairness = self._compute_market_fairness(benchmark)

        return ScoreResult(
            overall_score=score,
            grade=grade,
            score_confidence=confidence,
            score_formula=formula_str,
            breakdown=breakdown,
            safety_score=safety_score,
            market_fairness_score=market_fairness
        )

    def _compute_grade(self, score: float) -> str:
        if score >= 85:
            return "EXCELLENT"
        elif score >= 70:
            return "GOOD"
        elif score >= 55:
            return "FAIR"
        elif score >= 40:
            return "POOR"
        else:
            return "CRITICAL"

    def _compute_confidence(
        self, 
        extraction: ContractExtractionResult, 
        benchmark: Optional[BenchmarkResult]
    ) -> float:
        """
        Confidence based on extraction completeness and cohort size.
        """
        # Base extraction confidence from field presence
        key_fields = [
            extraction.ctc_inr, 
            extraction.notice_period_days, 
            extraction.bond_amount_inr, 
            extraction.non_compete_months
        ]
        present_fields = [f for f in key_fields if f and f.value is not None]
        
        if not present_fields:
            extraction_confidence = 0.2
        else:
            # Average of individual field confidences
            avg_field_conf = sum(f.confidence or 0.5 for f in present_fields) / len(present_fields)
            # completeness factor (0.5 to 1.0)
            completeness = 0.5 + (len(present_fields) / len(key_fields)) * 0.5
            extraction_confidence = avg_field_conf * completeness
            
        # Factor in cohort size
        cohort_confidence = 1.0
        if not benchmark or benchmark.cohort_size == 0:
            cohort_confidence = 0.4
        elif benchmark.cohort_size < 10:
            cohort_confidence = 0.6
        elif benchmark.cohort_size < 30:
            cohort_confidence = 0.8
        
        return min(1.0, 0.7 * extraction_confidence + 0.3 * cohort_confidence)

    def _compute_safety_score(self, extraction: ContractExtractionResult) -> float:
        """Legacy safety score for backward compatibility."""
        score = 100.0
        
        bond = extraction.bond_amount_inr.value if extraction.bond_amount_inr else None
        if bond and bond > 50000:
            score -= 15.0
            
        notice = extraction.notice_period_days.value if extraction.notice_period_days else None
        if notice and notice >= 90:
            score -= 10.0
            
        nc = extraction.non_compete_months.value if extraction.non_compete_months else None
        if nc and nc > 6:
            score -= 20.0
            
        return max(0.0, score)

    def _compute_market_fairness(self, benchmark: Optional[BenchmarkResult]) -> float:
        """Legacy market fairness score for backward compatibility."""
        if not benchmark or benchmark.percentile_salary is None:
            return 50.0
            
        p = benchmark.percentile_salary
        if p < 10:
            return 20.0
        elif p < 25:
            return 40.0
        elif p < 50:
            return 55.0
        elif p < 75:
            return 70.0
        elif p < 90:
            return 85.0
        else:
            return 95.0
