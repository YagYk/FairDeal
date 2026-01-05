# FairDeal - AI-Powered Contract Analysis Platform

A production-grade contract analysis system that evaluates employment contracts against a knowledge base to provide fairness assessments, percentile rankings, and negotiation guidance. Built with RAG (Retrieval-Augmented Generation) technology, specifically designed for Indian employment and service contracts.

## 🎯 Overview

This system enables:
- **Ingestion**: Parse PDF/DOCX contracts, extract metadata, chunk semantically, and store in ChromaDB
- **Retrieval**: Query similar contracts using semantic search with metadata filtering
- **Analysis**: Compare contracts against a knowledge base for fairness assessment

## 🏗️ Architecture

```
[ PDFs / DOCX ]
       ↓
[ Ingestion Service ]
  ├── Parse (PDF/DOCX)
  ├── Extract Metadata (LLM)
  ├── Chunk (Clause-aware)
  ├── Embed (Gemini)
  └── Store (ChromaDB)
       ↓
[ ChromaDB Vector Store ]
       ↓
[ RAG Service ]
  ├── Query Embedding
  ├── Similarity Search
  └── Metadata Filtering
       ↓
[ Retrieved Chunks ]
```

## 📁 Project Structure

```
backend/
├── app/
│   ├── config.py              # Configuration management
│   ├── api/                   # FastAPI endpoints (future)
│   ├── services/
│   │   ├── ingestion_service.py    # Orchestrates ingestion pipeline
│   │   ├── rag_service.py          # RAG retrieval logic
│   │   ├── llm_service.py          # LLM service (Gemini Flash)
│   │   └── embedding_service.py    # Embedding generation
│   ├── parsers/
│   │   ├── pdf_parser.py           # PDF text extraction
│   │   └── docx_parser.py          # DOCX text extraction
│   ├── utils/
│   │   └── chunking.py             # Clause-aware chunking
│   ├── models/
│   │   └── contract_schema.py      # Pydantic schemas
│   └── db/
│       └── chroma_client.py        # ChromaDB client
test_rag_pipeline.py                 # End-to-end test script
requirements.txt
.env.example
```

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```env
GOOGLE_API_KEY=your_google_api_key_here
LLM_PROVIDER=gemini
EMBEDDING_PROVIDER=gemini
```

### 3. Prepare Data

Create the data directory and add your contracts:

```bash
mkdir -p data/raw_contracts
# Add PDF or DOCX files to data/raw_contracts/
```

### 4. Run Test Script

```bash
python test_rag_pipeline.py
```

This will:
1. Ingest all contracts from `data/raw_contracts/`
2. Test retrieval with sample queries
3. Print results with similarity scores

## 🔧 Key Components

### Ingestion Service

Orchestrates the complete pipeline:
- Parses PDF/DOCX files
- Extracts structured metadata using LLM
- Chunks text by clause boundaries
- Generates embeddings
- Stores in ChromaDB

### RAG Service

Handles similarity retrieval:
- Generates query embeddings
- Searches ChromaDB with metadata filters
- Returns ranked results with similarity scores

### Chunking Strategy

**Clause-aware chunking**:
- Detects legal clause headings (TERMINATION, NOTICE PERIOD, etc.)
- Splits by clause boundaries
- Respects token limits (800 tokens max, 100 overlap)
- Preserves clause context

### Metadata Extraction

Uses LLM to extract:
- `contract_type`: employment, consulting, etc.
- `industry`: technology, finance, etc.
- `role`: Job position
- `location`: Geographic location
- `salary`: Compensation amount
- `notice_period_days`: Notice period
- `non_compete`: Boolean flag
- `risky_clauses`: List of concerning clauses

## 📊 Usage Example

```python
from app.services.ingestion_service import IngestionService
from app.services.rag_service import RAGService
from pathlib import Path

# Ingest contracts
ingestion = IngestionService()
results = ingestion.ingest_directory(Path("data/raw_contracts/"))

# Query similar contracts
rag = RAGService()
results = rag.retrieve_similar_contracts(
    query_text="90 day notice period employment contract",
    n_results=20,
    filters={"contract_type": "employment", "location": "India"}
)

for result in results:
    print(f"Similarity: {result['similarity_score']:.4f}")
    print(f"Text: {result['text'][:200]}...")
```

## 🎓 Design Decisions

### Why Clause-Aware Chunking?
Legal contracts have clear structure. Splitting by clause boundaries preserves semantic meaning better than arbitrary text splits.

### Why ChromaDB?
- Persistent storage (no need to re-embed on restart)
- Metadata filtering (filter by contract_type, industry, etc.)
- Easy to use and maintain
- Good performance for RAG workloads

### Why Gemini Flash?
- Fast and cost-effective for structured extraction
- High-quality embeddings with Google's text-embedding-004
- Excellent performance for legal document analysis
- Easy to extend to other Gemini models if needed

### Why Separate Services?
- **Modularity**: Each service has a single responsibility
- **Testability**: Easy to test components in isolation
- **Extensibility**: Easy to add new features or swap implementations

## 🔬 Research Features

The codebase is designed for research:
- **Transparency**: All metadata stored in JSON files
- **Explainability**: Similarity scores and metadata for each result
- **Logging**: Comprehensive logging for evaluation
- **TODO comments**: Marked areas for future research

## 📝 Next Steps

1. **Statistics Engine**: Precompute percentiles for salary, notice period, etc.
2. **Comparison Engine**: Compare user contracts against dataset
3. **Insight Generation**: LLM-generated fairness scores and negotiation scripts
4. **Frontend**: React + TypeScript dashboard
5. **FastAPI Endpoints**: REST API for frontend integration

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not set"
Make sure your `.env` file exists and contains a valid Google API key. Get one from https://makersuite.google.com/app/apikey

### "No PDF or DOCX files found"
Add contract files to `data/raw_contracts/` directory.

### ChromaDB errors
Delete `chroma_db/` directory and re-run ingestion to start fresh.

## 📄 License

Designed for research and open-source release.
