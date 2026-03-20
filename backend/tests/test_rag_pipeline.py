"""
RAG Pipeline Verification Test.

Tests that:
1. ChromaDB has ingested data
2. RAG queries return results for each clause type
3. Evidence service collects evidence from KB
4. KB stats are computed correctly

Run from backend/:
    python -m tests.test_rag_pipeline
"""

import json
import sys
from pathlib import Path

# Ensure backend is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.db.chroma_client import get_collection, collection_stats
from app.services.rag_service import RAGService
from app.services.evidence_service import EvidenceService
from app.models.schemas import (
    ClauseType,
    ContractExtractionResult,
    ExtractedClause,
    ExtractedField,
    ExtractionMethod,
)


PASS = 0
FAIL = 0


def record(name: str, ok: bool, detail: str = ""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name}: {detail}")


def test_chroma_has_data():
    """Verify ChromaDB collection has ingested chunks."""
    print("\n=== TEST 1: ChromaDB Data Check ===")
    stats = collection_stats()
    count = stats["count"]
    print(f"  Collection count: {count} chunks")
    record("ChromaDB has data", count > 0, f"count={count}")
    return count


def test_rag_service_init():
    """Verify RAG service initializes successfully."""
    print("\n=== TEST 2: RAG Service Initialization ===")
    rag = RAGService()
    record("RAG enabled", rag.enabled, "RAG disabled on init")
    record("Collection exists", rag.collection is not None, "collection is None")
    record("Embedder exists", rag._embedder is not None, "_embedder is None")
    return rag


def test_rag_queries(rag: RAGService):
    """Verify RAG queries return results for each clause type."""
    print("\n=== TEST 3: RAG Semantic Queries ===")

    test_queries = {
        ClauseType.termination: "The employee must provide 30 days written notice before resignation.",
        ClauseType.compensation: "The total annual CTC shall be Rs 12,00,000 including all allowances.",
        ClauseType.confidentiality: "The employee shall not disclose any proprietary information.",
        ClauseType.non_compete: "For a period of 12 months after termination, employee shall not join competitors.",
        ClauseType.general: "This employment agreement is entered into between the company and the employee.",
        ClauseType.ip: "All inventions and intellectual property created during employment belong to the company.",
    }

    total = 0
    for ctype, query in test_queries.items():
        results = rag.find_similar_clauses(query, ctype, top_k=3)
        count = len(results)
        total += count
        record(
            f"Query {ctype.value}",
            count > 0,
            f"0 results for clause_type={ctype.value}",
        )
        if results:
            doc, sim, meta = results[0]
            print(f"    Top: sim={sim:.3f} file={meta.get('filename', '?')[:40]}")

    print(f"  Total results: {total}")
    record("At least some queries returned results", total > 0, f"total={total}")
    return total


def test_evidence_service(rag: RAGService):
    """Verify evidence service collects evidence from extraction."""
    print("\n=== TEST 4: Evidence Service ===")
    evidence_svc = EvidenceService(rag)

    # Build a mock extraction with some clause text
    extraction = ContractExtractionResult()
    extraction.ctc_inr = ExtractedField(
        value=1200000,
        confidence=0.9,
        source_text="annual CTC of Rs 12,00,000",
        method=ExtractionMethod.regex,
    )
    extraction.extracted_clauses = {
        "termination": ExtractedClause(
            text="Either party may terminate this agreement by providing 30 days written notice.",
            evidence=ExtractedField(value=1, confidence=0.7, method=ExtractionMethod.regex),
        ),
        "confidentiality": ExtractedClause(
            text="The employee agrees to maintain strict confidentiality of all proprietary information.",
            evidence=ExtractedField(value=1, confidence=0.7, method=ExtractionMethod.regex),
        ),
    }
    extraction.benefits = ["health_insurance", "provident_fund", "paid_leave"]
    extraction.benefits_count = 3
    extraction.role = ExtractedField(value="Software Engineer", confidence=0.8, method=ExtractionMethod.regex)

    evidence_map, drift = evidence_svc.collect_evidence_and_drift(extraction)

    clause_types_found = list(evidence_map.keys())
    total_evidence = sum(len(v) for v in evidence_map.values())

    record("Evidence map is non-empty", len(evidence_map) > 0, f"keys={clause_types_found}")
    record("Total evidence > 0", total_evidence > 0, f"total={total_evidence}")
    record("Compensation evidence queried", "compensation" in evidence_map, f"keys={clause_types_found}")
    record("General evidence queried", "general" in evidence_map, f"keys={clause_types_found}")

    for ct, chunks in evidence_map.items():
        print(f"    {ct}: {len(chunks)} chunks")
        if chunks:
            print(f"      Top: sim={chunks[0].similarity:.3f} id={chunks[0].contract_id}")

    return evidence_map


def test_kb_stats(rag: RAGService):
    """Verify KB stats are computed correctly."""
    print("\n=== TEST 5: KB Stats ===")
    stats = rag.get_kb_stats()

    record("num_contracts > 0", stats.num_contracts > 0, f"num_contracts={stats.num_contracts}")
    record("num_chunks > 0", stats.num_chunks > 0, f"num_chunks={stats.num_chunks}")

    print(f"  Contracts: {stats.num_contracts}")
    print(f"  Chunks: {stats.num_chunks}")
    if stats.clause_type_counts:
        print("  Clause type counts:")
        for ct, count in stats.clause_type_counts.items():
            print(f"    {ct}: {count}")
            if count > 0:
                record(f"clause_type {ct} has chunks", True)


def test_manifest_integrity():
    """Verify manifest.json matches processed files."""
    print("\n=== TEST 6: Manifest Integrity ===")
    manifest_path = settings.processed_dir / "manifest.json"
    record("Manifest exists", manifest_path.exists(), str(manifest_path))

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        files_dict = manifest.get("files", {})
        num_in_manifest = len(files_dict)
        record("Manifest has entries", num_in_manifest > 0, f"count={num_in_manifest}")
        print(f"  Manifest entries: {num_in_manifest}")

        # Check that each manifest entry has a matching processed JSON
        missing = 0
        for file_hash, entry in list(files_dict.items())[:5]:  # Check first 5
            cid = entry.get("contract_id", "")
            json_path = settings.processed_dir / f"{cid}.json"
            if not json_path.exists():
                missing += 1
                print(f"    MISSING: {cid}.json for {entry.get('filename', '?')}")

        record(
            "Processed JSONs match manifest (sampled 5)",
            missing == 0,
            f"{missing} missing",
        )


def test_market_data():
    """Verify market data loads correctly."""
    print("\n=== TEST 7: Market Data ===")
    from app.services.benchmark_service import BenchmarkService

    bench = BenchmarkService()
    df = bench._df
    record("Market DataFrame is non-empty", not df.empty, f"shape={df.shape if not df.empty else 'EMPTY'}")
    if not df.empty:
        print(f"  Records: {len(df)}")
        print(f"  Columns: {list(df.columns)[:10]}")

        # Test a benchmark query
        result = bench.compare_salary(
            ctc_inr=1200000,
            role="sde",
            yoe=1,
            company_type="product",
        )
        record(
            "Benchmark query returns percentile",
            result.percentile_salary is not None,
            f"percentile={result.percentile_salary}, warning={result.warning}",
        )
        if result.percentile_salary is not None:
            print(f"  Percentile for 12L SDE: {result.percentile_salary:.1f}%")
            print(f"  Cohort: {result.cohort_size}, Median: {result.market_median}")


if __name__ == "__main__":
    print("=" * 60)
    print("  FairDeal Comprehensive Test Suite")
    print("=" * 60)

    try:
        test_chroma_has_data()
        rag = test_rag_service_init()
        if rag.enabled:
            test_rag_queries(rag)
            test_evidence_service(rag)
            test_kb_stats(rag)
        else:
            print("\n  SKIPPING RAG tests - service is disabled")
        test_manifest_integrity()
        test_market_data()

    except Exception as e:
        print(f"\n  FATAL: {e}")
        import traceback
        traceback.print_exc()
        FAIL += 1

    print("\n" + "=" * 60)
    print(f"  Results: {PASS} PASSED, {FAIL} FAILED")
    if FAIL == 0:
        print("  ALL TESTS PASSED")
    else:
        print("  SOME TESTS FAILED - see details above")
    print("=" * 60)
    sys.exit(1 if FAIL > 0 else 0)
