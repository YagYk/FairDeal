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
        except (ValueError, TypeError):
            return None

    def _safe_int(self, s: str | None) -> int | None:
        if not s:
            return None
        try:
            clean = re.sub(r"[^\d]", "", s)
            return int(clean) if clean else None
        except (ValueError, TypeError):
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

        # ── Post-process bond: negative sentinel means "N months of salary" ──
        salary_val = result.ctc_inr.value if result.ctc_inr else None
        bond_val = result.bond_amount_inr.value if result.bond_amount_inr else None
        bond_source = result.bond_amount_inr.source_text if result.bond_amount_inr else ""
        
        if bond_val is not None and bond_val < 0:
            # Negative sentinel: -N means N months of salary
            months = abs(bond_val)
            if salary_val and salary_val > 0:
                monthly = salary_val / 12.0
                actual_bond = months * monthly
                log.info(f"Bond is {months:.0f} months salary → ₹{actual_bond:.0f} (CTC={salary_val})")
                result.bond_amount_inr.value = actual_bond
            else:
                # Can't calculate without salary — clear the bond
                log.warning(f"Bond expressed as {months:.0f} months salary but CTC unknown — clearing")
                result.bond_amount_inr = ExtractedField(
                    value=None, confidence=0.0, method=ExtractionMethod.missing
                )
        
        # ── Cross-validation: bond must NOT equal salary ──
        bond_val = result.bond_amount_inr.value if result.bond_amount_inr else None
        if salary_val and bond_val and abs(salary_val - bond_val) < 1.0:
            log.warning(f"Bond ({bond_val}) == Salary ({salary_val}) — clearing bogus bond extraction")
            result.bond_amount_inr = ExtractedField(
                value=None, confidence=0.0, method=ExtractionMethod.missing
            )

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
                if lpa_value and 1 <= lpa_value <= 500:
                    start_idx = max(0, match.start() - 50)
                    end_idx = min(len(text_lower), match.end() + 50)
                    context_window = text_lower[start_idx:end_idx]
                    
                    exclusion_keywords = [
                        "gratuity", "insurance", "mediclaim", "coverage", "maximum", "limit", "cap", 
                        "sum assured", "benefit up to", "variable pay", "performance bonus"
                    ]
                    
                    if any(kw in context_window for kw in exclusion_keywords):
                        log.info(f"Ignored LPA match '{match.group(0)}' due to context keywords")
                        continue

                    annual_inr = lpa_value * 100000
                    log.info(f"Found LPA salary: {lpa_value} LPA = {annual_inr} INR from: {match.group(0)}")
                    return annual_inr, match.group(0)
        
        # 2. Explicit CTC/Annual mentions with large numbers (already in INR)
        ctc_patterns = [
            r"(?:total|annual|gross|fixed)?\s*ctc\s*(?:offered|is|:|-|–)?\s*(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)(?:\s*(?:inr|rs\.?|/-))?",
            r"cost\s*to\s*company\s*(?:is|:|-|–)?\s*(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)(?:\s*(?:inr|rs\.?|/-))?",
            r"(?:annual|yearly)\s*(?:salary|compensation|package)\s*(?:is|:|-|–)?\s*(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)(?:\s*(?:inr|rs\.?|/-))?",
            r"(?:salary|ctc)\s+is\s+(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)(?:\s*(?:inr|rs\.?|/-))?",
        ]
        
        for p in ctc_patterns:
            match = re.search(p, text_lower, flags=re.I)
            if match:
                amt = self._safe_float(match.group(1))
                if amt:
                    if amt > 100000:
                        log.info(f"Found annual CTC: {amt} INR from: {match.group(0)}")
                        return amt, match.group(0)
                    elif 1 <= amt <= 500:
                        annual_inr = amt * 100000
                        log.info(f"Found LPA-style CTC: {amt} LPA = {annual_inr} INR")
                        return annual_inr, match.group(0)
        
        # 3. Monthly salary patterns (convert to annual)
        monthly_patterns = [
            r"(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)\s*(?:per\s*month|monthly|p\.?\s*m\.?|/\s*month)",
            r"monthly\s*(?:salary|ctc|compensation|pay)\s*(?:is|:|-|–)?\s*(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)",
            r"cost\s*to\s*company\s*(?:per\s*month|monthly)\s*(?:₹|rs\.?|inr)?[\s]*([0-9,]+(?:\.[0-9]+)?)",
        ]
        
        for p in monthly_patterns:
            match = re.search(p, text_lower, flags=re.I)
            if match:
                monthly = self._safe_float(match.group(1))
                if monthly and 10000 <= monthly <= 1000000:
                    annual = monthly * 12
                    log.info(f"Found monthly salary: {monthly}/month = {annual}/year from: {match.group(0)}")
                    return annual, match.group(0)
        
        # 4. Large INR amounts with currency symbols (fallback)
        inr_patterns = [
            r"(?:₹|rs\.?|inr)[\s]*([0-9,]{6,})(?:\s*/-|\s*per\s*annum|p\.a\.)?",
            r"([0-9,]{6,})\s*(?:inr|rs\.?)(?:\s*/-|\s*per\s*annum|p\.a\.)?",
        ]
        
        for p in inr_patterns:
            match = re.search(p, text_lower, flags=re.I)
            if match:
                amt = self._safe_float(match.group(1))
                if amt and amt > 100000:
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
                if total < 200000:
                    total *= 12
                log.info(f"Found Fixed+Variable: {fixed}+{var} = {total}")
                return total, fv_match.group(0)
        
        log.warning("No salary found in text")
        return None, None

    # ──────────────────────────────────────────────────────────────────
    #  NOTICE PERIOD
    # ──────────────────────────────────────────────────────────────────

    def _extract_notice_logic(self, text: str) -> Tuple[int | None, str | None]:
        """
        Extract notice period in days.
        Handles hyphenated forms (one-month), various quote styles, and many phrasing variants.
        """
        log.info("Starting notice period extraction...")
        text_lower = text.lower()

        # ── Pre-process: normalize hyphens between number-words and units ──
        # "one-month" → "one month", "three-months'" → "three months'"
        # This handles the extremely common Indian contract hyphenation
        _unit_words = r"(?:month|week|day|calendar)"
        text_norm = re.sub(
            rf"(\b(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|thirty|sixty|ninety|\d+))\s*[-–—]\s*({_unit_words})",
            r"\1 \2",
            text_lower,
            flags=re.I
        )

        word_nums = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12, "fifteen": 15, "thirty": 30,
            "sixty": 60, "ninety": 90,
        }

        def _to_days(val: int, unit: str) -> int | None:
            unit = unit.lower().strip()
            days = val
            if "week" in unit:
                days = val * 7
            elif "month" in unit or "calendar" in unit:
                days = val * 30
            return int(days) if 1 <= days <= 365 else None

        # Helper: try to parse a raw token as int or word-number
        def _parse_num(raw: str) -> int | None:
            raw = raw.strip().lower()
            if raw in word_nums:
                return word_nums[raw]
            v = self._safe_int(raw)
            return v if v and v > 0 else None

        # All apostrophe/quote variants
        _Q = r"['\u2018\u2019\u0027`\u00B4]"
        # Separator between number and unit: space, hyphen, or nothing
        _S = r"[\s\-]*"

        # ── 1. Explicit "notice period" phrasing ──
        explicit_patterns = [
            rf"notice\s*period\s*(?:is|of|shall\s*be|will\s*be|:|-|–)?\s*(\w+){_S}(days?|weeks?|months?|calendar\s*months?)",
        ]
        for p in explicit_patterns:
            m = re.search(p, text_norm, flags=re.I | re.S)
            if m:
                val = _parse_num(m.group(1))
                if val:
                    days = _to_days(val, m.group(2))
                    if days:
                        log.info(f"Found notice period (explicit): {val} {m.group(2)} = {days} days from: {m.group(0)}")
                        return days, m.group(0)

        # ── 2. "giving X month(s)' [written/advance/prior] notice" ──
        giving_patterns = [
            rf"(?:by\s+)?giving\s+(\w+){_S}(months?|weeks?|days?)(?:{_Q}?s?)?\s*(?:written\s+|advance\s+|prior\s+)*notice",
            rf"(?:by\s+)?provid(?:e|ing)\s+(\w+){_S}(months?|weeks?|days?)(?:{_Q}?s?)?\s*(?:written\s+|advance\s+|prior\s+)*notice",
            rf"serve\s+(?:a\s+)?(\w+){_S}(months?|weeks?|days?)(?:{_Q}?s?)?\s*(?:written\s+|advance\s+|prior\s+)*notice",
        ]
        for p in giving_patterns:
            m = re.search(p, text_norm, flags=re.I | re.S)
            if m:
                val = _parse_num(m.group(1))
                if val:
                    days = _to_days(val, m.group(2))
                    if days:
                        log.info(f"Found notice period (giving): {val} {m.group(2)} = {days} days from: {m.group(0)}")
                        return days, m.group(0)

        # ── 3. "X month(s)['] [written] notice" (generic) ──
        generic_patterns = [
            rf"(\w+){_S}(months?|weeks?|days?)(?:{_Q}?s?)?\s*(?:written\s+|advance\s+|prior\s+)*notice(?:\s+period)?",
            rf"(\w+){_S}(months?|weeks?|days?)(?:{_Q}?s?)?\s*notice\s+(?:in\s+writing)",
        ]
        _generic_exclusions = ["probation", "bond", "training", "gratuity", "leave", "insurance", "maternity", "paternity"]
        for p in generic_patterns:
            m = re.search(p, text_norm, flags=re.I | re.S)
            if m:
                # Context-check: reject if nearby text mentions unrelated clauses
                ctx_start = max(0, m.start() - 80)
                ctx_end = min(len(text_norm), m.end() + 80)
                ctx_window = text_norm[ctx_start:ctx_end]
                if any(kw in ctx_window for kw in _generic_exclusions):
                    log.info(f"Ignored generic notice match due to context exclusion: {m.group(0)[:60]}")
                    continue
                val = _parse_num(m.group(1))
                if val:
                    days = _to_days(val, m.group(2))
                    if days:
                        log.info(f"Found notice period (generic): {val} {m.group(2)} = {days} days from: {m.group(0)}")
                        return days, m.group(0)

        # ── 4. "notice of X days/months" ──
        of_patterns = [
            rf"notice\s*of\s*(\w+){_S}(days?|weeks?|months?)",
            rf"advance\s*(?:written\s+)?notice\s*of\s*(\w+){_S}(days?|weeks?|months?)",
        ]
        for p in of_patterns:
            m = re.search(p, text_norm, flags=re.I | re.S)
            if m:
                val = _parse_num(m.group(1))
                if val:
                    days = _to_days(val, m.group(2))
                    if days:
                        log.info(f"Found notice period (of): {val} {m.group(2)} = {days} days from: {m.group(0)}")
                        return days, m.group(0)

        # ── 5. Broader termination/resignation-section scan ──
        termination_patterns = [
            rf"terminat(?:ion|e|able).{{0,250}}?(?:giving|provide|serve)\s+(\w+){_S}(months?|weeks?|days?)(?:{_Q}?s?)?\s*(?:written\s+|advance\s+|prior\s+)*notice",
            rf"resign(?:ation|ing)?.{{0,200}}?(?:giving|provide)\s+(\w+){_S}(months?|weeks?|days?)(?:{_Q}?s?)?\s*(?:written\s+|advance\s+|prior\s+)*notice",
            # Also catch: "terminable ... X month notice" without giving/provide
            rf"terminat(?:ion|e|able).{{0,250}}?(\w+){_S}(months?|weeks?|days?)(?:{_Q}?s?)?\s*(?:written\s+|advance\s+|prior\s+)*notice",
        ]
        for p in termination_patterns:
            m = re.search(p, text_norm, flags=re.I | re.S)
            if m:
                val = _parse_num(m.group(1))
                if val:
                    days = _to_days(val, m.group(2))
                    if days:
                        log.info(f"Found notice period (termination): {val} {m.group(2)} = {days} days from: {m.group(0)[:80]}")
                        return days, m.group(0)

        # ── 6. "salary in lieu of notice" / "in lieu of the notice period" ──
        lieu_patterns = [
            rf"(\w+){_S}(months?|weeks?|days?)(?:{_Q}?s?)?\s*(?:salary|pay|compensation).{{0,30}}?in\s*lieu\s*(?:of)?\s*(?:the\s*)?notice",
            rf"in\s*lieu\s*(?:of)?\s*(?:the\s*)?notice\s*(?:period)?.{{0,40}}?(\w+){_S}(months?|weeks?|days?)",
        ]
        for p in lieu_patterns:
            m = re.search(p, text_norm, flags=re.I | re.S)
            if m:
                val = _parse_num(m.group(1))
                if val:
                    days = _to_days(val, m.group(2))
                    if days:
                        log.info(f"Found notice period (lieu): {val} {m.group(2)} = {days} days from: {m.group(0)[:80]}")
                        return days, m.group(0)

        # ── 7. Last resort: scan for ANY "X month/day" near "notice" within 80 chars ──
        last_resort = re.finditer(rf"(\w+){_S}(months?|weeks?|days?)(?:{_Q}?s?)?", text_norm)
        for m in last_resort:
            val = _parse_num(m.group(1))
            if val is None:
                continue
            # Check if "notice" appears within 80 chars before or after
            start = max(0, m.start() - 80)
            end = min(len(text_norm), m.end() + 80)
            window = text_norm[start:end]
            if "notice" in window:
                # Make sure this isn't a probation, bond, leave or insurance mention
                if any(kw in window for kw in ["probation", "bond", "training", "gratuity", "leave", "insurance", "maternity", "paternity"]):
                    continue
                days = _to_days(val, m.group(2))
                if days:
                    log.info(f"Found notice period (proximity): {val} {m.group(2)} = {days} days from window: {window[:80]}")
                    return days, m.group(0)

        log.warning("No notice period found in text")
        return None, None

    # ──────────────────────────────────────────────────────────────────
    #  BOND EXTRACTION (tightened to avoid salary leakage)
    # ──────────────────────────────────────────────────────────────────

    def _extract_bond_logic(self, text: str) -> Tuple[float | None, str | None]:
        """
        Extract training bond / service bond / service agreement penalty amount in INR.
        Handles:
          - "service bond of Rs. 1,00,000"
          - "training bond amount: ₹50,000"
          - "liquidated damages of Rs 2,00,000"
          - "penalty of 3 months gross salary" (relative to CTC)
          - "liable to pay Rs. 75,000 if you leave before 2 years"
          - "service agreement of 2 years" (duration-only, no explicit amount)
        """
        log.info("Starting bond extraction...")
        text_lower = text.lower()
        
        # Currency prefix pattern
        _CUR = r"(?:₹|rs\.?\s*|inr\.?\s*)"

        # ── Phase 1: Bond keyword BEFORE the amount (high confidence) ──
        bond_before_patterns = [
            # "service bond of Rs. 1,00,000"
            rf"(?:service\s*)?bond\s*(?:of|amount|:|-|–|is|for)?\s*{_CUR}([0-9,]+(?:\.\d+)?)",
            # "training bond of Rs. 50000"
            rf"training\s*(?:bond|cost|fee|amount)\s*(?:of|amount|:|-|–|is|for)?\s*{_CUR}([0-9,]+(?:\.\d+)?)",
            # "liquidated damages of Rs. 2,00,000"
            rf"liquidated\s*damages\s*(?:of|amount|:|-|–|is)?\s*{_CUR}([0-9,]+(?:\.\d+)?)",
            # "penalty of Rs. 1,00,000"
            rf"penalty\s*(?:of|amount|:|-|–)?\s*{_CUR}([0-9,]+(?:\.\d+)?)",
            # "recovery of Rs 50000"
            rf"recovery\s*(?:of)?\s*{_CUR}([0-9,]+(?:\.\d+)?)",
            # "pay Rs. 1,00,000 as bond/penalty/damages"
            rf"(?:pay|refund|reimburse)\s*{_CUR}([0-9,]+(?:\.\d+)?)\s*(?:as|towards|by way of)\s*(?:bond|penalty|damages|compensation)",
            # "bond/penalty amount is Rs. 50000"
            rf"(?:bond|penalty|damages)\s*(?:amount)?\s*(?:shall\s*be|is|of|=|:)\s*{_CUR}([0-9,]+(?:\.\d+)?)",
        ]

        for p in bond_before_patterns:
            match = re.search(p, text_lower, flags=re.I | re.S)
            if match:
                amount = self._safe_float(match.group(1))
                if amount and amount > 0:
                    log.info(f"Found bond (keyword-first): {amount} from: {match.group(0)[:80]}")
                    return amount, match.group(0)

        # ── Phase 2: Amount THEN bond keyword within 150 chars (medium confidence) ──
        amount_then_bond_patterns = [
            rf"{_CUR}([0-9,]+(?:\.\d+)?).{{0,150}}?(?:bond|training\s*cost|liquidated\s*damages|penalty|service\s*agreement\s*(?:breach|violation))",
            r"(?:pay|reimburse|recover|forfeit|liable).{0,100}?(?:₹|rs\.?|inr)\s*([0-9,]+(?:\.\d+)?).{0,80}?(?:leaving|resigning|breach|before\s*(?:complet|expir))",
        ]

        for p in amount_then_bond_patterns:
            match = re.search(p, text_lower, flags=re.I | re.S)
            if match:
                amount = self._safe_float(match.group(1))
                if amount and amount > 0:
                    log.info(f"Found bond (amount-then-keyword): {amount} from: {match.group(0)[:80]}")
                    return amount, match.group(0)

        # ── Phase 3: Service agreement / minimum service period with amount ──
        # "minimum service period of 2 years, failing which you shall pay Rs. 1,00,000"
        # "service agreement... pay... Rs. 50,000"
        service_agreement_patterns = [
            rf"(?:service\s*agreement|minimum\s*service\s*(?:period|commitment|tenure)).{{0,200}}?{_CUR}([0-9,]+(?:\.\d+)?)",
            rf"(?:agree\s*to\s*serve|commit\s*to\s*serve|undertake\s*to\s*serve).{{0,200}}?{_CUR}([0-9,]+(?:\.\d+)?)",
            rf"(?:leave|resign|separate).{{0,60}}?(?:before|prior|within).{{0,80}}?(?:pay|liable|forfeit|reimburse).{{0,60}}?{_CUR}([0-9,]+(?:\.\d+)?)",
        ]

        for p in service_agreement_patterns:
            match = re.search(p, text_lower, flags=re.I | re.S)
            if match:
                amount = self._safe_float(match.group(1))
                if amount and amount > 0:
                    log.info(f"Found bond (service-agreement): {amount} from: {match.group(0)[:80]}")
                    return amount, match.group(0)

        # ── Phase 4: Bond amount expressed as months of salary ──
        # "penalty of 3 months gross salary", "pay 2 months CTC"
        # Returns NEGATIVE value to signal "X months of salary" — the caller
        # (extract()) will multiply by actual salary/12 if known.
        salary_bond_patterns = [
            r"(?:bond|penalty|damages|forfeit|pay|reimburse|liable).{0,60}?(\d+)\s*months?\s*(?:of\s*)?(?:gross|basic|net|ctc|salary|pay|compensation)",
            r"(\d+)\s*months?\s*(?:of\s*)?(?:gross|basic|net|ctc|salary|pay|compensation).{0,60}?(?:bond|penalty|damages|forfeit)",
        ]

        for p in salary_bond_patterns:
            match = re.search(p, text_lower, flags=re.I | re.S)
            if match:
                months = self._safe_int(match.group(1))
                if months and 1 <= months <= 24:
                    log.info(f"Found bond as salary multiple: {months} months salary from: {match.group(0)[:80]}")
                    # Negative sentinel: -N means "N months of salary".
                    # extract() post-processing will convert to INR using actual CTC.
                    return float(-months), match.group(0)

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
                if 1 <= months <= 60:
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

        # Also handle word-based: "probation for a period of six months"
        word_nums = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
            "eleven": 11, "twelve": 12,
        }

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

        # Word-based probation: "probation for a period of six months"
        word_patterns = [
            r"probation(?:ary)?\s*(?:period)?\s*(?:of|is|for\s*(?:a\s*)?(?:period\s*of\s*)?)?\s*(\w+)\s*(months?|weeks?)",
        ]
        for p in word_patterns:
            match = re.search(p, text_lower, flags=re.I | re.S)
            if match:
                word = match.group(1).lower()
                if word in word_nums:
                    months = word_nums[word]
                    unit = match.group(2).lower()
                    if "week" in unit:
                        months = max(1, round(months / 4))
                    log.info(f"Found probation (word): {word} = {months} months from: {match.group(0)}")
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
        """Extract company name from contract text."""
        # Legal suffix pattern — anchors the company name match
        _SUFFIX = r"(?:Private\s+Limited|Pvt\.?\s*Ltd\.?|Limited|Ltd\.?|Inc\.?|LLP|Corporation|Corp\.?|Group|Technologies|Solutions|Infosystems|Consulting)"
        
        # Phase 1: Look for company name with a known legal/business suffix
        patterns = [
            rf"(?:welcome\s+to|offer\s+from|behalf\s+of|employee\s+of|employed\s+(?:by|with))\s+([A-Z][A-Za-z0-9\s.,&]{{1,60}}?{_SUFFIX})",
            rf"between\s+([A-Z][A-Za-z0-9\s.,&]{{1,60}}?{_SUFFIX})\s+(?:and|\()",
            rf"([A-Z][A-Za-z0-9\s.,&]{{1,50}}?{_SUFFIX})\s*(?:\(|,)?\s*(?:herein|here\s*in|the\s+company|the\s+employer)",
        ]
        for p in patterns:
            match = re.search(p, text)  # Case-SENSITIVE: company names start with uppercase
            if match:
                company = match.group(1).strip().rstrip('.,')
                if len(company) <= 80:
                    return company, match.group(0)
        
        # Phase 2: Look for known big company names directly
        known_companies = [
            "HCL Technologies", "HCL", "Wipro", "Infosys", "TCS",
            "Tata Consultancy Services", "Cognizant", "Tech Mahindra",
            "Accenture", "Capgemini", "Deloitte", "Google", "Microsoft",
            "Amazon", "Flipkart", "Zomato", "Swiggy", "Paytm", "Reliance",
            "HDFC", "ICICI", "Byju", "Zoho", "Freshworks", "Ola", "PhonePe",
        ]
        text_lower = text.lower()
        for name in known_companies:
            if name.lower() in text_lower:
                return name, f"Found company: {name}"
        
        return None, None

    def _extract_clause_block(self, text: str, clause_type: str) -> Tuple[str | None, str | None]:
        keywords = {
            "termination": ["termination", "resignation", "notice period"],
            "ip": ["intellectual property", "inventions", "ownership of work", "proprietary information"],
            "non_compete": ["non-compete", "non compete", "restrictive covenant", "solicitation"],
            "confidentiality": ["confidentiality", "non-disclosure", "secret information"],
        }
        
        for kw in keywords.get(clause_type, []):
            pattern = rf"(?i)(?:^|\n)(?:\d+\.|\*|\-)?\s*({re.escape(kw)}[^\n:]*)(?::|\n)(.*?)(?=\n\s*\d+\.|\n\s*[A-Z][A-Z\s]+\n|\n\n\n|$)"
            match = re.search(pattern, text, flags=re.S)
            if match:
                title = match.group(1)
                content = match.group(2).strip()
                if len(content) > 50:
                    return content, title + "\n" + content[:100]
        
        return None, None
