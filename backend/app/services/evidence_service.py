from __future__ import annotations

from typing import Dict, List, Tuple

from ..logging_config import get_logger
from ..models.schemas import (
    ClauseDriftResult,
    ClauseType,
    ContractExtractionResult,
    EvidenceChunk,
)
from .rag_service import RAGService


log = get_logger("service.evidence")


class EvidenceService:
    def __init__(self, rag: RAGService) -> None:
        self.rag = rag

    def _query_rag_for_clause(
        self,
        query_text: str,
        clause_type: ClauseType,
        top_k: int = 3,
    ) -> List[EvidenceChunk]:
        """Query RAG for similar clauses and return EvidenceChunks."""
        try:
            similar = self.rag.find_similar_clauses(
                query_text=query_text,
                clause_type=clause_type,
                top_k=top_k,
            )
        except Exception as e:
            log.error(f"ChromaDB query error for {clause_type.value}: {e}")
            return []

        return [
            EvidenceChunk(
                contract_id=meta.get("contract_id", "unknown"),
                chunk_id=meta.get("chunk_id", "unknown"),
                clause_type=clause_type,
                similarity=sim,
                text_preview=doc[:300],
                metadata=meta,
            )
            for doc, sim, meta in similar
        ]

    def collect_evidence_and_drift(
        self,
        extraction: ContractExtractionResult,
    ) -> Tuple[Dict[str, List[EvidenceChunk]], List[ClauseDriftResult]]:
        """
        Uses RAG to find similar clauses (evidence) from real contracts.
        Queries the KB for:
        1. All clause types found in extracted_clauses (termination, ip, etc.)
        2. Compensation clauses (using salary/benefits text as query)
        3. General clauses (broad contract language match)

        Drift analysis has been deprecated and returns an empty list.
        """
        evidence_map: Dict[str, List[EvidenceChunk]] = {}
        drift_results: List[ClauseDriftResult] = []

        if not self.rag.enabled:
            return {}, []

        # 1. Query for each extracted clause type
        for ctype_str, extracted_clause in extraction.extracted_clauses.items():
            if not extracted_clause.text:
                continue

            try:
                ctype = ClauseType(ctype_str)
            except ValueError:
                continue

            try:
                chunks = self._query_rag_for_clause(extracted_clause.text, ctype)
                if chunks:
                    evidence_map[ctype_str] = chunks
            except Exception as e:
                log.error(f"Error gathering evidence for {ctype_str}: {e}")
                continue

        # 2. Query for compensation clauses even if not in extracted_clauses
        #    This gives evidence about salary/benefits from similar contracts
        if "compensation" not in evidence_map:
            comp_query_parts = []
            if extraction.ctc_inr and extraction.ctc_inr.source_text:
                comp_query_parts.append(extraction.ctc_inr.source_text)
            if extraction.benefits:
                comp_query_parts.append(
                    "Benefits: " + ", ".join(extraction.benefits[:5])
                )
            if not comp_query_parts:
                comp_query_parts.append("compensation salary CTC annual package")

            comp_query = " ".join(comp_query_parts)
            try:
                comp_chunks = self._query_rag_for_clause(
                    comp_query, ClauseType.compensation, top_k=3
                )
                if comp_chunks:
                    evidence_map["compensation"] = comp_chunks
            except Exception as e:
                log.error(f"Error gathering compensation evidence: {e}")

        # 3. Query for general clauses (broad match for overall contract language)
        if "general" not in evidence_map:
            general_query_parts = []
            if extraction.role and extraction.role.value:
                general_query_parts.append(f"Role: {extraction.role.value}")
            if extraction.company_type and extraction.company_type.value:
                general_query_parts.append(
                    f"Company: {extraction.company_type.value}"
                )
            general_query_parts.append("employment agreement offer letter terms")
            general_query = " ".join(general_query_parts)

            try:
                gen_chunks = self._query_rag_for_clause(
                    general_query, ClauseType.general, top_k=3
                )
                if gen_chunks:
                    evidence_map["general"] = gen_chunks
            except Exception as e:
                log.error(f"Error gathering general evidence: {e}")

        total_evidence = sum(len(v) for v in evidence_map.values())
        log.info(
            f"RAG evidence collected: {total_evidence} chunks across "
            f"{len(evidence_map)} clause types"
        )

        return evidence_map, drift_results

