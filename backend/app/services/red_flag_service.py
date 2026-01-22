from __future__ import annotations

from typing import List, Optional, Tuple

from ..logging_config import get_logger
from ..models.schemas import (
    ContractExtractionResult,
    BenchmarkResult,
    RedFlag,
    FavorableTerm,
    Severity,
)


log = get_logger("service.red_flag")


class RedFlagService:
    """
    Rule engine for detecting red flags and favorable terms in contracts.
    Based on market standards and legal best practices.
    """

    def __init__(self) -> None:
        from .benchmark_service import BenchmarkService
        self.benchmarker = BenchmarkService()

    def analyze(
        self,
        extraction: ContractExtractionResult,
        benchmark: Optional[BenchmarkResult],
        benefits_count: int = 0,
        *,
        industry: Optional[str] = None,
        company_type: Optional[str] = None,
        notice_percentile: Optional[float] = None,
    ) -> Tuple[List[RedFlag], List[FavorableTerm]]:
        """
        Analyze extraction results and return red flags and favorable terms.
        """
        red_flags: List[RedFlag] = []
        favorable_terms: List[FavorableTerm] = []

        # Load industry standards
        industry = (industry or "tech").lower()
        standards = self.benchmarker.get_industry_standards(industry)
        
        std_notice = standards.get("notice_days", 60)
        std_probation = standards.get("probation_months", 6)
        std_non_compete = standards.get("non_compete_months", 12)
        _ = (std_probation, std_non_compete)  # reserved for future rule tuning

        # Market-driven notice stats (if available)
        notice_stats = self.benchmarker.get_notice_stats(company_type) if company_type else {}
        notice_median = notice_stats.get("median")

        # Get values
        salary = extraction.ctc_inr.value if extraction.ctc_inr else None
        salary_source = extraction.ctc_inr.source_text if extraction.ctc_inr else None
        
        notice = extraction.notice_period_days.value if extraction.notice_period_days else None
        notice_source = extraction.notice_period_days.source_text if extraction.notice_period_days else None
        
        bond = extraction.bond_amount_inr.value if extraction.bond_amount_inr else None
        bond_source = extraction.bond_amount_inr.source_text if extraction.bond_amount_inr else None
        
        non_compete = extraction.non_compete_months.value if extraction.non_compete_months else None
        non_compete_source = extraction.non_compete_months.source_text if extraction.non_compete_months else None
        
        probation = extraction.probation_months.value if extraction.probation_months else None
        probation_source = extraction.probation_months.source_text if extraction.probation_months else None
        
        salary_percentile = benchmark.percentile_salary if benchmark else None

        # ═══════════════════════════════════════════════════════
        # SALARY RED FLAGS
        # ═══════════════════════════════════════════════════════
        if salary_percentile is not None:
            if salary_percentile < 10:
                red_flags.append(RedFlag(
                    id="SALARY_CRITICAL_LOW",
                    severity=Severity.critical,
                    rule="Salary below 10th percentile",
                    explanation=f"Your salary is in the bottom 10% of similar contracts. This is significantly below market rate.",
                    source_text=salary_source,
                    impact_score=-25.0,
                    market_context=f"90% of similar contracts offer more than ₹{salary:,.0f}" if salary else None,
                    recommendation="This should be your #1 negotiation priority. Request at least 25-30% increase to reach market average."
                ))
            elif salary_percentile < 25:
                red_flags.append(RedFlag(
                    id="SALARY_LOW",
                    severity=Severity.high,
                    rule="Salary below 25th percentile",
                    explanation=f"Your salary is below average for your role and experience level.",
                    source_text=salary_source,
                    impact_score=-15.0,
                    market_context=f"75% of similar contracts offer more than ₹{salary:,.0f}" if salary else None,
                    recommendation="Request a 15-20% increase to reach market median."
                ))
            elif salary_percentile >= 75:
                favorable_terms.append(FavorableTerm(
                    id="SALARY_EXCELLENT",
                    term="Above-Market Salary",
                    explanation=f"Your salary is in the top 25% of similar contracts.",
                    source_text=salary_source,
                    value=f"₹{salary:,.0f} ({salary_percentile:.0f}th percentile)" if salary else "Top quartile",
                    impact_score=10.0,
                    market_context="Only 25% of similar roles get this compensation level."
                ))

        # ═══════════════════════════════════════════════════════
        # NOTICE PERIOD FLAGS
        # ═══════════════════════════════════════════════════════
        if notice is not None:
            # Prefer percentile-based judgement if we have it (higher percentile = longer notice = worse)
            if notice_percentile is not None:
                mc = None
                if notice_median is not None:
                    mc = f"Median notice period for {company_type or 'this cohort'} is ~{int(notice_median)} days."
                elif std_notice is not None:
                    mc = f"Industry baseline notice period is ~{int(std_notice)} days."

                if notice_percentile >= 80:
                    red_flags.append(RedFlag(
                        id="NOTICE_EXCESSIVE",
                        severity=Severity.high,
                        rule="Notice period in worst 20% (long notice)",
                        explanation=f"Your notice period is longer than ~{notice_percentile:.0f}% of similar contracts, which significantly limits mobility.",
                        source_text=notice_source,
                        impact_score=-15.0,
                        market_context=mc,
                        recommendation="Negotiate down materially (e.g., 30-60 days). Offer structured handover as an alternative."
                    ))
                elif notice_percentile >= 60:
                    red_flags.append(RedFlag(
                        id="NOTICE_HIGH",
                        severity=Severity.medium,
                        rule="Notice period above average (longer notice)",
                        explanation=f"Your notice period is longer than ~{notice_percentile:.0f}% of similar contracts.",
                        source_text=notice_source,
                        impact_score=-8.0,
                        market_context=mc,
                        recommendation="Try to negotiate closer to the median (or 45 days if feasible)."
                    ))
                elif notice_percentile <= 20:
                    favorable_terms.append(FavorableTerm(
                        id="NOTICE_SHORT",
                        term="Short Notice Period",
                        explanation=f"Your notice period is shorter than ~{100 - notice_percentile:.0f}% of similar contracts, which is excellent for mobility.",
                        source_text=notice_source,
                        value=f"{int(notice)} days",
                        impact_score=10.0,
                        market_context=mc
                    ))
            else:
                # Fallback: raw thresholds (kept for when market data lacks notice)
                if notice >= 90:
                    red_flags.append(RedFlag(
                        id="NOTICE_EXCESSIVE",
                        severity=Severity.high,
                        rule="Notice period 90+ days",
                        explanation=f"A {notice}-day notice period significantly limits your career mobility. You'll be locked in for 3+ months after resignation.",
                        source_text=notice_source,
                        impact_score=-15.0,
                        market_context=f"Baseline notice period is ~{int(std_notice)} days for {industry}.",
                        recommendation="Negotiate down to 60 days maximum. Offer to complete handover documentation as alternative."
                    ))
                elif notice >= 60:
                    red_flags.append(RedFlag(
                        id="NOTICE_HIGH",
                        severity=Severity.medium,
                        rule="Notice period 60-89 days",
                        explanation=f"A {notice}-day notice period is on the higher side but common in larger companies.",
                        source_text=notice_source,
                        impact_score=-8.0,
                        market_context=f"Baseline notice period is ~{int(std_notice)} days for {industry}.",
                        recommendation="Try to negotiate to 45 days where feasible."
                    ))
                elif notice <= 30:
                    favorable_terms.append(FavorableTerm(
                        id="NOTICE_SHORT",
                        term="Short Notice Period",
                        explanation=f"Your {notice}-day notice period gives you excellent career mobility.",
                        source_text=notice_source,
                        value=f"{notice} days",
                        impact_score=10.0,
                        market_context=f"Baseline notice period is ~{int(std_notice)} days for {industry}."
                    ))

        # ═══════════════════════════════════════════════════════
        # NON-COMPETE FLAGS
        # ═══════════════════════════════════════════════════════
        if non_compete is not None and non_compete > 0:
            if non_compete > 12:
                red_flags.append(RedFlag(
                    id="NON_COMPETE_EXCESSIVE",
                    severity=Severity.critical,
                    rule="Non-compete exceeds 12 months",
                    explanation=f"A {non_compete}-month non-compete is unreasonably long and may not be enforceable in India.",
                    source_text=non_compete_source,
                    impact_score=-25.0,
                    market_context="Non-compete clauses over 12 months are rarely enforceable in Indian courts. Standard is 6 months or less.",
                    recommendation="Insist on removal or reduction to 6 months for direct competitors only."
                ))
            elif non_compete > 6:
                red_flags.append(RedFlag(
                    id="NON_COMPETE_HIGH",
                    severity=Severity.high,
                    rule="Non-compete 7-12 months",
                    explanation=f"A {non_compete}-month non-compete is aggressive and limits your next opportunity.",
                    source_text=non_compete_source,
                    impact_score=-15.0,
                    market_context="Only 35% of tech contracts have non-compete clauses. Standard duration is 6 months.",
                    recommendation="Negotiate to reduce to 6 months or define 'competitor' narrowly."
                ))
            else:
                red_flags.append(RedFlag(
                    id="NON_COMPETE_PRESENT",
                    severity=Severity.medium,
                    rule="Non-compete clause present",
                    explanation=f"This contract restricts you from joining competitors for {non_compete} months after leaving.",
                    source_text=non_compete_source,
                    impact_score=-10.0,
                    market_context="Only 35% of tech contracts include non-compete. Duration of 6 months is standard when present.",
                    recommendation="Negotiate to remove entirely, or ensure it only applies to direct competitors."
                ))

        # ═══════════════════════════════════════════════════════
        # BOND/TRAINING COST FLAGS
        # ═══════════════════════════════════════════════════════
        if bond is not None and bond > 0:
            if bond >= 200000:
                red_flags.append(RedFlag(
                    id="BOND_CRITICAL",
                    severity=Severity.critical,
                    rule="Bond amount ≥ ₹2,00,000",
                    explanation=f"A training bond of ₹{bond:,.0f} is extremely high and financially risky.",
                    source_text=bond_source,
                    impact_score=-20.0,
                    market_context="Most legitimate companies don't require training bonds. This is common in service companies that provide minimal training.",
                    recommendation="Decline or negotiate removal. If training is truly valuable, the bond should be pro-rated based on tenure."
                ))
            elif bond >= 50000:
                red_flags.append(RedFlag(
                    id="BOND_HIGH",
                    severity=Severity.high,
                    rule="Bond amount ₹50,000-₹2,00,000",
                    explanation=f"A training bond of ₹{bond:,.0f} is significant. Ensure it's pro-rated if you leave early.",
                    source_text=bond_source,
                    impact_score=-12.0,
                    market_context="Product companies rarely have training bonds. This is more common in IT services.",
                    recommendation="Negotiate for pro-rated reduction based on months served, or removal after 12 months."
                ))
            else:
                red_flags.append(RedFlag(
                    id="BOND_PRESENT",
                    severity=Severity.low,
                    rule="Training bond present",
                    explanation=f"A training bond of ₹{bond:,.0f} exists but is relatively modest.",
                    source_text=bond_source,
                    impact_score=-5.0,
                    market_context="While not ideal, this amount is manageable if the role offers good growth.",
                    recommendation="Confirm the bond is pro-rated and understand the exact conditions for repayment."
                ))

        # ═══════════════════════════════════════════════════════
        # PROBATION FLAGS
        # ═══════════════════════════════════════════════════════
        if probation is not None:
            if probation > 6:
                red_flags.append(RedFlag(
                    id="PROBATION_LONG",
                    severity=Severity.medium,
                    rule="Probation exceeds 6 months",
                    explanation=f"A {probation}-month probation period is longer than standard. You may have reduced benefits during this time.",
                    source_text=probation_source,
                    impact_score=-8.0,
                    market_context="Standard probation is 3-6 months. Longer periods are unusual for experienced hires.",
                    recommendation="Request reduction to 3-6 months, especially if you're an experienced candidate."
                ))
            elif probation <= 3:
                favorable_terms.append(FavorableTerm(
                    id="PROBATION_SHORT",
                    term="Short Probation Period",
                    explanation=f"{probation}-month probation shows confidence in your abilities.",
                    source_text=probation_source,
                    value=f"{probation} months",
                    impact_score=3.0,
                    market_context="Many companies have 6-month probation. Yours is shorter than average."
                ))

        # ═══════════════════════════════════════════════════════
        # BENEFITS FLAGS
        # ═══════════════════════════════════════════════════════
        if benefits_count >= 4:
            favorable_terms.append(FavorableTerm(
                id="BENEFITS_EXCELLENT",
                term="Comprehensive Benefits Package",
                explanation=f"You have {benefits_count} benefits, placing you above average.",
                source_text=None,
                value=f"{benefits_count} benefits",
                impact_score=5.0,
                market_context="Average tech contract offers 3-4 benefits. Yours is comprehensive."
            ))
        elif benefits_count <= 1:
            red_flags.append(RedFlag(
                id="BENEFITS_MINIMAL",
                severity=Severity.medium,
                rule="Minimal benefits",
                explanation="This contract offers very few benefits beyond base salary.",
                source_text=None,
                impact_score=-8.0,
                market_context="Standard packages include health insurance, PF, and paid leave at minimum.",
                recommendation="Request health insurance coverage for family, and confirm PF contributions."
            ))

        # BENEFITS FAVORABLE TERMS
        if benefits_count >= 6:
            favorable_terms.append(FavorableTerm(
                id="BENEFITS_GENEROUS",
                term="Generous Benefits Package",
                explanation=f"You have {benefits_count} identified benefits, which is significantly above the market average of 4.",
                value=str(benefits_count),
                impact_score=10.0,
                market_context="Top 10% of contracts offer 6+ distinct benefits."
            ))

        # Sort by impact
        red_flags.sort(key=lambda x: x.impact_score)  # Most negative first
        favorable_terms.sort(key=lambda x: x.impact_score, reverse=True)  # Most positive first

        return red_flags, favorable_terms
