from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..config import settings
from ..db.chroma_client import get_collection
from ..logging_config import get_logger
from ..models.schemas import (
    ClauseType,
    KBStats,
    KBContractMetadata,
    KBChunkPreview,
)


log = get_logger("service.rag")


class RAGService:
    def __init__(self) -> None:
        self.enabled = True
        self._chroma_error_count = 0
        self._max_chroma_errors = 3  # Disable after 3 consecutive errors
        
        try:
            self.collection = get_collection()
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(settings.embedding_model_name)
        except Exception as exc:
            log.error(f"RAG initialization failed: {exc}")
            self.enabled = False
            self.collection = None
            self._embedder = None
            # Do not return here, let it proceed seamlessly with enabled=False

        # self._seed_gold_clauses()  # REMOVED

    def find_similar_clauses(
        self, 
        query_text: str, 
        clause_type: ClauseType, 
        top_k: int = 3,
    ) -> List[Tuple[str, float, Dict]]:
        """
        Find similar clauses in the KB.
        """
        if not self.enabled:
            return []
        
        # Early exit if we've hit too many errors
        if self._chroma_error_count >= self._max_chroma_errors:
            return []

        emb = self._embedder.encode([query_text], normalize_embeddings=True).tolist()
        
        # We only filter by clause_type now. This is simple and reliable.
        use_where = False 
        res = None
        
        try:
            where_clause = {"clause_type": clause_type.value}
            
            res = self.collection.query(
                query_embeddings=emb,
                n_results=top_k * 2, # Fetch more to account for any internal filtering
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            # Reset error count on success
            self._chroma_error_count = 0
            use_where = True
            
        except Exception as e:
            error_msg = str(e)
            log.warning(f"ChromaDB where clause failed, using fallback (no where clause): {error_msg}")
            
            try:
                # Fallback: fetch without where clause
                res = self.collection.query(
                    query_embeddings=emb,
                    n_results=top_k * 5, 
                    where=None,  # No where clause - fetch all and filter in Python
                    include=["documents", "metadatas", "distances"]
                )
                use_where = False
            except Exception as final_e:
                self._chroma_error_count += 1
                log.error(f"ChromaDB query failed completely: {final_e}")
                
                if self._chroma_error_count >= self._max_chroma_errors:
                    log.error(f"RAG disabled after {self._chroma_error_count} consecutive ChromaDB errors")
                    self.enabled = False
                return []
        
        if res is None:
            return []

        results = []
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        distances = res.get("distances", [[]])[0]

        for doc, meta, dist in zip(docs, metas, distances):
            # Python-side filtering:
            # 1. Filter by clause_type (if we didn't use where clause)
            if not use_where and meta.get("clause_type") != clause_type.value:
                continue
            
            # cosine similarity = 1 - distance/2 if using squared l2, 
            # but chroma cosine distance is 1 - cosine_similarity
            similarity = 1.0 - dist
            results.append((doc, float(similarity), meta))
            
            if len(results) >= top_k:
                break
        
        return results

    def get_kb_stats(self) -> KBStats:
        """
        Compute KB statistics using manifest and chroma count.
        """
        if not self.enabled:
            return KBStats(num_contracts=0, num_chunks=0, clause_type_counts={})
        
        processed_dir = settings.processed_dir
        manifest_path = processed_dir / "manifest.json"
        
        num_contracts = 0
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text())
                num_contracts = len(manifest.get("files", {}))
            except:
                pass
        
        num_chunks = int(self.collection.count()) if self.collection else 0
        clause_type_counts = {}
        
        if self.collection and num_chunks > 0:
            try:
                # We can't do a full group-by in Chroma easily without a lot of memory, 
                # but we can fetch just metadata for all chunks if count is manageable.
                # For high-principal usage, we'll iterate or use a simpler count.
                # Here we just iterate through standard clause types.
                for ct in ClauseType:
                    res = self.collection.get(where={"clause_type": ct.value}, include=[])
                    if res and res.get("ids"):
                        clause_type_counts[ct.value] = len(res["ids"])
                    else:
                        clause_type_counts[ct.value] = 0
            except Exception as e:
                log.error(f"Error computing clause counts: {e}")

        return KBStats(
            num_contracts=num_contracts,
            num_chunks=num_chunks,
            clause_type_counts=clause_type_counts
        )

    def list_contracts(self, limit: int, offset: int) -> Dict[str, Any]:
        processed_dir = settings.processed_dir
        manifest_path = processed_dir / "manifest.json"
        
        total = 0
        contracts = []
        
        if manifest_path.exists():
            try:
                manifest = json.loads(manifest_path.read_text())
                files = list(manifest.get("files", {}).values())
                total = len(files)
                page = files[offset: offset+limit]
                
                contracts = [
                    KBContractMetadata(
                        contract_id=f["contract_id"],
                        filename=f["filename"],
                    ) for f in page
                ]
            except Exception as e:
                log.error(f"Error listing contracts: {e}")
        
        return {
            "contracts": contracts,
            "total": total,
            "offset": offset,
            "limit": limit,
            "filters_applied": {}
        }

    def get_contract_chunks(self, contract_id: str) -> List[KBChunkPreview]:
        if not self.enabled or not self.collection:
            return []
        
        res = self.collection.get(
            where={"contract_id": contract_id},
            include=["documents", "metadatas"]
        )
        
        out = []
        docs = res.get("documents", [])
        metas = res.get("metadatas", [])
        ids = res.get("ids", [])
        
        for doc, meta, _id in zip(docs, metas, ids):
            out.append(KBChunkPreview(
                contract_id=contract_id,
                chunk_id=meta.get("chunk_id", _id),
                clause_type=ClauseType(meta.get("clause_type", "general")),
                text_preview=doc[:300]
            ))
        return out

    def search_chunks(
        self, 
        query: str, 
        clause_type: Optional[ClauseType], 
        top_k: int
    ) -> List[KBChunkPreview]:
        if not self.enabled or not self.collection:
            return []
        
        results = self.find_similar_clauses(query, clause_type or ClauseType.general, top_k=top_k)
        
        out = []
        for doc, sim, meta in results:
            out.append(KBChunkPreview(
                contract_id=meta.get("contract_id", "unknown"),
                chunk_id=meta.get("chunk_id", "unknown"),
                clause_type=ClauseType(meta.get("clause_type", "general")),
                text_preview=doc[:300],
                similarity=sim
            ))
        return out

    def get_contract(self, contract_id: str) -> KBContractMetadata:
        processed_dir = settings.processed_dir
        p = processed_dir / f"{contract_id}.json"
        if not p.exists():
            raise ValueError(f"Contract {contract_id} not found")
        
        data = json.loads(p.read_text())
        return KBContractMetadata(
            contract_id=data["contract_id"],
            filename=data["filename"],
            extra={"num_chunks": data.get("num_chunks", 0)}
        )

    def collection_count(self) -> int:
        if not self.enabled or not self.collection:
            return 0
        try:
            return int(self.collection.count())
        except Exception as e:
            log.error(f"Error getting collection count: {e}")
            return 0

