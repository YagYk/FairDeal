"""
FAIRDEAL pre-demo orchestrator.

Run this script once before walking into the project review. It will, in
order:

    1. Generate backend/data/market_data.json (deterministic synthetic
       Indian salary data, ~600 records spanning every cohort the benchmark
       service can ask about).

    2. Walk backend/data/contracts_raw/ and ingest every PDF/DOCX into
       ChromaDB so the RAG / Evidence panel and the KB Explorer have
       something to retrieve.

    3. Run the scoring validation suite end to end and print the headline
       metrics (pass rate, determinism, ordering accuracy, Cohen's d).

    4. Print a final health summary so you know exactly what to expect when
       the reviewers connect to the backend.

Usage:

    python prepare_demo.py                # full prep
    python prepare_demo.py --skip-ingest  # only seed market data + validate
    python prepare_demo.py --skip-eval    # skip the validation step

The script does NOT need the FastAPI server to be running. It calls the
underlying services directly.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"

# Make the `backend` package importable when this file is at the repo root.
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
DIM = "\033[2m"
RESET = "\033[0m"


def _section(title: str) -> None:
    print()
    print(f"{CYAN}{'=' * 72}{RESET}")
    print(f"{CYAN}{title}{RESET}")
    print(f"{CYAN}{'=' * 72}{RESET}")


def _ok(msg: str) -> None:
    print(f"  {GREEN}[ok]{RESET} {msg}")


def _warn(msg: str) -> None:
    print(f"  {YELLOW}[warn]{RESET} {msg}")


def _fail(msg: str) -> None:
    print(f"  {RED}[fail]{RESET} {msg}")


# ---------------------------------------------------------------------------
# Step 1: Market data
# ---------------------------------------------------------------------------

def step_seed_market_data() -> None:
    _section("Step 1 / 3 — Seed market data")

    out_path = BACKEND / "data" / "market_data.json"
    if out_path.exists() and out_path.stat().st_size > 1024:
        _ok(f"market_data.json already present ({out_path.stat().st_size // 1024} KB), skipping regenerate")
        return

    try:
        # Import lazily so missing deps surface only here.
        from scripts.generate_market_data import generate
    except Exception as exc:
        _fail(f"could not import the market-data generator: {exc}")
        raise

    records = generate(seed=42)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(records, indent=2))
    _ok(f"wrote {len(records)} records to {out_path.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Step 2: Knowledge-base ingestion
# ---------------------------------------------------------------------------

def step_ingest_kb(skip: bool = False) -> None:
    _section("Step 2 / 3 — Ingest contracts into ChromaDB")

    if skip:
        _warn("--skip-ingest passed, leaving the knowledge base alone")
        return

    raw_dir = BACKEND / "data" / "contracts_raw"
    if not raw_dir.exists():
        _fail(f"{raw_dir.relative_to(ROOT)} not found, nothing to ingest")
        return

    contracts = list(raw_dir.rglob("*.pdf")) + list(raw_dir.rglob("*.docx"))
    if not contracts:
        _fail(f"no PDF/DOCX contracts under {raw_dir.relative_to(ROOT)}")
        return

    print(f"  found {len(contracts)} candidate files under {raw_dir.relative_to(ROOT)}")

    try:
        from app.services.ingestion_service import IngestionService
    except Exception as exc:
        _fail(f"could not import IngestionService: {exc}")
        _warn("ingestion needs sentence-transformers + chromadb installed")
        return

    started = time.time()
    svc = IngestionService()
    res = svc.ingest_directory(raw_dir)
    elapsed = time.time() - started

    _ok(
        f"ingestion finished in {elapsed:.1f}s — "
        f"ingested={res.get('ingested', 0)}, "
        f"skipped={res.get('skipped', 0)}, "
        f"chunks_added={res.get('chunks_added', 0)}"
    )

    try:
        from app.db.chroma_client import collection_stats
        stats = collection_stats()
        _ok(f"ChromaDB collection now holds {stats.get('count', '?')} chunks")
    except Exception as exc:
        _warn(f"could not read collection stats: {exc}")


# ---------------------------------------------------------------------------
# Step 3: Validation suite
# ---------------------------------------------------------------------------

def step_validate(skip: bool = False) -> None:
    _section("Step 3 / 3 — Run the scoring validation suite")

    if skip:
        _warn("--skip-eval passed, validation not run")
        return

    try:
        from app.evaluation.evaluator import FairDealEvaluator
    except Exception as exc:
        _fail(f"could not import FairDealEvaluator: {exc}")
        return

    started = time.time()
    report = FairDealEvaluator().run_full_evaluation()
    elapsed = time.time() - started

    pass_rate = getattr(report, "scoring_pass_rate", None)             # already 0-100
    determinism = getattr(report, "determinism_score", None)            # already 0-100
    ordering_total = getattr(report, "known_ordering_total", None)
    ordering_correct = getattr(report, "known_ordering_correct", None)
    ordering_accuracy = getattr(report, "known_ordering_accuracy", None)
    n = getattr(report, "total_test_cases", None)

    _ok(f"validation finished in {elapsed:.1f}s on {n} test cases")
    if pass_rate is not None:
        _ok(f"scoring pass rate     : {pass_rate:.1f} %")
    if determinism is not None:
        _ok(f"determinism (3 runs)  : {determinism:.1f} %")
    if ordering_total is not None and ordering_correct is not None:
        acc = ordering_accuracy if ordering_accuracy is not None else 0.0
        _ok(f"known-ordering        : {ordering_correct} / {ordering_total} pairs correct ({acc:.1f} %)")

    cmps = getattr(report, "category_comparisons", []) or []
    for c in cmps[:3]:
        _ok(
            f"{c.category_a:>11} vs {c.category_b:<11}  "
            f"t={c.t_statistic:+.2f}  d={c.effect_size:+.2f}  "
            f"{'sig' if c.significant else 'ns '}"
        )


# ---------------------------------------------------------------------------
# Final health summary
# ---------------------------------------------------------------------------

def health_summary() -> None:
    _section("Final health summary")

    md = BACKEND / "data" / "market_data.json"
    chroma = BACKEND / "data" / "chroma"
    processed = BACKEND / "data" / "processed"
    manifest = processed / "manifest.json"
    env = ROOT / ".env"

    rows = [
        ("Market data file",    md.exists() and md.stat().st_size > 1024,
         f"{md.stat().st_size // 1024} KB" if md.exists() else "missing"),
        ("ChromaDB persistent dir", chroma.exists() and any(chroma.iterdir()) if chroma.exists() else False,
         "populated" if chroma.exists() and any(chroma.iterdir()) else "empty"),
        ("KB manifest.json",    manifest.exists(),
         "present" if manifest.exists() else "missing"),
        (".env file at repo root", env.exists(),
         "present (LLM features available)" if env.exists() else "absent (deterministic mode only)"),
    ]
    for label, ok, detail in rows:
        marker = f"{GREEN}OK  {RESET}" if ok else f"{YELLOW}WARN{RESET}"
        print(f"  [{marker}] {label:<28}  {DIM}{detail}{RESET}")

    print()
    print(f"  {DIM}Next steps:{RESET}")
    print("    1. Start the backend  :  uvicorn app.main:app --reload   (from backend/)")
    print("    2. Start the frontend :  npm run dev                     (from frontend/)")
    print("    3. Open               :  http://localhost:5173/")
    print()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-ingest", action="store_true", help="Do not rebuild the RAG knowledge base.")
    parser.add_argument("--skip-eval", action="store_true", help="Do not run the validation suite.")
    args = parser.parse_args()

    print()
    print(f"{CYAN}FAIRDEAL pre-demo prep{RESET}")
    print(f"{DIM}  repo : {ROOT}{RESET}")

    try:
        step_seed_market_data()
    except Exception as exc:
        _fail(f"step 1 crashed: {exc}")
        return 1

    try:
        step_ingest_kb(skip=args.skip_ingest)
    except Exception as exc:
        _fail(f"step 2 crashed: {exc}")
        # don't return; we still want validation output even if KB fails

    try:
        step_validate(skip=args.skip_eval)
    except Exception as exc:
        _fail(f"step 3 crashed: {exc}")

    health_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())
