"""
Fast extraction service using rules + small model for runtime analysis.
Optimized for speed - no heavy LLM calls.
"""
import re
from typing import Dict, Any, Optional
from loguru import logger
from app.models.contract_schema import ContractMetadata, ExtractedField


class FastExtractionService:
    """
    Fast rule-based extraction for runtime analysis.
    Uses regex patterns and simple heuristics instead of LLM.
    """
    
    def __init__(self):
        # Patterns (keeping existing ones)
        self.salary_patterns = [
            r'(?:salary|compensation|remuneration|pay|CTC|cost to company)[\s:]*[₹]?\s*(\d+(?:[,\s]\d+)*(?:\s*lakhs?|\s*crores?|\s*k|\s*L)?)',
            r'(\d+(?:[,\s]\d+)*)\s*(?:lakhs?|L|LPA|per annum|annually)',
            r'₹\s*(\d+(?:[,\s]\d+)*)',
        ]
        
        self.notice_period_patterns = [
            r'notice[\s-]?period[\s:]*(\d+)\s*(?:days?|months?|weeks?)',
            r'(\d+)\s*(?:days?|months?|weeks?)[\s-]?notice',
            r'termination[\s-]?notice[\s:]*(\d+)',
        ]
        
        self.contract_type_keywords = {
            'employment': ['employment', 'job', 'work', 'employee', 'staff', 'worker'],
            'consulting': ['consulting', 'consultant', 'freelance', 'independent contractor'],
            'service_agreement': ['service', 'agreement', 'vendor', 'supplier'],
            'nda': ['nda', 'non-disclosure', 'confidentiality'],
            'non_compete': ['non-compete', 'noncompete', 'restrictive covenant'],
        }
        
        self.industry_keywords = {
            'technology': ['technology', 'tech', 'software', 'IT', 'computer', 'developer'],
            'finance': ['finance', 'financial', 'banking', 'investment', 'accounting'],
            'healthcare': ['healthcare', 'medical', 'hospital', 'clinic', 'doctor'],
            'manufacturing': ['manufacturing', 'production', 'factory', 'industrial'],
            'general': [],
        }
    
    def extract_metadata(self, contract_text: str) -> ContractMetadata:
        """
        Fast extraction using rules and patterns.
        Returns ContractMetadata with extracted fields.
        """
        logger.info("Fast extraction: Using rule-based extraction")
        
        # Extract all fields and convert to dicts for Pydantic validation
        contract_type = self._extract_contract_type(contract_text)
        industry = self._extract_industry(contract_text)
        role = self._extract_role(contract_text)
        location = self._extract_location(contract_text)
        salary = self._extract_salary(contract_text)
        notice_period_days = self._extract_notice_period(contract_text)
        non_compete = self._check_non_compete(contract_text)
        termination_clauses = self._extract_termination_clauses(contract_text)
        benefits = self._extract_benefits(contract_text)
        risky_clauses = self._extract_risky_clauses(contract_text)
        
        # Convert ExtractedField instances to dicts for Pydantic v2 validation
        def to_dict(extracted_field):
            if hasattr(extracted_field, 'model_dump'):
                return extracted_field.model_dump()
            elif hasattr(extracted_field, 'dict'):
                return extracted_field.dict()
            elif isinstance(extracted_field, dict):
                return extracted_field
            else:
                # Fallback: create dict from attributes
                return {
                    "value": getattr(extracted_field, 'value', None),
                    "confidence": getattr(extracted_field, 'confidence', 0.0),
                    "source_text": getattr(extracted_field, 'source_text', None),
                    "explanation": getattr(extracted_field, 'explanation', None),
                }
        
        # Use model_validate with dicts to ensure proper Pydantic v2 validation
        return ContractMetadata.model_validate({
            "contract_type": to_dict(contract_type),
            "industry": to_dict(industry),
            "role": to_dict(role),
            "location": to_dict(location),
            "salary": to_dict(salary),
            "notice_period_days": to_dict(notice_period_days),
            "non_compete": to_dict(non_compete),
            "termination_clauses": to_dict(termination_clauses),
            "benefits": to_dict(benefits),
            "risky_clauses": to_dict(risky_clauses),
        })
    
    def _extract_salary(self, text: str) -> ExtractedField[float]:
        text_lower = text.lower()
        for pattern in self.salary_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                value_str = match.group(1).replace(',', '').replace(' ', '')
                source_text = match.group(0)
                try:
                    value = 0.0
                    multiplier = 1.0
                    if 'lakh' in source_text.lower() or 'l' in source_text.lower():
                        multiplier = 100000.0
                    elif 'crore' in source_text.lower():
                        multiplier = 10000000.0
                    
                    value = float(value_str) * multiplier
                    
                    return ExtractedField(
                        value=value,
                        confidence=0.9,
                        source_text=source_text,
                        explanation="Extracted via regex pattern matching"
                    )
                except:
                    continue
        
        return ExtractedField(value=None, confidence=0.0, explanation="No salary pattern found")

    def _extract_notice_period(self, text: str) -> ExtractedField[int]:
        text_lower = text.lower()
        for pattern in self.notice_period_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                try:
                    value = int(match.group(1))
                    source_text = match.group(0)
                    if 'month' in source_text.lower():
                        value *= 30
                    elif 'week' in source_text.lower():
                        value *= 7
                        
                    return ExtractedField(
                        value=value,
                        confidence=0.95,
                        source_text=source_text
                    )
                except:
                    continue
        return ExtractedField(value=None, confidence=0.0)

    def _extract_contract_type(self, text: str) -> ExtractedField[str]:
        text_lower = text.lower()
        for contract_type, keywords in self.contract_type_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Find exact match span for source text
                    match_idx = text_lower.find(keyword)
                    source = text[match_idx:match_idx+len(keyword)] if match_idx != -1 else keyword
                    return ExtractedField(
                        value=contract_type,
                        confidence=0.8,
                        source_text=source
                    )
        return ExtractedField(value="employment", confidence=0.5, explanation="Defaulted to employment")

    def _extract_industry(self, text: str) -> ExtractedField[str]:
        text_lower = text.lower()
        for industry, keywords in self.industry_keywords.items():
            if industry == 'general': continue
            for keyword in keywords:
                if keyword in text_lower:
                    return ExtractedField(value=industry, confidence=0.85, source_text=keyword)
        return ExtractedField(value="general", confidence=0.5)

    def _extract_location(self, text: str) -> ExtractedField[str]:
        text_lower = text.lower()
        locations = ['mumbai', 'delhi', 'bangalore', 'chennai', 'hyderabad', 'pune', 'kolkata']
        for location in locations:
            if location in text_lower:
                return ExtractedField(value=location.capitalize(), confidence=0.9, source_text=location)
        if 'india' in text_lower:
            return ExtractedField(value="India", confidence=0.8, source_text="India")
        return ExtractedField(value="India", confidence=0.3, explanation="Defaulted")

    def _extract_role(self, text: str) -> ExtractedField[str]:
        text_lower = text.lower()
        role_patterns = [
            r'(?:position|role|designation|title)[\s:]*([a-z\s]+?)(?:\.|,|\n|$)',
            r'(?:as|for the position of)\s+([a-z\s]+?)(?:\.|,|\n|$)',
        ]
        for pattern in role_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                role = match.group(1).strip()
                if 3 < len(role) < 50:
                    return ExtractedField(
                        value=role.title(),
                        confidence=0.85,
                        source_text=match.group(0)
                    )
        return ExtractedField(value=None, confidence=0.0)

    def _check_non_compete(self, text: str) -> ExtractedField[bool]:
        text_lower = text.lower()
        keywords = ['non-compete', 'noncompete', 'restrictive covenant']
        for k in keywords:
            if k in text_lower:
                return ExtractedField(value=True, confidence=0.9, source_text=k)
        return ExtractedField(value=False, confidence=0.7)

    def _extract_termination_clauses(self, text: str) -> ExtractedField[list]:
        text_lower = text.lower()
        clauses = []
        if 'termination' in text_lower: clauses.append("Termination clause present")
        if 'resignation' in text_lower: clauses.append("Resignation terms specified")
        
        if clauses:
            return ExtractedField(value=clauses, confidence=0.8, source_text="detected termination keywords")
        return ExtractedField(value=[], confidence=0.0)

    def _extract_benefits(self, text: str) -> ExtractedField[list]:
        text_lower = text.lower()
        benefits = []
        keywords = {
            'health insurance': 'health insurance',
            'medical insurance': 'medical insurance',
            'provident fund': 'provident fund',
            'stock options': 'stock options'
        }
        found_source = []
        for k, v in keywords.items():
            if k in text_lower:
                benefits.append(v)
                found_source.append(k)
        
        return ExtractedField(value=benefits, confidence=0.9 if benefits else 0.0, source_text=", ".join(found_source))

    def _extract_risky_clauses(self, text: str) -> ExtractedField[list]:
        text_lower = text.lower()
        risky = []
        keywords = {'arbitration': 'Mandatory arbitration', 'liability': 'Liability limitation'}
        found_source = []
        for k, v in keywords.items():
            if k in text_lower:
                risky.append(v)
                found_source.append(k)
        return ExtractedField(value=risky, confidence=0.9 if risky else 0.0, source_text=", ".join(found_source))
