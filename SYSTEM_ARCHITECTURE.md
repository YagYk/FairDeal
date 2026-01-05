# System Architecture & Performance

## 🚀 How the System Works (Performance Optimized)

### Storage & Caching Strategy

The system uses **persistent disk storage**, not memory cache. Here's how it works:

```
┌─────────────────────────────────────────────────────────┐
│                    INGESTION (One-Time)                 │
├─────────────────────────────────────────────────────────┤
│ 1. Parse PDF/DOCX → Extract Text                       │
│ 2. Extract Metadata (LLM call - ~2-5 seconds)          │
│ 3. Chunk Text → Create semantic chunks                  │
│ 4. Generate Embeddings (API call - ~1-3 seconds)       │
│ 5. Store in ChromaDB (PERSISTENT DISK STORAGE)         │
│    └─> Location: ./chroma_db/                          │
│    └─> Format: Vector embeddings + metadata            │
│    └─> Persistence: Survives server restarts           │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              ANALYSIS (Fast - Uses Cached Data)        │
├─────────────────────────────────────────────────────────┤
│ 1. Parse User Contract → Extract Text                  │
│ 2. Extract Metadata (LLM call - ~2-5 seconds)          │
│ 3. Generate Query Embedding (API call - ~0.5 seconds)  │
│ 4. Query ChromaDB (FAST - reads from disk)              │
│    └─> No re-embedding of knowledge base contracts!    │
│    └─> Direct vector similarity search                 │
│    └─> Returns top 20 similar contracts instantly     │
│ 5. Compute Statistics (reads from disk metadata)      │
│ 6. Generate Insights (LLM call - ~3-7 seconds)         │
│                                                         │
│ TOTAL TIME: ~10-20 seconds per analysis               │
└─────────────────────────────────────────────────────────┘
```

## 💾 Storage Locations

### 1. ChromaDB (Vector Database)
- **Location**: `./chroma_db/`
- **Contains**: 
  - Vector embeddings (768-dimensional vectors)
  - Contract chunks (text)
  - Metadata (contract_type, industry, role, etc.)
- **Persistence**: ✅ Permanent disk storage
- **Performance**: Fast similarity search (milliseconds)

### 2. Processed Metadata
- **Location**: `data/processed/`
- **Contains**: JSON files with contract metadata
- **Used for**: Statistics computation (percentiles)
- **Format**: `{contract_id}_metadata.json`

### 3. SQLite/PostgreSQL Database
- **Location**: `./chroma_db/fairdeal.db` (SQLite) or PostgreSQL
- **Contains**: 
  - User accounts
  - Analysis history
  - User-specific data
- **Persistence**: ✅ Permanent

## ⚡ Performance Characteristics

### First-Time Ingestion
- **Time per contract**: ~10-30 seconds
  - Text extraction: ~1-2 seconds
  - LLM metadata extraction: ~2-5 seconds
  - Embedding generation: ~1-3 seconds per chunk
  - Storage: ~0.5 seconds
- **One-time cost**: Contracts are processed once and stored forever

### Analysis (User Upload)
- **Time**: ~10-20 seconds total
  - Text extraction: ~1-2 seconds
  - LLM metadata extraction: ~2-5 seconds
  - Query embedding: ~0.5 seconds
  - **ChromaDB query: ~0.1-0.5 seconds** ⚡ (FAST - uses cached embeddings)
  - Statistics computation: ~0.5-1 second
  - LLM insight generation: ~3-7 seconds
- **No re-processing**: Knowledge base contracts are never re-embedded

### Why It's Fast

1. **Embeddings are pre-computed**: 
   - Contracts in knowledge base are embedded once during ingestion
   - Embeddings stored permanently in ChromaDB
   - No need to re-embed on every query

2. **Vector similarity search is optimized**:
   - ChromaDB uses efficient indexing (HNSW algorithm)
   - Searches are sub-second even with thousands of contracts

3. **Metadata is cached**:
   - Statistics computed from pre-processed JSON files
   - No need to re-parse contracts for statistics

## 📊 Scalability

### Current Setup
- **Knowledge Base**: Unlimited contracts (disk space dependent)
- **Concurrent Users**: Limited by LLM API rate limits
- **Query Speed**: O(log n) - logarithmic with number of contracts

### Production Optimizations
1. **Batch Processing**: Ingest contracts in batches
2. **Caching**: Add Redis for frequently accessed statistics
3. **CDN**: Serve static metadata files via CDN
4. **Load Balancing**: Multiple backend instances
5. **Database**: Use PostgreSQL for better concurrency

## 🔄 Data Flow

### Ingestion Flow
```
Contract File
    ↓
Parse (PDF/DOCX) → Text
    ↓
LLM Extract Metadata → Structured Data
    ↓
Chunk Text → Semantic Chunks
    ↓
Generate Embeddings → Vector Arrays
    ↓
Store in ChromaDB → PERSISTENT STORAGE
    ↓
Save Metadata JSON → Disk
```

### Analysis Flow
```
User Uploads Contract
    ↓
Parse → Text
    ↓
LLM Extract Metadata
    ↓
Generate Query Embedding
    ↓
Query ChromaDB → RETRIEVE CACHED EMBEDDINGS ⚡
    ↓
Compute Statistics (from cached metadata)
    ↓
LLM Generate Insights
    ↓
Store Result in Database
```

## 🖼️ Image Support

### Current Capabilities

**PDF Files:**
- ✅ Text-based PDFs: Full support
- ✅ Image-based PDFs: OCR support (requires Tesseract)
- ⚠️ Scanned PDFs: Requires OCR setup

**DOCX Files:**
- ✅ Text extraction: Full support
- ✅ Tables: Extracted as text
- ⚠️ Images in DOCX: Not currently extracted (text only)

### OCR Setup (For Image PDFs)

1. **Install Tesseract OCR**:
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - Mac: `brew install tesseract`
   - Linux: `sudo apt-get install tesseract-ocr`

2. **Install Python packages** (already in requirements.txt):
   ```bash
   pip install pytesseract Pillow
   ```

3. **The system will automatically**:
   - Detect when a PDF page has no text
   - Attempt OCR extraction
   - Fall back gracefully if OCR fails

### Limitations

- **Complex layouts**: May not preserve exact formatting
- **Handwritten text**: OCR accuracy varies
- **Multi-language**: Currently supports English only
- **Large images**: May take longer to process

## 🎯 Best Practices

1. **Ingest contracts once**: Don't re-ingest the same contracts
2. **Use descriptive filenames**: They become contract IDs
3. **Batch ingestion**: Process multiple contracts together
4. **Monitor disk space**: ChromaDB grows with more contracts
5. **Backup ChromaDB**: Important for production

## 📈 Performance Metrics

### Typical Timings (Production)

| Operation | Time | Notes |
|-----------|------|-------|
| Ingestion (per contract) | 10-30s | One-time cost |
| Analysis (user upload) | 10-20s | Uses cached data |
| ChromaDB query | 0.1-0.5s | Very fast |
| LLM metadata extraction | 2-5s | API dependent |
| LLM insight generation | 3-7s | API dependent |
| Statistics computation | 0.5-1s | From cached metadata |

### Optimization Tips

1. **Pre-ingest contracts**: Build knowledge base before going live
2. **Use async processing**: For better concurrency
3. **Cache LLM responses**: For similar contracts (future enhancement)
4. **Batch API calls**: Group embedding requests (future enhancement)

