# FAIRDEAL — Demo Quickstart

One page. Read it once before walking into the review.

---

## 1. Prep the project (run once, ~5 minutes)

From the repo root:

```bash
python prepare_demo.py
```

That single command:

1. Generates `backend/data/market_data.json` (~600 deterministic Indian-market salary records covering every role/city/experience/company-type cohort the benchmark service can ask for).
2. Ingests every contract under `backend/data/contracts_raw/` into ChromaDB so the RAG / Evidence panel and the KB Explorer have something to retrieve.
3. Runs the scoring validation suite on all 30 ground-truth test cases and prints the pass rate, determinism, ordering accuracy, and Cohen's d numbers.
4. Prints a final health summary so you know what state you're in.

Useful flags:

```bash
python prepare_demo.py --skip-ingest   # only seed market data + validate (fast)
python prepare_demo.py --skip-eval     # do everything except the validation pass
```

If `prepare_demo.py` reports `[fail]` on any step, fix that step before continuing — the demo will look broken otherwise.

---

## 2. Optional: enable LLM features

If you have a Google Gemini API key, copy `.env.example` to `.env` at the repo root and fill in:

```env
FAIRDEAL_LLM_API_KEY=AIza...
```

This unlocks:

- Gemini Vision OCR for scanned/photographed offer letters
- Sniper extraction for fields the regex layer misses
- AI narration on the Results page

Without a key, the system stays in deterministic mode — every panel still renders, just without LLM-generated prose. **This is fine for the demo** as long as you mention "running in deterministic mode for reliability".

---

## 3. Start the servers

Two terminals.

**Terminal A — backend:**
```bash
cd backend
uvicorn app.main:app --reload
```
Backend listens at `http://127.0.0.1:8000`. Open `http://127.0.0.1:8000/docs` to verify Swagger loads (title now reads "FairDeal", not "FairDeal DEBUG").

**Terminal B — frontend:**
```bash
cd frontend
npm install   # only the first time
npm run dev
```
Frontend runs at `http://127.0.0.1:5173`.

---

## 4. Demo flight plan (≈ 6 minutes)

Walk reviewers through the system in this order — it puts your strongest material first and leaves no panel blank.

| Step | Page | What to say |
|------|------|-------------|
| 1 | `/evaluation` | "30 ground-truth contracts, 100 % pass rate, 100 % determinism across three runs, 15 / 15 known orderings correct, Cohen's d = 4.60 between product and service companies." Show the metrics card and the boxplot. |
| 2 | `/analyze` | Upload a real-looking contract (use one of the DOCX files from `backend/data/contracts_raw/`, e.g. `Salesforce_Riya_Saxena_offer_letter.docx`). Walk through the eight stages live. |
| 3 | `/results` | After the upload, narrate: extraction → market percentile (now backed by your seeded data) → red flags → fairness score with grade → negotiation playbook → RAG evidence chunks. |
| 4 | `/kb` | Show the Knowledge Base explorer with all ingested contracts. Run a semantic search for "non-compete" or "training bond" to demonstrate retrieval. |
| 5 | Back to slides / report | Close with the architecture diagram (`backend/results/report_fig_pipeline.png`) and the validation figures. |

---

## 5. If something breaks live

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| "Market data unavailable" on Results page | `prepare_demo.py` step 1 failed | Re-run `python backend/scripts/generate_market_data.py` |
| Evidence panel empty | ChromaDB not built | Re-run `python prepare_demo.py --skip-eval` (or just the ingestion: `python -m backend.app.services.ingestion_service --input backend/data/contracts_raw`) |
| OCR / sniper errors | No Gemini key | Either add a key to `.env`, or stay in deterministic mode and skip the OCR demo |
| ChromaDB "tenant not found" on cold start | known Windows flake | Hit the endpoint again — there's a tenacity retry around the client; the second call works |
| Validation page numbers look wrong | Stale cache | Backend has `clear_service_caches()` on startup, so just restart uvicorn |

---

## 6. What you can defend honestly

- **Validation methodology**: 30 test cases with predefined expected score ranges, encoded in `backend/app/evaluation/ground_truth.py`. Reproducible from a clean clone.
- **Determinism**: scoring engine has zero randomness; same input always produces the same score. Verified across three runs.
- **Hybrid extraction**: 93 regex patterns, then a per-field LLM sniper for misses. Per-field prompting was a deliberate decision after the single-prompt approach produced inconsistent JSON.
- **Three-tier OCR**: Gemini Vision → PyMuPDF → Tesseract. Each tier has a documented post-processing density check that catches confident-looking garbage.
- **Synthetic market data**: clearly labelled `fairdeal_synthetic_v1` in every record. State this honestly. The benchmark methodology is real even if the demo data is generated.
- **Knowledge base**: 110+ Indian contracts (30 synthetic offer letters + ~80 real reference contracts across employment / consultancy / internship categories), all under `backend/data/contracts_raw/`.

---

## 7. What NOT to claim

- Do not call the synthetic offer-letter corpus "real anonymised contracts" — they are programmatically generated. The report wording was already corrected.
- Do not claim live market-data integration. The current cohorts are curated synthetic data; live API integration is on the future-work list.
- Do not pretend OCR works without a Gemini key. PyMuPDF / Tesseract fallbacks work but are not as good — call this out.

---

You're ready. Good luck tomorrow.
