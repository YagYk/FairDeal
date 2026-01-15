# FairDeal - Deterministic Contract Analysis System

A deterministic, auditable, fast contract benchmarking system. Analyzes employment contracts and provides fair market comparison with traceable scoring.

## Features

- **Deterministic Scoring**: No LLM for scores - uses exact mathematical formula
- **Auditable Results**: Every output traceable to source text snippets
- **Fast Analysis**: Target ≤3s for deterministic path
- **RAG for Evidence**: Similar contracts for provenance, not scoring
- **Knowledge Base**: Ingest and compare against 75-100+ contracts

## Quick Start

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt

# Create .env file with:
# GOOGLE_API_KEY=your_key
# DATABASE_URL=sqlite:///./chroma_db/fairdeal.db

# Ingest contracts
python -m app.ingest_cli --input ../data/raw_contracts

# Start server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### V2 Analysis (Deterministic)
```
POST /api/v2/analyze - Analyze a contract
GET /api/v2/scoring-info - Get scoring formula docs
```

### Knowledge Base Admin
```
GET /api/kb/contracts - List ingested contracts
GET /api/kb/stats - Cohort counts and statistics
GET /api/kb/health - System health check
```

## Scoring Formula

```
S = 50 + 0.4*(P_salary - 50) + 0.3*(50 - P_notice) - 0.3*(N_flags*5) + bonuses - penalties
```

See `backend/README.md` for full documentation.

## Project Structure

```
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── services/ # Business logic
│   │   ├── models/   # Pydantic schemas
│   │   ├── eval/     # Evaluation tools
│   │   └── tests/    # Unit tests
│   └── gold/         # Gold annotations
├── frontend/         # React frontend
├── data/
│   ├── raw_contracts/    # Input contracts
│   └── processed/        # Processed metadata
└── chroma_db/        # Vector database
```

## Requirements

- Python 3.10+
- Node.js 18+
- Google Gemini API key (for embeddings only)
- Optional: Tesseract OCR, Poppler (for scanned PDFs)
