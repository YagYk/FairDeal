from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from .parser_service import ParsedDocument
from ..logging_config import get_logger
from ..models.schemas import (
    ContractExtractionResult,
    ExtractedClause,
    ExtractedField,
    ExtractionMethod,
)


log = get_logger("service.rule_extraction")


class RuleExtractionService:
    """
    Deterministic regex-based extraction for salary, notice period, bond, non-compete, probation, role, and company.
    Also handles basic clause block extraction.
    """

    def _safe_float(self, s: str | None) -> float | None:
        if not s:
            return None
        try:
            # Remove commas and other non-numeric chars except dot
            clean = re.sub(r"[^\d.]", "", s)
            return float(clean) if clean else None
        except:
            return None

    def _safe_int(self, s: str | None) -> int | None:
        if not s:
            return None
        try:
            clean = re.sub(r"[^\d]", "", s)
            return int(clean) if clean else None
        except:
            return None

    def extract(self, parsed: ParsedDocument) -> ContractExtractionResult:
        text = parsed.full_text
        
        result = ContractExtractionResult()

        # Extract fixed fields (Deterministic)
        result.ctc_inr = self._extract_field(text, parsed, "ctc_inr", self._extract_ctc_logic)
        result.notice_period_days = self._extract_field(text, parsed, "notice_period_days", self._extract_notice_logic)
        result.bond_amount_inr = self._extract_field(text, parsed, "bond_amount_inr", self._extract_bond_logic)
        result.non_compete_months = self._extract_field(text, parsed, "non_compete_months", self._extract_non_compete_logic)
        result.probation_months = self._extract_field(text, parsed, "probation_months", self._extract_probation_logic)
        result.role = self._extract_field(text, parsed, "role", self._extract_role_logic)
        result.company_type = self._extract_field(text, parsed, "company_type", self._extract_company_logic)

        # Stage 3 Requirement: Benefits Engine (regex-first, 12+ categories)
        result.benefits, result.benefits_count = self._extract_benefits(text)

        # Extract clauses
        clause_types = ["termination", "ip", "non_compete", "confidentiality"]
        for ct in clause_types:
            clause_text, source = self._extract_clause_block(text, ct)
            if clause_text:
                page = self._find_page(parsed, source)
                result.extracted_clauses[ct] = ExtractedClause(
                    text=clause_text,
                    evidence=ExtractedField(
                        value=len(clause_text),
                        confidence=0.7,
                        source_text=source,
                        page_number=page,
                        method=ExtractionMethod.regex,
                    )
                )

        return result

    def _extract_benefits(self, text: str) -> Tuple[List[str], int]:
        benefits_map = {
            "health_insurance": [r"health\s+insurance", r"medical\s+insurance", r"mediclaim"],
            "provident_fund": [r"provident\s+fund", r"\bPF\b"],
            "gratuity": [r"gratuity"],
            "paid_leave": [r"paid\s+leave", r"vacation", r"annual\s+leave", r"sick\s+leave"],
            "performance_bonus": [r"performance\s+bonus", r"variable\s+pay", r"incentive"],
            "stock_options": [r"stock\s+options", r"esop", r"rsu"],
            "transportation": [r"transport", r"cab\s+facility", r"commute"],
            "gym_wellness": [r"gym", r"wellness", r"fitness"],
            "internet_broadband": [r"internet", r"broadband", r"wfh\s+allowance"],
            "relocation": [r"relocation", r"moving\s+allowance"],
            "insurance_life": [r"life\s+insurance", r"accidental\s+insurance"],
            "training": [r"training", r"certification", r"learning\s+development"],
        }
        
        found = []
        for benefit, patterns in benefits_map.items():
            for p in patterns:
                if re.search(p, text, flags=re.I):
                    found.append(benefit)
                    break
        
        return found, len(found)

    def _extract_field(self, text: str, parsed: ParsedDocument, name: str, logic_func) -> ExtractedField:
        value, source = logic_func(text)
        if value is not None:
            page = self._find_page(parsed, source)
            return ExtractedField(
                value=value,
                confidence=0.9,
                source_text=source,
                page_number=page,
                method=ExtractionMethod.regex,
            )
        return ExtractedField(
            value=None,
            confidence=0.0,
            method=ExtractionMethod.missing,
        )

    def _find_page(self, parsed: ParsedDocument, source_text: str) -> int | None:
        if not source_text:
            return None
        # Clean source text for easier matching
        s = source_text.strip().lower()[:100]  # Take first 100 chars
        for p in parsed.pages:
            if s in (p.text or "").lower():
                return p.page_number
        return None

    def _extract_ctc_logic(self, text: str) -> Tuple[float | None, str | None]:
        """
        Extract annual CTC in INR from contract text.
        Handles: LPA, lakhs, monthly, annual amounts, and various formats.
        """
        log.info("Starting salary extraction...")
        
        # Normalize text for matching
        text_lower = text.lower()
        
        # 1. LPA patterns (HIGHEST PRIORITY - most common in Indian contracts)
        # Matches: "20 LPA", "20.5 LPA", "Rs. 20 LPA", "₹20 lpa", "20 lakhs per annum"
        lpa_patterns = [
            r"(?:₹|rs\.?|inr)?[\s]*([0-9]+(?:\.[0-9]+)?)\s*(?:/-)?[\s]*(?:lpa|l\.p\.a\.)",
            r"(?:₹|rs\.?|inr)?[\s]*([0-9]+(?:\.[0-9]+)?)\s*(?:lakhs?|lacs?|lac)\s*(?:per\s*annum|p\.?\s*a\.?|annual(?:ly)?)",
            r"ctc[\s:]*(?:₹|rs\.?|inr)?[\s]*([0-9]+(?:\.[0-9]+)?)\s*(?:lpa|lakhs?|lacs?)",
            r"salary[\s:]*(?:₹|rs\.?|inr)?[\s]*([0-9]+(?:\.[0-9]+)?)\s*(?:lpa|lakhs?|lacs?)",
            r"package[\s:]*(?:₹|rs\.?|inr)?[\s]*([0-9]+(?:\.[0-9]+)?)\s*(?:lpa|lakhs?|lacs?)",
            r"compensation[\s:]*(?:₹|rs\.?|inr)?[\s]*([0-9]+(?:\.[0-9]+)?)\s*(?:lpa|lakhs?|lacs?)",
        ]
        
        for p in lpa_patterns:
            match = re.search(p, text_lower, flags=re.I)
            if match:
                lpa_value = self._safe_float(match.group(1))
                if lpa_value and 1 <= lpa_value <= 500:  # Sanity check: 1 LPA to 500 LPA (5 CR)
                    annual_inr = lpa_value * 100000
                    log.info(f"Found LPA salary: {lpa_value} LPA = {annual_inr} INR from pattern: {match.group(0)}")
                    return annual_inr, match.group(0)
        
        # 2. Explicit CTC/Annual mentions with large numbers (already in INR)
        # Matches: "Total CTC: ₹20,00,000", "Annual CTC Rs. 2000000", "CTC offered: 18,50,000"
        ctc_patterns = [
            r"(?:total|annual|gross|fixed)?\s*ctc\s*(?:offered|is|:|-|–)?\s*(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)(?:\s*(?:inr|rs\.?|/-))?",
            r"cost\s*to\s*company\s*(?:is|:|-|–)?\s*(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)(?:\s*(?:inr|rs\.?|/-))?",
            r"(?:annual|yearly)\s*(?:salary|compensation|package)\s*(?:is|:|-|–)?\s*(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)(?:\s*(?:inr|rs\.?|/-))?",
            r"(?:salary|ctc)\s+is\s+(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)(?:\s*(?:inr|rs\.?|/-))?",  # Contextual: "Salary is 18,00,000"
        ]
        
        for p in ctc_patterns:
            match = re.search(p, text_lower, flags=re.I)
            if match:
                amt = self._safe_float(match.group(1))
                if amt:
                    # Check if it's already in INR (> 100000) or needs conversion
                    if amt > 100000:  # Already annual INR
                        log.info(f"Found annual CTC: {amt} INR from pattern: {match.group(0)}")
                        return amt, match.group(0)
                    elif 1 <= amt <= 500:  # Likely LPA
                        annual_inr = amt * 100000
                        log.info(f"Found LPA-style CTC: {amt} LPA = {annual_inr} INR")
                        return annual_inr, match.group(0)
        
        # 3. Monthly salary patterns (convert to annual)
        # Matches: "₹50,000 per month", "monthly salary: Rs. 75000", "60000/month"
        monthly_patterns = [
            r"(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)\s*(?:per\s*month|monthly|p\.?\s*m\.?|/\s*month)",
            r"monthly\s*(?:salary|ctc|compensation|pay)\s*(?:is|:|-|–)?\s*(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)",
        ]
        
        for p in monthly_patterns:
            match = re.search(p, text_lower, flags=re.I)
            if match:
                monthly = self._safe_float(match.group(1))
                if monthly and 10000 <= monthly <= 1000000:  # Sanity: 10K to 10L monthly
                    annual = monthly * 12
                    log.info(f"Found monthly salary: {monthly}/month = {annual}/year from: {match.group(0)}")
                    return annual, match.group(0)
        
        # 4. Large INR amounts with currency symbols (fallback)
        # 4. Large INR amounts with currency symbols (fallback)
        # Matches: "₹18,50,000", "Rs. 2000000/-", "INR 1500000", "15,00,000 INR"
        inr_patterns = [
            r"(?:₹|rs\.?|inr)[\s]*([0-9,]{6,})(?:\s*/-|\s*per\s*annum|p\.a\.)?",
            r"([0-9,]{6,})\s*(?:inr|rs\.?)(?:\s*/-|\s*per\s*annum|p\.a\.)?", # Suffix fallback
        ]
        
        for p in inr_patterns:
            match = re.search(p, text_lower, flags=re.I)
            if match:
                amt = self._safe_float(match.group(1))
                if amt and amt > 100000:  # Must be at least 1 lakh
                    # Check context - avoid matching gratuity/insurance caps
                    context = text_lower[max(0, match.start()-50):min(len(text_lower), match.end()+20)]
                    if not any(x in context for x in ['gratuity', 'insurance', 'maximum', 'limit', 'cap', 'coverage']):
                        log.info(f"Found INR amount: {amt} from: {match.group(0)}")
                        return amt, match.group(0)
        
        # 5. Fixed + Variable breakdown
        fv_match = re.search(r"fixed[\s:]+(?:₹|rs\.?|inr)?[\s]*([0-9,]+).*?variable[\s:]+(?:₹|rs\.?|inr)?[\s]*([0-9,]+)", text_lower, flags=re.I | re.S)
        if fv_match:
            fixed = self._safe_float(fv_match.group(1))
            var = self._safe_float(fv_match.group(2))
            if fixed:
                total = fixed + (var or 0)
                # If total is small, assume monthly
                if total < 200000:
                    total *= 12
                log.info(f"Found Fixed+Variable: {fixed}+{var} = {total}")
                return total, fv_match.group(0)
        
        log.warning("No salary found in text")
        return None, None

    def _extract_notice_logic(self, text: str) -> Tuple[int | None, str | None]:
        """
        Extract notice period in days.
        Handles: "notice period is 30 days", "60 days notice", "3 months notice", 
        "two months", "one month notice", etc.
        """
        log.info("Starting notice period extraction...")
        text_lower = text.lower()
        
        # Word-to-number mapping for common cases
        word_nums = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "fifteen": 15, "thirty": 30,
            "sixty": 60, "ninety": 90
        }
        
        # Numeric patterns (highest priority)
        patterns = [
            r"notice\s*period\s*(?:is|of|shall\s*be|will\s*be|:|-|–)?\s*(\d{1,3})\s*(days?|weeks?|months?|calendar\s*months?)",
            r"(\d{1,3})\s*(days?|weeks?|months?|calendar\s*months?)\s*(?:'?s?\s*)?notice\s*period",
            r"(\d{1,3})\s*(days?|weeks?|months?)\s*(?:'?s?\s*)?notice",
            r"notice\s*of\s*(\d{1,3})\s*(days?|weeks?|months?)",
            r"resignation.*?notice\s*(?:period)?\s*(?:is|of|shall\s*be)?\s*(\d{1,3})\s*(days?|weeks?|months?)",
            r"termination.*?notice\s*(?:period)?\s*(?:is|of|shall\s*be)?\s*(\d{1,3})\s*(days?|weeks?|months?)",
            r"serve\s*(?:a)?\s*(\d{1,3})\s*(days?|weeks?|months?)\s*notice",
        ]

        for p in patterns:
            m = re.search(p, text_lower, flags=re.I | re.S)
            if m:
                value = self._safe_int(m.group(1))
                unit = (m.group(2) or "").lower()
                if value is None or value <= 0:
                    continue

                days = value
                if "week" in unit:
                    days = value * 7
                elif "month" in unit:
                    days = value * 30

                if 1 <= days <= 365:  # Sanity check
                    log.info(f"Found notice period: {value} {unit} = {days} days from: {m.group(0)}")
                    return int(days), m.group(0)
        
        # Word-based patterns (e.g., "three months notice")
        word_patterns = [
            r"notice\s*period\s*(?:is|of|shall\s*be|:)?\s*(\w+)\s*(days?|weeks?|months?)",
            r"(\w+)\s*(days?|weeks?|months?)\s*(?:'?s?\s*)?notice",
        ]
        
        for p in word_patterns:
            m = re.search(p, text_lower, flags=re.I | re.S)
            if m:
                word = m.group(1).lower()
                unit = (m.group(2) or "").lower()
                if word in word_nums:
                    value = word_nums[word]
                    days = value
                    if "week" in unit:
                        days = value * 7
                    elif "month" in unit:
                        days = value * 30
                    
                    if 1 <= days <= 365:
                        log.info(f"Found word-based notice: {word} {unit} = {days} days")
                        return int(days), m.group(0)
        
        log.warning("No notice period found in text")
        return None, None

    def _extract_bond_logic(self, text: str) -> Tuple[float | None, str | None]:
        """
        Extract training bond / service bond amount in INR.
        Handles: "bond of Rs. 1,00,000", "training cost: ₹50000", "liquidated damages", etc.
        """
        log.info("Starting bond extraction...")
        text_lower = text.lower()
        
        # Patterns for bond detection
        patterns = [
            r"(?:service\s*)?bond.*?(?:₹|rs\.?|inr)\s*([0-9,]+)",
            r"training\s*(?:bond|cost|fee).*?(?:₹|rs\.?|inr)\s*([0-9,]+)",
            r"liquidated\s*damages.*?(?:₹|rs\.?|inr)\s*([0-9,]+)",
            r"(?:pay|reimburse|recover).*?(?:₹|rs\.?|inr)\s*([0-9,]+).*?(?:leaving|resigning|terminating|breach)",
            r"recovery\s*(?:of)?\s*(?:₹|rs\.?|inr)\s*([0-9,]+)",
            r"(?:₹|rs\.?|inr)\s*([0-9,]+).*?(?:bond|training\s*cost|service\s*agreement)",
        ]
        
        for p in patterns:
            match = re.search(p, text_lower, flags=re.I | re.S)
            if match:
                amount = self._safe_float(match.group(1))
                if amount and amount > 0:
                    log.info(f"Found bond: {amount} from: {match.group(0)[:50]}...")
                    return amount, match.group(0)
        
        log.info("No bond found in text")
        return None, None

    def _extract_non_compete_logic(self, text: str) -> Tuple[int | None, str | None]:
        """
        Extract non-compete duration in months.
        """
        log.info("Starting non-compete extraction...")
        text_lower = text.lower()
        
        patterns = [
            r"non[-\s]?compete.*?(\d+)\s*(months?|years?)",
            r"non[-\s]?solicitation.*?(\d+)\s*(months?|years?)",
            r"restrictive\s*covenant.*?(\d+)\s*(months?|years?)",
            r"shall\s*not\s*join.*?competitor.*?(\d+)\s*(months?|years?)",
        ]
        
        for p in patterns:
            match = re.search(p, text_lower, flags=re.I | re.S)
            if match:
                value = self._safe_int(match.group(1))
                if value is None:
                    continue
                unit = match.group(2).lower()
                months = value
                if "year" in unit:
                    months = value * 12
                if 1 <= months <= 60:  # Sanity check: 1 month to 5 years
                    log.info(f"Found non-compete: {value} {unit} = {months} months")
                    return months, match.group(0)
        
        log.info("No non-compete clause found")
        return None, None

    def _extract_probation_logic(self, text: str) -> Tuple[int | None, str | None]:
        """
        Extract probation period in months.
        """
        log.info("Starting probation extraction...")
        text_lower = text.lower()
        
        patterns = [
            r"probation(?:ary)?\s*(?:period)?\s*(?:of|is|:|shall\s+be)?\s*(\d+)\s*(months?|weeks?|days?)",
            r"(\d+)\s*(months?|weeks?)\s*probation",
            r"trial\s+period\s*(?:of|is)?\s*(\d+)\s*(months?|weeks?)",
            r"confirmation\s+after\s*(\d+)\s*(months?|weeks?)",
        ]
        
        for p in patterns:
            match = re.search(p, text_lower, flags=re.I | re.S)
            if match:
                value = self._safe_int(match.group(1))
                if value is None or value <= 0:
                    continue
                unit = match.group(2).lower()
                months = value
                if "week" in unit:
                    months = max(1, round(value / 4))
                elif "day" in unit:
                    months = max(1, round(value / 30))
                log.info(f"Found probation: {value} {unit} = {months} months from: {match.group(0)}")
                return months, match.group(0)
        
        log.warning("No probation period found in text")
        return None, None
        
    def _extract_role_logic(self, text: str) -> Tuple[str | None, str | None]:
        # Look for "Designation : <Role>" or "Role : <Role>"
        patterns = [
            r"(?:designation|role|position|title)\s*[:\-\u2013]\s*([A-Z][a-zA-Z0-9\s\-\(\).]+?)(?:\n|$|\.)",
            r"offering\s+you\s+the\s+position\s+of\s+([A-Z][a-zA-Z0-9\s\-\(\).]+?)(?:\n|\.|,)",
            r"appointed\s+as\s+([A-Z][a-zA-Z0-9\s\-\(\).]+?)(?:\n|\.|,)",
            r"role\s+of\s+([A-Z][a-zA-Z0-9\s\-\(\).]+?)(?:\n|\.|,)",
        ]
        for p in patterns:
            match = re.search(p, text, flags=re.I)
            if match:
                role = match.group(1).strip()
                if 2 < len(role) < 50 and "following" not in role.lower():
                    return role, match.group(0)
        return None, None

    def _extract_company_logic(self, text: str) -> Tuple[str | None, str | None]:
        # Look for "Welcome to <Company>" or "between <Company> and ..."
        # Prioritize patterns with common legal suffixes.
        patterns = [
            r"(?:welcome\s+to|joining)\s+([A-Z][a-zA-Z0-9\s.,&]+?(?:Private\s+Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|Inc\.?|LLP|Group))",
            r"between\s+([A-Z][a-zA-Z0-9\s.,&]+?(?:Private\s+Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|Inc\.?|LLP))\s+and",
            r"offer\s+from\s+([A-Z][a-zA-Z0-9\s.,&]+?(?:Private\s+Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|Inc\.?|LLP))",
        ]
        for p in patterns:
            match = re.search(p, text, flags=re.I)
            if match:
                company = match.group(1).strip()
                return company, match.group(0)
        return None, None

    def _extract_clause_block(self, text: str, clause_type: str) -> Tuple[str | None, str | None]:
        keywords = {
            "termination": ["termination", "resignation", "notice period"],
            "ip": ["intellectual property", "inventions", "ownership of work", "proprietary information"],
            "non_compete": ["non-compete", "non compete", "restrictive covenant", "solicitation"],
            "confidentiality": ["confidentiality", "non-disclosure", "secret information"],
        }
        
        # Simple heuristic: look for heading and then a block of text
        for kw in keywords.get(clause_type, []):
            # Regex to find heading followed by paragraphs
            # Captures till next capitalized heading or double newline
            pattern = rf"(?i)(?:^|\n)(?:\d+\.|\*|\-)?\s*({re.escape(kw)}[^\n:]*)(?::|\n)(.*?)(?=\n\s*\d+\.|\n\s*[A-Z][A-Z\s]+\n|\n\n\n|$)"
            match = re.search(pattern, text, flags=re.S)
            if match:
                title = match.group(1)
                content = match.group(2).strip()
                if len(content) > 50: # avoids mini matches
                    return content, title + "\n" + content[:100]
        
        return None, None
