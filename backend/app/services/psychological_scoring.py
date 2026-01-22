"""
Psychological Scoring Engine v3.0
Revolutionary scoring system that feels emotionally true.
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Any, Optional
import math
from dataclasses import dataclass

from ..logging_config import get_logger

log = get_logger("service.psych_scoring")

@dataclass
class PsychScoreResult:
    score: int
    grade: str
    confidence: float
    breakdown: Dict[str, Any]
    raw_score: float
    multiplier: float
    badges: List[str]
    risk_factors: List[str]
    legal_violations: List[str]

class PsychologicalScoringEngine:
    """
    Revolutionary scoring system that feels emotionally true.
    """
    
    def __init__(self):
        self.version = "3.0"
        self.calibration_enabled = True
    
    def compute_score(
        self,
        salary_percentile: Optional[float],
        notice_percentile: Optional[float],
        benefits_count: int,
        benefits_list: List[str],
        non_compete: bool,
        non_compete_months: int,
        role_level: str,
        industry: str,
        **kwargs
    ) -> PsychScoreResult:
        """
        Main scoring function
        
        Multi-dimensional scoring with psychological calibration
        """
        
        # ═══════════════════════════════════════════════════════
        # STEP 1: COMPONENT SCORES (0-100 each)
        # ═══════════════════════════════════════════════════════
        
        salary_score = self._score_salary(salary_percentile)
        notice_score = self._score_notice(notice_percentile)
        benefits_score = self._score_benefits(benefits_count, benefits_list)
        clauses_score, risk_factors = self._score_clauses(
            non_compete, non_compete_months, kwargs
        )
        legal_score, violations = self._score_legal_compliance(kwargs)
        
        # ═══════════════════════════════════════════════════════
        # STEP 2: WEIGHTED AVERAGE (with dynamic weights)
        # ═══════════════════════════════════════════════════════
        
        weights = self._calculate_dynamic_weights(
            role_level, industry, bool(violations)
        )
        
        raw_score = (
            weights['salary'] * salary_score +
            weights['notice'] * notice_score +
            weights['benefits'] * benefits_score +
            weights['clauses'] * clauses_score +
            weights['legal'] * legal_score
        )
        
        # ═══════════════════════════════════════════════════════
        # STEP 3: CONTEXT MULTIPLIERS
        # ═══════════════════════════════════════════════════════
        
        multiplier, badges = self._get_context_multiplier(
            salary_percentile, notice_percentile,
            benefits_count, non_compete, kwargs
        )
        
        adjusted_score = raw_score * multiplier
        
        # ═══════════════════════════════════════════════════════
        # STEP 4: CALIBRATION (ensure distribution feels right)
        # ═══════════════════════════════════════════════════════
        
        final_score = self._calibrate(adjusted_score)
        grade = self._get_grade(final_score)
        
        return PsychScoreResult(
            score=round(final_score),
            grade=grade,
            confidence=0.95,
            breakdown={
                "salary": {"score": salary_score, "weight": weights['salary']},
                "notice": {"score": notice_score, "weight": weights['notice']},
                "benefits": {"score": benefits_score, "weight": weights['benefits']},
                "clauses": {"score": clauses_score, "weight": weights['clauses']},
                "legal": {"score": legal_score, "weight": weights['legal']}
            },
            raw_score=round(raw_score, 2),
            multiplier=multiplier,
            badges=badges,
            risk_factors=risk_factors,
            legal_violations=violations
        )
    
    def _score_salary(self, percentile: Optional[float]) -> float:
        """
        Salary scoring with exponential rewards for top performers
        Maps percentile to 20-100 points
        """
        if percentile is None:
            return 50.0
        
        if percentile <= 10:
            return 20 + (percentile / 10) * 15
        elif percentile <= 25:
            return 35 + ((percentile - 10) / 15) * 20
        elif percentile <= 50:
            return 55 + ((percentile - 25) / 25) * 15
        elif percentile <= 75:
            return 70 + ((percentile - 50) / 25) * 15
        elif percentile <= 90:
            return 85 + ((percentile - 75) / 15) * 10
        else:
            return 95 + ((percentile - 90) / 10) * 5
    
    def _score_notice(self, percentile: Optional[float]) -> float:
        """
        Inverted sigmoid for notice period
        Lower percentile (shorter notice) is better
        """
        if percentile is None:
            return 50.0
        
        if percentile <= 10:
            return 95 + (10 - percentile)
        elif percentile <= 25:
            return 85 + (25 - percentile) / 1.5
        elif percentile <= 50:
            return 70 + (50 - percentile) / 1.7
        elif percentile <= 75:
            return 50 + (75 - percentile) / 1.25
        elif percentile <= 90:
            return 35 + (90 - percentile) / 1.5
        else:
            return 20 + (100 - percentile) * 1.5
    
    def _score_benefits(self, count: int, benefits: List[str]) -> float:
        """Tiered benefits scoring with quality bonus and mandatory penalty"""
        base_scores = {
            0: 30, 1: 50, 2: 60, 3: 70,
            4: 80, 5: 88, 6: 93, 7: 97, 8: 99
        }
        base = base_scores.get(count, 100)
        
        # Premium benefits bonus
        premium = [
            'equity', 'stock_options', 'esop', 'relocation',
            'signing_bonus', 'education_allowance', 'gym_membership',
            'mental_health', 'parental_leave'
        ]
        
        premium_count = 0
        benefits_lower = [b.lower() for b in benefits]
        for p in premium:
            if any(p in b for b in benefits_lower):
                premium_count += 1
                
        quality_bonus = min(premium_count * 3, 10)
        
        # Mandatory penalty
        mandatory = ['provident', 'gratuity'] # Simplified check keywords
        # Note: 'provident' matches 'provident fund' and 'pf' matches 'pf'
        missing_mandatory = 0
        for m in mandatory:
            found = False
            term = "pf" if m == "provident" else m
            for b in benefits_lower:
                if m in b or term in b: # Check if 'provident' or 'pf' is in the benefit string
                    found = True
                    break
            if not found:
                missing_mandatory += 1
                
        mandatory_penalty = missing_mandatory * 15
        
        return max(20.0, min(100.0, float(base + quality_bonus - mandatory_penalty)))
    
    def _score_clauses(self, non_compete: bool, nc_months: int,
                       data: Dict) -> Tuple[float, List[str]]:
        """Risk-based clause scoring"""
        score = 100.0
        risks = []
        
        if non_compete:
            if nc_months <= 3:
                score -= 5
                risks.append("Short non-compete (3mo): -5")
            elif nc_months <= 6:
                score -= 12
                risks.append("Standard non-compete (6mo): -12")
            elif nc_months <= 12:
                score -= 20
                risks.append("Long non-compete (12mo): -20")
            else:
                score -= 30
                risks.append("Excessive non-compete (>12mo): -30")
                
            if data.get('non_compete_scope') == "all_companies":
                score -= 10
                risks.append("Overly broad scope: -10")
        
        if data.get('training_bond'):
            bond_months = data.get('training_bond_months', 24) or 24
            bond_amount = data.get('training_bond_amount', 0) or 0
            
            deduction = 0
            if bond_months <= 12:
                deduction = 5
            elif bond_months <= 24:
                deduction = 12
            else:
                deduction = 20
            score -= deduction
            risks.append(f"Training bond ({bond_months}mo): -{deduction}")
            
            if bond_amount > 200000:
                score -= 10
                risks.append(f"High bond amount (>₹2L): -10")
                
            if not data.get('bond_justification'): # If bond exists but no clear justification extracted
                 pass # We skip this specific -15 check strictly unless we are sure, to avoid false positives on vague extraction
        
        if data.get('garden_leave'):
            score -= 8
            risks.append("Garden leave clause: -8")
            
        if data.get('ip_assignment') == "all_work":
            score -= 15
            risks.append("Owns ALL your work: -15")
            
        if data.get('probation_months', 0) > 6:
            score -= 8
            risks.append("Long probation (>6 months): -8")
            
        if data.get('termination_without_cause'):
            score -= 12
            risks.append("Can fire without reason: -12")
        
        return max(20.0, score), risks
    
    def _score_legal_compliance(self, data: Dict) -> Tuple[float, List[str]]:
        """Legal compliance checking"""
        score = 100.0
        violations = []
        
        if (data.get('notice_period_days') or 0) > 90:
            score -= 30
            violations.append("Notice >90 days (likely illegal): -30")
        
        if not data.get('has_provident_fund'):
             # PF is standard for most formal employment in India.
             # Removed arbitrary 21LPA threshold as per requirement.
             score -= 25
             violations.append("Missing mandatory PF: -25")
        
        # Gratuity check - Only penalize if explicitly absent
        if data.get('gratuity_status') == 'absent':
             score -= 15
             violations.append("No gratuity clause: -15")

        if data.get('working_hours_per_week', 0) > 48:
            score -= 20
            violations.append("Hours >48/week: -20")
            
        if data.get('unlimited_deductions'):
            score -= 20
            violations.append("Unlimited salary deductions: -20")
            
        return max(0.0, score), violations
    
    def _calculate_dynamic_weights(self, role_level: str,
                                   industry: str,
                                   has_violations: bool) -> Dict[str, float]:
        """Context-aware weight adjustment"""
        weights = {
            'salary': 0.35,
            'notice': 0.20,
            'benefits': 0.20,
            'clauses': 0.15,
            'legal': 0.10
        }
        
        if role_level == "junior" or role_level == "entry":
            weights['salary'] = 0.40
            weights['benefits'] = 0.25
            weights['notice'] = 0.15
        elif role_level == "senior":
            weights['notice'] = 0.25
            weights['clauses'] = 0.20
            weights['salary'] = 0.30
        elif role_level == "manager":
            weights['clauses'] = 0.25
            weights['salary'] = 0.30
            weights['notice'] = 0.20
        
        if industry == "startup":
            weights['benefits'] = 0.30
            weights['salary'] = 0.25
        
        if has_violations:
            weights['legal'] = 0.20
            # Normalize others
            remaining = 0.8
            current_sum = sum(v for k, v in weights.items() if k != 'legal')
            if current_sum > 0:
                factor = remaining / current_sum
                for key in weights:
                    if key != 'legal':
                        weights[key] *= factor
        
        return weights
    
    def _get_context_multiplier(self, sal_pct: Optional[float], not_pct: Optional[float],
                                ben_cnt: int, non_comp: bool,
                                data: Dict) -> Tuple[float, List[str]]:
        """Holistic quality multipliers"""
        multiplier = 1.0
        badges = []
        
        s_p = sal_pct if sal_pct is not None else 50
        n_p = not_pct if not_pct is not None else 50
        
        # Unicorn contract
        # High salary, short notice (low percentile), good benefits, no non-compete
        if s_p >= 80 and n_p <= 20 and ben_cnt >= 5 and not non_comp:
            multiplier *= 1.15
            badges.append("🦄 UNICORN CONTRACT")
            
        # Golden Handcuffs
        if s_p >= 90 and (data.get('non_compete_months') or 0) >= 12:
            multiplier *= 0.95
            badges.append("⚠️ Golden Handcuffs")
            
        # Startup with Equity
        if data.get('has_equity') and data.get('industry') == 'startup':
            multiplier *= 1.08
            badges.append("🚀 STARTUP ROCKET")
            
        # Standard MNC
        if 40 <= s_p <= 60 and 30 <= (data.get('notice_period_days') or 0) <= 60 and ben_cnt >= 3:
            multiplier *= 1.02
            badges.append("🏢 Standard MNC Package")
            
        # Toxic contract
        toxic_count = 0
        if s_p < 15: toxic_count += 1
        if (data.get('notice_period_days') or 0) > 90: toxic_count += 1
        if (data.get('non_compete_months') or 0) > 12: toxic_count += 1
        if (data.get('training_bond_amount') or 0) > 300000: toxic_count += 1
        if data.get('has_legal_violations'): toxic_count += 1
        
        if toxic_count >= 3:
            multiplier *= 0.85
            badges.append("🚨 TOXIC CONTRACT")
            
        # Service company pattern
        if (data.get('notice_period_days') or 0) >= 90 and s_p < 40 and data.get('training_bond'):
            multiplier *= 0.90
            badges.append("⚠️ SERVICE TRAP")
            
        return multiplier, badges
    
    def _calibrate(self, raw_score: float) -> float:
        """Psychological calibration"""
        if raw_score >= 85:
            # Compress top range
            return 85 + (raw_score - 85) * 1.5
        elif raw_score >= 70:
            return 70 + (raw_score - 70) * 1.2
        elif raw_score >= 50:
            return raw_score
        elif raw_score >= 30:
            return 30 + (raw_score - 30) * 0.9
        else:
            return raw_score * 0.8
    
    def _get_grade(self, score: float) -> str:
        if score >= 90:
            return "EXCEPTIONAL"
        elif score >= 80:
            return "EXCELLENT"
        elif score >= 70:
            return "GOOD"
        elif score >= 60:
            return "AVERAGE"
        elif score >= 50:
            return "BELOW AVERAGE"
        elif score >= 40:
            return "POOR"
        else:
            return "CRITICAL"
