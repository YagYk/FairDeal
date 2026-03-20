<div align="center">

# ⚖️ FAIRDEAL

### AI-Powered Employment Contract Intelligence Engine

**Drop a contract. Get the truth.**

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Tailwind](https://img.shields.io/badge/Tailwind-3.4-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.6-FF6F00?style=for-the-badge)](https://www.trychroma.com)

---

*FairDeal dissects Indian employment contracts through an **8-stage analysis pipeline** — hybrid regex+LLM extraction, psychological scoring, market benchmarking against real salary data, RAG-powered clause evidence retrieval, red flag detection, and auto-generated negotiation playbooks — all in under 5 seconds.*

</div>

---

## The Problem

Every year, millions of fresh graduates in India sign employment contracts they don't fully understand. Buried in legalese are training bonds worth ₹2,00,000+, 90-day notice periods, aggressive non-competes, and missing statutory benefits — all designed to lock employees in.

**FairDeal fights back.** Upload your offer letter, and the engine tells you exactly where you stand — backed by market data, legal analysis, and precedent from real contracts.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        React + Tailwind UI                       │
│   Upload → Context Form → Score Gauges → Heatmaps → Playbook    │
└────────────────────────────┬─────────────────────────────────────┘
                             │ REST API
┌────────────────────────────▼─────────────────────────────────────┐
│                      FastAPI Backend                              │
│                                                                   │
│  ┌─────────┐  ┌──────────┐  ┌───────────┐  ┌────────────────┐   │
│  │ Stage 1  │→ │ Stage 2   │→ │ Stage 3    │→ │ Stage 4         │  │
│  │ Parse    │  │ Extract   │  │ Benchmark  │  │ Red Flags       │  │
│  │ + OCR    │  │ Regex+LLM │  │ Percentile │  │ + Favorable     │  │
│  └─────────┘  └──────────┘  └───────────┘  └────────────────┘   │
│                                                                   │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Stage 5       │→ │ Stage 6      │→ │ Stage 7   │→ │ Stage 8   │ │
│  │ Psych Scoring │  │ Negotiation  │  │ RAG       │  │ Narration │ │
│  │ Engine v3.0   │  │ Playbook     │  │ Evidence  │  │ LLM/Det.  │ │
│  └──────────────┘  └─────────────┘  └──────────┘  └──────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │              ChromaDB Vector Store (RAG KB)                 │   │
│  │     sentence-transformers/all-MiniLM-L6-v2 embeddings       │   │
│  └────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

## The 8-Stage Pipeline

### Stage 1 — Parse + OCR
Ingests PDF/DOCX contracts. If the document is a scanned image (no extractable text), automatically triggers **Gemini 2.0 Flash Vision OCR** to reconstruct the text layer. Handles Indian contract formats with multi-column salary breakdowns, letterhead noise, and regional formatting.

### Stage 2 — Hybrid Extraction (Regex → LLM Sniper)
First pass: **deterministic regex extraction** using battle-tested patterns for CTC, notice period, training bonds, non-compete clauses, probation period, and benefits.

If any critical field is missing, the **Sniper LLM** takes over — it scores every page for salary-relevance, selects only the highest-scoring pages, and sends a surgical prompt to Gemini. This avoids hallucination by never sending the full document to the LLM.

Extracted values pass through a **sanitization pipeline**: string-to-number conversion, Indian number format handling (₹18,00,000), LPA-to-INR conversion, monthly-to-annual correction, and an upper-bound sanity check.

### Stage 3 — Market Benchmarking
Computes your salary and notice period **percentile** against real market data segmented by:
- Role category (SDE, analyst, HR, marketing, operations, finance)
- City (Bangalore, Mumbai, Delhi, Pune, Hyderabad, Tier-2)
- Experience band (0-2, 2-5, 5-10 YOE)
- Company type (product, service, startup)

Uses **progressive cohort broadening** — if your exact cohort has fewer than 5 data points, filters are relaxed one-by-one (location → experience → role) until statistical significance is reached. Returns P25, P50, P75, and your exact percentile.

### Stage 4 — Red Flag & Favorable Term Detection
A **rule engine** that cross-references extracted data against market standards and Indian labor law:

| Category | What it catches |
|----------|----------------|
| Salary | Below 10th/25th percentile, above 75th (favorable) |
| Notice Period | Percentile-based flagging, >90 day critical flag |
| Non-Compete | Duration severity (3/6/12/12+ months), scope analysis |
| Training Bond | Amount tiers (₹50K/₹2L+), pro-ration check |
| Probation | >6 month flag, <3 month favorable |
| Benefits | Missing statutory (PF/gratuity), generous package detection |

Each flag includes: severity level, impact score, market context, source text, and an actionable recommendation.

### Stage 5 — Psychological Scoring Engine v3.0
Not your average weighted average. The scoring engine applies:

1. **Component Scores** — Salary, notice, benefits, clauses, and legal compliance each scored 0-100
2. **Dynamic Weights** — Weights shift based on role level (entry/mid/senior) and industry context
3. **Context Multipliers** — Pattern detection triggers multipliers:
   - 🦄 **Unicorn Contract** (top salary + short notice + great benefits + no non-compete → 1.15x)
   - ⚠️ **Golden Handcuffs** (amazing pay but locked in → 0.95x)
   - 🚀 **Startup Rocket** (equity-backed startup → 1.08x)
   - 🏢 **Standard MNC Package** (middle-of-road → 1.02x)
   - 🚨 **Toxic Contract** (3+ risk factors → 0.85x)
   - ⚠️ **Service Trap** (90-day notice + low salary + bond → 0.90x)
4. **Psychological Calibration** — Compresses top scores (truly great contracts are rare) and softens the bottom (nothing feels like a zero)
5. **Confidence Score** — Based on how much real data vs. defaults were used in computation

Grades: EXCEPTIONAL → EXCELLENT → GOOD → FAIR → AVERAGE → BELOW AVERAGE → POOR → CRITICAL

### Stage 6 — Negotiation Playbook
Generates **prioritized, context-aware negotiation points** with:
- Current term vs. target term
- Success probability assessment
- Ready-to-use email scripts
- Fallback positions
- Market evidence to back your ask

Smart enough to know that salary negotiation is pointless at TCS/Infosys/Wipro campus placements — skips it and focuses on notice period and bond negotiation instead.

### Stage 7 — RAG Evidence Retrieval
Queries a **ChromaDB vector knowledge base** of real contract clauses using `all-MiniLM-L6-v2` embeddings. For each clause type (termination, IP, non-compete, confidentiality, compensation), retrieves the most similar precedent clauses from ingested contracts.

Also performs **clause drift detection** — measures how far your contract's language deviates from "gold standard" clauses. Anomalous clauses are flagged.

### Stage 8 — AI Narration
Generates a human-readable verdict using Gemini LLM. If the API is unavailable, falls back to a **deterministic verdict generator** that assembles context-aware prose from the scoring results — no AI dependency required for the core product.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11+, FastAPI, Pydantic v2, ORJSONResponse |
| **Frontend** | React 18, TypeScript, Vite 5, Tailwind CSS 3.4 |
| **Vector DB** | ChromaDB with sentence-transformers embeddings |
| **LLM** | Google Gemini 1.5 Pro (extraction) + Gemini 2.0 Flash (OCR) |
| **PDF Parsing** | pdfplumber (native) + Gemini Vision (scanned docs) |
| **Data** | pandas + numpy for percentile computation |
| **Charts** | Recharts (bell curves, gauges, heatmaps) |
| **Animations** | Framer Motion |
| **State** | TanStack React Query + localStorage persistence |
| **Caching** | SHA-256 content-addressed file cache (context-aware keys) |

---

## Frontend

Built with React + TypeScript + Tailwind. Highlights:

- **Drag-and-drop upload** with real-time progress
- **Score gauges** with animated gradients (overall, safety, market fairness)
- **Bell curve visualization** — see exactly where your salary falls on the market distribution
- **Clause heatmap** — visual severity map of every contract clause
- **Evidence panel** — RAG-retrieved similar clauses from real contracts
- **Clause drift panel** — deviation analysis from standard contract language
- **Red flags panel** — severity-coded risk analysis with recommendations
- **Negotiation playbook** — copy-paste email scripts
- **Knowledge Base explorer** — browse ingested contracts, search by clause type
- **Responsive layout** with sidebar navigation and keyboard shortcuts

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) Google Gemini API key for LLM features

### Backend Setup

```bash
# Clone and enter project
git clone https://github.com/YagYk/FairDeal.git
cd FairDeal

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install RAG dependencies (ChromaDB)
pip install -r requirements-rag.txt

# Start the backend
uvicorn backend.app.main:app --reload
```

Backend API runs at `http://127.0.0.1:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://127.0.0.1:5173`

### Environment Variables (Optional)

Create a `.env` file in the project root:

```env
FAIRDEAL_LLM_API_KEY=your_gemini_api_key_here
```

Without an API key, FairDeal runs in **fully deterministic mode** — regex extraction, rule-based scoring, and deterministic narration. No AI dependency for the core pipeline.

### Load Market Data

Place your market data JSON files in `backend/data/market_data/`. Each file should contain salary records with fields like `ctc`, `role_category`, `yoe_band`, `location`, and `company_type`.

### Ingest Contract Knowledge Base (for RAG)

```bash
python -m backend.app.services.ingestion_service --input backend/data/contracts_raw
```

This parses contracts, chunks them by clause type, generates embeddings, and stores them in ChromaDB.

---

## API Reference

### `POST /api/analyze`
Upload a contract and get comprehensive analysis.

**Request:** `multipart/form-data`
- `file` — PDF or DOCX contract
- `context` — JSON string:
```json
{
  "role": "Software Engineer",
  "experience_level": 2.0,
  "company_type": "product",
  "location": "Bangalore",
  "industry": "tech"
}
```

**Response:** Full analysis payload including extraction, scoring, percentiles, red flags, favorable terms, negotiation points, RAG evidence, narration, and timing data.

### Knowledge Base Endpoints
| Endpoint | Description |
|----------|------------|
| `GET /api/kb/stats` | Collection statistics (contracts, chunks, clause types) |
| `GET /api/kb/contracts` | List ingested contracts (paginated) |
| `GET /api/kb/contracts/{id}` | Contract metadata |
| `GET /api/kb/contracts/{id}/chunks` | Contract chunks with clause types |
| `GET /api/kb/search?query=...` | Semantic search across the knowledge base |

---

## Project Structure

```
FairDeal/
├── backend/
│   ├── app/
│   │   ├── main.py                         # FastAPI app with global error handling
│   │   ├── config.py                       # Pydantic settings with env support
│   │   ├── api/
│   │   │   ├── analyze.py                  # 8-stage analysis pipeline orchestrator
│   │   │   └── kb_admin.py                 # Knowledge base CRUD endpoints
│   │   ├── db/
│   │   │   └── chroma_client.py            # ChromaDB connection manager
│   │   ├── models/
│   │   │   └── schemas.py                  # 30+ Pydantic models (typed API contracts)
│   │   └── services/
│   │       ├── parser_service.py           # PDF/DOCX text extraction
│   │       ├── ocr_service.py              # Gemini Vision OCR for scanned docs
│   │       ├── rule_extraction_service.py  # Deterministic regex extraction engine
│   │       ├── sniper_extraction_service.py # LLM-targeted page extraction
│   │       ├── llm_service.py              # Gemini API wrapper with retries
│   │       ├── benchmark_service.py        # Market percentile computation
│   │       ├── psychological_scoring.py    # Scoring Engine v3.0
│   │       ├── red_flag_service.py         # Rule-based risk detection
│   │       ├── negotiation_service.py      # Playbook generator with email scripts
│   │       ├── rag_service.py              # ChromaDB vector search
│   │       ├── evidence_service.py         # Clause evidence + drift detection
│   │       ├── ingestion_service.py        # Contract KB ingestion pipeline
│   │       ├── chunking_service.py         # Clause-aware document chunking
│   │       ├── cache_service.py            # Content-addressed result caching
│   │       └── context_aware_scoring.py    # Scoring context helpers
│   ├── data/
│   │   ├── market_data/                    # Salary datasets by role/city/band
│   │   ├── market_intelligence/            # Industry standards
│   │   ├── contracts_raw/                  # Raw contracts for KB ingestion
│   │   ├── processed/                      # Ingestion cache + manifest
│   │   └── chroma/                         # ChromaDB persistent storage
│   └── tests/                              # Test suite
├── frontend/
│   ├── src/
│   │   ├── pages/                          # 7 route pages
│   │   ├── components/
│   │   │   ├── analyze/                    # 14 analysis visualization components
│   │   │   ├── kb/                         # 4 knowledge base components
│   │   │   ├── layout/                     # App shell, sidebar, top nav
│   │   │   └── ui/                         # 8 reusable UI primitives
│   │   └── lib/                            # API client, types, utilities
│   └── ...config files
├── analyze_cli.py                          # CLI interface for contract analysis
├── requirements.txt                        # Backend dependencies (pinned)
├── requirements-rag.txt                    # ChromaDB dependency
└── start_server.ps1                        # Quick-start script (Windows)
```

---

## Windows Note

ChromaDB depends on `chroma-hnswlib`. On **Windows + Python 3.12**, pip may require **Microsoft C++ Build Tools**. If install fails, either:
- Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- Or use **Python 3.11** which has pre-built wheels

---

## License

This project was built as a final year project. Use it, learn from it, improve it.

---

<div align="center">

**Built with an unreasonable amount of coffee and an irrational hatred for unfair contracts.**

</div>
