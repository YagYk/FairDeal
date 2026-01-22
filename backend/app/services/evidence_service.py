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

    def collect_evidence_and_drift(
        self,
        extraction: ContractExtractionResult
    ) -> Tuple[Dict[str, List[EvidenceChunk]], List[ClauseDriftResult]]:
        """
        Uses RAG to find similar clauses (evidence) and compute drift from gold standards.
        """
        evidence_map: Dict[str, List[EvidenceChunk]] = {}
        drift_results: List[ClauseDriftResult] = []

        if not self.rag.enabled:
            return {}, []

        for ctype_str, extracted_clause in extraction.extracted_clauses.items():
            if not extracted_clause.text:
                continue
            
            try:
                ctype = ClauseType(ctype_str)
            except ValueError:
                continue

            # 1. Collect Evidence (top 3 similar clauses from KB)
            try:
                similar = self.rag.find_similar_clauses(
                    query_text=extracted_clause.text,
                    clause_type=ctype,
                    top_k=3,
                    include_gold=False
                )
                
                chunks = [
                    EvidenceChunk(
                        contract_id=meta.get("contract_id", "unknown"),
                        chunk_id=meta.get("chunk_id", "unknown"),
                        clause_type=ctype,
                        similarity=sim,
                        text_preview=doc[:300],
                        metadata=meta
                    )
                    for doc, sim, meta in similar
                ]
                evidence_map[ctype_str] = chunks

                # 2. Compute Drift against Gold
                gold_text = self.rag.query_gold_clause(ctype)
                if gold_text:
                    # We can use the same embedding logic to get similarity to gold
                    # RAGService could have a helper for this or we just use find_similar_clauses with gold included
                    gold_similar = self.rag.find_similar_clauses(
                        query_text=extracted_clause.text,
                        clause_type=ctype,
                        top_k=1,
                        include_gold=True
                    )
                    
                    # Check if the most similar one is gold
                    gold_sim = 0.0
                    gold_preview = "No gold clause found"
                    for doc, sim, meta in gold_similar:
                        if meta.get("is_gold"):
                            gold_sim = sim
                            gold_preview = doc[:100] + "..."
                            break
                    
                    status = "standard" if gold_sim >= 0.6 else "anomalous"
                    
                    drift_results.append(
                        ClauseDriftResult(
                            clause_type=ctype,
                            similarity_to_gold=gold_sim,
                            status=status,
                            matched_gold_clause_preview=gold_preview,
                            retrieved_examples=chunks
                        )
                    )
            except Exception as e:
                log.error(f"Error gathering evidence/drift for {ctype_str}: {e}")
                # Continue to next clause type instead of failing
                continue

        return evidence_map, drift_results

