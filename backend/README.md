# FairDeal Backend - Deterministic Contract Analysis System

A deterministic, auditable, fast contract benchmarking system with RAG used ONLY for evidence retrieval (not scoring).

## Key Features

- **Deterministic Scoring**: No LLM for scores - uses exact mathematical formula
- **Auditable**: Every output traceable to source text snippets
- **Fast**: Target ≤3s for deterministic path, ≤6s with optional narration
- **RAG for Evidence Only**: Similar contracts retrieved for provenance, not for scoring

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./chroma_db/fairdeal.db
JWT_SECRET_KEY=your_secret_key
```

### 3. Ingest Contracts into Knowledge Base

```bash
# From structured folders (employment/tech/junior/mumbai/*.pdf)
python -m app.ingest_cli --input data/raw_contracts

# From flat folder
python -m app.ingest_cli --input data/raw_contracts --flat

# Dry run (preview only)
python -m app.ingest_cli --input data --dry-run

# Force reprocess all files
python -m app.ingest_cli --input data --force
```

### 4. Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Test Analysis

```bash
curl -X POST "http://localhost:8000/api/v2/analyze" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@contract.pdf"
```

## Scoring Formula

The fairness score is computed deterministically:

```
S_raw = 50 + 0.4*(P_salary - 50) + 0.3*(50 - P_notice) - 0.3*(N_flags*5) + bonuses - penalties
S = clamp(round(S_raw), 0, 100)
```

Where:
- `P_salary`: Salary percentile (0-100), higher is better
- `P_notice`: Notice period percentile (0-100), lower is better for employee
- `N_flags`: Number of red flags identified
- Bonuses: +3 per favorable term, +5 for good benefits
- Penalties: -10 for non-compete clause, -5 for no benefits

### Missing Value Handling

If salary or notice is missing, its weight is redistributed proportionally to remaining components.

### Confidence Calculation

```
confidence = 0.6 * extraction_confidence + 0.4 * cohort_confidence
```

Penalties applied if cohort_size < 30 or missing critical fields.

## Cohort Broadening

To ensure meaningful percentile comparisons:

1. Start with strict filters: `contract_type + role_level + industry + location`
2. If cohort_size < MIN_N (30), broaden in order:
   - Remove `location`
   - Remove `industry`
   - Remove `role_level`
3. Always keep `contract_type`
4. Return `cohort_size` and `filters_used` + `broaden_steps`

## Red Flag Rules (Deterministic)

| Rule ID | Condition | Severity |
|---------|-----------|----------|
| SALARY_CRITICAL_LOW | salary < 10th percentile | Critical |
| SALARY_HIGH_LOW | salary 10-25th percentile | High |
| NOTICE_EXCESSIVE | notice > 90th percentile | High |
| NOTICE_LONG | notice 75-90th percentile | Medium |
| NON_COMPETE_PRESENT | non_compete = true | Medium |
| BENEFITS_LIMITED | benefits_count < 3 | Low |
| BENEFITS_NONE | benefits_count = 0 | Medium |

## API Endpoints

### V2 Analysis (Deterministic)

```
POST /api/v2/analyze
  - file: Upload file
  - enable_narration: bool (optional, default false)

Returns:
  - score: 0-100
  - score_confidence: 0-1
  - score_formula: Traceable calculation
  - percentiles: {salary, notice_period} with cohort info
  - cohort: {filters_used, cohort_size, broaden_steps}
  - red_flags: [{id, severity, rule, explanation, source_text}]
  - favorable_terms: [...]
  - negotiation_points: [...]
  - evidence: [{contract_id, chunk_index, similarity, preview}]
  - timings: {parse_ms, extract_ms, stats_ms, rag_ms, total_ms}
```

### Knowledge Base Admin

```
GET /api/kb/contracts          - List ingested contracts
GET /api/kb/contracts/{id}     - Full contract metadata
GET /api/kb/contracts/{id}/chunks - Chunk previews
GET /api/kb/stats              - Cohort counts and statistics
GET /api/kb/health             - ChromaDB status
DELETE /api/kb/contracts/{id}  - Remove contract
```

### Scoring Info

```
GET /api/v2/scoring-info       - Get formula and rules documentation
```

## Evaluation

### Run Extraction Accuracy Tests

```bash
# Create gold annotations in gold/annotations.jsonl
python -m app.eval.evaluate --gold gold/annotations.jsonl

# With verbose output
python -m app.eval.evaluate --gold gold/annotations.jsonl --verbose
```

Gold annotations format (JSONL):
```json
{"file": "path/to/contract.pdf", "salary_in_inr": 1500000, "notice_period_days": 60, "non_compete": true}
```

### Run Unit Tests

```bash
pytest app/tests/ -v
```

### Run Runtime Benchmarks

```bash
# Deterministic only (target: 3s)
python -m app.eval.benchmark --contracts data/raw_contracts

# With narration (target: 6s)
python -m app.eval.benchmark --contracts data/raw_contracts --with-narration
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── analyze.py         # V2 deterministic analysis endpoint
│   │   ├── kb_admin.py        # Knowledge base admin endpoints
│   │   ├── contracts.py       # Legacy analysis (V1)
│   │   └── ...
│   ├── services/
│   │   ├── analysis_service_v2.py  # Deterministic analysis pipeline
│   │   ├── scoring_engine.py       # Exact scoring formula
│   │   ├── stats_service_v2.py     # Cohort broadening logic
│   │   ├── clause_matcher_v2.py    # Rule-based red flags
│   │   ├── fast_extraction_service.py  # Regex-based extraction
│   │   └── ...
│   ├── models/
│   │   └── schemas.py         # Pydantic schemas with provenance
│   ├── eval/
│   │   ├── evaluate.py        # Gold set evaluation
│   │   └── benchmark.py       # Runtime benchmarks
│   ├── tests/
│   │   └── test_percentile.py # Unit tests
│   └── ingest_cli.py          # Folder-based ingestion CLI
├── gold/
│   └── annotations.jsonl      # Gold standard annotations
├── data/
│   ├── raw_contracts/         # Input contracts
│   └── processed/             # Processed metadata
└── chroma_db/                 # Vector database
```

## Architecture Principles

1. **Deterministic First**: No LLM for scoring or red flags
2. **Provenance Everywhere**: Every value has `source_text` and `confidence`
3. **Transparent Formulas**: Score computation is fully traceable
4. **Fast by Default**: Target <3s without LLM, <6s with optional narration
5. **RAG for Evidence**: Similar contracts provide provenance, not scores

## LLM Usage Policy

| Component | LLM Used? | Notes |
|-----------|-----------|-------|
| Text Extraction | NO | Regex patterns |
| Metadata Extraction | NO | Rule-based |
| Percentile Computation | NO | Mathematical |
| Red Flag Detection | NO | Deterministic rules |
| Fairness Score | NO | Exact formula |
| Narration | OPTIONAL | Single call, must not invent facts |

## Rate Limit Handling

- Embedding calls use batch processing (100 items)
- Exponential backoff with jitter for API errors
- Analysis results cached by `text_hash`
- Ingestion has configurable delay between files
