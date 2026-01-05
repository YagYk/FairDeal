"""
Explanation service for generating detailed justifications and transparency reports.
Provides comprehensive explanations for all analysis results.
"""
from typing import Dict, Any, List, Optional
from loguru import logger
from app.services.llm_service import LLMService
from app.models.contract_schema import ContractMetadata


class ExplanationService:
    """
    Service for generating detailed explanations and justifications.
    
    Provides:
    - Detailed reasoning for fairness scores
    - Explanation of percentile rankings
    - Justification for red flags and favorable terms
    - Data source transparency
    - Market comparison context
    """
    
    def __init__(self):
        self.llm_service = LLMService()
    
    def generate_detailed_explanation(
        self,
        metadata: ContractMetadata,
        percentile_rankings: Dict[str, float],
        market_stats: Dict[str, Any],
        similar_contracts: List[Dict[str, Any]],
        red_flags: List[Any],
        favorable_terms: List[Any],
        fairness_score: int,
    ) -> Dict[str, Any]:
        """
        Generate comprehensive explanation report.
        
        Returns:
            Detailed explanation with reasoning for all assessments
        """
        logger.info("Generating detailed explanation report")
        
        # Build data source transparency
        data_sources = self._build_data_sources_report(similar_contracts, market_stats)
        
        # Generate detailed explanations
        explanations = {
            "fairness_score_explanation": self._explain_fairness_score(
                fairness_score, percentile_rankings, red_flags, favorable_terms
            ),
            "percentile_explanations": self._explain_percentiles(
                metadata, percentile_rankings, market_stats
            ),
            "red_flags_explanations": self._explain_red_flags(
                red_flags, metadata, market_stats
            ),
            "favorable_terms_explanations": self._explain_favorable_terms(
                favorable_terms, metadata, market_stats
            ),
            "negotiation_recommendations": self._generate_negotiation_recommendations(
                metadata, percentile_rankings, red_flags, market_stats
            ),
            "overall_assessment": self._generate_overall_assessment(
                metadata, fairness_score, percentile_rankings, red_flags, favorable_terms
            ),
        }
        
        return {
            "data_sources": data_sources,
            "explanations": explanations,
            "confidence_metrics": self._compute_confidence_metrics(
                similar_contracts, market_stats
            ),
        }
    
    def _build_data_sources_report(
        self,
        similar_contracts: List[Dict[str, Any]],
        market_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build transparency report on data sources."""
        # Extract unique contract IDs from similar contracts
        contract_ids = set()
        contract_details = []
        
        for contract in similar_contracts[:10]:  # Top 10 for display
            contract_id = contract.get("contract_id") or contract.get("metadata", {}).get("contract_id")
            if contract_id:
                contract_ids.add(contract_id)
                contract_details.append({
                    "contract_id": contract_id,
                    "similarity_score": round(contract.get("similarity_score", 0) * 100, 1),
                    "contract_type": contract.get("metadata", {}).get("contract_type"),
                    "industry": contract.get("metadata", {}).get("industry"),
                    "role": contract.get("metadata", {}).get("role"),
                })
        
        return {
            "knowledge_base_contracts_used": len(contract_ids),
            "total_contracts_in_knowledge_base": market_stats.get("total_contracts", 0),
            "similar_contracts_details": contract_details,
            "data_quality": {
                "sample_size": market_stats.get("sample_size", 0),
                "coverage": "High" if len(contract_ids) >= 10 else "Medium" if len(contract_ids) >= 5 else "Low",
                "relevance": "High" if contract_details and contract_details[0].get("similarity_score", 0) > 70 else "Medium",
            },
        }
    
    def _explain_fairness_score(
        self,
        score: int,
        percentiles: Dict[str, float],
        red_flags: List[Any],
        favorable_terms: List[Any],
    ) -> Dict[str, Any]:
        """Generate detailed explanation of fairness score."""
        score_category = "Excellent" if score >= 80 else "Good" if score >= 60 else "Fair" if score >= 40 else "Poor"
        
        factors = []
        
        # Salary factor
        if percentiles.get("salary"):
            salary_pct = percentiles["salary"]
            if salary_pct >= 70:
                factors.append(f"Salary is in the top {100 - salary_pct:.0f}% of similar contracts (excellent)")
            elif salary_pct >= 40:
                factors.append(f"Salary is in the {salary_pct:.0f}th percentile (average)")
            else:
                factors.append(f"Salary is in the bottom {salary_pct:.0f}% of similar contracts (below average)")
        
        # Notice period factor
        if percentiles.get("notice_period"):
            notice_pct = percentiles["notice_period"]
            if notice_pct <= 30:
                factors.append(f"Notice period is shorter than {100 - notice_pct:.0f}% of similar contracts (favorable)")
            elif notice_pct <= 60:
                factors.append(f"Notice period is in the {notice_pct:.0f}th percentile (standard)")
            else:
                factors.append(f"Notice period is longer than {notice_pct:.0f}% of similar contracts (unfavorable)")
        
        # Red flags impact
        red_flag_count = len(red_flags)
        if red_flag_count == 0:
            factors.append("No significant red flags identified")
        elif red_flag_count <= 2:
            factors.append(f"{red_flag_count} minor concern(s) identified")
        else:
            factors.append(f"{red_flag_count} significant red flags identified (major concerns)")
        
        # Favorable terms impact
        favorable_count = len(favorable_terms)
        if favorable_count >= 3:
            factors.append(f"{favorable_count} favorable terms identified (strong contract)")
        elif favorable_count >= 1:
            factors.append(f"{favorable_count} favorable term(s) identified")
        
        explanation = f"""
Your contract has received a fairness score of {score}% ({score_category}).

This score is calculated based on:
{chr(10).join(f"• {factor}" for factor in factors)}

The score reflects how your contract compares to similar contracts in our knowledge base, considering:
- Market competitiveness of compensation and terms
- Presence of standard vs. unusual clauses
- Balance between employer and employee protections
- Industry and role-specific norms

A score of {score}% indicates that your contract is {'highly competitive and favorable' if score >= 80 else 'generally fair with some areas for improvement' if score >= 60 else 'below market standards in several areas' if score >= 40 else 'significantly below market standards and requires negotiation'}.
        """.strip()
        
        return {
            "score": score,
            "category": score_category,
            "explanation": explanation,
            "factors": factors,
            "calculation_method": "Weighted combination of percentile rankings, red flags count, favorable terms count, and clause analysis",
        }
    
    def _explain_percentiles(
        self,
        metadata: ContractMetadata,
        percentiles: Dict[str, float],
        market_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate detailed percentile explanations."""
        explanations = {}
        
        if percentiles.get("salary") and metadata.salary:
            salary_pct = percentiles["salary"]
            salary_stats = market_stats.get("salary", {})
            
            explanations["salary"] = {
                "your_value": f"₹{metadata.salary:,}",
                "percentile": salary_pct,
                "market_comparison": {
                    "median": f"₹{salary_stats.get('median', 0):,}",
                    "mean": f"₹{salary_stats.get('mean', 0):,}",
                    "p25": f"₹{salary_stats.get('p25', 0):,}",
                    "p75": f"₹{salary_stats.get('p75', 0):,}",
                },
                "explanation": f"""
Your salary of ₹{metadata.salary:,} places you in the {salary_pct:.1f}th percentile compared to similar contracts.

This means:
- {'Your salary is higher than' if salary_pct >= 50 else 'Your salary is lower than'} {abs(50 - salary_pct):.1f}% of similar contracts
- Market median: ₹{salary_stats.get('median', 0):,}
- Market average: ₹{salary_stats.get('mean', 0):,}
- {'Your salary is competitive and above market standards' if salary_pct >= 70 else 'Your salary is at market rate' if salary_pct >= 40 else 'Your salary is below market standards and should be negotiated'}

Based on {salary_stats.get('count', 0)} similar contracts in our knowledge base.
                """.strip(),
            }
        
        if percentiles.get("notice_period") and metadata.notice_period_days:
            notice_pct = percentiles["notice_period"]
            notice_stats = market_stats.get("notice_period", {})
            
            explanations["notice_period"] = {
                "your_value": f"{metadata.notice_period_days} days",
                "percentile": notice_pct,
                "market_comparison": {
                    "median": f"{notice_stats.get('median', 0)} days",
                    "mean": f"{notice_stats.get('mean', 0):.1f} days",
                    "p25": f"{notice_stats.get('p25', 0)} days",
                    "p75": f"{notice_stats.get('p75', 0)} days",
                },
                "explanation": f"""
Your notice period of {metadata.notice_period_days} days places you in the {notice_pct:.1f}th percentile.

For notice periods, lower is better:
- {'Your notice period is shorter than' if notice_pct <= 50 else 'Your notice period is longer than'} {abs(50 - notice_pct):.1f}% of similar contracts
- Market median: {notice_stats.get('median', 0)} days
- Market average: {notice_stats.get('mean', 0):.1f} days
- {'Your notice period is favorable and shorter than most' if notice_pct <= 30 else 'Your notice period is standard' if notice_pct <= 60 else 'Your notice period is longer than typical and may limit flexibility'}

Based on {notice_stats.get('count', 0)} similar contracts in our knowledge base.
                """.strip(),
            }
        
        return explanations
    
    def _explain_red_flags(
        self,
        red_flags: List[Any],
        metadata: ContractMetadata,
        market_stats: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate detailed explanations for each red flag."""
        explanations = []
        
        for i, flag in enumerate(red_flags, 1):
            if isinstance(flag, dict):
                flag_text = flag.get("issue") or flag.get("title") or str(flag)
                flag_explanation = flag.get("explanation") or ""
            else:
                flag_text = str(flag)
                flag_explanation = ""
            
            explanations.append({
                "flag_number": i,
                "issue": flag_text,
                "explanation": flag_explanation or f"This is identified as a concern based on comparison with similar contracts in our knowledge base.",
                "severity": "High" if "non-compete" in flag_text.lower() or "termination" in flag_text.lower() else "Medium",
                "recommendation": "Should be negotiated or clarified before signing",
            })
        
        return explanations
    
    def _explain_favorable_terms(
        self,
        favorable_terms: List[Any],
        metadata: ContractMetadata,
        market_stats: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Generate detailed explanations for each favorable term."""
        explanations = []
        
        for i, term in enumerate(favorable_terms, 1):
            if isinstance(term, dict):
                term_text = term.get("term") or term.get("title") or str(term)
                term_explanation = term.get("explanation") or ""
            else:
                term_text = str(term)
                term_explanation = ""
            
            explanations.append({
                "term_number": i,
                "term": term_text,
                "explanation": term_explanation or f"This is identified as a favorable term compared to similar contracts.",
                "value": "High" if "salary" in term_text.lower() or "benefit" in term_text.lower() else "Medium",
            })
        
        return explanations
    
    def _generate_negotiation_recommendations(
        self,
        metadata: ContractMetadata,
        percentiles: Dict[str, float],
        red_flags: List[Any],
        market_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate detailed negotiation recommendations."""
        recommendations = []
        priority = "High"
        
        # Salary recommendation
        if percentiles.get("salary") and percentiles["salary"] < 50:
            recommendations.append({
                "item": "Salary",
                "current": f"₹{metadata.salary:,}",
                "recommended": f"₹{market_stats.get('salary', {}).get('p75', metadata.salary):,.0f}",
                "reason": f"Your salary is in the {percentiles['salary']:.1f}th percentile. Negotiating to the 75th percentile would bring you closer to top market rates.",
                "priority": "High",
            })
        
        # Notice period recommendation
        if percentiles.get("notice_period") and percentiles["notice_period"] > 60:
            recommendations.append({
                "item": "Notice Period",
                "current": f"{metadata.notice_period_days} days",
                "recommended": f"{market_stats.get('notice_period', {}).get('p25', metadata.notice_period_days):.0f} days",
                "reason": f"Your notice period is longer than {percentiles['notice_period']:.1f}% of similar contracts. A shorter notice period provides more flexibility.",
                "priority": "Medium",
            })
        
        # Red flags recommendations
        for flag in red_flags[:3]:  # Top 3
            if isinstance(flag, dict):
                flag_text = flag.get("issue") or flag.get("title") or str(flag)
            else:
                flag_text = str(flag)
            
            recommendations.append({
                "item": flag_text,
                "current": "Present in contract",
                "recommended": "Negotiate removal or modification",
                "reason": "This clause is identified as unfavorable compared to market standards.",
                "priority": "High" if "non-compete" in flag_text.lower() else "Medium",
            })
        
        return {
            "should_negotiate": len(recommendations) > 0,
            "recommendations": recommendations,
            "overall_advice": "Negotiate" if len(recommendations) >= 3 else "Consider negotiating" if len(recommendations) >= 1 else "Contract is generally fair",
        }
    
    def _generate_overall_assessment(
        self,
        metadata: ContractMetadata,
        fairness_score: int,
        percentiles: Dict[str, float],
        red_flags: List[Any],
        favorable_terms: List[Any],
    ) -> Dict[str, Any]:
        """Generate overall contract assessment."""
        assessment = "Excellent" if fairness_score >= 80 else "Good" if fairness_score >= 60 else "Fair" if fairness_score >= 40 else "Needs Improvement"
        
        summary = f"""
Overall Assessment: {assessment}

Your contract has been analyzed against {len(red_flags) + len(favorable_terms)} key factors and compared with similar contracts in our knowledge base.

Key Findings:
• Fairness Score: {fairness_score}% ({assessment})
• Red Flags: {len(red_flags)} concern(s) identified
• Favorable Terms: {len(favorable_terms)} positive aspect(s) identified
• Market Comparison: {'Above average' if fairness_score >= 60 else 'At market rate' if fairness_score >= 40 else 'Below market standards'}

{'Your contract is competitive and generally favorable. Minor negotiations may still be beneficial.' if fairness_score >= 70 else 'Your contract is acceptable but has room for improvement. Consider negotiating key terms.' if fairness_score >= 50 else 'Your contract has several areas that should be negotiated before signing.'}
        """.strip()
        
        return {
            "assessment": assessment,
            "summary": summary,
            "signing_recommendation": "Sign as-is" if fairness_score >= 80 else "Sign after minor negotiations" if fairness_score >= 60 else "Negotiate before signing" if fairness_score >= 40 else "Strongly recommend negotiation",
        }
    
    def _compute_confidence_metrics(
        self,
        similar_contracts: List[Dict[str, Any]],
        market_stats: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compute confidence metrics for the analysis."""
        sample_size = market_stats.get("sample_size", len(similar_contracts))
        
        confidence = "High" if sample_size >= 20 else "Medium" if sample_size >= 10 else "Low"
        
        return {
            "confidence_level": confidence,
            "sample_size": sample_size,
            "data_quality": "High" if sample_size >= 20 else "Medium" if sample_size >= 10 else "Low",
            "explanation": f"Analysis based on {sample_size} similar contracts. {'High confidence' if sample_size >= 20 else 'Medium confidence' if sample_size >= 10 else 'Lower confidence - consider adding more contracts to knowledge base'}.",
        }

