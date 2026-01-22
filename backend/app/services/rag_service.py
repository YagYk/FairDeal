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

        self._seed_gold_clauses()

    def _seed_gold_clauses(self) -> None:
        """
        Seeds/Updates gold standard clauses into Chroma.
        Uses a fixed contract_id='gold' for identification.
        """
        if not self.enabled:
            return

        # Check if already seeded
        try:
            res = self.collection.get(where={"contract_id": "gold"})
            if res and res.get("ids") and len(res["ids"]) >= 5:
                # Already seeded, skip unless we want to force refresh
                return
        except:
            pass

        gold_sources = [
            (ClauseType.termination, "Either party may terminate the employment by giving 30 days' notice in writing or by paying 30 days' salary in lieu thereof."),
            (ClauseType.ip, "Employee agrees that all inventions, improvements, and copyrightable works made by Employee during employment shall be the sole property of the Company."),
            (ClauseType.non_compete, "Employee shall not, for a period of 6 months following termination, engage in any business that competes with the Company within the relevant territory."),
            (ClauseType.confidentiality, "Employee shall maintain strict confidentiality regarding all proprietary information and trade secrets of the Company during and after employment."),
            (ClauseType.compensation, "The Employee's Total Cost to Company (CTC) shall be as specified in the compensation annexure, subject to applicable statutory deductions.")
        ]

        ids = []
        docs = []
        metas = []
        for i, (ctype, text) in enumerate(gold_sources):
            ids.append(f"gold_{ctype.value}")
            docs.append(text)
            metas.append({
                "contract_id": "gold",
                "clause_type": ctype.value,
                "is_gold": True,
                "label": f"Standard {ctype.value.capitalize()} Clause"
            })

        embeddings = self._embedder.encode(docs, normalize_embeddings=True).tolist()
        self.collection.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
        log.info("Seeded gold clauses into Chroma")

    def query_gold_clause(self, clause_type: ClauseType) -> Optional[str]:
        """
        Retrieve the gold standard text for a given clause type.
        """
        if not self.enabled:
            return None
        
        res = self.collection.get(where={"contract_id": "gold", "clause_type": clause_type.value})
        if res and res.get("documents"):
            return res["documents"][0]
        return None

    def find_similar_clauses(
        self, 
        query_text: str, 
        clause_type: ClauseType, 
        top_k: int = 3,
        include_gold: bool = False
    ) -> List[Tuple[str, float, Dict]]:
        """
        Find similar clauses in the KB.
        """
        if not self.enabled:
            return []

        emb = self._embedder.encode([query_text], normalize_embeddings=True).tolist()
        
        # Use simple where clause - ChromaDB is very strict about operators
        where = {"clause_type": clause_type.value}
        
        try:
            res = self.collection.query(
                query_embeddings=emb,
                n_results=top_k * 2 if not include_gold else top_k,  # Fetch extra to filter
                where=where,
                include=["documents", "metadatas", "distances"]
            )
        except Exception as e:
            log.error(f"ChromaDB query failed: {e}")
            return []

        results = []
        docs = res.get("documents", [[]])[0]
        metas = res.get("metadatas", [[]])[0]
        distances = res.get("distances", [[]])[0]

        for doc, meta, dist in zip(docs, metas, distances):
            # cosine similarity = 1 - distance/2 if using squared l2, 
            # but chroma cosine distance is 1 - cosine_similarity
            similarity = 1.0 - dist
            results.append((doc, float(similarity), meta))
        
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
        
        results = self.find_similar_clauses(query, clause_type or ClauseType.general, top_k=top_k, include_gold=True)
        
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
        return int(self.collection.count()) if self.collection else 0

