"""
Deterministic Scoring Engine for contract fairness analysis.
NO LLM CALLS - All scores computed from extracted values and dataset statistics.

Formula:
S_raw = 50 + 0.4*(P_salary - 50) + 0.3*(50 - P_notice) - 0.3*(N_flags*5)
S = clamp(round(S_raw), 0, 100)

Missing value handling:
- If salary missing: drop salary term and renormalize remaining weights
- If notice missing: same
"""
from typing import Dict, Optional, List, Any, Tuple
from loguru import logger
import math


class ScoringEngine:
    """
    Deterministic scoring engine for contract fairness.
    
    Key principles:
    1. NO LLM calls - purely mathematical
    2. Transparent formula - every calculation is traceable
    3. Handles missing values gracefully
    4. Returns confidence based on data quality
    """
    
    # Base weights (sum should equal 1.0 for core components)
    WEIGHT_SALARY = 0.4
    WEIGHT_NOTICE = 0.3
    WEIGHT_FLAGS = 0.3
    
    # Penalty per red flag (multiplied by count)
    FLAG_PENALTY = 5
    
    # Bonus per favorable term
    FAVORABLE_BONUS = 3
    
    # Non-compete penalty
    NON_COMPETE_PENALTY = 10
    
    # Minimum cohort size for confidence
    MIN_COHORT_FULL_CONFIDENCE = 30
    MIN_COHORT_ACCEPTABLE = 10
    
    def __init__(self):
        """Initialize the scoring engine."""
        pass
    
    def compute_score(
        self,
        salary_percentile: Optional[float],
        notice_percentile: Optional[float],
        red_flags_count: int,
        favorable_terms_count: int = 0,
        non_compete: bool = False,
        cohort_size: int = 0,
        extraction_confidence: float = 1.0,
        benefits_count: int = 0,
    ) -> Tuple[int, float, str]:
        """
        Compute deterministic fairness score.
        
        Args:
            salary_percentile: Percentile of salary (0-100) or None if missing
            notice_percentile: Percentile of notice period (0-100) or None if missing
            red_flags_count: Number of red flags identified
            favorable_terms_count: Number of favorable terms identified
            non_compete: Whether contract has non-compete clause
            cohort_size: Size of comparison cohort
            extraction_confidence: Confidence in extracted values (0-1)
            benefits_count: Number of benefits mentioned
            
        Returns:
            Tuple of (score: int, confidence: float, formula: str)
        """
        logger.info(f"Computing score: salary_pct={salary_percentile}, notice_pct={notice_percentile}, "
                   f"flags={red_flags_count}, favorable={favorable_terms_count}, non_compete={non_compete}")
        
        # Track which components are used for formula string
        components = []
        formula_parts = ["50"]  # Base score
        
        # Calculate effective weights based on available data
        available_weight = 0.0
        salary_contrib = 0.0
        notice_contrib = 0.0
        
        has_salary = salary_percentile is not None
        has_notice = notice_percentile is not None
        
        # Determine total available weight for normalization
        if has_salary:
            available_weight += self.WEIGHT_SALARY
        if has_notice:
            available_weight += self.WEIGHT_NOTICE
        
        # If both missing, use simplified scoring
        if available_weight == 0:
            available_weight = 1.0  # Avoid division by zero
        
        # Normalization factor to redistribute weights
        norm_factor = (self.WEIGHT_SALARY + self.WEIGHT_NOTICE) / available_weight if available_weight > 0 else 1.0
        
        # Calculate salary contribution
        if has_salary:
            # Normalize weight if notice is missing
            effective_salary_weight = self.WEIGHT_SALARY * (norm_factor if not has_notice else 1.0)
            salary_contrib = effective_salary_weight * (salary_percentile - 50)
            components.append(f"salary:{salary_percentile:.1f}%")
            formula_parts.append(f"+ {effective_salary_weight:.2f}*({salary_percentile:.1f}-50)")
        
        # Calculate notice contribution (lower is better for employee)
        if has_notice:
            # Normalize weight if salary is missing
            effective_notice_weight = self.WEIGHT_NOTICE * (norm_factor if not has_salary else 1.0)
            notice_contrib = effective_notice_weight * (50 - notice_percentile)
            components.append(f"notice:{notice_percentile:.1f}%")
            formula_parts.append(f"+ {effective_notice_weight:.2f}*(50-{notice_percentile:.1f})")
        
        # Calculate flag penalty
        flag_penalty = self.WEIGHT_FLAGS * (red_flags_count * self.FLAG_PENALTY)
        components.append(f"flags:{red_flags_count}")
        if red_flags_count > 0:
            formula_parts.append(f"- {self.WEIGHT_FLAGS:.2f}*({red_flags_count}*{self.FLAG_PENALTY})")
        
        # Calculate favorable bonus
        favorable_bonus = favorable_terms_count * self.FAVORABLE_BONUS
        if favorable_terms_count > 0:
            components.append(f"favorable:{favorable_terms_count}")
            formula_parts.append(f"+ {favorable_terms_count}*{self.FAVORABLE_BONUS}")
        
        # Non-compete penalty
        non_compete_penalty = self.NON_COMPETE_PENALTY if non_compete else 0
        if non_compete:
            components.append("non_compete")
            formula_parts.append(f"- {self.NON_COMPETE_PENALTY}")
        
        # Benefits adjustment
        benefits_adjustment = 0
        if benefits_count >= 3:
            benefits_adjustment = 5
            formula_parts.append("+ 5 (good benefits)")
        elif benefits_count == 0:
            benefits_adjustment = -5
            formula_parts.append("- 5 (no benefits)")
        
        # Compute raw score
        score_raw = (
            50  # Base score
            + salary_contrib
            + notice_contrib
            - flag_penalty
            + favorable_bonus
            - non_compete_penalty
            + benefits_adjustment
        )
        
        # Clamp to 0-100
        score = max(0, min(100, round(score_raw)))
        
        # Build formula string
        formula = " ".join(formula_parts) + f" = {score_raw:.1f} → {score}"
        
        # Calculate confidence
        confidence = self._compute_confidence(
            extraction_confidence=extraction_confidence,
            cohort_size=cohort_size,
            has_salary=has_salary,
            has_notice=has_notice,
        )
        
        logger.info(f"Score computed: {score} (confidence: {confidence:.2f})")
        logger.debug(f"Formula: {formula}")
        
        return score, confidence, formula
    
    def _compute_confidence(
        self,
        extraction_confidence: float,
        cohort_size: int,
        has_salary: bool,
        has_notice: bool,
    ) -> float:
        """
        Compute confidence in the score based on data quality.
        
        Formula:
        conf = 0.6 * extraction_confidence + 0.4 * cohort_confidence
        
        Adjustments:
        - If salary missing: -0.1
        - If notice missing: -0.1
        """
        # Cohort confidence
        if cohort_size >= self.MIN_COHORT_FULL_CONFIDENCE:
            cohort_confidence = 1.0
        elif cohort_size >= self.MIN_COHORT_ACCEPTABLE:
            # Linear interpolation between min and full
            cohort_confidence = cohort_size / self.MIN_COHORT_FULL_CONFIDENCE
        else:
            # Below acceptable threshold
            cohort_confidence = max(0.3, cohort_size / self.MIN_COHORT_ACCEPTABLE * 0.5)
        
        # Base confidence
        confidence = 0.6 * extraction_confidence + 0.4 * cohort_confidence
        
        # Penalties for missing data
        if not has_salary:
            confidence -= 0.1
        if not has_notice:
            confidence -= 0.1
        
        # Clamp to valid range
        confidence = max(0.1, min(1.0, confidence))
        
        return round(confidence, 2)
    
    def get_score_category(self, score: int) -> str:
        """Get human-readable category for a score."""
        if score >= 80:
            return "Excellent"
        elif score >= 65:
            return "Good"
        elif score >= 50:
            return "Fair"
        elif score >= 35:
            return "Below Average"
        else:
            return "Poor"
    
    def get_recommendation(self, score: int, confidence: float) -> str:
        """Get recommendation based on score and confidence."""
        category = self.get_score_category(score)
        
        if confidence < 0.5:
            return f"Score is {score}/100 ({category}), but confidence is low ({confidence:.0%}). " \
                   f"Consider verifying the extracted values before making decisions."
        
        if score >= 75:
            return f"This contract scores {score}/100 ({category}). " \
                   f"Terms are competitive. No major negotiation required."
        elif score >= 50:
            return f"This contract scores {score}/100 ({category}). " \
                   f"Some terms could be improved. Consider negotiating on highlighted issues."
        else:
            return f"This contract scores {score}/100 ({category}). " \
                   f"Multiple concerns identified. Strong negotiation recommended before signing."
