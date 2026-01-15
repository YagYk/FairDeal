"""
Quick verification script to check the setup is working.
Run with: python verify_setup.py
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))


def check_imports():
    """Check all new modules can be imported."""
    print("Checking imports...")
    
    try:
        from app.models.schemas import AnalysisResult, RedFlag, CohortInfo
        print("  ✓ schemas.py")
    except ImportError as e:
        print(f"  ✗ schemas.py: {e}")
        return False
    
    try:
        from app.services.scoring_engine import ScoringEngine
        print("  ✓ scoring_engine.py")
    except ImportError as e:
        print(f"  ✗ scoring_engine.py: {e}")
        return False
    
    try:
        from app.services.stats_service_v2 import StatsServiceV2
        print("  ✓ stats_service_v2.py")
    except ImportError as e:
        print(f"  ✗ stats_service_v2.py: {e}")
        return False
    
    try:
        from app.services.clause_matcher_v2 import ClauseMatcherV2
        print("  ✓ clause_matcher_v2.py")
    except ImportError as e:
        print(f"  ✗ clause_matcher_v2.py: {e}")
        return False
    
    try:
        from app.services.analysis_service_v2 import AnalysisServiceV2
        print("  ✓ analysis_service_v2.py")
    except ImportError as e:
        print(f"  ✗ analysis_service_v2.py: {e}")
        return False
    
    try:
        from app.api.kb_admin import router as kb_router
        print("  ✓ kb_admin.py")
    except ImportError as e:
        print(f"  ✗ kb_admin.py: {e}")
        return False
    
    try:
        from app.api.analyze import router as analyze_router
        print("  ✓ analyze.py")
    except ImportError as e:
        print(f"  ✗ analyze.py: {e}")
        return False
    
    return True


def check_scoring_formula():
    """Verify the scoring formula works correctly."""
    print("\nTesting scoring formula...")
    
    from app.services.scoring_engine import ScoringEngine
    
    engine = ScoringEngine()
    
    # Test case: 60% salary, 40% notice, 1 flag, 3 benefits
    score, confidence, formula = engine.compute_score(
        salary_percentile=60,
        notice_percentile=40,
        red_flags_count=1,
        favorable_terms_count=1,
        non_compete=False,
        cohort_size=50,
        extraction_confidence=0.9,
        benefits_count=3,  # Good benefits
    )
    
    print(f"  Input: salary=60%, notice=40%, flags=1, favorable=1, benefits=3")
    print(f"  Score: {score}/100")
    print(f"  Confidence: {confidence}")
    print(f"  Formula: {formula[:80]}...")
    
    # Expected: 50 + 0.4*(60-50) + 0.3*(50-40) - 0.3*(1*5) + 3 + 5 = 50 + 4 + 3 - 1.5 + 3 + 5 = 63.5 → 64
    expected_range = (60, 68)
    if expected_range[0] <= score <= expected_range[1]:
        print(f"  ✓ Score {score} is in expected range {expected_range}")
        return True
    else:
        print(f"  ✗ Score {score} is NOT in expected range {expected_range}")
        return False


def check_clause_matcher():
    """Verify clause matcher produces expected flags."""
    print("\nTesting clause matcher...")
    
    from app.services.clause_matcher_v2 import ClauseMatcherV2
    
    matcher = ClauseMatcherV2()
    
    # Test: low salary, long notice, non-compete
    red_flags, favorable, negotiation = matcher.match_clauses(
        salary_percentile=15,
        notice_percentile=85,
        salary_value=500000,
        notice_value=90,
        non_compete=True,
        benefits=["health insurance"],
    )
    
    print(f"  Input: salary=15%, notice=85%, non_compete=True, benefits=1")
    print(f"  Red flags: {len(red_flags)}")
    print(f"  Favorable: {len(favorable)}")
    print(f"  Negotiation points: {len(negotiation)}")
    
    # Should have at least 3 red flags: low salary, long notice, non-compete
    if len(red_flags) >= 3:
        print(f"  ✓ Expected at least 3 red flags, got {len(red_flags)}")
        for flag in red_flags[:3]:
            print(f"    - {flag.id}: {flag.severity}")
        return True
    else:
        print(f"  ✗ Expected at least 3 red flags, got {len(red_flags)}")
        return False


def check_config():
    """Check configuration is loaded."""
    print("\nChecking configuration...")
    
    from app.config import settings
    
    print(f"  ChromaDB path: {settings.get_chroma_db_path()}")
    print(f"  Processed path: {settings.get_processed_contracts_path()}")
    
    if settings.google_api_key:
        print(f"  ✓ Google API key is set")
    else:
        print(f"  ⚠ Google API key is NOT set (embeddings will fail)")
    
    return True


def main():
    """Run all checks."""
    print("=" * 60)
    print("FAIRDEAL V2 - SETUP VERIFICATION")
    print("=" * 60)
    
    all_passed = True
    
    if not check_imports():
        all_passed = False
    
    if not check_scoring_formula():
        all_passed = False
    
    if not check_clause_matcher():
        all_passed = False
    
    check_config()
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL CHECKS PASSED")
    else:
        print("✗ SOME CHECKS FAILED")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
