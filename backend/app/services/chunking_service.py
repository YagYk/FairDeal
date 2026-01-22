from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional

from ..logging_config import get_logger
from ..models.schemas import ClauseType


log = get_logger("service.chunking")


@dataclass
class TextChunk:
    chunk_id: str
    text: str
    clause_type: ClauseType
    metadata: dict


class ChunkingService:
    """
    Clause-aware chunking for contract ingestion.
    """

    def chunk_text(
        self, 
        contract_id: str, 
        full_text: str, 
        max_chunk_size: int = 1500
    ) -> List[TextChunk]:
        if not full_text:
            return []

        # 1. Split by headings / numbered sections / paragraph boundaries
        # Look for things like "1. Termination", "Section 5: IP", "CONFIDENTIALITY", "Annexure A"
        pattern = r"(?:\n\s*(?:Section|Clause|Article|Annexure|Schedule)\s+\d+[.:\s]+|(?:\n|^)\s*\d+\.\s+[A-Z][a-zA-Z\s]{4,}(?:\n|:)|(?:\n|^)\s*[A-Z][A-Z\s]{5,}(?:\n|:))"
        sections = re.split(pattern, full_text)
        headers = re.findall(pattern, full_text)
        
        # Prepend empty string if first split didn't have a header
        if len(sections) > len(headers):
            headers = [""] + headers

        chunks: List[TextChunk] = []
        for idx, (header, content) in enumerate(zip(headers, sections)):
            combined = (header + content).strip()
            if not combined or len(combined) < 20:
                continue

            # Detect clause type from header or first line
            clause_type = self._detect_clause_type(combined)
            
            # Further split if content is too large
            if len(combined) > max_chunk_size:
                sub_parts = self._split_by_length(combined, max_chunk_size)
                for sub_idx, sub_text in enumerate(sub_parts):
                    chunks.append(
                        TextChunk(
                            chunk_id=f"{contract_id}_{idx}_{sub_idx}",
                            text=sub_text,
                            clause_type=clause_type,
                            metadata={"contract_id": contract_id}
                        )
                    )
            else:
                chunks.append(
                    TextChunk(
                        chunk_id=f"{contract_id}_{idx}",
                        text=combined,
                        clause_type=clause_type,
                        metadata={"contract_id": contract_id}
                    )
                )

        return chunks

    def _detect_clause_type(self, text: str) -> ClauseType:
        text_low = text.lower()[:300]
        mapping = {
            ClauseType.termination: ["termination", "resignation", "notice period", "separation", "relieving"],
            ClauseType.ip: ["intellectual property", "inventions", "ownership of work", "proprietary", "copyright"],
            ClauseType.non_compete: ["non-compete", "non compete", "restrictive covenant", "solicitation", "non-solicit"],
            ClauseType.confidentiality: ["confidentiality", "non-disclosure", "secret information", "ndp", "privacy"],
            ClauseType.compensation: ["compensation", "salary", "ctc", "remuneration", "benefits", "bonus", "variable pay", "incentive"],
        }
        
        for ctype, keywords in mapping.items():
            if any(k in text_low for k in keywords):
                return ctype
        
        return ClauseType.general

    def _split_by_length(self, text: str, max_size: int) -> List[str]:
        # Simple split by paragraph if possible, otherwise hard split
        paragraphs = text.split("\n\n")
        sub_chunks = []
        current = ""
        
        for p in paragraphs:
            if len(current) + len(p) < max_size:
                current += p + "\n\n"
            else:
                if current:
                    sub_chunks.append(current.strip())
                if len(p) > max_size:
                    # Hard split
                    for i in range(0, len(p), max_size):
                        sub_chunks.append(p[i:i+max_size])
                    current = ""
                else:
                    current = p + "\n\n"
        
        if current:
            sub_chunks.append(current.strip())
        return sub_chunks

