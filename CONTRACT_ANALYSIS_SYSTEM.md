# Complete Contract Analysis System

## Overview

This is a **production-ready, end-to-end contract analysis system** that:
1. **Ingests contracts** into a knowledge base (RAG system)
2. **Analyzes user-uploaded contracts** by comparing them against the knowledge base
3. **Generates insights** using AI and statistical analysis
4. **Stores results** in a database for user history

## System Architecture

```
┌─────────────────┐
│  User Uploads   │
│   Contract      │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  1. Parse PDF/DOCX                  │
│  2. Extract Text                    │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  3. LLM Metadata Extraction         │
│     - Contract type                 │
│     - Industry, role, location      │
│     - Salary, notice period         │
│     - Clauses (non-compete, etc.)   │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  4. RAG Retrieval                  │
│     - Query ChromaDB                │
│     - Find similar contracts         │
│     - Filter by metadata            │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  5. Statistical Analysis            │
│     - Compute percentiles           │
│     - Market statistics             │
│     - Frequency analysis            │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  6. Insight Generation              │
│     - Red flags                      │
│     - Favorable terms                │
│     - Negotiation scripts            │
│     - Fairness score                 │
└────────┬────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  7. Store in Database               │
│     - User analysis history          │
│     - Results for profile page      │
└─────────────────────────────────────┘
```

## API Endpoints

### Contract Analysis

**POST `/api/contracts/analyze`**
- **Purpose**: Analyze a user-uploaded contract
- **Auth**: Required (JWT token)
- **Input**: Multipart form data with `file` (PDF/DOCX)
- **Output**: Complete analysis result

**Response:**
```json
{
  "success": true,
  "analysis_id": "uuid",
  "fairness_score": 72,
  "contract_metadata": {
    "contract_type": "employment",
    "industry": "technology",
    "role": "Software Engineer",
    "location": "Bangalore, India",
    "salary": 1500000,
    "notice_period_days": 90,
    "non_compete": true
  },
  "percentile_rankings": {
    "salary": 65.0,
    "notice_period": 85.0
  },
  "red_flags": ["..."],
  "favorable_terms": ["..."],
  "negotiation_priorities": ["..."],
  "negotiation_scripts": [
    {
      "clause": "Notice Period",
      "script": "...",
      "success_probability": 0.7
    }
  ],
  "similar_contracts_count": 20,
  "market_statistics": {...}
}
```

### Knowledge Base Ingestion

**POST `/api/contracts/ingest`**
- **Purpose**: Add contracts to the knowledge base (for building the RAG database)
- **Auth**: Required (JWT token)
- **Input**: Multipart form data with `file` (PDF/DOCX)
- **Output**: Ingestion result

**Response:**
```json
{
  "success": true,
  "contract_id": "contract_123",
  "metadata": {...},
  "num_chunks": 15,
  "status": "success"
}
```

### Knowledge Base Stats

**GET `/api/contracts/stats`**
- **Purpose**: Get statistics about the knowledge base
- **Auth**: Required (JWT token)
- **Output**: Collection statistics

## Setting Up the Knowledge Base

### Step 1: Prepare Contract Files

Place contract PDFs/DOCX files in `data/raw_contracts/` directory:
```
data/
└── raw_contracts/
    ├── contract1.pdf
    ├── contract2.docx
    └── ...
```

### Step 2: Ingest Contracts

**Option A: Using API (Recommended)**
```bash
# Use the /api/contracts/ingest endpoint
# Upload contracts via the frontend or API client
```

**Option B: Using Python Script**
```python
from pathlib import Path
from app.services.ingestion_service import IngestionService

ingestion_service = IngestionService()
results = ingestion_service.ingest_directory(Path("./data/raw_contracts"))
print(f"Ingested {len(results)} contracts")
```

### Step 3: Verify Knowledge Base

Check ChromaDB collection:
```python
from app.db.chroma_client import ChromaClient

client = ChromaClient()
stats = client.get_collection_stats()
print(f"Total chunks: {stats['total_chunks']}")
```

## How Analysis Works

### 1. File Parsing
- **PDF**: Uses `pdfplumber` for text extraction
- **DOCX**: Uses `python-docx` for text extraction
- Handles headers/footers and preserves structure

### 2. Metadata Extraction (LLM)
- Uses **Gemini Flash** to extract structured data
- Validates output with Pydantic schemas
- Extracts: contract type, industry, role, salary, notice period, clauses

### 3. RAG Retrieval
- Generates embeddings for the contract
- Queries ChromaDB for similar contracts
- Filters by: contract_type, industry, role, location
- Returns top 20 most similar contracts

### 4. Statistical Analysis
- Computes **percentiles** for numeric fields (salary, notice period)
- Compares against similar contracts in the database
- Calculates market statistics (mean, median, IQR)

### 5. Insight Generation (LLM)
- Analyzes contract against market data
- Identifies red flags and favorable terms
- Generates negotiation priorities
- Creates professional negotiation scripts

### 6. Fairness Score
- Computed from:
  - Salary percentile (higher = better)
  - Notice period percentile (lower = better)
  - Red flags count (fewer = better)
  - Favorable terms count (more = better)
  - Non-compete clause presence (absence = better)

## Data Flow

### Knowledge Base (RAG)
```
Raw Contracts → Parse → Extract Metadata → Chunk → Embed → Store in ChromaDB
```

### User Analysis
```
User Upload → Parse → Extract Metadata → RAG Query → Statistics → Insights → Store in DB
```

## Database Schema

### Users Table
- `id`: UUID
- `email`: Unique email
- `hashed_password`: Bcrypt hash
- `name`: Full name
- `created_at`: Timestamp
- `is_active`: Boolean

### ContractAnalysis Table
- `id`: UUID
- `user_id`: Foreign key to users
- `contract_filename`: Original filename
- `fairness_score`: 0-100
- `contract_type`, `industry`, `role`, `location`: Metadata
- `salary`, `notice_period_days`: Numeric fields
- `created_at`: Timestamp

## Environment Variables

Required in `.env`:
```env
# Google AI
GOOGLE_API_KEY=your_key_here

# Database
DATABASE_URL=sqlite:///./chroma_db/fairdeal.db
# Or for PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/fairdeal

# JWT
JWT_SECRET_KEY=your-secret-key-min-32-chars

# ChromaDB
CHROMA_DB_PATH=./chroma_db
CHROMA_COLLECTION_NAME=contracts

# Data Paths
RAW_CONTRACTS_PATH=./data/raw_contracts
PROCESSED_CONTRACTS_PATH=./data/processed
```

## Usage Example

### Frontend (React)
```typescript
import { contractAPI } from './services/api'

const file = // File from input
const result = await contractAPI.analyze(file)
console.log('Fairness Score:', result.fairness_score)
console.log('Red Flags:', result.red_flags)
```

### Backend (Python)
```python
from app.services.analysis_service import AnalysisService

service = AnalysisService()
with open('contract.pdf', 'rb') as f:
    result = service.analyze_contract(
        file_content=f.read(),
        filename='contract.pdf'
    )
print(f"Fairness Score: {result['fairness_score']}")
```

## Important Notes

1. **Knowledge Base Required**: The system needs contracts in the knowledge base to compare against. Without ingested contracts, percentiles will default to 50%.

2. **LLM Dependency**: Requires Google API key for Gemini Flash. Analysis will fail without it.

3. **File Size Limit**: Maximum 10MB per file.

4. **Supported Formats**: PDF, DOCX, DOC

5. **Authentication**: All analysis endpoints require JWT authentication.

## Troubleshooting

### "No similar contracts found"
- **Solution**: Ingest contracts into the knowledge base first using `/api/contracts/ingest`

### "LLM API error"
- **Solution**: Check `GOOGLE_API_KEY` in `.env` file

### "Percentile always 50%"
- **Solution**: Need more contracts in the knowledge base for accurate percentiles

### "Empty analysis result"
- **Solution**: Check that the contract file is valid and contains text

## Production Deployment

1. **Use PostgreSQL** instead of SQLite
2. **Set strong JWT_SECRET_KEY** (min 32 characters)
3. **Configure CORS** for your frontend domain
4. **Set up proper logging** (already using loguru)
5. **Add rate limiting** for API endpoints
6. **Use environment variables** for all secrets
7. **Backup ChromaDB** regularly (it's on disk)

