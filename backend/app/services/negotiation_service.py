from __future__ import annotations

from typing import List, Optional, Dict, Any

from ..logging_config import get_logger
from ..models.schemas import (
    ContractExtractionResult,
    BenchmarkResult,
    RedFlag,
    NegotiationPoint,
)


log = get_logger("service.negotiation")


# Service companies with fixed, non-negotiable salaries
SERVICE_COMPANIES = {
    "tcs", "infosys", "wipro", "hcl", "cognizant", "accenture", "capgemini",
    "tech mahindra", "ltimindtree", "mphasis", "hexaware", "zensar", "persistent",
}


class NegotiationService:
    """
    Generates actionable negotiation points with context-awareness.
    Skips salary negotiation for service companies and entry-level roles.
    """

    def generate_playbook(
        self,
        extraction: ContractExtractionResult,
        benchmark: Optional[BenchmarkResult],
        red_flags: List[RedFlag],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[NegotiationPoint]:
        """
        Generate prioritized negotiation points based on context, red flags and market data.
        """
        points: List[NegotiationPoint] = []
        priority = 0

        # Get values
        salary = extraction.ctc_inr.value if extraction.ctc_inr else None
        notice = extraction.notice_period_days.value if extraction.notice_period_days else None
        non_compete = extraction.non_compete_months.value if extraction.non_compete_months else None
        bond = extraction.bond_amount_inr.value if extraction.bond_amount_inr else None
        
        salary_percentile = benchmark.percentile_salary if benchmark else None
        p75 = benchmark.market_p75 if benchmark else None
        cohort_size = benchmark.cohort_size if benchmark else 0
        
        # Detect if salary is negotiable based on context
        salary_negotiable = True
        company_type = "unknown"
        
        if context:
            salary_negotiable = context.get("salary_negotiable", True)
            company_type = context.get("company_type", "unknown")

        # Auto-detect service company from extracted company name
        company_name = context.get("company_name", "") if context else ""
        if company_name and any(sc in company_name.lower() for sc in SERVICE_COMPANIES):
            salary_negotiable = False
            log.info(f"Auto-detected service company '{company_name}' — salary negotiation skipped")

        # ═══════════════════════════════════════════════════════
        # NON-COMPETE NEGOTIATION (Always relevant)
        # ═══════════════════════════════════════════════════════
        if non_compete and non_compete > 0:
            priority += 1
            target = "Removed entirely" if non_compete > 6 else "3 months for direct competitors only"
            
            points.append(NegotiationPoint(
                id="NEG_NON_COMPETE",
                priority=priority,
                topic="Remove/Reduce Non-Compete Clause",
                current_term=f"{non_compete} months, all competitors",
                target_term=target,
                rationale="Non-compete clauses are uncommon in tech and legally difficult to enforce in India. Companies often include them as boilerplate.",
                success_probability="Likely achievable" if non_compete <= 6 else "Worth trying",
                script=self._get_non_compete_script(non_compete),
                fallback="If they won't remove it, ask for: (1) Narrow definition of 'competitor', (2) Geographic restriction to India only, (3) Exemption if laid off",
                evidence=[
                    "Non-compete clauses are rarely enforced in India",
                    "Courts favor employee mobility",
                    "Many companies remove on request"
                ]
            ))

        # ═══════════════════════════════════════════════════════
        # SALARY NEGOTIATION (Context-aware - skip for service/entry)
        # ═══════════════════════════════════════════════════════
        if salary_negotiable and salary_percentile and salary_percentile < 75 and salary and p75 and cohort_size >= 30:
            priority += 1
            target_salary = min(p75, salary * 1.20)  # Max 20% increase ask
            increase_pct = ((target_salary - salary) / salary) * 100
            
            points.append(NegotiationPoint(
                id="NEG_SALARY",
                priority=priority,
                topic="Salary Enhancement",
                current_term=f"₹{salary:,.0f} ({salary_percentile:.0f}th percentile)",
                target_term=f"₹{target_salary:,.0f} ({increase_pct:.0f}% increase)",
                rationale=f"Your current offer is at the {salary_percentile:.0f}th percentile. Market 75th percentile is ₹{p75:,.0f}. A modest increase is reasonable.",
                success_probability="Medium (50%)" if salary_percentile > 40 else "High (65%)",
                script=self._get_salary_script(salary, target_salary, salary_percentile),
                fallback="If base salary is fixed, ask for: (1) Signing bonus, (2) Earlier performance review, (3) Stock options or RSUs, (4) Higher variable component",
                evidence=[
                    f"Market median for similar roles: ₹{benchmark.market_median:,.0f}" if benchmark else "",
                    f"Market 75th percentile: ₹{p75:,.0f}" if p75 else "",
                    "Salary negotiation is expected - 80% of offers have room"
                ]
            ))

        # ═══════════════════════════════════════════════════════
        # NOTICE PERIOD NEGOTIATION
        # ═══════════════════════════════════════════════════════
        if notice and notice >= 60:
            priority += 1
            target_notice = 30 if notice >= 90 else 45
            
            points.append(NegotiationPoint(
                id="NEG_NOTICE",
                priority=priority,
                topic="Reduce Notice Period",
                current_term=f"{notice} days",
                target_term=f"{target_notice} days",
                rationale=f"A {notice}-day notice period limits career mobility. Product companies typically have 30-45 days.",
                success_probability="Medium (45%)" if notice >= 90 else "Low (30%)",
                script=self._get_notice_script(notice, target_notice),
                fallback="If they can't reduce it: (1) Ask for notice buyout option, (2) Garden leave with full pay, (3) Waiver clause for mutual agreement",
                evidence=[
                    "Product company median: 30-45 days",
                    "Only service companies require 90+ days",
                    "Long notice periods correlate with lower retention"
                ]
            ))

        # ═══════════════════════════════════════════════════════
        # BOND NEGOTIATION
        # ═══════════════════════════════════════════════════════
        if bond and bond > 0:
            priority += 1
            
            points.append(NegotiationPoint(
                id="NEG_BOND",
                priority=priority,
                topic="Remove Training Bond",
                current_term=f"₹{bond:,.0f}",
                target_term="Removed, or pro-rated based on tenure",
                rationale="Training bonds are uncommon in product companies and often indicate the company values retention over talent happiness.",
                success_probability="Medium (40%)",
                script=self._get_bond_script(bond),
                fallback="If bond is mandatory: (1) Ensure it's pro-rated monthly, (2) Get it waived after 12 months, (3) Clarify exact training you'll receive",
                evidence=[
                    "Product companies rarely have training bonds",
                    "Pro-rating is industry standard when bonds exist",
                    "Bond value should reflect actual training cost"
                ]
            ))

        # Sort by priority
        points.sort(key=lambda x: x.priority)
        
        return points

    def _get_non_compete_script(self, months: int) -> str:
        return f"""Dear [Hiring Manager],

Thank you for the offer! I'm very excited about the opportunity to join [Company].

While reviewing the offer letter, I noticed a {months}-month non-compete clause. Given the dynamic nature of the tech industry and my career goals, I was hoping we could discuss this provision.

Would it be possible to either:
1. Remove the non-compete clause entirely, OR
2. Limit it to direct competitors only, with a shorter duration of 3 months?

I'm fully committed to maintaining confidentiality and protecting [Company]'s interests. I believe we can find a solution that works for both of us.

Looking forward to your thoughts.

Best regards,
[Your Name]"""

    def _get_salary_script(self, current: float, target: float, percentile: float) -> str:
        return f"""Dear [Hiring Manager],

Thank you for extending the offer. I'm genuinely excited about the role and [Company].

After careful consideration and market research, I'd like to discuss the compensation. The offered CTC of ₹{current:,.0f} is at the {percentile:.0f}th percentile for similar roles.

Based on my experience, skills, and the market range for this position, would there be flexibility to adjust the compensation to ₹{target:,.0f}? This would better align with industry standards and reflect my ability to contribute from day one.

I'm open to discussing alternatives like a signing bonus, accelerated review, or enhanced variable pay if base adjustment isn't possible.

Looking forward to finding a solution that works for us both.

Best regards,
[Your Name]"""

    def _get_notice_script(self, current: int, target: int) -> str:
        return f"""Dear [Hiring Manager],

I'm thrilled about the opportunity to join [Company]!

I noticed the notice period is set at {current} days. Given that product companies typically have 30-45 day notice periods, would it be possible to reduce this to {target} days?

I understand the importance of proper handover and am committed to ensuring a smooth transition whenever the time comes. A shorter notice period would help me commit more confidently to a long-term career with [Company].

Would you be open to discussing this?

Best regards,
[Your Name]"""

    def _get_bond_script(self, amount: float) -> str:
        return f"""Dear [Hiring Manager],

Thank you for the offer! I'm very interested in the role.

I noticed there's a training bond of ₹{amount:,.0f} in the terms. I'd like to understand:
1. What specific training does this cover?
2. Is the bond pro-rated based on tenure?
3. Can it be waived after 12 months of service?

I'm committed to a long-term career with [Company] and would appreciate if we could discuss alternative arrangements for this clause.

Looking forward to your response.

Best regards,
[Your Name]"""
