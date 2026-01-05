# Design Decisions & Architecture

## 🎯 Core Design Philosophy

This RAG system is built with **research extensibility** and **production readiness** in mind. Every design choice prioritizes:
1. **Modularity**: Easy to swap components
2. **Explainability**: Clear why each decision was made
3. **Type Safety**: Pydantic schemas and type hints throughout
4. **Observability**: Comprehensive logging

## 📐 Architecture Decisions

### 1. Clause-Aware Chunking

**Why?** Legal contracts have explicit structure. Splitting by clause boundaries (TERMINATION, NOTICE PERIOD, etc.) preserves semantic meaning better than arbitrary text splits.

**Implementation:**
- Detects 20+ common clause headings via regex
- Splits text at clause boundaries
- Further splits large clauses with overlap (100 tokens)
- Preserves clause context in metadata

**Trade-offs:**
- ✅ Better semantic coherence
- ✅ Easier to filter by clause type
- ⚠️ May miss non-standard clause names (extensible via CLAUSE_HEADINGS list)

### 2. ChromaDB for Vector Storage

**Why?** 
- Persistent storage (no re-embedding on restart)
- Built-in metadata filtering
- Easy to use and maintain
- Good performance for RAG workloads

**Alternative considered:** Pinecone (cloud-based, but requires subscription)

**Implementation:**
- One collection per project
- Metadata attached to each chunk (contract_type, industry, clause_type, etc.)
- Enables filtering during retrieval

### 3. Gemini Flash LLM

**Why Gemini Flash?**
- Fast and cost-effective for structured extraction
- High-quality outputs for legal document analysis
- Excellent performance-to-cost ratio
- Google's latest generation model optimized for speed

**Implementation:**
- Single `LLMService` class using Gemini Flash
- JSON extraction via prompt engineering (Gemini doesn't have native JSON mode)
- Easy to extend to other Gemini models (Pro, Ultra) if needed

### 4. Separate Services Architecture

**Services:**
- `IngestionService`: Orchestrates full pipeline
- `RAGService`: Handles retrieval logic
- `LLMService`: LLM interactions
- `EmbeddingService`: Vector generation
- `ChromaClient`: Database operations

**Why?** 
- Single Responsibility Principle
- Easy to test in isolation
- Easy to extend (e.g., add caching layer)

### 5. Metadata Extraction Strategy

**Why use LLM for metadata?**
- Contracts are unstructured
- Need to extract structured fields (salary, notice period, etc.)
- Rule-based extraction would be brittle

**Schema Design:**
- Pydantic models for validation
- Type-safe extraction
- Easy to extend with new fields

**Trade-offs:**
- ✅ Handles varied contract formats
- ⚠️ Requires API calls (cost/speed)
- ⚠️ May have extraction errors (mitigated by validation)

### 6. Token-Based Chunking Limits

**Why 800 tokens max?**
- Fits comfortably in LLM context windows
- Leaves room for query + retrieved chunks
- Balances granularity vs. context

**Why 100 token overlap?**
- Prevents losing context at boundaries
- Ensures clause transitions are captured
- Standard practice in RAG systems

### 7. Embedding Strategy

**Why Google text-embedding-004?**
- High quality semantic representations
- State-of-the-art performance
- Excellent for legal domain
- Cost-effective and fast

**Batch Processing:**
- Processes texts individually (Google API limitation)
- Batched for logging and progress tracking
- Efficient error handling per text

## 🔄 Data Flow

```
Contract File (PDF/DOCX)
    ↓
[PDFParser/DOCXParser]
    ↓ Raw Text
[LLMService.extract_metadata()]
    ↓ Structured Metadata (Pydantic)
[ClauseAwareChunker.chunk_text()]
    ↓ List of Chunks (with clause_type)
[EmbeddingService.generate_embeddings()]
    ↓ Vector Embeddings (numpy array)
[ChromaClient.add_chunks()]
    ↓ Stored in ChromaDB
```

**Retrieval Flow:**
```
Query Text
    ↓
[EmbeddingService.generate_embedding()]
    ↓ Query Embedding
[ChromaClient.query()]
    ↓ Similar Chunks (with metadata)
[RAGService.format_results()]
    ↓ Ranked Results
```

## 🎓 Research Extensibility

### Areas for Future Research

1. **Chunking Strategies**
   - TODO: Experiment with semantic chunking (sentence embeddings)
   - TODO: Try different overlap strategies
   - TODO: Evaluate chunk quality metrics

2. **Embedding Models**
   - TODO: Compare Google embeddings vs. open-source models (sentence-transformers)
   - TODO: Fine-tune embeddings on legal corpus
   - TODO: Domain-specific embeddings
   - TODO: Test batch embedding API if available

3. **Retrieval Strategies**
   - TODO: Hybrid search (keyword + semantic)
   - TODO: Re-ranking with cross-encoders
   - TODO: Multi-vector retrieval

4. **Metadata Extraction**
   - TODO: Few-shot learning for better extraction
   - TODO: Multi-stage extraction (coarse → fine)
   - TODO: Validation rules for common errors

5. **Evaluation Metrics**
   - TODO: Precision@K, Recall@K
   - TODO: Human evaluation framework
   - TODO: A/B testing infrastructure

## 🔧 Extension Points

### Adding a New Parser

1. Create class in `backend/app/parsers/`
2. Implement `extract_text()` and `extract_metadata()` methods
3. Add to `IngestionService._parse_document()`

### Adding a New LLM Provider

1. Add provider check in `LLMService.__init__()`
2. Implement `_call_llm()` method for new provider
3. Update `settings.llm_provider` enum

### Adding New Clause Patterns

1. Add regex pattern to `ClauseAwareChunker.CLAUSE_HEADINGS`
2. Update clause name normalization if needed

### Custom Chunking Strategy

1. Create new chunker class in `backend/app/utils/`
2. Implement `chunk_text()` method
3. Use in `IngestionService` instead of `ClauseAwareChunker`

## 📊 Performance Considerations

### Ingestion
- **Bottleneck**: LLM metadata extraction (sequential)
- **Optimization**: Could parallelize across contracts
- **Cost**: ~$0.01-0.05 per contract (depending on size)

### Retrieval
- **Speed**: <100ms for 20 results (local ChromaDB)
- **Scalability**: ChromaDB handles millions of vectors
- **Cost**: Embedding generation only (~$0.0001 per query)

### Storage
- **ChromaDB**: ~1-5MB per 1000 chunks (depends on text length)
- **Metadata JSON**: ~1-5KB per contract

## 🛡️ Error Handling

### Graceful Degradation
- Falls back to character-based chunking if tiktoken fails
- Validates LLM output with Pydantic (raises clear errors)
- Continues ingestion even if one contract fails

### Logging
- Comprehensive logging at DEBUG/INFO/ERROR levels
- Logs to both console and file (`rag_test.log`)
- Includes timing and error details

## 🔐 Security & Privacy

### Current State
- API keys stored in `.env` (not committed)
- Contracts stored locally
- No data sent to third parties except LLM providers

### Future Considerations
- TODO: Add encryption for stored contracts
- TODO: Support for PII redaction
- TODO: Audit logging for compliance

## 📈 Scalability

### Current Limits
- Tested with 100+ contracts
- ChromaDB handles millions of vectors
- API rate limits are the main constraint

### Scaling Strategies
1. **Horizontal**: Run multiple ingestion workers
2. **Caching**: Cache embeddings for repeated contracts
3. **Batch Processing**: Process contracts in batches
4. **Distributed**: Use distributed ChromaDB (future)

