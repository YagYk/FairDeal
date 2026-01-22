"""
Context-Aware Scoring Service.
Adjusts scoring based on company type, role level, and other context.
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from ..logging_config import get_logger
from ..models.schemas import (
    ContractExtractionResult,
    BenchmarkResult,
    ScoreResult,
    ScoreBreakdownItem,
    RedFlag,
    FavorableTerm,
)


log = get_logger("service.context_scoring")


# Known service companies (non-negotiable salaries)
SERVICE_COMPANIES = {
    # Indian IT Services
    "tcs", "tata consultancy", "infosys", "wipro", "hcl", "hcltech",
    "tech mahindra", "cognizant", "capgemini", "accenture", "ltimindtree",
    "ltim", "l&t infotech", "mindtree", "mphasis", "hexaware", "cyient",
    "zensar", "persistent", "birlasoft", "sonata software", "mastek",
    "coforge", "niit", "kpit", "sasken", "tata elxsi",
    # Global Services
    "ibm", "deloitte", "ey", "pwc", "kpmg", "mckinsey", "bcg", "bain",
}

# Product companies with typically negotiable salaries
PRODUCT_COMPANIES = {
    "google", "microsoft", "amazon", "apple", "meta", "facebook", "netflix",
    "flipkart", "swiggy", "zomato", "razorpay", "phonepe", "paytm", "cred",
    "meesho", "groww", "zerodha", "bharatpe", "uber", "ola", "byjus",
    "unacademy", "upgrad", "vedantu", "freshworks", "zoho", "postman",
    "atlassian", "adobe", "salesforce", "oracle", "sap", "vmware",
}


@dataclass
class ScoringContext:
    """Context for scoring adjustments."""
    company_type: str  # "service", "product", "startup", "unknown"
    role_level: str  # "entry", "mid", "senior", "unknown"
    is_campus_hire: bool
    salary_negotiable: bool
    cohort_confidence: str  # "high", "medium", "low", "insufficient"
    warnings: List[str]


class ContextAwareScoringService:
    """
    Scoring service that adapts based on contract context.
    
    Key adjustments:
    1. Service companies: Disable salary benchmarking (fixed pay)
    2. Entry-level: Reduce salary weight (less variance)
    3. Small cohorts: Don't show percentile (unreliable)
    4. Focus on actual risks: bond, notice, non-compete
    """

    MINIMUM_COHORT_SIZE = 30  # Don't show percentile below this

    def detect_context(
        self,
        extraction: ContractExtractionResult,
        benchmark: Optional[BenchmarkResult],
        user_context: Optional[Dict[str, Any]] = None,
    ) -> ScoringContext:
        """
        Detect scoring context from extraction and user input.
        """
        warnings = []
        
        # 1. Detect company type
        company_name = ""
        if extraction.company_type and extraction.company_type.value:
            company_name = str(extraction.company_type.value).lower()
        if user_context and user_context.get("company_type"):
            company_name = str(user_context["company_type"]).lower()
        
        company_type = self._detect_company_type(company_name)
        
        # 2. Detect role level
        role_level = "unknown"
        if user_context and user_context.get("experience_level") is not None:
            exp = user_context["experience_level"]
            if exp <= 1:
                role_level = "entry"
            elif exp <= 5:
                role_level = "mid"
            else:
                role_level = "senior"
        
        # 3. Is this a campus hire?
        is_campus = role_level == "entry" and company_type == "service"
        
        # 4. Is salary negotiable?
        salary_negotiable = True
        if company_type == "service":
            salary_negotiable = False
            warnings.append("Service company salaries are typically fixed and non-negotiable.")
        elif is_campus:
            salary_negotiable = False
            warnings.append("Campus hire packages are standardized.")
        elif role_level == "entry":
            warnings.append("Entry-level salaries have less negotiation room.")
        
        # 5. Cohort confidence
        cohort_confidence = "insufficient"
        if benchmark and benchmark.cohort_size:
            if benchmark.cohort_size >= 100:
                cohort_confidence = "high"
            elif benchmark.cohort_size >= self.MINIMUM_COHORT_SIZE:
                cohort_confidence = "medium"
            elif benchmark.cohort_size >= 10:
                cohort_confidence = "low"
                warnings.append(f"Limited market data ({benchmark.cohort_size} records). Percentile may be unreliable.")
            else:
                warnings.append("Insufficient market data for reliable salary comparison.")
        else:
            warnings.append("No market data available for comparison.")
        
        return ScoringContext(
            company_type=company_type,
            role_level=role_level,
            is_campus_hire=is_campus,
            salary_negotiable=salary_negotiable,
            cohort_confidence=cohort_confidence,
            warnings=warnings,
        )
    
    def _detect_company_type(self, company_name: str) -> str:
        """Detect if company is service, product, or startup."""
        name_lower = company_name.lower().strip()
        
        # Check against known lists
        for service in SERVICE_COMPANIES:
            if service in name_lower or name_lower in service:
                return "service"
        
        for product in PRODUCT_COMPANIES:
            if product in name_lower or name_lower in product:
                return "product"
        
        # Heuristics
        if any(x in name_lower for x in ["services", "solutions", "consulting", "technologies ltd", "infotech"]):
            return "service"
        
        if any(x in name_lower for x in ["labs", "ai", "tech", "app", "platform"]):
            return "startup"
        
        return "unknown"

    def compute_scores(
        self,
        extraction: ContractExtractionResult,
        benchmark: Optional[BenchmarkResult],
        red_flags: List[RedFlag],
        favorable_terms: List[FavorableTerm],
        notice_percentile: Optional[float] = None,
        context: Optional[ScoringContext] = None,
    ) -> ScoreResult:
        """
        Compute context-aware scores.
        
        Formula:
        S = 50 (Base)
            + Salary_Impact (only if salary_negotiable and cohort sufficient)
            + Notice_Impact
            + Sum(RedFlag_Impacts)
            + Sum(Favorable_Impacts)
        """
        breakdown: List[ScoreBreakdownItem] = []
        formula_parts: List[str] = ["50.0 (Base)"]
        
        # Detect context if not provided
        if context is None:
            context = self.detect_context(extraction, benchmark)
        
        # 1. Base Score
        score = 50.0
        breakdown.append(ScoreBreakdownItem(
            factor="base_baseline",
            points=50.0,
            reason="Starting point for a standard contract."
        ))

        # 2. Salary Market Positioning (CONTEXT-AWARE)
        if context.salary_negotiable and context.cohort_confidence in ("high", "medium"):
            p_sal = benchmark.percentile_salary if benchmark and benchmark.percentile_salary is not None else 50.0
            
            # Adjust weight based on role level
            salary_weight = 0.4
            if context.role_level == "entry":
                salary_weight = 0.2  # Less impact for entry level
            
            sal_impact = (p_sal - 50.0) * salary_weight
            score += sal_impact
            breakdown.append(ScoreBreakdownItem(
                factor="salary_benchmarking",
                points=round(sal_impact, 1),
                reason=f"Compensation is at the {p_sal:.0f}th percentile compared to peers."
            ))
            formula_parts.append(f"{sal_impact:+.1f} (Salary)")
        else:
            # Skip salary benchmarking
            breakdown.append(ScoreBreakdownItem(
                factor="salary_benchmarking",
                points=0.0,
                reason="Salary comparison skipped: " + (
                    "Service company salaries are fixed." if context.company_type == "service"
                    else "Insufficient market data for comparison."
                )
            ))

        # 3. Notice Period Mobility
        p_not = notice_percentile if notice_percentile is not None else 50.0
        not_impact = (50.0 - p_not) * 0.2
        score += not_impact
        breakdown.append(ScoreBreakdownItem(
            factor="notice_mobility",
            points=round(not_impact, 1),
            reason=f"Notice period mobility score based on the {p_not:.0f}th percentile."
        ))
        formula_parts.append(f"{not_impact:+.1f} (Notice)")

        # 4. Red Flag Penalties
        flag_total = 0.0
        for flag in red_flags:
            impact = flag.impact_score * 0.8
            flag_total += impact
            breakdown.append(ScoreBreakdownItem(
                factor=f"risk_{flag.id.lower()}",
                points=round(impact, 1),
                reason=flag.rule,
                source_text=flag.source_text
            ))
        
        score += flag_total
        if flag_total != 0:
            formula_parts.append(f"{flag_total:+.1f} (Risks)")

        # 5. Favorable Terms Bonuses
        term_total = 0.0
        for term in favorable_terms:
            impact = term.impact_score * 0.5
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
        confidence = self._compute_confidence(extraction, benchmark, context)
        
        formula_str = " ".join(formula_parts) + f" = {score:.1f}"

        # Legacy fields
        safety_score = self._compute_safety_score(extraction)
        market_fairness = self._compute_market_fairness(benchmark, context)

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
        benchmark: Optional[BenchmarkResult],
        context: ScoringContext,
    ) -> float:
        """Compute confidence based on extraction and context."""
        # Base extraction confidence
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
            avg_field_conf = sum(f.confidence or 0.5 for f in present_fields) / len(present_fields)
            completeness = 0.5 + (len(present_fields) / len(key_fields)) * 0.5
            extraction_confidence = avg_field_conf * completeness
        
        # Cohort confidence factor
        cohort_factor = {
            "high": 1.0,
            "medium": 0.8,
            "low": 0.6,
            "insufficient": 0.4,
        }.get(context.cohort_confidence, 0.5)
        
        return min(1.0, 0.7 * extraction_confidence + 0.3 * cohort_factor)

    def _compute_safety_score(self, extraction: ContractExtractionResult) -> float:
        """Legacy safety score."""
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

    def _compute_market_fairness(
        self,
        benchmark: Optional[BenchmarkResult],
        context: ScoringContext,
    ) -> float:
        """Legacy market fairness score with context awareness."""
        if not benchmark or benchmark.percentile_salary is None:
            return 50.0
        
        # If salary not negotiable, return neutral
        if not context.salary_negotiable:
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
