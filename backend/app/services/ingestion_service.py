from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Optional

from ..config import settings
from ..logging_config import get_logger
from ..models.schemas import ClauseType, ExtractionMethod
from .chunking_service import ChunkingService
from .parser_service import ParserService
from .rule_extraction_service import RuleExtractionService


log = get_logger("service.ingestion")


class IngestionService:
    def __init__(self) -> None:
        self.settings = settings
        self.parser = ParserService()
        self.chunker = ChunkingService()
        self.rule_extractor = RuleExtractionService()
        
        from ..db.chroma_client import get_collection
        self.collection = get_collection()
        
        self.settings.processed_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.settings.processed_dir / "manifest.json"
        self._load_manifest()

    def _load_manifest(self):
        if self.manifest_path.exists():
            try:
                self.manifest = json.loads(self.manifest_path.read_text())
            except:
                self.manifest = {"files": {}}
        else:
            self.manifest = {"files": {}}

    def _save_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest, indent=2))

    def count_processed_contracts(self) -> int:
        return len(self.manifest.get("files", {}))

    def ingest_directory(self, input_dir: Path) -> Dict[str, int]:
        files = []
        for ext in ["*.pdf", "*.docx"]:
            files.extend(input_dir.rglob(ext))
        
        results = {"ingested": 0, "skipped": 0, "chunks_added": 0}
        for f in files:
            try:
                added = self.ingest_file(f)
                if added == 0:
                    results["skipped"] += 1
                else:
                    results["ingested"] += 1
                    results["chunks_added"] += added
            except Exception as exc:
                log.error(f"Failed ingesting {f.name}: {exc}")
        
        self._save_manifest()
        return results

    def ingest_file(self, file_path: Path) -> int:
        content = file_path.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Deduplication by hash
        if file_hash in self.manifest["files"]:
            log.info(f"Skipping {file_path.name}, already ingested.")
            return 0

        contract_id = file_hash[:16]
        parsed = self.parser.parse(content, filename=file_path.name)
        
        # Rule-based extraction for metadata during ingestion
        extraction = self.rule_extractor.extract(parsed)

        # Chunk the contract text for RAG storage
        chunks = self.chunker.chunk_text(contract_id=contract_id, full_text=parsed.full_text)
        if not chunks:
            log.warning(f"No chunks produced for {file_path.name} (empty/low-text document?)")
        
        # Metadata from path
        # Expected structure: industry/level/location/filename
        # e.g., tech/senior/mumbai/google_sde3_2024.pdf
        rel_path = file_path.relative_to(self.settings.contracts_raw_dir)
        path_parts = rel_path.parts
        
        path_metadata = {
            "industry": path_parts[0] if len(path_parts) > 0 else "unknown",
            "level": path_parts[1] if len(path_parts) > 1 else "unknown",
            "location": path_parts[2] if len(path_parts) > 2 else "unknown",
        }

        ids = []
        docs = []
        metas = []

        for ch in chunks:
            ids.append(ch.chunk_id)
            docs.append(ch.text)
            metas.append(
                {
                    "contract_id": contract_id,
                    "chunk_id": ch.chunk_id,
                    "clause_type": ch.clause_type.value,
                    "filename": file_path.name,
                    "file_hash": file_hash,
                    **path_metadata
                }
            )

        # Local embeddings
        from sentence_transformers import SentenceTransformer
        embedder = SentenceTransformer(settings.embedding_model_name)
        embeddings = embedder.encode(docs, normalize_embeddings=True).tolist()
        
        self.collection.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)

        # Store metadata JSON
        meta_data = {
            "contract_id": contract_id,
            "filename": file_path.name,
            "file_hash": file_hash,
            "extraction": extraction.model_dump(),
            "num_chunks": len(chunks),
            "path_metadata": path_metadata
        }
        (self.settings.processed_dir / f"{contract_id}.json").write_text(json.dumps(meta_data, indent=2))

        # Update manifest
        self.manifest["files"][file_hash] = {
            "filename": file_path.name,
            "contract_id": contract_id,
            "timestamp": str(Path(file_path).stat().st_mtime)
        }
        
        log.info(f"Ingested {file_path.name} -> {contract_id}")
        return len(chunks)

def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest contracts into FairDeal KB")
    parser.add_argument("--input", required=True, help="Input directory")
    args = parser.parse_args()

    svc = IngestionService()
    res = svc.ingest_directory(Path(args.input))
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    main()

