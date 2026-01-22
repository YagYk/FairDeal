## FairDeal (FastAPI + React + Tailwind)

### What you get
- **Backend**: FastAPI with deterministic extraction/scoring/benchmarking + Chroma RAG for clause evidence + KB admin endpoints.
- **Frontend**: React + TypeScript + Tailwind dashboard + KB explorer.

### Prereqs
- Python 3.11+
- Node 18+

### Put your assets in place (required)
- Copy your market data to: `backend/data/market_data.json`
- Copy your contracts to: `backend/data/contracts_raw/` (PDF/DOCX)

### Backend: install + run
From repo root:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Backend API is at `http://127.0.0.1:8000`.

### Windows note (Chroma)
Chroma depends on `chroma-hnswlib`. On **Windows + Python 3.12**, pip may require **Microsoft C++ Build Tools** to compile it.
- If install fails with “Microsoft Visual C++ 14.0 or greater is required”, install “Microsoft C++ Build Tools”, then re-run `pip install -r requirements.txt`.
- If you want a no-build-tool path, use **Python 3.11** for the backend venv.

Install RAG dependencies (Chroma) separately:

```bash
pip install -r requirements-rag.txt
```

### Ingest the contract knowledge base (required for RAG)
From repo root:

```bash
.\.venv\Scripts\activate
python -m backend.app.services.ingestion_service --input backend/data/contracts_raw
```

### Frontend: install + run
From repo root:

```bash
cd frontend
npm install
npm run dev
```

Frontend is at `http://127.0.0.1:5173`.

### Key endpoints
- **Analyze**: `POST /api/analyze` (multipart: `file`, `context` JSON string)
- **KB**:
  - `GET /api/kb/health`
  - `GET /api/kb/stats`
  - `GET /api/kb/contracts?limit=&offset=`
  - `GET /api/kb/contracts/{id}`
  - `GET /api/kb/contracts/{id}/chunks`
  - `GET /api/kb/search?query=&clause_type=&top_k=`

