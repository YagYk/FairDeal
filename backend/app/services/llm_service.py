from __future__ import annotations

import asyncio
import json
import re
import time
from typing import Any, Dict, List, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from ..config import settings
from ..logging_config import get_logger
from ..models.schemas import (
    ContractExtractionResult,
    ExtractedField,
    ExtractionMethod,
)


log = get_logger("service.llm")


# Global rate limiter state (shared across instances)
_rate_limit_cooldown_until: float = 0.0
_last_request_time: float = 0.0
_MIN_REQUEST_INTERVAL = 4.0  # Minimum seconds between requests (15 req/min = 4s apart)


class LLMService:
    """
    Wrapper around Gemini API with strict JSON enforcement and safety.
    Includes rate limiting to prevent 429 errors.
    """

    def __init__(self) -> None:
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model

    def _is_enabled(self) -> bool:
        return bool(self.api_key)
    
    def _is_rate_limited(self) -> bool:
        """Check if we're currently in cooldown from a previous rate limit."""
        global _rate_limit_cooldown_until
        if time.time() < _rate_limit_cooldown_until:
            remaining = _rate_limit_cooldown_until - time.time()
            log.warning(f"LLM rate limited - skipping call (cooldown: {remaining:.0f}s remaining)")
            return True
        return False
    
    async def _wait_for_rate_limit(self) -> None:
        """Ensure minimum interval between requests."""
        global _last_request_time
        elapsed = time.time() - _last_request_time
        if elapsed < _MIN_REQUEST_INTERVAL:
            wait_time = _MIN_REQUEST_INTERVAL - elapsed
            log.info(f"Rate limiting: waiting {wait_time:.1f}s before LLM call")
            await asyncio.sleep(wait_time)
        _last_request_time = time.time()
    
    def _set_rate_limit_cooldown(self, seconds: float = 60.0) -> None:
        """Set cooldown period after hitting rate limit."""
        global _rate_limit_cooldown_until
        _rate_limit_cooldown_until = time.time() + seconds
        log.warning(f"Rate limit hit - entering {seconds}s cooldown period")

    @retry(
        stop=stop_after_attempt(3),  # Reduced retries since we have cooldown
        wait=wait_exponential(multiplier=2, min=10, max=60),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
        reraise=True,
    )
    async def _call_gemini(self, prompt: str) -> str:
        if not self._is_enabled():
            raise RuntimeError("LLM API key not configured")
        
        # Check if we're in cooldown from previous rate limit
        if self._is_rate_limited():
            raise RuntimeError("LLM in cooldown - skipping")
        
        # Wait to respect rate limit
        await self._wait_for_rate_limit()

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload: Dict[str, Any] = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.0,
                "topP": 0.0,
                "topK": 1,
                "maxOutputTokens": 1024,
                "response_mime_type": "application/json",
            },
        }
        
        timeout = httpx.Timeout(30.0, connect=5.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 429:
                # Set cooldown to prevent further calls
                self._set_rate_limit_cooldown(60.0)
                log.error(f"LLM rate limited (429). Entering 60s cooldown.")
                resp.raise_for_status()
            if resp.status_code == 503:
                log.warning(f"LLM service unavailable (503). Retrying...")
                resp.raise_for_status()
            resp.raise_for_status()
            data = resp.json()

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return text
        except (KeyError, IndexError) as exc:
            log.error(f"Unexpected LLM response format: {data}")
            raise RuntimeError("Invalid LLM response") from exc

    async def extract_salary_from_text(self, sniper_text: str) -> Optional[Dict[str, Any]]:
        """
        Targeted salary extraction.
        """
        prompt = (
            "Extract the employee's total annual CTC in Indian Rupees from the text.\n"
            "Rules:\n"
            "- Ignore gratuity/statutory caps or insurance limits.\n"
            "- Return ONLY JSON with fields: value (number|null), source_text (string|null), confidence (0.0-1.0).\n"
            "- If not sure, return null for value.\n"
            f"TEXT:\n{sniper_text}"
        )
        return await self._safe_json_call(prompt)

    async def extract_notice_from_text(self, sniper_text: str) -> Optional[Dict[str, Any]]:
        """
        Targeted notice period extraction.
        """
        prompt = (
            "Extract the employee notice period in DAYS from the text.\n"
            "Rules:\n"
            "- Convert weeks to days (x7), months to days (x30).\n"
            "- Return ONLY JSON with fields: value (number|null), source_text (string|null), confidence (0.0-1.0).\n"
            f"TEXT:\n{sniper_text}"
        )
        return await self._safe_json_call(prompt)

    async def extract_missing_fields(self, full_text_chunked: str) -> Optional[Dict[str, Any]]:
        """
        LLM Fallback for other fields if needed.
        """
        prompt = (
            "Extract following fields from the contract snippet:\n"
            "- bond_amount_inr (e.g. 50000)\n"
            "- non_compete_months (e.g. 12)\n"
            "- probation_months (e.g. 6)\n"
            "Rules:\n"
            "- If explicitly NOT present, return 0 for that field.\n"
            "- If mentioned but amount not specified, return null.\n"
            "- Do NOT hallucinate values.\n"
            "Return JSON matching the ContractExtractionResult schema (values only).\n"
            f"TEXT:\n{full_text_chunked}"
        )
        return await self._safe_json_call(prompt)

    async def extract_all_fields(self, document_text: str) -> Optional[Dict[str, Any]]:
        """
        COMPREHENSIVE extraction of ALL contract fields in a single optimized LLM call.
        This is more reliable and efficient than multiple separate sniper calls.
        
        Returns dict with keys:
        - ctc_inr: Annual salary in INR (number or null)
        - notice_period_days: Notice period in days (number or null)
        - bond_amount_inr: Training bond amount in INR (number or null)
        - non_compete_months: Non-compete duration in months (number or null)
        - probation_months: Probation duration in months (number or null)
        - role: Job title/designation (string or null)
        - company_name: Company name (string or null)
        - source_texts: Dict mapping field names to their source text snippets
        """
        if not self._is_enabled():
            return None
            
        # Truncate text to fit context window while preserving key sections
        max_chars = 12000
        text = document_text[:max_chars] if len(document_text) > max_chars else document_text
        
        prompt = """You are an expert contract analyst. Extract the following fields from this employment contract/offer letter.

EXTRACTION RULES:
1. For SALARY (ctc_inr):
   - Extract the TOTAL annual CTC (Cost to Company) in Indian Rupees
   - Convert LPA to INR: multiply by 100000 (e.g., 12 LPA = 1200000)
   - Convert monthly to annual: multiply by 12
   - IGNORE: gratuity limits, insurance caps, reimbursement maximums
   - Return the total package, not just basic salary

2. For NOTICE PERIOD (notice_period_days):
   - Extract in DAYS
   - Convert: weeks × 7, months × 30
   - Look for phrases: "notice period", "termination notice", "resignation notice"

3. For BOND (bond_amount_inr):
   - Training bond, service bond, or liquidated damages amount in INR
   - Return 0 if explicitly stated "no bond" or absent
   - Return the amount if bond exists

4. For NON-COMPETE (non_compete_months):
   - Duration of non-compete/non-solicitation clause in MONTHS
   - Convert years to months (× 12)
   - Return 0 if no non-compete clause exists

5. For PROBATION (probation_months):
   - Probation/trial period duration in MONTHS
   - Convert weeks to months (÷ 4)
   - Return null if not mentioned

6. For ROLE:
   - Job title, designation, or position offered
   - Extract the exact title mentioned

7. For COMPANY_NAME:
   - The employer's company name
   - Look for legal suffixes: Pvt Ltd, LLC, Inc, LLP

RESPONSE FORMAT (strict JSON):
{
  "ctc_inr": <number or null>,
  "notice_period_days": <number or null>,
  "bond_amount_inr": <number or null>,
  "non_compete_months": <number or null>,
  "probation_months": <number or null>,
  "role": "<string or null>",
  "company_name": "<string or null>",
  "source_texts": {
    "ctc_inr": "<exact text snippet where salary was found or null>",
    "notice_period_days": "<exact text snippet or null>",
    "bond_amount_inr": "<exact text snippet or null>",
    "non_compete_months": "<exact text snippet or null>",
    "probation_months": "<exact text snippet or null>"
  },
  "confidence_scores": {
    "ctc_inr": <0.0 to 1.0>,
    "notice_period_days": <0.0 to 1.0>,
    "bond_amount_inr": <0.0 to 1.0>,
    "non_compete_months": <0.0 to 1.0>,
    "probation_months": <0.0 to 1.0>
  }
}

CRITICAL: 
- Return null for fields you cannot find with confidence
- Do NOT hallucinate or guess values
- Include the exact source text for each extracted value

CONTRACT TEXT:
""" + text

        try:
            result = await self._safe_json_call(prompt)
            if result:
                log.info(f"LLM extracted all fields: ctc={result.get('ctc_inr')}, notice={result.get('notice_period_days')}, bond={result.get('bond_amount_inr')}, non_compete={result.get('non_compete_months')}, probation={result.get('probation_months')}")
            return result
        except Exception as exc:
            log.error(f"extract_all_fields failed: {exc}")
            return None

    async def extract_probation_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Targeted probation period extraction.
        """
        prompt = (
            "Extract the probation/trial period duration in MONTHS from this employment contract text.\n"
            "Rules:\n"
            "- Convert weeks to months (divide by 4)\n"
            "- Look for: 'probation period', 'trial period', 'probationary period'\n"
            "- Return ONLY JSON with fields: value (number|null), source_text (string|null), confidence (0.0-1.0).\n"
            f"TEXT:\n{text}"
        )
        return await self._safe_json_call(prompt)

    async def extract_bond_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Targeted bond/training cost extraction.
        """
        prompt = (
            "Extract the training bond or service bond amount in Indian Rupees from this contract text.\n"
            "Rules:\n"
            "- Look for: 'training bond', 'service bond', 'liquidated damages', 'recovery amount'\n"
            "- If bond is mentioned but amount not specified, return null for value\n"
            "- If explicitly 'no bond' or bond section absent, return 0 for value\n"
            "- Return ONLY JSON with fields: value (number|null), source_text (string|null), confidence (0.0-1.0).\n"
            f"TEXT:\n{text}"
        )
        return await self._safe_json_call(prompt)

    async def extract_non_compete_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Targeted non-compete clause extraction.
        """
        prompt = (
            "Extract the non-compete or non-solicitation clause duration in MONTHS from this contract text.\n"
            "Rules:\n"
            "- Convert years to months (multiply by 12)\n"
            "- Look for: 'non-compete', 'non-solicitation', 'restrictive covenant', 'shall not join competitor'\n"
            "- If no such clause exists, return 0 for value\n"
            "- Return ONLY JSON with fields: value (number|null), source_text (string|null), confidence (0.0-1.0).\n"
            f"TEXT:\n{text}"
        )
        return await self._safe_json_call(prompt)

    async def narrate(self, result_payload: Dict[str, Any]) -> Optional[str]:
        """
        Optional 2–3 sentence narration. Skipped if rate limited.
        """
        if not self._is_enabled():
            return None
        
        # Skip narration if we're rate limited (it's non-essential)
        if self._is_rate_limited():
            log.info("Skipping narration - in rate limit cooldown")
            return None
        
        # Wait for rate limit
        await self._wait_for_rate_limit()
        
        prompt = (
            "You are FairDeal Architect. Summarize this contract analysis in 2 sentences for the candidate.\n"
            "Be professional and mention if anything is anomalous or great.\n"
            f"DATA:\n{json.dumps(result_payload)}"
        )
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 429:
                    self._set_rate_limit_cooldown(60.0)
                    return None
                resp.raise_for_status()
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as exc:
            log.error(f"Narration failed: {exc}")
            return None

    async def _safe_json_call(self, prompt: str) -> Optional[Dict[str, Any]]:
        if not self._is_enabled():
            return None
        try:
            raw = await self._call_gemini(prompt)
            # Remove markdown code blocks if any
            clean = re.sub(r"```json\s*|\s*```", "", raw).strip()
            return json.loads(clean)
        except Exception as exc:
            log.error(f"JSON LLM call failed: {exc}")
            return None

