# FairDeal - Comprehensive Project Documentation

> **A Deterministic, Auditable Contract Benchmarking System**

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [System Architecture](#2-system-architecture)
3. [Core Components](#3-core-components)
4. [Scoring System](#4-scoring-system)
5. [Data Flow](#5-data-flow)
6. [API Reference](#6-api-reference)
7. [Installation Guide](#7-installation-guide)
8. [Usage Guide](#8-usage-guide)
9. [Knowledge Base Management](#9-knowledge-base-management)
10. [Testing & Evaluation](#10-testing--evaluation)
11. [Configuration](#11-configuration)
12. [Troubleshooting](#12-troubleshooting)

---

## 1. Project Overview

### What is FairDeal?

FairDeal is a contract analysis system that helps job seekers understand if their employment contract is fair compared to market standards. It analyzes contracts and provides:

- **Fairness Score (0-100)**: A deterministic score based on salary, notice period, and contract terms
- **Percentile Rankings**: Where your contract stands compared to similar contracts
- **Red Flags**: Potential issues identified using rule-based analysis
- **Negotiation Points**: Actionable suggestions for improving contract terms

### Key Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Deterministic** | No LLM for scoring - exact mathematical formulas |
| **Auditable** | Every value traceable to source text |
| **Fast** | Target <3 seconds for analysis |
| **Transparent** | Full visibility into how scores are computed |
| **Privacy-First** | Contracts processed locally, not sent to external LLMs |

### What Makes This Different?

**Traditional AI Contract Analysis:**
```
Contract → LLM → "Trust me, the score is 65"
```

**FairDeal's Approach:**
```
Contract → Regex Extraction → Math Formula → "Score is 65 because:
  - Salary at 70th percentile (+8 points)
  - Notice at 40th percentile (+3 points)
  - 1 red flag (-1.5 points)
  - Non-compete clause (-10 points)
  Formula: 50 + 8 + 3 - 1.5 - 10 = 49.5 → 50"
```

---

## 2. System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Upload    │  │  Dashboard  │  │   Results   │              │
│  │  Contract   │  │             │  │   Display   │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                            │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    API Layer                              │   │
│  │  /api/v2/analyze  /api/kb/*  /api/auth/*                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Service Layer                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
│  │  │  Analysis   │  │   Scoring   │  │    Stats    │       │   │
│  │  │  Service    │  │   Engine    │  │   Service   │       │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
│  │  │   Clause    │  │    Fast     │  │     RAG     │       │   │
│  │  │  Matcher    │  │ Extraction  │  │   Service   │       │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                              │                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Storage Layer                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
│  │  │  ChromaDB   │  │   SQLite    │  │  JSON Files │       │   │
│  │  │  (Vectors)  │  │  (Users)    │  │ (Metadata)  │       │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
final_year_project/
├── backend/
│   ├── app/
│   │   ├── api/                    # API endpoints
│   │   │   ├── analyze.py          # V2 deterministic analysis
│   │   │   ├── kb_admin.py         # Knowledge base admin
│   │   │   ├── contracts.py        # Legacy analysis
│   │   │   ├── auth.py             # Authentication
│   │   │   └── profile.py          # User profiles
│   │   │
│   │   ├── services/               # Business logic
│   │   │   ├── analysis_service_v2.py   # Main analysis orchestrator
│   │   │   ├── scoring_engine.py        # Deterministic scoring
│   │   │   ├── stats_service_v2.py      # Percentile computation
│   │   │   ├── clause_matcher_v2.py     # Rule-based flags
│   │   │   ├── fast_extraction_service.py # Regex extraction
│   │   │   ├── rag_service.py           # Vector retrieval
│   │   │   ├── embedding_service.py     # Text embeddings
│   │   │   └── ingestion_service.py     # Contract ingestion
│   │   │
│   │   ├── models/                 # Data models
│   │   │   ├── schemas.py          # Pydantic schemas (V2)
│   │   │   ├── contract_schema.py  # Contract metadata
│   │   │   └── user.py             # User & analysis models
│   │   │
│   │   ├── parsers/                # Document parsing
│   │   │   ├── pdf_parser.py       # PDF text extraction
│   │   │   └── docx_parser.py      # DOCX text extraction
│   │   │
│   │   ├── db/                     # Database
│   │   │   ├── database.py         # SQLAlchemy setup
│   │   │   └── chroma_client.py    # ChromaDB client
│   │   │
│   │   ├── eval/                   # Evaluation tools
│   │   │   ├── evaluate.py         # Gold set evaluation
│   │   │   └── benchmark.py        # Performance benchmarks
│   │   │
│   │   ├── tests/                  # Unit tests
│   │   │   └── test_percentile.py  # Percentile & scoring tests
│   │   │
│   │   ├── utils/                  # Utilities
│   │   │   └── chunking.py         # Text chunking
│   │   │
│   │   ├── main.py                 # FastAPI app entry
│   │   ├── config.py               # Configuration
│   │   └── ingest_cli.py           # Ingestion CLI
│   │
│   ├── gold/                       # Gold annotations
│   │   └── annotations.jsonl
│   │
│   ├── chroma_db/                  # Vector database storage
│   ├── requirements.txt
│   └── verify_setup.py             # Setup verification
│
├── frontend/
│   ├── src/
│   │   ├── components/             # React components
│   │   ├── pages/                  # Page components
│   │   ├── services/               # API services
│   │   └── App.tsx                 # Main app
│   ├── package.json
│   └── vite.config.ts
│
├── data/
│   ├── raw_contracts/              # Input contracts (PDF/DOCX)
│   └── processed/                  # Processed metadata (JSON)
│
└── .env                            # Environment variables
```

---

## 3. Core Components

### 3.1 Analysis Service V2

**File:** `app/services/analysis_service_v2.py`

The main orchestrator that coordinates the entire analysis pipeline:

```python
class AnalysisServiceV2:
    def analyze_contract(self, file_content, filename):
        # Step 1: Parse document (PDF/DOCX → text)
        text = self._parse_file(file_content, filename)
        
        # Step 2: Extract metadata (regex patterns)
        metadata = self.fast_extraction.extract_metadata(text)
        
        # Step 3: Compute percentiles (compare to knowledge base)
        salary_percentile = self.stats_service.compute_percentile(...)
        
        # Step 4: Match clauses (rule-based red flags)
        red_flags, favorable, negotiation = self.clause_matcher.match_clauses(...)
        
        # Step 5: Compute score (exact formula)
        score, confidence, formula = self.scoring_engine.compute_score(...)
        
        # Step 6: Retrieve evidence (RAG)
        evidence = self.rag_service.retrieve_similar_contracts(...)
        
        return AnalysisResult(...)
```

### 3.2 Scoring Engine

**File:** `app/services/scoring_engine.py`

Computes the fairness score using a deterministic formula:

```python
class ScoringEngine:
    # Weights
    WEIGHT_SALARY = 0.4
    WEIGHT_NOTICE = 0.3
    WEIGHT_FLAGS = 0.3
    
    def compute_score(self, salary_percentile, notice_percentile, ...):
        # Base score
        score = 50
        
        # Salary contribution (higher percentile = better)
        if salary_percentile is not None:
            score += WEIGHT_SALARY * (salary_percentile - 50)
        
        # Notice contribution (lower percentile = better for employee)
        if notice_percentile is not None:
            score += WEIGHT_NOTICE * (50 - notice_percentile)
        
        # Penalties
        score -= WEIGHT_FLAGS * (red_flags_count * 5)
        score -= 10 if non_compete else 0
        
        # Bonuses
        score += favorable_terms_count * 3
        score += 5 if benefits_count >= 3 else (-5 if benefits_count == 0 else 0)
        
        return clamp(round(score), 0, 100)
```

### 3.3 Stats Service V2

**File:** `app/services/stats_service_v2.py`

Computes percentiles with cohort broadening:

```python
class StatsServiceV2:
    MIN_N = 30  # Minimum cohort size
    BROADENING_ORDER = ["location", "industry", "role_level"]
    
    def compute_percentile_with_cohort(self, value, field_name, filters):
        # Try with all filters
        cohort = self._get_cohort(filters)
        
        # Broaden if too small
        while len(cohort) < MIN_N and filters:
            filter_to_remove = BROADENING_ORDER.pop(0)
            del filters[filter_to_remove]
            cohort = self._get_cohort(filters)
        
        # Compute percentile
        count_below = sum(1 for v in cohort if v <= value)
        percentile = (count_below / len(cohort)) * 100
        
        return percentile, cohort_info
```

### 3.4 Clause Matcher V2

**File:** `app/services/clause_matcher_v2.py`

Rule-based red flag detection:

```python
class ClauseMatcherV2:
    RULES = {
        "SALARY_CRITICAL_LOW": {
            "condition": lambda pct: pct < 10,
            "severity": "critical",
            "description": "Salary significantly below market"
        },
        "SALARY_HIGH_LOW": {
            "condition": lambda pct: 10 <= pct < 25,
            "severity": "high",
            "description": "Salary below market average"
        },
        "NOTICE_EXCESSIVE": {
            "condition": lambda pct: pct > 90,
            "severity": "high",
            "description": "Excessive notice period"
        },
        # ... more rules
    }
    
    def match_clauses(self, salary_pct, notice_pct, ...):
        red_flags = []
        
        for rule_id, rule in RULES.items():
            if rule["condition"](salary_pct):
                red_flags.append(RedFlag(
                    id=rule_id,
                    severity=rule["severity"],
                    explanation=rule["description"],
                    source_text=source_texts.get("salary")
                ))
        
        return red_flags, favorable_terms, negotiation_points
```

### 3.5 Fast Extraction Service

**File:** `app/services/fast_extraction_service.py`

Regex-based metadata extraction (no LLM):

```python
class FastExtractionService:
    SALARY_PATTERNS = [
        r'(?:CTC|salary)[\s:]*₹?\s*(\d+(?:,\d+)*)\s*(?:LPA|lakhs?)',
        r'(\d+(?:\.\d+)?)\s*(?:LPA|lakhs?)',
        # ... more patterns
    ]
    
    def extract_metadata(self, text):
        salary = self._extract_salary(text)      # Uses regex
        notice = self._extract_notice_period(text)
        non_compete = self._check_non_compete(text)
        benefits = self._extract_benefits(text)
        
        return ContractMetadata(
            salary=ExtractedField(value=salary, source_text=match),
            notice_period_days=ExtractedField(value=notice, ...),
            ...
        )
```

---

## 4. Scoring System

### 4.1 The Formula

```
S_raw = 50 + 0.4*(P_salary - 50) + 0.3*(50 - P_notice) - 0.3*(N_flags × 5) + bonuses - penalties
S = clamp(round(S_raw), 0, 100)
```

### 4.2 Components Explained

| Component | Formula | Range | Meaning |
|-----------|---------|-------|---------|
| **Base Score** | 50 | Fixed | Everyone starts here |
| **Salary Impact** | 0.4 × (P_salary - 50) | -20 to +20 | Higher percentile = more points |
| **Notice Impact** | 0.3 × (50 - P_notice) | -15 to +15 | Lower percentile = more points |
| **Flag Penalty** | 0.3 × (N_flags × 5) | 0 to ~15 | Each flag costs 1.5 points |
| **Non-Compete** | -10 | -10 or 0 | Big penalty if present |
| **Good Benefits** | +5 | +5 or 0 | Bonus for 3+ benefits |
| **No Benefits** | -5 | -5 or 0 | Penalty for 0 benefits |
| **Favorable Terms** | +3 per term | 0 to ~15 | Bonus for good terms |

### 4.3 Example Calculations

**Example 1: Good Contract**
```
Input:
- Salary: 75th percentile (above average)
- Notice: 30th percentile (shorter than average)
- Red flags: 0
- Non-compete: No
- Benefits: 4 (health, PF, gratuity, leave)

Calculation:
Base:           50
Salary:         +0.4 × (75 - 50) = +10
Notice:         +0.3 × (50 - 30) = +6
Flags:          -0.3 × (0 × 5) = 0
Non-compete:    0
Benefits:       +5

Total: 50 + 10 + 6 + 0 + 0 + 5 = 71
```

**Example 2: Poor Contract**
```
Input:
- Salary: 20th percentile (below average)
- Notice: 85th percentile (very long)
- Red flags: 2 (low salary, long notice)
- Non-compete: Yes
- Benefits: 1

Calculation:
Base:           50
Salary:         +0.4 × (20 - 50) = -12
Notice:         +0.3 × (50 - 85) = -10.5
Flags:          -0.3 × (2 × 5) = -3
Non-compete:    -10
Benefits:       0 (between 1-2, no bonus/penalty)

Total: 50 - 12 - 10.5 - 3 - 10 = 14.5 → 15
```

### 4.4 Missing Value Handling

When salary or notice period cannot be extracted:

1. The missing component's weight is **redistributed** to remaining components
2. Confidence score is **reduced** by 0.1 per missing field
3. Analysis continues with available data

```python
# Example: Only notice available (no salary)
available_weight = WEIGHT_NOTICE  # 0.3
norm_factor = (0.4 + 0.3) / 0.3  # 2.33

# Notice now has weight: 0.3 × 2.33 = 0.7 (normalized)
```

### 4.5 Confidence Score

```
confidence = 0.6 × extraction_confidence + 0.4 × cohort_confidence
```

Where:
- `extraction_confidence` = minimum confidence across extracted fields
- `cohort_confidence` = min(1.0, cohort_size / 30)

Adjustments:
- Missing salary: -0.1
- Missing notice: -0.1
- Cohort < 10: Warning displayed

---

## 5. Data Flow

### 5.1 Ingestion Flow (Offline)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  PDF/DOCX   │────▶│   Parser    │────▶│    Text     │
│   Files     │     │ (pdfplumber)│     │  (string)   │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  ChromaDB   │◀────│  Embedding  │◀────│   Chunker   │
│  (vectors)  │     │  (Gemini)   │     │  (clause)   │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │    JSON     │
                                        │  Metadata   │
                                        └─────────────┘
```

### 5.2 Analysis Flow (Runtime)

```
┌─────────────┐
│   Upload    │
│  Contract   │
└─────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Parse Document                                      │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │   PDF?      │────▶│ pdfplumber  │────▶│    Text     │    │
│  │   DOCX?     │────▶│ python-docx │────▶│  (string)   │    │
│  └─────────────┘     └─────────────┘     └─────────────┘    │
│                                                 │            │
│  Timing: ~500ms                                 │            │
└─────────────────────────────────────────────────┼────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Extract Metadata (NO LLM)                          │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │    Text     │────▶│   Regex     │────▶│  Metadata   │    │
│  │             │     │  Patterns   │     │  + Source   │    │
│  └─────────────┘     └─────────────┘     └─────────────┘    │
│                                                 │            │
│  Timing: ~100ms                                 │            │
└─────────────────────────────────────────────────┼────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 3: Compute Percentiles                                 │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │  Metadata   │────▶│   Stats     │────▶│ Percentiles │    │
│  │  (salary,   │     │  Service    │     │  + Cohort   │    │
│  │   notice)   │     │ (broadening)│     │    Info     │    │
│  └─────────────┘     └─────────────┘     └─────────────┘    │
│                                                 │            │
│  Timing: ~100ms                                 │            │
└─────────────────────────────────────────────────┼────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 4: Match Clauses (NO LLM)                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │ Percentiles │────▶│   Rules     │────▶│  Red Flags  │    │
│  │  + Data     │     │  Engine     │     │ + Favorable │    │
│  └─────────────┘     └─────────────┘     └─────────────┘    │
│                                                 │            │
│  Timing: ~10ms                                  │            │
└─────────────────────────────────────────────────┼────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 5: Compute Score (NO LLM)                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │ All Data    │────▶│   Scoring   │────▶│   Score     │    │
│  │             │     │   Engine    │     │ + Formula   │    │
│  └─────────────┘     └─────────────┘     └─────────────┘    │
│                                                 │            │
│  Timing: ~5ms                                   │            │
└─────────────────────────────────────────────────┼────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 6: Retrieve Evidence (RAG)                            │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐    │
│  │   Query     │────▶│  ChromaDB   │────▶│  Evidence   │    │
│  │  Embedding  │     │   Search    │     │   Chunks    │    │
│  └─────────────┘     └─────────────┘     └─────────────┘    │
│                                                 │            │
│  Timing: ~1000ms                                │            │
└─────────────────────────────────────────────────┼────────────┘
                                                  │
                                                  ▼
                                        ┌─────────────────┐
                                        │ Analysis Result │
                                        │  (JSON Response)│
                                        └─────────────────┘
```

---

## 6. API Reference

### 6.1 Authentication

#### POST /api/auth/register
Create a new user account.

```json
// Request
{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe"
}

// Response
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "John Doe"
}
```

#### POST /api/auth/login
Authenticate and get JWT token.

```json
// Request
{
  "email": "user@example.com",
  "password": "securepassword"
}

// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 6.2 Contract Analysis

#### POST /api/v2/analyze
Analyze a contract using deterministic scoring.

**Request:**
- `file`: PDF/DOCX file (multipart/form-data)
- `enable_narration`: boolean (optional, default: false)

**Response:**
```json
{
  "success": true,
  "analysis_id": "uuid",
  "version": "v2",
  
  "score": 64,
  "score_confidence": 0.85,
  "score_formula": "50 + 0.40*(65.0-50) + 0.30*(50-45.0) - 0.30*(1*5) + 5 = 63.5 → 64",
  
  "percentiles": {
    "salary": {
      "value": 65.0,
      "field_value": 1200000,
      "cohort_size": 42,
      "comparable_values_range": "500,000 - 2,500,000"
    },
    "notice_period": {
      "value": 45.0,
      "field_value": 60,
      "cohort_size": 42
    }
  },
  
  "cohort": {
    "filters_used": {
      "contract_type": "employment",
      "industry": "tech"
    },
    "cohort_size": 42,
    "broaden_steps": ["Removed location=mumbai"],
    "min_n": 30,
    "confidence_note": null
  },
  
  "red_flags": [
    {
      "id": "NON_COMPETE_PRESENT",
      "severity": "medium",
      "rule": "Non-compete clause present",
      "explanation": "This contract contains a non-compete clause...",
      "source_text": "non-compete",
      "threshold": null,
      "actual_value": null
    }
  ],
  
  "favorable_terms": [
    {
      "id": "SALARY_EXCELLENT",
      "term": "Above-market salary",
      "explanation": "Your salary is in the 65th percentile...",
      "source_text": "CTC: 12,00,000",
      "value": "₹12,00,000 (65th percentile)"
    }
  ],
  
  "negotiation_points": [
    {
      "id": "NEG_NON_COMPETE",
      "topic": "Non-Compete Clause",
      "script": "I have concerns about the non-compete clause...",
      "reason": "Non-compete clauses can limit future career options",
      "priority": 2
    }
  ],
  
  "evidence": [
    {
      "contract_id": "EMPLOYMENT_AGREEMENT_1",
      "chunk_index": 3,
      "clause_type": "compensation",
      "similarity": 0.89,
      "chunk_text_preview": "The Employee shall be entitled to...",
      "metadata": {}
    }
  ],
  
  "narration": null,
  
  "contract_metadata": {
    "contract_type": "employment",
    "industry": "tech",
    "role_level": "senior",
    "location": "Mumbai",
    "salary_in_inr": 1200000,
    "salary_source_text": "CTC: 12,00,000 per annum",
    "notice_period_days": 60,
    "notice_source_text": "60 days notice period",
    "non_compete": true,
    "benefits": ["health insurance", "provident fund"],
    "extraction_confidence": 0.85
  },
  
  "timings": {
    "parse_ms": 450,
    "extract_ms": 120,
    "stats_ms": 85,
    "rag_ms": 890,
    "score_ms": 5,
    "total_ms": 1650
  },
  
  "text_hash": "a1b2c3...",
  "cached": false
}
```

#### GET /api/v2/scoring-info
Get documentation of the scoring system.

```json
{
  "version": "v2",
  "type": "deterministic",
  "formula": "S = 50 + 0.4*(P_salary - 50) + 0.3*(50 - P_notice) - 0.3*(N_flags*5) + bonuses - penalties",
  "components": {
    "base_score": 50,
    "salary_weight": 0.4,
    "notice_weight": 0.3,
    "flag_weight": 0.3,
    "flag_penalty": 5,
    "favorable_bonus": 3,
    "non_compete_penalty": 10
  },
  "red_flag_rules": {
    "SALARY_CRITICAL_LOW": "salary < 10th percentile → critical",
    "SALARY_HIGH_LOW": "salary < 25th percentile → high",
    "NOTICE_EXCESSIVE": "notice > 90th percentile → high",
    "NOTICE_LONG": "notice > 75th percentile → medium",
    "NON_COMPETE_PRESENT": "non_compete = true → medium",
    "BENEFITS_LIMITED": "benefits_count < 3 → low"
  }
}
```

### 6.3 Knowledge Base Admin

#### GET /api/kb/contracts
List ingested contracts.

**Query Parameters:**
- `contract_type`: Filter by type (employment, internship, etc.)
- `industry`: Filter by industry (tech, finance, etc.)
- `role_level`: Filter by role (junior, senior, etc.)
- `location`: Filter by location
- `limit`: Max results (default: 100)
- `offset`: Pagination offset

```json
{
  "contracts": [
    {
      "contract_id": "EMPLOYMENT_AGREEMENT_1",
      "contract_type": "employment",
      "industry": "tech",
      "role_level": "senior",
      "location": "Mumbai",
      "salary_in_inr": 1200000,
      "notice_period_days": 60,
      "non_compete": true,
      "num_chunks": 15,
      "processed_date": "2024-01-15"
    }
  ],
  "total": 85,
  "offset": 0,
  "limit": 100,
  "filters_applied": {}
}
```

#### GET /api/kb/contracts/{contract_id}
Get full metadata for a contract.

#### GET /api/kb/contracts/{contract_id}/chunks
Get chunk previews for a contract.

#### GET /api/kb/stats
Get knowledge base statistics.

```json
{
  "stats": {
    "total_contracts": 85,
    "total_chunks": 1250,
    "contracts_by_type": {
      "employment": 60,
      "internship": 15,
      "consultancy": 10
    },
    "contracts_by_industry": {
      "tech": 45,
      "finance": 25,
      "healthcare": 10,
      "other": 5
    },
    "contracts_by_role_level": {
      "junior": 20,
      "mid": 35,
      "senior": 25,
      "manager": 5
    },
    "chroma_status": "healthy"
  },
  "chroma": {
    "collection_name": "contracts",
    "total_chunks": 1250
  }
}
```

#### GET /api/kb/health
Health check for knowledge base.

```json
{
  "status": "healthy",
  "chroma": {
    "status": "connected",
    "collection_name": "contracts",
    "total_chunks": 1250
  },
  "metadata_dir": {
    "status": "accessible",
    "path": "/path/to/processed",
    "file_count": 85
  },
  "issues": []
}
```

#### DELETE /api/kb/contracts/{contract_id}
Remove a contract from the knowledge base.

---

## 7. Installation Guide

### 7.1 Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Google Cloud account (for Gemini API key)
- (Optional) Tesseract OCR for scanned PDFs
- (Optional) Poppler for PDF image extraction

### 7.2 Backend Setup

```bash
# Clone repository
git clone <repository-url>
cd final_year_project

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

### 7.3 Environment Configuration

Create `.env` file in **project root**:

```env
# Required
GOOGLE_API_KEY=your_gemini_api_key_here

# Database (SQLite by default)
DATABASE_URL=sqlite:///./chroma_db/fairdeal.db

# JWT Authentication
JWT_SECRET_KEY=your_random_secret_key_at_least_32_chars

# Optional
LLM_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=models/text-embedding-004
```

### 7.4 Verify Installation

```bash
cd backend
python verify_setup.py
```

Expected output:
```
============================================================
FAIRDEAL V2 - SETUP VERIFICATION
============================================================
Checking imports...
  ✓ schemas.py
  ✓ scoring_engine.py
  ✓ stats_service_v2.py
  ✓ clause_matcher_v2.py
  ✓ analysis_service_v2.py
  ✓ kb_admin.py
  ✓ analyze.py

Testing scoring formula...
  ✓ Score 64 is in expected range (60, 68)

Testing clause matcher...
  ✓ Expected at least 3 red flags, got 4

Checking configuration...
  ✓ Google API key is set

============================================================
✓ ALL CHECKS PASSED
============================================================
```

### 7.5 Frontend Setup

```bash
cd frontend
npm install
```

### 7.6 OCR Setup (Optional)

For scanned PDFs:

**Windows:**
```powershell
# Install Tesseract
winget install UB-Mannheim.TesseractOCR

# Install Poppler
# Download from: https://github.com/osber/poppler-windows/releases
# Extract to C:\poppler and add C:\poppler\Library\bin to PATH
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**Mac:**
```bash
brew install tesseract poppler
```

---

## 8. Usage Guide

### 8.1 Building the Knowledge Base

The system needs contracts to compare against:

```bash
cd backend

# Option 1: Ingest from flat folder
python -m app.ingest_cli --input ../data/raw_contracts --flat

# Option 2: Ingest from structured folders
# Folder structure: contract_type/industry/role_level/location/
python -m app.ingest_cli --input ../data

# Option 3: Dry run (see what would be ingested)
python -m app.ingest_cli --input ../data --dry-run

# Option 4: Force reprocess all files
python -m app.ingest_cli --input ../data --force
```

### 8.2 Starting the Server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

API documentation available at: `http://localhost:8000/docs`

### 8.3 Starting the Frontend

```bash
cd frontend
npm run dev
```

Frontend available at: `http://localhost:5173`

### 8.4 Analyzing a Contract

**Using the Frontend:**
1. Navigate to `http://localhost:5173`
2. Log in or register
3. Upload a contract (PDF/DOCX)
4. View the analysis results

**Using cURL:**
```bash
# 1. Login to get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}' \
  | jq -r '.access_token')

# 2. Analyze contract
curl -X POST "http://localhost:8000/api/v2/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@contract.pdf"
```

**Using Python:**
```python
import requests

# Login
login = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"email": "user@example.com", "password": "password"}
)
token = login.json()["access_token"]

# Analyze
with open("contract.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/v2/analyze",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": f}
    )

result = response.json()
print(f"Score: {result['score']}/100")
print(f"Formula: {result['score_formula']}")

for flag in result['red_flags']:
    print(f"⚠ {flag['id']}: {flag['explanation']}")
```

---

## 9. Knowledge Base Management

### 9.1 Folder Structure for Ingestion

**Structured (Recommended):**
```
data/
├── employment/
│   ├── tech/
│   │   ├── junior/
│   │   │   └── mumbai/
│   │   │       ├── contract1.pdf
│   │   │       └── contract2.pdf
│   │   └── senior/
│   │       └── delhi/
│   │           └── contract3.pdf
│   └── finance/
│       └── mid/
│           └── contract4.pdf
├── internship/
│   └── tech/
│       └── intern_contract.pdf
└── consultancy/
    └── other/
        └── consulting_agreement.pdf
```

**Flat:**
```
data/raw_contracts/
├── contract1.pdf
├── contract2.pdf
├── contract3.docx
└── ...
```

### 9.2 Checking Ingestion Status

```bash
# View statistics
curl http://localhost:8000/api/kb/stats

# List contracts
curl "http://localhost:8000/api/kb/contracts?limit=10"

# Health check
curl http://localhost:8000/api/kb/health
```

### 9.3 Removing a Contract

```bash
curl -X DELETE "http://localhost:8000/api/kb/contracts/CONTRACT_ID" \
  -H "Authorization: Bearer $TOKEN"
```

### 9.4 Minimum Recommended Dataset

For reliable percentile comparisons:
- **Minimum:** 30 contracts per cohort (contract type)
- **Recommended:** 75-100 contracts total
- **Ideal distribution:**
  - Employment: 50+ contracts
  - Internship: 15+ contracts
  - Consultancy: 10+ contracts

---

## 10. Testing & Evaluation

### 10.1 Unit Tests

```bash
cd backend
python -m pytest app/tests/ -v
```

Tests cover:
- Percentile computation
- Cohort broadening logic
- Scoring formula
- Score clamping

### 10.2 Extraction Accuracy Evaluation

Create gold annotations (`gold/annotations.jsonl`):
```json
{"file": "../data/raw_contracts/contract1.pdf", "salary_in_inr": 1200000, "notice_period_days": 60, "non_compete": true}
{"file": "../data/raw_contracts/contract2.pdf", "salary_in_inr": 800000, "notice_period_days": 30, "non_compete": false}
```

Run evaluation:
```bash
python -m app.eval.evaluate --gold gold/annotations.jsonl
```

Output:
```
============================================================
EXTRACTION ACCURACY EVALUATION
============================================================
Total samples: 10

SALARY:
  Exact match: 60.0%
  Within ±5%:  80.0%

NOTICE PERIOD:
  Exact match: 90.0%

NON-COMPETE:
  Precision: 0.857
  Recall:    0.923
  F1 Score:  0.889

CONFUSION EXAMPLES:
  salary: gold=1200000, extracted=1150000 (contract1.pdf)
============================================================
```

### 10.3 Performance Benchmarks

```bash
# Deterministic only (target: 3s)
python -m app.eval.benchmark --contracts ../data/raw_contracts --limit 10

# With narration (target: 6s)
python -m app.eval.benchmark --contracts ../data/raw_contracts --with-narration
```

Output:
```
============================================================
RUNTIME BENCHMARK RESULTS
============================================================
Mode: Deterministic Only
Target: 3000ms

Total files: 10
Successful:  10
Failed:      0

TIMING (ms):
  Average Total:   1850.5
  Average Parse:    520.3
  Average Extract:  115.2
  Average Stats:     95.8
  Average RAG:      985.4
  Average Score:      5.2

  Min:  1250ms
  Max:  2450ms
  P50:  1820ms
  P90:  2350ms

✓ PASS: Average 1850ms <= target 3000ms
============================================================
```

---

## 11. Configuration

### 11.1 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | - | Gemini API key for embeddings |
| `DATABASE_URL` | No | SQLite | Database connection string |
| `JWT_SECRET_KEY` | Yes | - | Secret for JWT tokens |
| `LLM_MODEL` | No | `gemini-1.5-flash` | LLM model name |
| `EMBEDDING_MODEL` | No | `text-embedding-004` | Embedding model |
| `CHROMA_DB_PATH` | No | `./chroma_db` | ChromaDB storage path |
| `MAX_CHUNK_SIZE_TOKENS` | No | 800 | Max tokens per chunk |
| `CHUNK_OVERLAP_TOKENS` | No | 100 | Overlap between chunks |

### 11.2 Scoring Configuration

In `app/services/scoring_engine.py`:

```python
# Weights
WEIGHT_SALARY = 0.4
WEIGHT_NOTICE = 0.3
WEIGHT_FLAGS = 0.3

# Penalties/Bonuses
FLAG_PENALTY = 5
FAVORABLE_BONUS = 3
NON_COMPETE_PENALTY = 10

# Cohort thresholds
MIN_COHORT_FULL_CONFIDENCE = 30
MIN_COHORT_ACCEPTABLE = 10
```

### 11.3 Red Flag Rules

In `app/services/clause_matcher_v2.py`:

```python
RULES = {
    "SALARY_CRITICAL_LOW": {"threshold": 10, "severity": "critical"},
    "SALARY_HIGH_LOW": {"threshold": 25, "severity": "high"},
    "NOTICE_EXCESSIVE": {"threshold": 90, "severity": "high"},
    "NOTICE_LONG": {"threshold": 75, "severity": "medium"},
    # Add custom rules here
}
```

---

## 12. Troubleshooting

### 12.1 Common Issues

#### "No contracts in knowledge base"
```bash
# Check if ingestion ran
curl http://localhost:8000/api/kb/stats

# Re-run ingestion
python -m app.ingest_cli --input ../data/raw_contracts --flat --force
```

#### "Google API key not set"
```bash
# Verify .env file exists in project root
cat ../.env

# Should contain:
# GOOGLE_API_KEY=your_key_here
```

#### "Rate limit exceeded"
The system has built-in rate limiting. If you hit limits:
- Ingestion waits 5 seconds between files
- Exponential backoff on API errors
- Analysis results are cached by text_hash

#### "Extraction confidence low"
- Check if the PDF is scanned (needs OCR)
- Verify Tesseract is installed for scanned PDFs
- Check extraction patterns in `fast_extraction_service.py`

#### "Cohort size too small"
- Ingest more contracts of the same type
- The system automatically broadens filters
- Check `cohort.broaden_steps` in response

### 12.2 Debug Mode

Enable debug logging:
```python
# In main.py
logger.add("debug.log", level="DEBUG")
```

### 12.3 Verifying Components

```bash
cd backend
python verify_setup.py
```

### 12.4 Getting Help

1. Check the API docs: `http://localhost:8000/docs`
2. Review logs: `backend/backend.log`
3. Run unit tests: `pytest app/tests/ -v`
4. Check KB health: `curl http://localhost:8000/api/kb/health`

---

## Appendix A: Red Flag Rules Reference

| Rule ID | Condition | Severity | Description |
|---------|-----------|----------|-------------|
| `SALARY_CRITICAL_LOW` | P < 10% | Critical | Salary in bottom 10% |
| `SALARY_HIGH_LOW` | 10% ≤ P < 25% | High | Salary below 25th percentile |
| `NOTICE_EXCESSIVE` | P > 90% | High | Notice longer than 90% of contracts |
| `NOTICE_LONG` | 75% < P ≤ 90% | Medium | Notice longer than 75% of contracts |
| `NON_COMPETE_PRESENT` | Clause exists | Medium | Has non-compete restriction |
| `NON_COMPETE_LONG` | Duration > 12mo | High | Non-compete over 12 months |
| `BENEFITS_NONE` | Count = 0 | Medium | No benefits mentioned |
| `BENEFITS_LIMITED` | Count < 3 | Low | Fewer than 3 benefits |

## Appendix B: Favorable Terms Reference

| Term ID | Condition | Description |
|---------|-----------|-------------|
| `SALARY_EXCELLENT` | P ≥ 75% | Salary in top 25% |
| `NOTICE_SHORT` | P ≤ 25% | Notice shorter than 75% of contracts |
| `BENEFITS_GOOD` | Count ≥ 3 | Good benefits package |

## Appendix C: API Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid file, missing fields) |
| 401 | Unauthorized (missing/invalid token) |
| 404 | Not found (contract, analysis) |
| 429 | Rate limited |
| 500 | Internal server error |

---

*Last updated: January 2026*
*Version: 2.0.0*
