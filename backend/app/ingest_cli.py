"""
Folder-Based Contract Ingestion CLI.

Processes labeled folders of contracts and builds the knowledge base.

Folder structure (configurable):
data/
  employment/tech/junior/mumbai/*.pdf
  employment/finance/mid/delhi/*.docx
  internship/tech/junior/bangalore/*.pdf
  consultancy/other/senior/delhi/*.pdf

Or flat structure with metadata inference:
data/raw_contracts/*.pdf

Usage:
  python -m app.ingest_cli --input data --chroma_path backend/chroma_db
  python -m app.ingest_cli --input data/raw_contracts --flat
  python -m app.ingest_cli --resume  # Resume from last run
"""
import argparse
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from loguru import logger

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.parsers.pdf_parser import PDFParser
from app.parsers.docx_parser import DOCXParser
from app.services.fast_extraction_service import FastExtractionService
from app.services.embedding_service import EmbeddingService
from app.utils.chunking import ClauseAwareChunker
from app.db.chroma_client import ChromaClient
from app.config import settings


class IngestionCLI:
    """
    Command-line ingestion service for building the knowledge base.
    
    Features:
    - Folder-based processing with labeled structure
    - Resumable (skips already processed files by text_hash)
    - Batch embeddings for efficiency
    - Rate limiting for API calls
    - Progress tracking and reporting
    """
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.doc'}
    BATCH_SIZE = 100  # Embeddings batch size
    RATE_LIMIT_DELAY = 2  # Seconds between files to avoid rate limits
    
    def __init__(
        self,
        input_path: Path,
        chroma_path: Optional[Path] = None,
        flat_mode: bool = False,
        skip_existing: bool = True,
        dry_run: bool = False,
    ):
        """
        Initialize the ingestion CLI.
        
        Args:
            input_path: Path to input directory
            chroma_path: Path to ChromaDB storage (uses config default if None)
            flat_mode: If True, don't parse folder structure for labels
            skip_existing: If True, skip files already processed
            dry_run: If True, don't actually ingest, just report what would be done
        """
        self.input_path = Path(input_path).resolve()
        self.chroma_path = Path(chroma_path).resolve() if chroma_path else settings.get_chroma_db_path()
        self.flat_mode = flat_mode
        self.skip_existing = skip_existing
        self.dry_run = dry_run
        
        # Initialize components
        self.pdf_parser = PDFParser()
        self.docx_parser = DOCXParser()
        self.fast_extraction = FastExtractionService()
        self.embedding_service = EmbeddingService()
        self.chunker = ClauseAwareChunker()
        
        # ChromaDB client (only if not dry run)
        self.chroma_client = None if dry_run else ChromaClient()
        
        # Tracking
        self.processed_hashes: set = set()
        self.stats = {
            "total_files": 0,
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "total_chunks": 0,
        }
        
        # Load existing hashes
        self._load_processed_hashes()
    
    def _load_processed_hashes(self):
        """Load hashes of already processed files."""
        processed_dir = settings.get_processed_contracts_path()
        if processed_dir.exists():
            for metadata_file in processed_dir.glob("*_metadata.json"):
                try:
                    with open(metadata_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if "text_hash" in data:
                            self.processed_hashes.add(data["text_hash"])
                except Exception:
                    continue
        logger.info(f"Loaded {len(self.processed_hashes)} existing file hashes")
    
    def discover_files(self) -> List[Tuple[Path, Dict[str, str]]]:
        """
        Discover all contract files with their labels.
        
        Returns:
            List of (file_path, labels_dict) tuples
        """
        files = []
        
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input path not found: {self.input_path}")
        
        if self.flat_mode or self.input_path.is_file():
            # Flat mode: just find all files
            if self.input_path.is_file():
                files.append((self.input_path, {}))
            else:
                for ext in self.SUPPORTED_EXTENSIONS:
                    for f in self.input_path.rglob(f"*{ext}"):
                        files.append((f, {}))
        else:
            # Structured mode: parse folder structure for labels
            # Expected: contract_type/industry/role_level/location/*.pdf
            for f in self.input_path.rglob("*"):
                if f.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    labels = self._parse_folder_structure(f)
                    files.append((f, labels))
        
        logger.info(f"Discovered {len(files)} files to process")
        return files
    
    def _parse_folder_structure(self, file_path: Path) -> Dict[str, str]:
        """
        Parse folder structure to extract labels.
        
        Expected structure:
        input_path/contract_type/industry/role_level/location/file.pdf
        
        Also supports:
        input_path/contract_type/file.pdf
        input_path/file.pdf
        """
        labels = {}
        
        try:
            rel_path = file_path.relative_to(self.input_path)
            parts = rel_path.parts[:-1]  # Exclude filename
            
            if len(parts) >= 1:
                labels["contract_type"] = parts[0].lower().replace("_", " ").replace("-", " ")
            if len(parts) >= 2:
                labels["industry"] = parts[1].lower()
            if len(parts) >= 3:
                labels["role_level"] = parts[2].lower()
            if len(parts) >= 4:
                labels["location"] = parts[3].lower()
        except ValueError:
            pass  # File not under input_path
        
        return labels
    
    def process_file(
        self,
        file_path: Path,
        folder_labels: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single contract file.
        
        Args:
            file_path: Path to the file
            folder_labels: Labels extracted from folder structure
            
        Returns:
            Processing result dict or None if skipped/failed
        """
        logger.info(f"Processing: {file_path.name}")
        
        # Step 1: Parse document
        try:
            text = self._parse_document(file_path)
        except Exception as e:
            logger.error(f"Failed to parse {file_path.name}: {e}")
            self.stats["errors"] += 1
            return {"status": "error", "error": str(e), "file": str(file_path)}
        
        if not text or len(text.strip()) < 50:
            logger.warning(f"Insufficient text extracted from {file_path.name}")
            self.stats["errors"] += 1
            return {"status": "error", "error": "Insufficient text", "file": str(file_path)}
        
        # Step 2: Compute hash and check for duplicates
        text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
        
        if self.skip_existing and text_hash in self.processed_hashes:
            logger.info(f"Skipping (already processed): {file_path.name}")
            self.stats["skipped"] += 1
            return {"status": "skipped", "reason": "duplicate", "file": str(file_path)}
        
        # Step 3: Extract metadata using fast extraction
        try:
            metadata = self.fast_extraction.extract_metadata(text)
        except Exception as e:
            logger.error(f"Extraction failed for {file_path.name}: {e}")
            self.stats["errors"] += 1
            return {"status": "error", "error": f"Extraction failed: {e}", "file": str(file_path)}
        
        # Merge folder labels with extracted metadata (folder labels take precedence if specified)
        contract_id = file_path.stem
        contract_metadata = self._build_contract_metadata(metadata, folder_labels, contract_id, text_hash, file_path)
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would ingest: {file_path.name} with metadata: {contract_metadata}")
            self.stats["processed"] += 1
            return {"status": "dry_run", "metadata": contract_metadata, "file": str(file_path)}
        
        # Step 4: Chunk text
        chunks = self.chunker.chunk_text(text, contract_id)
        logger.debug(f"Created {len(chunks)} chunks for {file_path.name}")
        
        # Step 5: Generate embeddings (with retry)
        try:
            chunk_texts = [chunk["text"] for chunk in chunks]
            embeddings = self._generate_embeddings_with_retry(chunk_texts)
        except Exception as e:
            logger.error(f"Embedding failed for {file_path.name}: {e}")
            self.stats["errors"] += 1
            return {"status": "error", "error": f"Embedding failed: {e}", "file": str(file_path)}
        
        # Step 6: Store in ChromaDB
        try:
            self.chroma_client.add_chunks(
                chunks=chunks,
                embeddings=embeddings.tolist(),
                contract_metadata=contract_metadata,
            )
        except Exception as e:
            logger.error(f"ChromaDB storage failed for {file_path.name}: {e}")
            self.stats["errors"] += 1
            return {"status": "error", "error": f"Storage failed: {e}", "file": str(file_path)}
        
        # Step 7: Save metadata to disk
        self._save_metadata(contract_id, metadata, contract_metadata, chunks, text_hash)
        
        # Update tracking
        self.processed_hashes.add(text_hash)
        self.stats["processed"] += 1
        self.stats["total_chunks"] += len(chunks)
        
        logger.info(f"✓ Ingested: {file_path.name} ({len(chunks)} chunks)")
        
        return {
            "status": "success",
            "contract_id": contract_id,
            "num_chunks": len(chunks),
            "metadata": contract_metadata,
            "file": str(file_path),
        }
    
    def _parse_document(self, file_path: Path) -> str:
        """Parse PDF or DOCX file and return text."""
        suffix = file_path.suffix.lower()
        
        if suffix == ".pdf":
            return self.pdf_parser.extract_text(file_path)
        elif suffix in [".docx", ".doc"]:
            return self.docx_parser.extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
    
    def _build_contract_metadata(
        self,
        extracted: Any,
        folder_labels: Dict[str, str],
        contract_id: str,
        text_hash: str,
        file_path: Path,
    ) -> Dict[str, Any]:
        """Build contract metadata dict from extraction and folder labels."""
        def get_val(field):
            if hasattr(field, 'value'):
                return field.value
            elif isinstance(field, dict):
                return field.get('value')
            return field
        
        # Start with extracted values
        metadata = {
            "contract_id": contract_id,
            "contract_type": folder_labels.get("contract_type") or get_val(extracted.contract_type) or "employment",
            "industry": folder_labels.get("industry") or get_val(extracted.industry) or "other",
            "role_level": folder_labels.get("role_level") or get_val(extracted.role) or "mid",
            "location": folder_labels.get("location") or get_val(extracted.location) or "India",
            "salary_in_inr": get_val(extracted.salary) or 0,
            "notice_period_days": get_val(extracted.notice_period_days) or 0,
            "non_compete": get_val(extracted.non_compete) or False,
            "text_hash": text_hash,
            "raw_file_path": str(file_path),
            "processed_date": datetime.now().strftime("%Y-%m-%d"),
        }
        
        return metadata
    
    def _generate_embeddings_with_retry(self, texts: List[str], max_retries: int = 3) -> Any:
        """Generate embeddings with exponential backoff retry."""
        import numpy as np
        
        for attempt in range(max_retries):
            try:
                return self.embedding_service.generate_embeddings(texts, batch_size=self.BATCH_SIZE)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "rate" in error_str.lower() or "quota" in error_str.lower():
                    delay = (2 ** attempt) * 5  # 5, 10, 20 seconds
                    logger.warning(f"Rate limit hit, waiting {delay}s before retry...")
                    time.sleep(delay)
                else:
                    raise
        
        raise ValueError(f"Embedding failed after {max_retries} retries")
    
    def _save_metadata(
        self,
        contract_id: str,
        extracted: Any,
        contract_metadata: Dict[str, Any],
        chunks: List[Dict[str, Any]],
        text_hash: str,
    ):
        """Save processed metadata to disk."""
        processed_dir = settings.get_processed_contracts_path()
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = processed_dir / f"{contract_id}_metadata.json"
        
        # Serialize extracted metadata
        if hasattr(extracted, 'model_dump'):
            extracted_dict = extracted.model_dump()
        elif hasattr(extracted, 'dict'):
            extracted_dict = extracted.dict()
        else:
            extracted_dict = {}
        
        data = {
            "contract_id": contract_id,
            "text_hash": text_hash,
            "metadata": extracted_dict,
            "contract_metadata": contract_metadata,
            "num_chunks": len(chunks),
            "processed_date": datetime.now().isoformat(),
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    
    def run(self) -> Dict[str, Any]:
        """
        Run the full ingestion pipeline.
        
        Returns:
            Summary dict with statistics
        """
        start_time = time.time()
        
        logger.info(f"Starting ingestion from: {self.input_path}")
        logger.info(f"ChromaDB path: {self.chroma_path}")
        logger.info(f"Mode: {'flat' if self.flat_mode else 'structured'}, Skip existing: {self.skip_existing}")
        
        # Discover files
        files = self.discover_files()
        self.stats["total_files"] = len(files)
        
        if not files:
            logger.warning("No files found to process")
            return self.stats
        
        # Process each file
        results = []
        for i, (file_path, labels) in enumerate(files):
            try:
                # Rate limiting
                if i > 0 and not self.dry_run:
                    time.sleep(self.RATE_LIMIT_DELAY)
                
                result = self.process_file(file_path, labels)
                results.append(result)
                
                # Progress update
                if (i + 1) % 10 == 0:
                    logger.info(f"Progress: {i + 1}/{len(files)} files processed")
                
            except Exception as e:
                logger.error(f"Unexpected error processing {file_path}: {e}")
                self.stats["errors"] += 1
                results.append({"status": "error", "error": str(e), "file": str(file_path)})
        
        # Summary
        elapsed = time.time() - start_time
        self.stats["elapsed_seconds"] = round(elapsed, 2)
        self.stats["files_per_second"] = round(len(files) / elapsed, 2) if elapsed > 0 else 0
        
        logger.info("=" * 60)
        logger.info("INGESTION COMPLETE")
        logger.info(f"Total files: {self.stats['total_files']}")
        logger.info(f"Processed: {self.stats['processed']}")
        logger.info(f"Skipped: {self.stats['skipped']}")
        logger.info(f"Errors: {self.stats['errors']}")
        logger.info(f"Total chunks: {self.stats['total_chunks']}")
        logger.info(f"Elapsed: {elapsed:.1f}s")
        logger.info("=" * 60)
        
        return self.stats


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest contracts into the FairDeal knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest from structured folders
  python -m app.ingest_cli --input data/contracts

  # Ingest from flat folder
  python -m app.ingest_cli --input data/raw_contracts --flat

  # Dry run (no actual changes)
  python -m app.ingest_cli --input data --dry-run

  # Force reprocess all files
  python -m app.ingest_cli --input data --force
"""
    )
    
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="data/raw_contracts",
        help="Input directory containing contracts"
    )
    
    parser.add_argument(
        "--chroma-path",
        type=str,
        default=None,
        help="Path to ChromaDB storage (default: from config)"
    )
    
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Flat mode: don't parse folder structure for labels"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force reprocess all files (ignore existing)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run: report what would be done without making changes"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")
    
    # Run ingestion
    cli = IngestionCLI(
        input_path=args.input,
        chroma_path=args.chroma_path,
        flat_mode=args.flat,
        skip_existing=not args.force,
        dry_run=args.dry_run,
    )
    
    stats = cli.run()
    
    # Exit code based on errors
    sys.exit(1 if stats.get("errors", 0) > 0 else 0)


if __name__ == "__main__":
    main()
