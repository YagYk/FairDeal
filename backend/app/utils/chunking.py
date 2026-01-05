"""
Clause-aware chunking service for legal contracts.
Splits contracts by headings/clauses while respecting token limits.
"""
import re
from typing import List, Dict, Optional, Any
import tiktoken
from loguru import logger

from app.config import settings


class ClauseAwareChunker:
    """
    Chunks contracts by detecting clause boundaries (headings).
    
    Design choices:
    1. Clause-aware: Legal contracts have clear structure (TERMINATION, NOTICE PERIOD, etc.)
       Splitting by these preserves semantic meaning
    2. Token-based limits: Ensures chunks fit within LLM context windows
    3. Overlap: Prevents losing context at chunk boundaries
    4. Preserves clause names: Each chunk knows which clause it belongs to
    """
    
    # Common legal clause headings (case-insensitive patterns)
    CLAUSE_HEADINGS = [
        r"^TERMINATION\s*$",
        r"^NOTICE\s+PERIOD\s*$",
        r"^NON-?COMPETE\s*$",
        r"^NON-?DISCLOSURE\s*$",
        r"^COMPENSATION\s*$",
        r"^SALARY\s*$",
        r"^BENEFITS\s*$",
        r"^LEAVE\s*$",
        r"^INTELLECTUAL\s+PROPERTY\s*$",
        r"^CONFIDENTIALITY\s*$",
        r"^RESTRICTIVE\s+COVENANTS\s*$",
        r"^DISPUTE\s+RESOLUTION\s*$",
        r"^GOVERNING\s+LAW\s*$",
        r"^JURISDICTION\s*$",
        r"^LIABILITY\s*$",
        r"^INDEMNIFICATION\s*$",
        r"^SEVERABILITY\s*$",
        r"^ENTIRE\s+AGREEMENT\s*$",
        r"^AMENDMENT\s*$",
        r"^ASSIGNMENT\s*$",
    ]
    
    def __init__(
        self,
        max_chunk_size_tokens: Optional[int] = None,
        chunk_overlap_tokens: Optional[int] = None,
    ):
        """
        Initialize chunker with token limits.
        
        Args:
            max_chunk_size_tokens: Maximum tokens per chunk (default from config)
            chunk_overlap_tokens: Overlap between chunks in tokens (default from config)
        """
        self.max_chunk_size = max_chunk_size_tokens or settings.max_chunk_size_tokens
        self.chunk_overlap = chunk_overlap_tokens or settings.chunk_overlap_tokens
        
        # Initialize tokenizer (using cl100k_base for GPT models)
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            logger.warning("Could not load tiktoken, falling back to character-based chunking")
            self.tokenizer = None
    
    def chunk_text(self, text: str, contract_id: str) -> List[Dict[str, Any]]:
        """
        Chunk text by clause boundaries with token limits.
        
        Args:
            text: Full contract text
            contract_id: Identifier for the contract
            
        Returns:
            List of chunk dictionaries with:
            - text: Chunk text
            - clause_type: Detected clause name or "general"
            - chunk_index: Index within contract
            - start_char: Character start position
            - end_char: Character end position
        """
        logger.info(f"Chunking contract {contract_id} (text length: {len(text)} chars)")
        
        # Step 1: Split by clause headings
        clause_sections = self._split_by_clauses(text)
        
        # Step 2: Further chunk large sections if needed
        all_chunks = []
        chunk_index = 0
        
        for section_text, clause_type in clause_sections:
            # If section is small enough, use as-is
            if self._count_tokens(section_text) <= self.max_chunk_size:
                all_chunks.append({
                    "text": section_text,
                    "clause_type": clause_type,
                    "chunk_index": chunk_index,
                    "contract_id": contract_id,
                })
                chunk_index += 1
            else:
                # Split large section with overlap
                sub_chunks = self._split_with_overlap(section_text, clause_type, chunk_index, contract_id)
                all_chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks from contract {contract_id}")
        return all_chunks
    
    def _split_by_clauses(self, text: str) -> List[tuple[str, str]]:
        """
        Split text by detected clause headings.
        
        Returns:
            List of (section_text, clause_type) tuples
        """
        lines = text.split("\n")
        sections = []
        current_section = []
        current_clause = "general"
        
        for i, line in enumerate(lines):
            # Check if line matches a clause heading
            matched_clause = self._detect_clause_heading(line)
            
            if matched_clause:
                # Save previous section
                if current_section:
                    sections.append(("\n".join(current_section), current_clause))
                
                # Start new section
                current_section = [line]  # Include heading in section
                current_clause = matched_clause
            else:
                current_section.append(line)
        
        # Add final section
        if current_section:
            sections.append(("\n".join(current_section), current_clause))
        
        # If no clauses detected, return entire text as one section
        if not sections:
            sections = [(text, "general")]
        
        return sections
    
    def _detect_clause_heading(self, line: str) -> Optional[str]:
        """
        Detect if a line is a clause heading.
        
        Args:
            line: Text line to check
            
        Returns:
            Clause name if detected, None otherwise
        """
        line_upper = line.strip().upper()
        
        for pattern in self.CLAUSE_HEADINGS:
            if re.match(pattern, line_upper, re.IGNORECASE):
                # Extract clause name (normalize)
                clause_name = re.sub(r'\s+', '_', line_upper.strip())
                return clause_name.lower()
        
        return None
    
    def _split_with_overlap(
        self,
        text: str,
        clause_type: str,
        start_index: int,
        contract_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Split large text section into chunks with overlap.
        
        Uses sentence boundaries when possible to avoid breaking mid-sentence.
        
        Args:
            text: Text to split
            clause_type: Type of clause
            start_index: Starting chunk index
            contract_id: Contract identifier
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        # Split by sentences first (better than arbitrary character splits)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_tokens = 0
        chunk_index = start_index
        
        for sentence in sentences:
            sentence_tokens = self._count_tokens(sentence)
            
            # If adding this sentence exceeds limit, save current chunk
            if current_tokens + sentence_tokens > self.max_chunk_size and current_chunk:
                chunk_text = " ".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "clause_type": clause_type,
                    "chunk_index": chunk_index,
                    "contract_id": contract_id,
                })
                chunk_index += 1
                
                # Start new chunk with overlap (last N sentences)
                overlap_sentences = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sentences + [sentence]
                current_tokens = sum(self._count_tokens(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "clause_type": clause_type,
                "chunk_index": chunk_index,
                "contract_id": contract_id,
            })
        
        return chunks
    
    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """
        Get last N sentences for overlap, based on token count.
        
        Args:
            sentences: List of sentences
            
        Returns:
            Last sentences that fit within overlap token limit
        """
        if not sentences:
            return []
        
        overlap_sentences = []
        overlap_tokens = 0
        
        # Take sentences from end until we hit overlap limit
        for sentence in reversed(sentences):
            sentence_tokens = self._count_tokens(sentence)
            if overlap_tokens + sentence_tokens <= self.chunk_overlap:
                overlap_sentences.insert(0, sentence)
                overlap_tokens += sentence_tokens
            else:
                break
        
        return overlap_sentences
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text.
        
        Args:
            text: Text to count
            
        Returns:
            Number of tokens
        """
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            # Fallback: approximate 1 token = 4 characters
            return len(text) // 4

