"""
Full API Integration Test.

Tests the /api/analyze endpoint with a realistic mock contract and validates:
1. Response is 200 with valid JSON
2. All required fields are present
3. Scoring produces a valid grade
4. RAG evidence is returned (non-empty)
5. Red flags and favorable terms are generated
6. Benchmarking produces percentiles
7. Caching works (second identical upload returns cache hit)
8. Extraction handles salary correctly (sanity check)

Run from backend/:
    python -m tests.test_full_api
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

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


# Realistic mock contract text
MOCK_CONTRACT = """
OFFER OF EMPLOYMENT

Dear Candidate,

We are pleased to offer you the position of Software Development Engineer at TechCorp Private Limited, 
Bangalore, India.

1. COMPENSATION
Your total annual Cost to Company (CTC) shall be Rs. 18,00,000/- (Eighteen Lakhs Only) per annum.
The breakup is as follows:
- Basic Salary: Rs. 9,00,000 per annum
- HRA: Rs. 3,60,000 per annum
- Special Allowance: Rs. 3,40,000 per annum
- Performance Bonus: Up to Rs. 2,00,000 per annum (variable)

2. NOTICE PERIOD
Either party may terminate this employment by providing 60 (sixty) days written notice or 
salary in lieu thereof.

3. PROBATION PERIOD
You will be on probation for a period of 6 (six) months from the date of joining.

4. CONFIDENTIALITY
You shall maintain strict confidentiality regarding all proprietary information, trade secrets,
and business processes of the Company during and after your employment.

5. NON-COMPETE
For a period of 12 months following the termination of your employment, you shall not directly
or indirectly engage with any competitor of the Company.

6. TRAINING BOND
In the event of resignation within 2 years from the date of joining, you shall be liable to pay
Rs. 1,00,000/- (One Lakh Only) as training costs.

7. BENEFITS
- Health Insurance (self + family)
- Provident Fund as per statutory requirements
- Gratuity as per the Payment of Gratuity Act
- 24 days of paid leave per annum
- Internet/broadband allowance for WFH

8. INTELLECTUAL PROPERTY
All inventions, designs, and works created during the course of your employment shall be the
exclusive property of the Company.

Please sign and return this letter to confirm your acceptance.

Regards,
HR Department
TechCorp Private Limited
""".strip()


def make_request(content: bytes = MOCK_CONTRACT.encode(), filename: str = "test_offer.txt"):
    context = {
        "role": "sde",
        "experience_level": 2,
        "company_type": "product",
        "industry": "tech",
        "location": "bangalore",
    }
    files = {"file": (filename, content, "text/plain")}
    data = {"context": json.dumps(context)}
    return client.post("/api/analyze", files=files, data=data)


def test_basic_response():
    """Test that /api/analyze returns 200 with valid structure."""
    print("\n=== TEST 1: Basic API Response ===")
    resp = make_request()
    record("Status 200", resp.status_code == 200, f"got {resp.status_code}: {resp.text[:200]}")
    if resp.status_code != 200:
        return None

    data = resp.json()
    record("Response is dict", isinstance(data, dict), type(data).__name__)
    return data


def test_required_fields(data: dict):
    """Test all required top-level fields exist."""
    print("\n=== TEST 2: Required Fields ===")
    required = [
        "extraction", "contract_metadata", "score", "grade", "scoring",
        "percentiles", "red_flags", "favorable_terms", "negotiation_points",
        "rag", "evidence", "timings", "cache", "determinism",
    ]
    for field in required:
        record(f"Field '{field}' present", field in data, f"missing from response")


def test_extraction(data: dict):
    """Test extraction results are reasonable."""
    print("\n=== TEST 3: Extraction Quality ===")
    ext = data.get("extraction", {})

    # Salary
    ctc = ext.get("ctc_inr")
    if ctc:
        val = ctc.get("value")
        record("Salary extracted", val is not None, "value is None")
        if val:
            record("Salary is numeric", isinstance(val, (int, float)), f"type={type(val).__name__}")
            record("Salary in sane range (1L-10Cr)", 100000 <= val <= 100000000, f"value={val}")
            print(f"    Extracted CTC: {val}")
    else:
        record("Salary extracted", False, "ctc_inr is None/missing")

    # Notice
    notice = ext.get("notice_period_days")
    if notice and notice.get("value"):
        val = notice["value"]
        record("Notice period in range", 1 <= val <= 365, f"value={val}")
        print(f"    Notice: {val} days")

    # Bond
    bond = ext.get("bond_amount_inr")
    if bond and bond.get("value"):
        print(f"    Bond: {bond['value']}")

    # Benefits
    benefits = ext.get("benefits", [])
    count = ext.get("benefits_count", 0)
    record("Benefits detected", count > 0, f"count={count}")
    print(f"    Benefits ({count}): {benefits}")

    # Extracted clauses
    clauses = ext.get("extracted_clauses", {})
    record("At least 1 clause extracted", len(clauses) > 0, f"clauses={list(clauses.keys())}")
    print(f"    Clause types: {list(clauses.keys())}")


def test_scoring(data: dict):
    """Test scoring produces valid results."""
    print("\n=== TEST 4: Scoring ===")
    score = data.get("score", -1)
    grade = data.get("grade", "")
    scoring = data.get("scoring", {})

    record("Score is number", isinstance(score, (int, float)), f"type={type(score).__name__}")
    record("Score in 0-100", 0 <= score <= 100, f"score={score}")
    record("Grade is non-empty", bool(grade), f"grade='{grade}'")
    print(f"    Score: {score}, Grade: {grade}")

    # Breakdown
    breakdown = scoring.get("breakdown", [])
    record("Breakdown has items", len(breakdown) > 0, f"count={len(breakdown)}")

    # Badges
    badges = scoring.get("badges", [])
    print(f"    Badges: {badges}")
    risk_factors = scoring.get("risk_factors", [])
    print(f"    Risk factors: {risk_factors}")


def test_benchmarking(data: dict):
    """Test benchmark/percentile data."""
    print("\n=== TEST 5: Benchmarking ===")
    benchmark = data.get("benchmark")
    percentiles = data.get("percentiles", {})

    record("Benchmark present", benchmark is not None, "benchmark is null")
    if benchmark:
        pctile = benchmark.get("percentile_salary")
        record("Salary percentile computed", pctile is not None, "percentile_salary is null")
        if pctile is not None:
            record("Percentile in 0-100", 0 <= pctile <= 100, f"value={pctile}")
            print(f"    Salary percentile: {pctile:.1f}%")
            print(f"    Cohort: {benchmark.get('cohort_size')} records")
            print(f"    Market median: {benchmark.get('market_median')}")

    record("Percentiles dict has entries", len(percentiles) > 0, f"keys={list(percentiles.keys())}")


def test_red_flags_and_favorable(data: dict):
    """Test intelligence generation."""
    print("\n=== TEST 6: Red Flags & Favorable Terms ===")
    red_flags = data.get("red_flags", [])
    favorable = data.get("favorable_terms", [])
    negotiation = data.get("negotiation_points", [])

    # The mock contract has non-compete, bond, and 60-day notice, so there should be red flags
    record("Red flags generated", len(red_flags) > 0, f"count={len(red_flags)}")
    print(f"    Red flags: {len(red_flags)}")
    for rf in red_flags[:3]:
        print(f"      [{rf.get('severity')}] {rf.get('rule')}")

    print(f"    Favorable terms: {len(favorable)}")
    for ft in favorable[:3]:
        print(f"      {ft.get('term')}")

    record("Negotiation points generated", len(negotiation) > 0, f"count={len(negotiation)}")
    print(f"    Negotiation points: {len(negotiation)}")


def test_rag_evidence(data: dict):
    """Test that RAG evidence is returned from the KB."""
    print("\n=== TEST 7: RAG Evidence ===")
    evidence = data.get("evidence", [])
    rag = data.get("rag", {})
    evidence_by_type = rag.get("evidence_by_clause_type", {})

    record("Evidence list non-empty", len(evidence) > 0, f"count={len(evidence)}")
    record("Evidence by clause type non-empty", len(evidence_by_type) > 0, f"keys={list(evidence_by_type.keys())}")

    print(f"    Total evidence chunks: {len(evidence)}")
    print(f"    Clause types with evidence: {list(evidence_by_type.keys())}")

    for ctype, chunks in evidence_by_type.items():
        print(f"      {ctype}: {len(chunks)} chunks")
        if chunks:
            top = chunks[0]
            print(f"        Top: sim={top.get('similarity', 0):.3f} file={top.get('metadata', {}).get('filename', '?')[:40]}")

    # Check that at least compensation or general is present
    has_extra = "compensation" in evidence_by_type or "general" in evidence_by_type
    record("Compensation or general evidence present", has_extra, f"keys={list(evidence_by_type.keys())}")


def test_timings(data: dict):
    """Test timing metadata."""
    print("\n=== TEST 8: Timings ===")
    timings = data.get("timings", {})
    total = timings.get("total_ms", 0)
    record("Total time > 0", total > 0, f"total_ms={total}")
    record("Total time < 120s", total < 120000, f"total_ms={total} (>2 minutes!)")

    print(f"    Parse: {timings.get('parse_ms', 0):.0f}ms")
    print(f"    Extract: {timings.get('extract_ms', 0):.0f}ms")
    print(f"    Benchmark: {timings.get('benchmark_ms', 0):.0f}ms")
    print(f"    RAG: {timings.get('rag_ms', 0):.0f}ms")
    print(f"    Scoring: {timings.get('scoring_ms', 0):.0f}ms")
    print(f"    Narration: {timings.get('narration_ms', 0):.0f}ms")
    print(f"    TOTAL: {total:.0f}ms")


def test_cache():
    """Test that second identical upload hits cache."""
    print("\n=== TEST 9: Cache ===")
    # First request (might be cached from test 1)
    resp1 = make_request()
    record("First request 200", resp1.status_code == 200, f"got {resp1.status_code}")

    # Second identical request should hit cache
    resp2 = make_request()
    record("Second request 200", resp2.status_code == 200, f"got {resp2.status_code}")

    if resp2.status_code == 200:
        data2 = resp2.json()
        cache = data2.get("cache", {})
        record("Cache hit on duplicate", cache.get("hit") is True, f"cache={cache}")
        print(f"    Cache info: {cache}")


def test_determinism(data: dict):
    """Test determinism metadata."""
    print("\n=== TEST 10: Determinism Info ===")
    det = data.get("determinism", {})
    record("Scoring is deterministic", det.get("scoring") == "deterministic", f"scoring={det.get('scoring')}")
    record("Extraction method reported", det.get("extraction") in ("deterministic", "hybrid"), f"extraction={det.get('extraction')}")
    print(f"    Determinism: {det}")


if __name__ == "__main__":
    print("=" * 60)
    print("  FairDeal Full API Integration Test")
    print("=" * 60)

    try:
        data = test_basic_response()
        if data:
            test_required_fields(data)
            test_extraction(data)
            test_scoring(data)
            test_benchmarking(data)
            test_red_flags_and_favorable(data)
            test_rag_evidence(data)
            test_timings(data)
            test_cache()
            test_determinism(data)
        else:
            print("\n  ABORTING: Could not get valid response from API")

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
