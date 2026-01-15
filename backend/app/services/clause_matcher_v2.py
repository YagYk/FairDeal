"""
Deterministic Clause Matcher for contract analysis.
Uses ONLY rule-based logic - NO LLM calls.

Rules:
- salary < 25th percentile => below-market (severity high)
- salary < 10th => significantly below (critical)
- notice > 75th => long notice (medium)
- notice > 90th => excessive (high)
- non_compete true => restriction flag (medium)
- benefits_count < 3 => limited benefits (low)
- clause rarity: if clause appears in <10% of cohort => unusual (medium)
"""
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger

from app.models.schemas import (
    RedFlag, FavorableTerm, NegotiationPoint, 
    RedFlagSeverity, PercentileInfo
)


class ClauseMatcherV2:
    """
    Deterministic clause matching using rule-based logic.
    Every flag includes rule ID, explanation, and source text.
    """
    
    # Rule definitions
    RULES = {
        # Salary rules
        "SALARY_CRITICAL_LOW": {
            "condition": lambda pct: pct is not None and pct < 10,
            "severity": RedFlagSeverity.CRITICAL,
            "description": "Salary is significantly below market",
            "template": "Your salary is in the {percentile:.0f}th percentile - significantly below market rate. This is among the lowest {percentile:.0f}% of comparable contracts.",
        },
        "SALARY_HIGH_LOW": {
            "condition": lambda pct: pct is not None and 10 <= pct < 25,
            "severity": RedFlagSeverity.HIGH,
            "description": "Salary is below market average",
            "template": "Your salary is in the {percentile:.0f}th percentile - below market average. Consider negotiating for at least the 50th percentile.",
        },
        "SALARY_EXCELLENT": {
            "condition": lambda pct: pct is not None and pct >= 75,
            "is_favorable": True,
            "description": "Above-market salary",
            "template": "Your salary is in the {percentile:.0f}th percentile - above market average. This is competitive compensation.",
        },
        
        # Notice period rules
        "NOTICE_EXCESSIVE": {
            "condition": lambda pct: pct is not None and pct > 90,
            "severity": RedFlagSeverity.HIGH,
            "description": "Excessive notice period",
            "template": "Your notice period is longer than {percentile:.0f}% of comparable contracts. This significantly restricts job mobility.",
        },
        "NOTICE_LONG": {
            "condition": lambda pct: pct is not None and 75 < pct <= 90,
            "severity": RedFlagSeverity.MEDIUM,
            "description": "Long notice period",
            "template": "Your notice period is longer than {percentile:.0f}% of comparable contracts. Consider negotiating for industry standard (30-60 days).",
        },
        "NOTICE_SHORT": {
            "condition": lambda pct: pct is not None and pct <= 25,
            "is_favorable": True,
            "description": "Employee-friendly notice period",
            "template": "Your notice period is shorter than {percentile:.0f}% of comparable contracts. This gives you more flexibility.",
        },
        
        # Non-compete rules
        "NON_COMPETE_PRESENT": {
            "severity": RedFlagSeverity.MEDIUM,
            "description": "Non-compete clause restricts future employment",
            "template": "This contract contains a non-compete clause which may restrict your future employment options in the same industry.",
        },
        "NON_COMPETE_LONG": {
            "severity": RedFlagSeverity.HIGH,
            "description": "Extended non-compete period",
            "template": "The non-compete period of {duration} months is longer than typical. Standard is 6-12 months.",
        },
        
        # Benefits rules
        "BENEFITS_LIMITED": {
            "severity": RedFlagSeverity.LOW,
            "description": "Limited benefits package",
            "template": "Only {count} benefit(s) mentioned. Standard packages include health insurance, PF, gratuity, and leave.",
        },
        "BENEFITS_NONE": {
            "severity": RedFlagSeverity.MEDIUM,
            "description": "No benefits mentioned",
            "template": "No benefits are explicitly mentioned in the contract. Standard packages should include health insurance and statutory benefits.",
        },
        "BENEFITS_GOOD": {
            "is_favorable": True,
            "description": "Comprehensive benefits package",
            "template": "Contract includes {count} benefits: {benefits_list}. This is a comprehensive package.",
        },
    }
    
    def __init__(self):
        """Initialize the clause matcher."""
        pass
    
    def match_clauses(
        self,
        salary_percentile: Optional[float] = None,
        notice_percentile: Optional[float] = None,
        salary_value: Optional[float] = None,
        notice_value: Optional[int] = None,
        non_compete: bool = False,
        non_compete_duration_months: Optional[int] = None,
        benefits: Optional[List[str]] = None,
        source_texts: Optional[Dict[str, str]] = None,
        cohort_size: int = 0,
    ) -> Tuple[List[RedFlag], List[FavorableTerm], List[NegotiationPoint]]:
        """
        Match contract data against deterministic rules.
        
        Args:
            salary_percentile: Salary percentile (0-100)
            notice_percentile: Notice period percentile (0-100)
            salary_value: Actual salary value
            notice_value: Actual notice period in days
            non_compete: Whether non-compete clause exists
            non_compete_duration_months: Duration of non-compete
            benefits: List of benefits
            source_texts: Dict mapping field names to source text snippets
            cohort_size: Size of comparison cohort
            
        Returns:
            Tuple of (red_flags, favorable_terms, negotiation_points)
        """
        logger.info(f"Matching clauses: salary_pct={salary_percentile}, notice_pct={notice_percentile}")
        
        red_flags: List[RedFlag] = []
        favorable_terms: List[FavorableTerm] = []
        negotiation_points: List[NegotiationPoint] = []
        
        source_texts = source_texts or {}
        benefits = benefits or []
        
        # === SALARY RULES ===
        if salary_percentile is not None:
            # Critical low salary
            if salary_percentile < 10:
                red_flags.append(RedFlag(
                    id="SALARY_CRITICAL_LOW",
                    severity=RedFlagSeverity.CRITICAL,
                    rule="Salary < 10th percentile",
                    explanation=self.RULES["SALARY_CRITICAL_LOW"]["template"].format(percentile=salary_percentile),
                    source_text=source_texts.get("salary"),
                    threshold="10th percentile",
                    actual_value=f"₹{salary_value:,.0f}" if salary_value else None,
                ))
                negotiation_points.append(NegotiationPoint(
                    id="NEG_SALARY_CRITICAL",
                    topic="Salary Increase",
                    script=f"Based on my research of {cohort_size} comparable contracts, the offered salary of ₹{salary_value:,.0f} is in the bottom {salary_percentile:.0f}% of the market. I would like to discuss a significant adjustment to bring this closer to industry standards.",
                    reason=f"Salary is at {salary_percentile:.0f}th percentile - significantly below market",
                    priority=1,
                ))
            # High severity low salary
            elif salary_percentile < 25:
                red_flags.append(RedFlag(
                    id="SALARY_HIGH_LOW",
                    severity=RedFlagSeverity.HIGH,
                    rule="Salary < 25th percentile",
                    explanation=self.RULES["SALARY_HIGH_LOW"]["template"].format(percentile=salary_percentile),
                    source_text=source_texts.get("salary"),
                    threshold="25th percentile",
                    actual_value=f"₹{salary_value:,.0f}" if salary_value else None,
                ))
                negotiation_points.append(NegotiationPoint(
                    id="NEG_SALARY_LOW",
                    topic="Salary Negotiation",
                    script=f"The compensation of ₹{salary_value:,.0f} is below the market median for this role. I would like to request an adjustment of 15-20% to align with industry standards.",
                    reason=f"Salary is at {salary_percentile:.0f}th percentile",
                    priority=2,
                ))
            # Excellent salary (favorable)
            elif salary_percentile >= 75:
                favorable_terms.append(FavorableTerm(
                    id="SALARY_EXCELLENT",
                    term="Above-market salary",
                    explanation=self.RULES["SALARY_EXCELLENT"]["template"].format(percentile=salary_percentile),
                    source_text=source_texts.get("salary"),
                    value=f"₹{salary_value:,.0f} ({salary_percentile:.0f}th percentile)" if salary_value else None,
                ))
        
        # === NOTICE PERIOD RULES ===
        if notice_percentile is not None:
            # Excessive notice
            if notice_percentile > 90:
                red_flags.append(RedFlag(
                    id="NOTICE_EXCESSIVE",
                    severity=RedFlagSeverity.HIGH,
                    rule="Notice period > 90th percentile",
                    explanation=self.RULES["NOTICE_EXCESSIVE"]["template"].format(percentile=notice_percentile),
                    source_text=source_texts.get("notice_period"),
                    threshold="90th percentile",
                    actual_value=f"{notice_value} days" if notice_value else None,
                ))
                negotiation_points.append(NegotiationPoint(
                    id="NEG_NOTICE_EXCESSIVE",
                    topic="Notice Period Reduction",
                    script=f"The notice period of {notice_value} days is significantly longer than industry standard. I would like to request a reduction to 60 days, which is more typical for this role.",
                    reason=f"Notice period is at {notice_percentile:.0f}th percentile - excessive",
                    priority=2,
                ))
            # Long notice
            elif notice_percentile > 75:
                red_flags.append(RedFlag(
                    id="NOTICE_LONG",
                    severity=RedFlagSeverity.MEDIUM,
                    rule="Notice period > 75th percentile",
                    explanation=self.RULES["NOTICE_LONG"]["template"].format(percentile=notice_percentile),
                    source_text=source_texts.get("notice_period"),
                    threshold="75th percentile",
                    actual_value=f"{notice_value} days" if notice_value else None,
                ))
                negotiation_points.append(NegotiationPoint(
                    id="NEG_NOTICE_LONG",
                    topic="Notice Period",
                    script=f"I noticed the notice period is {notice_value} days. Could we discuss reducing this to 30-60 days, which is more aligned with industry norms?",
                    reason=f"Notice period is at {notice_percentile:.0f}th percentile",
                    priority=3,
                ))
            # Short notice (favorable)
            elif notice_percentile <= 25:
                favorable_terms.append(FavorableTerm(
                    id="NOTICE_SHORT",
                    term="Employee-friendly notice period",
                    explanation=self.RULES["NOTICE_SHORT"]["template"].format(percentile=notice_percentile),
                    source_text=source_texts.get("notice_period"),
                    value=f"{notice_value} days" if notice_value else None,
                ))
        
        # === NON-COMPETE RULES ===
        if non_compete:
            if non_compete_duration_months and non_compete_duration_months > 12:
                red_flags.append(RedFlag(
                    id="NON_COMPETE_LONG",
                    severity=RedFlagSeverity.HIGH,
                    rule="Non-compete duration > 12 months",
                    explanation=self.RULES["NON_COMPETE_LONG"]["template"].format(duration=non_compete_duration_months),
                    source_text=source_texts.get("non_compete"),
                    threshold="12 months",
                    actual_value=f"{non_compete_duration_months} months",
                ))
            else:
                red_flags.append(RedFlag(
                    id="NON_COMPETE_PRESENT",
                    severity=RedFlagSeverity.MEDIUM,
                    rule="Non-compete clause present",
                    explanation=self.RULES["NON_COMPETE_PRESENT"]["template"],
                    source_text=source_texts.get("non_compete"),
                ))
            
            negotiation_points.append(NegotiationPoint(
                id="NEG_NON_COMPETE",
                topic="Non-Compete Clause",
                script="I have concerns about the non-compete clause. Could we discuss limiting its scope to direct competitors or reducing the restricted period to 6 months?",
                reason="Non-compete clauses can significantly limit future career options",
                priority=2,
            ))
        
        # === BENEFITS RULES ===
        benefits_count = len(benefits)
        
        if benefits_count == 0:
            red_flags.append(RedFlag(
                id="BENEFITS_NONE",
                severity=RedFlagSeverity.MEDIUM,
                rule="No benefits mentioned",
                explanation=self.RULES["BENEFITS_NONE"]["template"],
                source_text=None,
            ))
            negotiation_points.append(NegotiationPoint(
                id="NEG_BENEFITS",
                topic="Benefits Package",
                script="I noticed the contract doesn't explicitly mention benefits. Could we discuss adding health insurance, provident fund, and leave entitlements?",
                reason="No benefits mentioned in contract",
                priority=3,
            ))
        elif benefits_count < 3:
            red_flags.append(RedFlag(
                id="BENEFITS_LIMITED",
                severity=RedFlagSeverity.LOW,
                rule="Benefits count < 3",
                explanation=self.RULES["BENEFITS_LIMITED"]["template"].format(count=benefits_count),
                source_text=", ".join(benefits) if benefits else None,
            ))
        else:
            favorable_terms.append(FavorableTerm(
                id="BENEFITS_GOOD",
                term="Comprehensive benefits",
                explanation=self.RULES["BENEFITS_GOOD"]["template"].format(
                    count=benefits_count,
                    benefits_list=", ".join(benefits[:5])
                ),
                source_text=", ".join(benefits),
                value=f"{benefits_count} benefits",
            ))
        
        # Sort by priority
        negotiation_points.sort(key=lambda x: x.priority)
        
        logger.info(f"Clause matching complete: {len(red_flags)} red flags, {len(favorable_terms)} favorable, {len(negotiation_points)} negotiation points")
        
        return red_flags, favorable_terms, negotiation_points
    
    def get_rule_summary(self) -> Dict[str, Any]:
        """Get summary of all rules for documentation."""
        return {
            "salary_rules": {
                "critical_low": "< 10th percentile",
                "high_low": "10-25th percentile",
                "excellent": ">= 75th percentile",
            },
            "notice_rules": {
                "excessive": "> 90th percentile",
                "long": "75-90th percentile",
                "short": "<= 25th percentile",
            },
            "non_compete_rules": {
                "present": "Any non-compete clause",
                "long": "> 12 months duration",
            },
            "benefits_rules": {
                "none": "0 benefits",
                "limited": "< 3 benefits",
                "good": ">= 3 benefits",
            },
        }
