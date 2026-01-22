from __future__ import annotations

from typing import List, Tuple

from ..logging_config import get_logger
from ..models.schemas import (
    ContractExtractionResult,
    ExtractedField,
    ExtractionMethod,
)
from .parser_service import ParsedDocument, PageText
from .llm_service import LLMService


log = get_logger("service.sniper")


class SniperExtractionService:
    """
    LLM-backed 'sniper' extraction on carefully targeted pages to avoid salary hallucinations.
    """

    def __init__(self, llm: LLMService) -> None:
        self.llm = llm

    async def extract_salary(self, parsed: ParsedDocument) -> ExtractedField | None:
        """
        Target pages and extract salary using LLM.
        """
        target_pages = self._score_pages(
            parsed.pages,
            rewards=["total cost to company", "cost to company", "ctc", "basic", "compensation", "salary breakup", "annual", "per annum"],
            penalties=["gratuity limit", "statutory limit", "maximum", "coverage", "reimbursement cap"],
            require_all=[("ctc", "basic"), ("cost to company", "basic")] # one of these pairs
        )
        
        if not target_pages:
            # looser fallback if no perfect match
            target_pages = self._score_pages(
                 parsed.pages,
                 rewards=["salary", "compensation", "remuneration", "ctc"],
                 penalties=[],
                 top_k=2
            )

        if not target_pages:
            return None

        combined_text = "\n\n".join([f"[Page {p.page_number}]\n{p.text}" for p in target_pages])
        res = await self.llm.extract_salary_from_text(combined_text)
        
        if res and res.get("value") is not None:
            return ExtractedField(
                value=res["value"],
                confidence=res.get("confidence", 0.8),
                source_text=res.get("source_text"),
                page_number=target_pages[0].page_number if target_pages else None,
                method=ExtractionMethod.sniper_llm
            )
        return None

    async def extract_notice(self, parsed: ParsedDocument) -> ExtractedField | None:
        """
        Target pages and extract notice period using LLM.
        """
        target_pages = self._score_pages(
            parsed.pages,
            rewards=["notice period", "termination", "resignation", "leaving the company"],
            penalties=[],
            top_k=2
        )
        
        if not target_pages:
            return None

        combined_text = "\n\n".join([f"[Page {p.page_number}]\n{p.text}" for p in target_pages])
        res = await self.llm.extract_notice_from_text(combined_text)
        
        if res and res.get("value") is not None:
            return ExtractedField(
                value=res["value"],
                confidence=res.get("confidence", 0.8),
                source_text=res.get("source_text"),
                page_number=target_pages[0].page_number if target_pages else None,
                method=ExtractionMethod.sniper_llm
            )
        return None

    def _score_pages(
        self, 
        pages: List[PageText], 
        rewards: List[str], 
        penalties: List[str], 
        require_all: List[Tuple[str, ...]] = None,
        top_k: int = 2
    ) -> List[PageText]:
        scored = []
        for p in pages:
            text = (p.text or "").lower()
            score = 0
            
            # Check requirements
            met_req = False
            if require_all:
                for req_pair in require_all:
                    if all(r in text for r in req_pair):
                        met_req = True
                        score += 10 # Big boost for meeting requirements
                        break
            else:
                met_req = True

            if not met_req:
                # Still score it but with less priority
                pass

            for r in rewards:
                if r in text:
                    score += 2
            
            for pen in penalties:
                if pen in text:
                    score -= 5
            
            if score > 0:
                scored.append((score, p))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        return [p for s, p in scored[:top_k]]

    async def extract_probation(self, parsed: ParsedDocument) -> ExtractedField | None:
        """
        Target pages and extract probation period using LLM.
        """
        target_pages = self._score_pages(
            parsed.pages,
            rewards=["probation", "probationary", "trial period", "confirmation"],
            penalties=[],
            top_k=2
        )
        
        if not target_pages:
            # Use full document if no targeted pages found
            target_pages = parsed.pages[:3]  # First 3 pages often have terms

        if not target_pages:
            return None

        combined_text = "\n\n".join([f"[Page {p.page_number}]\n{p.text}" for p in target_pages])
        res = await self.llm.extract_probation_from_text(combined_text)
        
        if res and res.get("value") is not None:
            return ExtractedField(
                value=res["value"],
                confidence=res.get("confidence", 0.8),
                source_text=res.get("source_text"),
                page_number=target_pages[0].page_number if target_pages else None,
                method=ExtractionMethod.sniper_llm
            )
        return None

    async def extract_bond(self, parsed: ParsedDocument) -> ExtractedField | None:
        """
        Target pages and extract bond/training cost using LLM.
        """
        target_pages = self._score_pages(
            parsed.pages,
            rewards=["bond", "training cost", "liquidated damages", "service agreement", "recovery", "reimburse"],
            penalties=[],
            top_k=2
        )
        
        if not target_pages:
            # Check all pages for bond-related terms
            target_pages = parsed.pages[:4]

        if not target_pages:
            return None

        combined_text = "\n\n".join([f"[Page {p.page_number}]\n{p.text}" for p in target_pages])
        res = await self.llm.extract_bond_from_text(combined_text)
        
        if res and res.get("value") is not None:
            return ExtractedField(
                value=res["value"],
                confidence=res.get("confidence", 0.8),
                source_text=res.get("source_text"),
                page_number=target_pages[0].page_number if target_pages else None,
                method=ExtractionMethod.sniper_llm
            )
        return None

    async def extract_non_compete(self, parsed: ParsedDocument) -> ExtractedField | None:
        """
        Target pages and extract non-compete clause using LLM.
        """
        target_pages = self._score_pages(
            parsed.pages,
            rewards=["non-compete", "non compete", "non-solicitation", "restrictive covenant", "competitor", "shall not join"],
            penalties=[],
            top_k=2
        )
        
        if not target_pages:
            target_pages = parsed.pages[-3:]  # Non-compete often near the end

        if not target_pages:
            return None

        combined_text = "\n\n".join([f"[Page {p.page_number}]\n{p.text}" for p in target_pages])
        res = await self.llm.extract_non_compete_from_text(combined_text)
        
        if res and res.get("value") is not None:
            return ExtractedField(
                value=res["value"],
                confidence=res.get("confidence", 0.8),
                source_text=res.get("source_text"),
                page_number=target_pages[0].page_number if target_pages else None,
                method=ExtractionMethod.sniper_llm
            )
        return None

    async def extract_all(self, parsed: ParsedDocument) -> ContractExtractionResult:
        """
        COMPREHENSIVE extraction using LLM to extract ALL fields at once.
        This is more reliable than individual sniper calls.
        
        Returns a populated ContractExtractionResult with all fields.
        """
        result = ContractExtractionResult()
        
        # Use the comprehensive LLM extraction
        llm_result = await self.llm.extract_all_fields(parsed.full_text)
        
        if not llm_result:
            log.warning("LLM extract_all_fields returned None, extraction failed")
            return result
        
        # Extract source texts and confidence scores
        source_texts = llm_result.get("source_texts", {})
        confidence_scores = llm_result.get("confidence_scores", {})
        
        # Map LLM results to ExtractedField objects
        if llm_result.get("ctc_inr") is not None:
            result.ctc_inr = ExtractedField(
                value=llm_result["ctc_inr"],
                confidence=confidence_scores.get("ctc_inr", 0.85),
                source_text=source_texts.get("ctc_inr"),
                method=ExtractionMethod.sniper_llm
            )
            log.info(f"Extracted CTC: {result.ctc_inr.value}")
        
        if llm_result.get("notice_period_days") is not None:
            result.notice_period_days = ExtractedField(
                value=llm_result["notice_period_days"],
                confidence=confidence_scores.get("notice_period_days", 0.85),
                source_text=source_texts.get("notice_period_days"),
                method=ExtractionMethod.sniper_llm
            )
            log.info(f"Extracted Notice: {result.notice_period_days.value} days")
        
        if llm_result.get("bond_amount_inr") is not None:
            result.bond_amount_inr = ExtractedField(
                value=llm_result["bond_amount_inr"],
                confidence=confidence_scores.get("bond_amount_inr", 0.85),
                source_text=source_texts.get("bond_amount_inr"),
                method=ExtractionMethod.sniper_llm
            )
            log.info(f"Extracted Bond: {result.bond_amount_inr.value}")
        
        if llm_result.get("non_compete_months") is not None:
            result.non_compete_months = ExtractedField(
                value=llm_result["non_compete_months"],
                confidence=confidence_scores.get("non_compete_months", 0.85),
                source_text=source_texts.get("non_compete_months"),
                method=ExtractionMethod.sniper_llm
            )
            log.info(f"Extracted Non-Compete: {result.non_compete_months.value} months")
        
        if llm_result.get("probation_months") is not None:
            result.probation_months = ExtractedField(
                value=llm_result["probation_months"],
                confidence=confidence_scores.get("probation_months", 0.85),
                source_text=source_texts.get("probation_months"),
                method=ExtractionMethod.sniper_llm
            )
            log.info(f"Extracted Probation: {result.probation_months.value} months")
        
        if llm_result.get("role"):
            result.role = ExtractedField(
                value=llm_result["role"],
                confidence=0.9,
                method=ExtractionMethod.sniper_llm
            )
        
        if llm_result.get("company_name"):
            result.company_type = ExtractedField(
                value=llm_result["company_name"],
                confidence=0.9,
                method=ExtractionMethod.sniper_llm
            )
        
        return result

