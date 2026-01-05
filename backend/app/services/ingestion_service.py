"""
Ingestion service that orchestrates the full pipeline:
1. Parse documents (PDF/DOCX)
2. Extract metadata (Fast Regex - NO LLM to avoid rate limits)
3. Chunk text (clause-aware)
4. Generate embeddings
5. Store in ChromaDB
"""
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger
import json

from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.services.fast_extraction_service import FastExtractionService
from app.services.embedding_service import EmbeddingService
from app.utils.chunking import ClauseAwareChunker
from app.db.chroma_client import ChromaClient
from app.config import settings


class IngestionService:
    """
    Orchestrates the complete ingestion pipeline.
    
    Design: Single service that coordinates all steps:
    - Parsing → Metadata → Chunking → Embedding → Storage
    
    Uses FastExtractionService instead of LLM to avoid rate limits.
    """
    
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.fast_extraction = FastExtractionService()  # Use fast extraction instead of LLM
        self.embedding_service = EmbeddingService()
        self.chunker = ClauseAwareChunker()
        self.chroma_client = ChromaClient()
    
    def _get_val(self, field):
        """Helper to extract value from ExtractedField."""
        if hasattr(field, 'value'):
            return field.value
        elif isinstance(field, dict):
            return field.get('value')
        return field
    
    def ingest_contract(self, file_path: Path) -> Dict[str, Any]:
        """
        Ingest a single contract file.
        
        Args:
            file_path: Path to PDF or DOCX file
            
        Returns:
            Dictionary with ingestion results and metadata
        """
        logger.info(f"Starting ingestion for: {file_path.name}")
        
        # Step 1: Parse document
        text = self._parse_document(file_path)
        logger.info(f"Extracted {len(text)} characters from document")
        
        # Step 2: Extract metadata using FAST extraction (no LLM)
        metadata = self.fast_extraction.extract_metadata(text)
        contract_id = file_path.stem  # Use filename without extension as ID
        
        # Step 3: Chunk text
        chunks = self.chunker.chunk_text(text, contract_id)
        logger.info(f"Created {len(chunks)} chunks")
        
        # Step 4: Generate embeddings
        chunk_texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_service.generate_embeddings(chunk_texts)
        logger.info(f"Generated embeddings with shape {embeddings.shape}")
        
        # Validate embedding count matches chunk count
        if len(embeddings) != len(chunks):
            raise ValueError(f"Embedding count mismatch: {len(embeddings)} embeddings for {len(chunks)} chunks")
        
        # Step 5: Prepare metadata for ChromaDB (extract values from ExtractedField)
        contract_metadata = {
            "contract_id": contract_id,
            "contract_type": self._get_val(metadata.contract_type) or "employment",
            "industry": self._get_val(metadata.industry) or "general",
            "role": self._get_val(metadata.role) or "",
            "location": self._get_val(metadata.location) or "India",
            "salary": self._get_val(metadata.salary) or 0.0,
            "notice_period_days": self._get_val(metadata.notice_period_days) or 0,
            "non_compete": self._get_val(metadata.non_compete) or False,
        }
        
        # Step 6: Store in ChromaDB
        self.chroma_client.add_chunks(
            chunks=chunks,
            embeddings=embeddings.tolist(),
            contract_metadata=contract_metadata,
        )
        
        # Step 7: Save processed metadata to disk (for statistics later)
        self._save_processed_metadata(contract_id, metadata, chunks)
        
        logger.info(f"Successfully ingested contract: {contract_id}")
        
        return {
            "contract_id": contract_id,
            "metadata": contract_metadata,
            "num_chunks": len(chunks),
            "status": "success",
        }
    
    def ingest_directory(self, directory_path: Path, skip_existing: bool = True) -> List[Dict[str, Any]]:
        """
        Ingest all contracts from a directory.
        
        Args:
            directory_path: Path to directory containing PDF/DOCX files
            skip_existing: If True, skip files that have already been processed
            
        Returns:
            List of ingestion results
        """
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find all PDF and DOCX files
        pdf_files = list(directory_path.glob("*.pdf"))
        docx_files = list(directory_path.glob("*.docx"))
        all_files = pdf_files + docx_files
        
        if not all_files:
            logger.warning(f"No PDF or DOCX files found in {directory_path}")
            return []
        
        # Check which files are already processed
        processed_dir = settings.get_processed_contracts_path()
        already_processed = set()
        if skip_existing and processed_dir.exists():
            for metadata_file in processed_dir.glob("*_metadata.json"):
                # Extract contract_id from filename (remove _metadata.json suffix)
                contract_id = metadata_file.stem.replace("_metadata", "")
                already_processed.add(contract_id)
        
        # Filter to only new files
        files_to_process = []
        skipped_files = []
        for file_path in all_files:
            contract_id = file_path.stem
            if skip_existing and contract_id in already_processed:
                skipped_files.append(file_path.name)
            else:
                files_to_process.append(file_path)
        
        if skipped_files:
            logger.info(f"Skipping {len(skipped_files)} already processed files: {skipped_files[:5]}{'...' if len(skipped_files) > 5 else ''}")
        
        if not files_to_process:
            logger.info("All files have already been processed. Nothing new to ingest.")
            return []
        
        logger.info(f"Found {len(files_to_process)} NEW files to ingest (skipped {len(skipped_files)} existing)")
        
        results = []
        import time
        
        for i, file_path in enumerate(files_to_process):
            try:
                # Rate limiting: Wait 5 seconds between contracts to avoid hitting quota
                if i > 0:
                    wait_time = 5
                    logger.info(f"Waiting {wait_time} seconds before next contract (rate limiting)...")
                    time.sleep(wait_time)
                
                result = self.ingest_contract(file_path)
                results.append(result)
                logger.info(f"✓ Ingested {i+1}/{len(files_to_process)}: {file_path.name}")
            except Exception as e:
                error_str = str(e)
                logger.error(f"Failed to ingest {file_path.name}: {e}")
                
                if "429" in error_str or "quota" in error_str.lower():
                    logger.warning("Rate limit detected. Waiting 60 seconds before continuing...")
                    time.sleep(60)
                
                results.append({
                    "contract_id": file_path.stem,
                    "status": "error",
                    "error": str(e),
                })
        
        logger.info(f"Ingested {len([r for r in results if r.get('status') == 'success'])}/{len(files_to_process)} contracts")
        return results
    
    def _parse_document(self, file_path: Path) -> str:
        """Parse PDF or DOCX file and return text."""
        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            return self.pdf_parser.extract_text(file_path)
        elif suffix in [".docx", ".doc"]:
            return self.docx_parser.extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    
    def _save_processed_metadata(
        self,
        contract_id: str,
        metadata: Any,
        chunks: List[Dict[str, Any]],
    ) -> None:
        """Save processed metadata to disk for later analysis."""
        processed_dir = settings.get_processed_contracts_path()
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = processed_dir / f"{contract_id}_metadata.json"
        
        # Serialize metadata properly (handle ExtractedField objects)
        if hasattr(metadata, 'model_dump'):
            metadata_dict = metadata.model_dump()
        elif hasattr(metadata, 'dict'):
            metadata_dict = metadata.dict()
        else:
            metadata_dict = dict(metadata) if metadata else {}
        
        data = {
            "contract_id": contract_id,
            "metadata": metadata_dict,
            "num_chunks": len(chunks),
            "chunk_summary": {
                chunk["clause_type"]: sum(1 for c in chunks if c["clause_type"] == chunk["clause_type"])
                for chunk in chunks
            },
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        logger.debug(f"Saved metadata to {output_file}")

