"""
Contract analysis service.
Orchestrates the complete analysis pipeline:
1. Extract metadata from user contract
2. Retrieve similar contracts using RAG
3. Compute statistics and percentiles
4. Generate insights and negotiation scripts
"""
from typing import Dict, Any, List, Optional
from loguru import logger
from pathlib import Path
import tempfile
import os

from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.services.llm_service import LLMService
from app.services.rag_service import RAGService
from app.services.stats_service import StatsService
from app.services.explanation_service import ExplanationService
from app.services.fast_extraction_service import FastExtractionService
from app.services.clause_matcher import ClauseMatcher
from app.models.contract_schema import ContractMetadata


class AnalysisService:
    """
    Service for analyzing user-uploaded contracts.
    
    Pipeline:
    1. Parse uploaded file → extract text
    2. Extract metadata using LLM
    3. Retrieve similar contracts using RAG
    4. Compute percentiles and statistics
    5. Generate insights and negotiation scripts
    """
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.llm_service = LLMService()
        self.rag_service = RAGService()
        self.stats_service = StatsService()
        self.explanation_service = ExplanationService()
        self.fast_extraction = FastExtractionService()
        self.clause_matcher = ClauseMatcher()
    
    def analyze_contract(
        self,
        file_content: bytes,
        filename: str,
    ) -> Dict[str, Any]:
        """
        Analyze a user-uploaded contract.
        
        Args:
            file_content: Raw file bytes
            filename: Original filename
            
        Returns:
            Complete analysis result with:
            - fairness_score
            - contract_metadata
            - percentile_rankings
            - red_flags
            - favorable_terms
            - negotiation_priorities
            - negotiation_scripts
            - similar_contracts (for explainability)
        """
        import time
        start_time = time.time()
        logger.info(f"Starting analysis for: {filename}")
        
        # Step 1: Parse document
        step_start = time.time()
        text = self._parse_file(file_content, filename)
        logger.info(f"Step 1 (Parse): {time.time() - step_start:.2f}s - Extracted {len(text)} characters")
        
        # Step 2: Fast extraction using rules (NO LLM)
        step_start = time.time()
        metadata = self.fast_extraction.extract_metadata(text)
        logger.info(f"Step 2 (Fast Extract): {time.time() - step_start:.2f}s - {metadata.contract_type}, {metadata.industry}, {metadata.role}")
        
        # QUALITY CHECK: If fast extraction missed critical fields, use LLM fallback
        # Helper to safely get value
        def get_val(field):
            if hasattr(field, 'value'):
                return field.value
            elif isinstance(field, dict):
                return field.get('value')
            return field
        
        # DISABLED LLM FALLBACK TO AVOID RATE LIMITS
        # The fast extraction is now sufficient for basic functionality.
        # To re-enable, uncomment the block below.
        # if not get_val(metadata.salary) or not get_val(metadata.role):
        #     logger.info("Fast extraction yielded incomplete data. Falling back to LLM...")
        #     try:
        #         llm_metadata = self.llm_service.extract_contract_metadata(text)
        #         ... (merge logic)
        #     except Exception as e:
        #         logger.error(f"LLM Fallback failed: {e}")
        logger.info("Skipping LLM fallback (disabled to avoid rate limits)")

        # Step 3: Compute percentiles (using pre-computed stats)
        step_start = time.time()
        percentile_rankings = self._compute_percentiles(metadata)
        logger.info(f"Step 3 (Percentiles): {time.time() - step_start:.2f}s")
        
        # Step 4: Retrieve similar contracts using RAG (Resilient)
        step_start = time.time()
        similar_contracts = []
        try:
            # Helper to safely get value
            def get_val(field):
                if hasattr(field, 'value'):
                    return field.value
                elif isinstance(field, dict):
                    return field.get('value')
                return field
            
            # Build query from metadata to find structurally similar contracts
            role_val = get_val(metadata.role) or 'Employee'
            industry_val = get_val(metadata.industry) or 'general'
            contract_type_val = get_val(metadata.contract_type) or 'employment'
            rag_query = f"{role_val} contract in {industry_val} industry. {contract_type_val}"
            similar_contracts = self.rag_service.retrieve_similar_contracts(
                query_text=rag_query,
                n_results=5,
                filters={"contract_type": contract_type_val} if contract_type_val else None
            )
            logger.info(f"Step 4 (RAG): {time.time() - step_start:.2f}s - Retrieved {len(similar_contracts)} similar contracts")
        except Exception as e:
            logger.warning(f"Step 4 (RAG) failed/skipped: {e}. Proceeding without comparison.")
            # Verify if this was a rate limit
            if "429" in str(e) or "quota" in str(e).lower():
                logger.warning("RAG skipped due to rate limit")

        
        # Step 5: Match clauses (NO LLM, uses pre-computed stats)
        step_start = time.time()
        # Helper to safely extract value
        def get_val(field):
            if hasattr(field, 'value'):
                return field.value
            elif isinstance(field, dict):
                val = field.get('value')
                # If value is still a dict, extract nested value
                if isinstance(val, dict):
                    return val.get('value')
                return val
            return field
        
        # Flatten metadata for clause matcher
        flat_metadata = {
            "salary": get_val(metadata.salary),
            "notice_period_days": get_val(metadata.notice_period_days),
            "contract_type": get_val(metadata.contract_type),
            "industry": get_val(metadata.industry),
            "role": get_val(metadata.role),
            "location": get_val(metadata.location),
            "non_compete": get_val(metadata.non_compete),
        }
        
        clause_insights = self.clause_matcher.match_clauses(
            metadata=flat_metadata,  # flatten for compatibility
            percentile_rankings=percentile_rankings,
        )
        logger.info(f"Step 5 (Clause Match): {time.time() - step_start:.2f}s")
        
        # Step 6: Get similar contracts count (fast, from RAG + stats)
        step_start = time.time()
        similar_contracts_count = self._get_similar_contracts_count(metadata)
        # Combine RAG count with total DB count logic if needed, but for now specific count is fine
        logger.info(f"Step 6 (Similar Count): {time.time() - step_start:.2f}s - Total pool: {similar_contracts_count}")
        
        # Step 7: Compute fairness score
        step_start = time.time()
        fairness_score = self._compute_fairness_score(
            metadata=metadata,
            percentile_rankings=percentile_rankings,
            insights=clause_insights,
        )
        logger.info(f"Step 7 (Fairness Score): {time.time() - step_start:.2f}s")
        
        # Step 8: Get market stats (pre-computed)
        step_start = time.time()
        market_stats = self._get_market_stats(metadata)
        market_stats["sample_size"] = similar_contracts_count
        market_stats["total_contracts"] = similar_contracts_count
        
        # Generate lightweight explanation (no LLM, just structure data)
        # Pass the actual similar_contracts here!
        detailed_explanation = self._generate_fast_explanation(
            metadata=metadata,
            percentile_rankings=percentile_rankings,
            market_stats=market_stats,
            similar_contracts=similar_contracts,
            red_flags=clause_insights.get("red_flags", []),
            favorable_terms=clause_insights.get("favorable_terms", []),
            fairness_score=fairness_score,
        )
        logger.info(f"Step 8 (Explanation): {time.time() - step_start:.2f}s")
        
        # Step 9: Generate template-based narration (NO LLM to avoid rate limits)
        step_start = time.time()
        contract_type_val = get_val(metadata.contract_type) or 'employment'
        role_val = get_val(metadata.role) or 'employee'
        salary_val = get_val(metadata.salary)
        industry_val = get_val(metadata.industry) or 'general'
        
        # Build intelligent template-based narration
        narration_parts = []
        narration_parts.append(f"This {contract_type_val} contract for a {role_val} position in the {industry_val} industry has a fairness score of {fairness_score}/100.")
        
        if salary_val and "salary" in percentile_rankings:
            pct = percentile_rankings["salary"]
            if pct >= 70:
                narration_parts.append(f"The salary of ₹{salary_val:,.0f} is above average (top {100-pct:.0f}% of similar contracts).")
            elif pct <= 30:
                narration_parts.append(f"The salary of ₹{salary_val:,.0f} is below average and may be worth negotiating.")
            else:
                narration_parts.append(f"The salary of ₹{salary_val:,.0f} is around the market median.")
        
        red_flag_count = len(clause_insights.get("red_flags", []))
        favorable_count = len(clause_insights.get("favorable_terms", []))
        
        if red_flag_count > 0:
            narration_parts.append(f"Found {red_flag_count} potential concern(s) to review.")
        if favorable_count > 0:
            narration_parts.append(f"Identified {favorable_count} favorable term(s).")
        
        narration = " ".join(narration_parts)
        logger.info(f"Step 9 (Template Narration): {time.time() - step_start:.2f}s")
        
        total_time = time.time() - start_time
        logger.info(f"Analysis complete in {total_time:.2f}s. Fairness score: {fairness_score}")
        
        # Helper to convert ExtractedField to simple value for API response
        def extract_for_api(field):
            """Extract value from ExtractedField for API response."""
            if hasattr(field, 'value'):
                return field.value
            elif isinstance(field, dict):
                return field.get('value')
            return field
        
        # Convert metadata to dict with simple values (not ExtractedField objects)
        metadata_dict = {
            "contract_type": extract_for_api(metadata.contract_type),
            "industry": extract_for_api(metadata.industry),
            "role": extract_for_api(metadata.role),
            "location": extract_for_api(metadata.location),
            "salary": extract_for_api(metadata.salary),
            "notice_period_days": extract_for_api(metadata.notice_period_days),
            "non_compete": extract_for_api(metadata.non_compete),
            "termination_clauses": extract_for_api(metadata.termination_clauses) or [],
            "benefits": extract_for_api(metadata.benefits) or [],
            "risky_clauses": extract_for_api(metadata.risky_clauses) or [],
        }
        
        return {
            "fairness_score": fairness_score,
            "contract_metadata": metadata_dict,
            "percentile_rankings": percentile_rankings,
            "red_flags": clause_insights.get("red_flags", []),
            "favorable_terms": clause_insights.get("favorable_terms", []),
            "negotiation_priorities": clause_insights.get("negotiation_priorities", []),
            "negotiation_scripts": [],  # Can be added later if needed
            "similar_contracts_count": similar_contracts_count,
            "similar_contracts_details": similar_contracts, # Return actual details
            "market_statistics": market_stats,
            "detailed_explanation": detailed_explanation,
            "narration": narration,  # Single LLM-generated summary
        }
    
    def _parse_file(self, file_content: bytes, filename: str) -> str:
        """Parse file content and extract text."""
        suffix = Path(filename).suffix.lower()
        
        # Handle plain text files directly
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
            # Clean up temp file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    
    def _get_similar_contracts_count(
        self,
        metadata: ContractMetadata,
    ) -> int:
        """Get count of similar contracts (fast, no RAG needed)."""
        # Helper to safely extract value
        def get_val(field):
            if hasattr(field, 'value'):
                return field.value
            elif isinstance(field, dict):
                val = field.get('value')
                if isinstance(val, dict):
                    return val.get('value')
                return val
            return field
        
        # Use stats service to count similar contracts
        contracts = self.stats_service._get_all_contracts_metadata(
            contract_type=get_val(metadata.contract_type),
            industry=get_val(metadata.industry),
            role=get_val(metadata.role),
            location=get_val(metadata.location),
        )
        return len(contracts)
    
    def _generate_narration(
        self,
        metadata: ContractMetadata,
        percentile_rankings: Dict[str, float],
        fairness_score: int,
        red_flags: List[Any],
        favorable_terms: List[Any],
        similar_count: int = 0,
    ) -> str:
        """Generate single LLM narration summarizing the analysis."""
        logger.info("Generating narration (single LLM call)")
        
        # Build concise prompt
        # Helper to safely get value
        def get_val(field):
            if hasattr(field, 'value'):
                return field.value
            elif isinstance(field, dict):
                val = field.get('value')
                if isinstance(val, dict):
                    return val.get('value')
                return val
            return field
        
        # Build concise prompt
        contract_type_val = get_val(metadata.contract_type) or 'employment'
        role_val = get_val(metadata.role) or 'employee'
        industry_val = get_val(metadata.industry) or 'general'
        
        prompt = f"""Summarize this contract analysis in 2-3 sentences based DIRECTLY on the provided data:

Contract: {contract_type_val} contract for {role_val} in {industry_val} industry
Fairness Score: {fairness_score}/100
Salary Percentile: {percentile_rankings.get('salary', 'N/A')}%
Notice Period Percentile: {percentile_rankings.get('notice_period', 'N/A')}%
Red Flags: {len(red_flags)}
Favorable Terms: {len(favorable_terms)}
Similar Contracts Found in Database: {similar_count}

CRITICAL INSTRUCTIONS:
1. Do NOT hallucinate statistics.
2. If "Similar Contracts Found" is 0, do NOT mention comparison with other contracts or industry standards. Just focus on the contract terms itself.
3. If "Similar Contracts Found" is > 0, you can mention how it compares to the {similar_count} similar contracts found.
4. Be professional and concise.

Provide a brief, professional summary of whether this contract is fair and what the user should know."""
        
        try:
            narration = self.llm_service._call_llm(prompt, max_tokens=200)
            return narration.strip()
        except Exception as e:
            logger.error(f"Narration generation failed: {e}")
            return f"This {contract_type_val} contract has a fairness score of {fairness_score}/100. Review the detailed analysis below."
    
    def _compute_percentiles(self, metadata: ContractMetadata) -> Dict[str, float]:
        """Compute percentile rankings for numeric fields."""
        rankings = {}
        
        # Helper to safely extract value from ExtractedField
        def get_value(extracted_field):
            if extracted_field is None:
                return None
            # If it's an ExtractedField object, get .value
            if hasattr(extracted_field, 'value'):
                val = extracted_field.value
            # If it's a dict, get the 'value' key
            elif isinstance(extracted_field, dict):
                val = extracted_field.get('value')
            else:
                val = extracted_field
            
            # Ensure it's not a dict - recursively extract if needed
            while isinstance(val, dict):
                if 'value' in val:
                    val = val.get('value')
                else:
                    # If it's a dict but no 'value' key, it's not a valid ExtractedField structure
                    logger.warning(f"Value is a dict without 'value' key: {val}")
                    return None
            
            # Ensure it's a number if we expect one
            if val is not None and not isinstance(val, (int, float, str, bool, type(None))):
                logger.warning(f"Unexpected value type: {type(val)}, value: {val}")
                return None
                
            return val
        
        salary_val = get_value(metadata.salary)
        if salary_val and isinstance(salary_val, (int, float)):
            rankings["salary"] = self.stats_service.compute_percentile(
                value=float(salary_val),
                field_name="salary",
                contract_type=get_value(metadata.contract_type),
                industry=get_value(metadata.industry),
                role=get_value(metadata.role),
                location=get_value(metadata.location),
            )
        
        notice_val = get_value(metadata.notice_period_days)
        if notice_val and isinstance(notice_val, (int, float)):
            rankings["notice_period"] = self.stats_service.compute_percentile(
                value=float(notice_val),
                field_name="notice_period_days",
                contract_type=get_value(metadata.contract_type),
                industry=get_value(metadata.industry),
                role=get_value(metadata.role),
                location=get_value(metadata.location),
            )
        
        return rankings
    
    def _get_market_stats(self, metadata: ContractMetadata) -> Dict[str, Any]:
        """Get market statistics for context."""
        stats = {}
        
        # Helper to safely extract value from ExtractedField
        def get_value(extracted_field):
            if extracted_field is None:
                return None
            if hasattr(extracted_field, 'value'):
                val = extracted_field.value
            elif isinstance(extracted_field, dict):
                val = extracted_field.get('value')
            else:
                val = extracted_field
            if isinstance(val, dict):
                return val.get('value') if 'value' in val else None
            return val
        
        salary_val = get_value(metadata.salary)
        if salary_val:
            stats["salary"] = self.stats_service.get_market_statistics(
                field_name="salary",
                contract_type=get_value(metadata.contract_type),
                industry=get_value(metadata.industry),
                role=get_value(metadata.role),
                location=get_value(metadata.location),
            )
        
        notice_val = get_value(metadata.notice_period_days)
        if notice_val:
            notice_stats = self.stats_service.get_market_statistics(
                field_name="notice_period_days",
                contract_type=get_value(metadata.contract_type),
                industry=get_value(metadata.industry),
                role=get_value(metadata.role),
                location=get_value(metadata.location),
            )
            stats["notice_period"] = notice_stats
        
        return stats
    
    def _compute_fairness_score(
        self,
        metadata: ContractMetadata,
        percentile_rankings: Dict[str, float],
        insights: Dict[str, Any],
    ) -> int:
        """
        Compute overall fairness score (0-100).
        
        Factors:
        - Salary percentile (higher is better)
        - Notice period percentile (lower is better for employee)
        - Red flags count (fewer is better)
        - Favorable terms count (more is better)
        - Non-compete clause (absence is better)
        """
        score = 50  # Base score
        
        # Salary impact (0-20 points)
        if "salary" in percentile_rankings:
            salary_pct = percentile_rankings["salary"]
            score += (salary_pct - 50) * 0.2  # Scale to ±10 points
        
        # Notice period impact (0-15 points)
        if "notice_period" in percentile_rankings:
            notice_pct = percentile_rankings["notice_period"]
            # Lower notice period is better (inverse)
            score += (100 - notice_pct - 50) * 0.15  # Scale to ±7.5 points
        
        # Red flags impact (-5 points each)
        red_flags = insights.get("red_flags", [])
        score -= len(red_flags) * 5
        
        # Favorable terms impact (+3 points each)
        favorable = insights.get("favorable_terms", [])
        score += len(favorable) * 3
        
        # Non-compete impact (-10 points if present)
        def get_val(field):
            if hasattr(field, 'value'):
                return field.value
            elif isinstance(field, dict):
                val = field.get('value')
                if isinstance(val, dict):
                    return val.get('value')
                return val
            return field
        
        if get_val(metadata.non_compete):
            score -= 10
        
        # Clamp to 0-100
        score = max(0, min(100, int(score)))
        
        return score
    
    def _generate_fast_explanation(
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
        Generate lightweight explanation without LLM calls for speed.
        This is much faster than the full ExplanationService.
        """
        # Build data sources info
        data_sources = {
            "knowledge_base_contracts_used": len(similar_contracts),
            "total_contracts_in_knowledge_base": len(similar_contracts),
            "data_quality": {
                "sample_size": len(similar_contracts),
                "coverage": "good" if len(similar_contracts) >= 10 else "limited",
                "relevance": "high" if len(similar_contracts) >= 5 else "medium",
            },
            "similar_contracts_details": [
                {
                    "contract_id": c.get("contract_id") or c.get("metadata", {}).get("contract_id", "unknown"),
                    "similarity_score": round(c.get("similarity_score", 0), 3),
                    "contract_type": c.get("metadata", {}).get("contract_type"),
                    "industry": c.get("metadata", {}).get("industry"),
                }
                for c in similar_contracts[:5]
            ],
        }
        
        # Build simple explanations
        explanations = {
            "overall_assessment": {
                "assessment": f"Fairness Score: {fairness_score}/100",
                "summary": f"This contract has a fairness score of {fairness_score}% based on market comparison.",
                "signing_recommendation": "Review carefully" if fairness_score < 70 else "Generally fair",
            },
            "fairness_score_explanation": {
                "score": fairness_score,
                "category": "Good" if fairness_score >= 70 else "Needs Review" if fairness_score >= 50 else "Poor",
                "explanation": f"Based on comparison with {len(similar_contracts)} similar contracts, this contract scores {fairness_score}%.",
                "factors": ["Salary percentile", "Notice period", "Red flags", "Favorable terms"],
                "calculation_method": "Weighted scoring based on market percentiles and clause analysis",
            },
        }
        
        # Add percentile explanations
        percentile_explanations = {}
        if "salary" in percentile_rankings:
            pct = percentile_rankings["salary"]
            percentile_explanations["salary"] = {
                "percentile": round(pct, 1),
                "explanation": f"Your salary is in the {round(pct, 1)}th percentile compared to similar contracts.",
                "your_value": f"{metadata.salary.value:,} INR" if metadata.salary.value else "N/A",
                "market_comparison": market_stats.get("salary", {}),
            }
        
        if "notice_period" in percentile_rankings:
            pct = percentile_rankings["notice_period"]
            percentile_explanations["notice_period"] = {
                "percentile": round(pct, 1),
                "explanation": f"Your notice period is in the {round(pct, 1)}th percentile compared to similar contracts.",
                "your_value": f"{metadata.notice_period_days.value} days" if metadata.notice_period_days.value else "N/A",
                "market_comparison": market_stats.get("notice_period", {}),
            }
        
        if percentile_explanations:
            explanations["percentile_explanations"] = percentile_explanations
        
        # Add red flags and favorable terms
        if red_flags:
            explanations["red_flags_explanations"] = [
                {
                    "issue": flag.get("issue", flag) if isinstance(flag, dict) else str(flag),
                    "explanation": flag.get("explanation", "Review this clause carefully") if isinstance(flag, dict) else "Review this clause carefully",
                    "severity": flag.get("severity", "medium") if isinstance(flag, dict) else "medium",
                    "recommendation": flag.get("recommendation", "Consider negotiating") if isinstance(flag, dict) else "Consider negotiating",
                }
                for flag in red_flags[:5]
            ]
        
        if favorable_terms:
            explanations["favorable_terms_explanations"] = [
                {
                    "term": term.get("term", term) if isinstance(term, dict) else str(term),
                    "explanation": term.get("explanation", "This is a favorable term") if isinstance(term, dict) else "This is a favorable term",
                    "value": term.get("value", "N/A") if isinstance(term, dict) else "N/A",
                }
                for term in favorable_terms[:5]
            ]
        
        return {
            "data_sources": data_sources,
            "explanations": explanations,
            "confidence_metrics": {
                "confidence_level": "High" if len(similar_contracts) >= 10 else "Medium",
                "explanation": f"Based on {len(similar_contracts)} similar contracts in the database.",
                "sample_size": len(similar_contracts),
                "data_quality": "Good" if len(similar_contracts) >= 10 else "Limited",
            },
        }

