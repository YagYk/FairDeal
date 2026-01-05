"""
Clause matching service for runtime comparison.
Matches user contract clauses against pre-processed knowledge base.
"""
from typing import List, Dict, Any, Optional
from loguru import logger
from app.db.chroma_client import ChromaClient
from app.services.stats_service import StatsService


class ClauseMatcher:
    """
    Fast clause matching using pre-computed statistics.
    No LLM calls - just pattern matching and percentile lookup.
    """
    
    def __init__(self):
        self.stats_service = StatsService()
        self.chroma_client = ChromaClient()
    
    def match_clauses(
        self,
        metadata: Dict[str, Any],
        percentile_rankings: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Match contract clauses against knowledge base.
        Returns red flags, favorable terms, and negotiation priorities.
        """
        logger.info("Matching clauses using pre-computed statistics")
        
        red_flags = []
        favorable_terms = []
        negotiation_priorities = []
        
        # Check salary percentile
        if "salary" in percentile_rankings:
            salary_pct = percentile_rankings["salary"]
            if salary_pct < 25:
                red_flags.append({
                    "issue": "Below-market salary",
                    "explanation": f"Your salary is in the {salary_pct:.1f}th percentile, significantly below market average.",
                    "severity": "high",
                    "recommendation": "Negotiate for a salary increase to at least the 50th percentile."
                })
                negotiation_priorities.append({
                    "priority": "Salary increase",
                    "reason": f"Current salary is below {salary_pct:.1f}th percentile. Market median would be significantly higher."
                })
            elif salary_pct >= 75:
                favorable_terms.append({
                    "term": "Above-market salary",
                    "explanation": f"Your salary is in the {salary_pct:.1f}th percentile, above market average.",
                    "value": f"{metadata.get('salary', 0):,} INR"
                })
        
        # Check notice period
        if "notice_period" in percentile_rankings:
            notice_pct = percentile_rankings["notice_period"]
            if notice_pct > 75:
                red_flags.append({
                    "issue": "Long notice period",
                    "explanation": f"Your notice period is in the {notice_pct:.1f}th percentile, longer than most contracts.",
                    "severity": "medium",
                    "recommendation": "Negotiate for a shorter notice period (30-60 days is standard)."
                })
                negotiation_priorities.append({
                    "priority": "Reduce notice period",
                    "reason": f"Current notice period ({metadata.get('notice_period_days', 0)} days) is longer than {notice_pct:.1f}% of similar contracts."
                })
            elif notice_pct < 25:
                favorable_terms.append({
                    "term": "Short notice period",
                    "explanation": f"Your notice period is in the {notice_pct:.1f}th percentile, shorter than most contracts.",
                    "value": f"{metadata.get('notice_period_days', 0)} days"
                })
        
        # Check non-compete
        if metadata.get("non_compete", False):
            red_flags.append({
                "issue": "Non-compete clause present",
                "explanation": "Non-compete clauses can restrict future employment opportunities.",
                "severity": "medium",
                "recommendation": "Review the scope and duration of the non-compete clause. Consider negotiating for limitations."
            })
        
        # Check for missing benefits
        benefits = metadata.get("benefits", [])
        if not benefits or len(benefits) < 3:
            red_flags.append({
                "issue": "Limited benefits",
                "explanation": "Contract mentions few or no benefits compared to market standards.",
                "severity": "low",
                "recommendation": "Negotiate for standard benefits like health insurance, provident fund, and gratuity."
            })
        
        return {
            "red_flags": red_flags,
            "favorable_terms": favorable_terms,
            "negotiation_priorities": negotiation_priorities,
        }

