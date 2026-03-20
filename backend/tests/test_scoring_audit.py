"""
Scoring Engine Audit Test
Verifies the PsychologicalScoringEngine produces sensible scores for different contract types.
Run: python -m pytest backend/tests/test_scoring_audit.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.psychological_scoring import PsychologicalScoringEngine


def test_score_ranges():
    """All scores must be in [0, 100]"""
    engine = PsychologicalScoringEngine()
    
    test_cases = [
        # (name, salary_pct, notice_pct, ben_count, benefits, nc, nc_months, role, industry, kwargs)
        ("Perfect contract", 95.0, 5.0, 8, ["health", "equity", "pf", "gratuity", "esop"], False, 0, "entry", "tech",
         {"pf_status": "present", "gratuity_status": "present"}),
        ("Terrible contract", 2.0, 98.0, 0, [], True, 24, "entry", "tech",
         {"training_bond": True, "training_bond_months": 36, "training_bond_amount": 500000,
          "notice_period_days": 120, "pf_status": "absent", "gratuity_status": "absent"}),
        ("Average service company", 30.0, 60.0, 4, ["health", "pf"], False, 0, "entry", "tech",
         {"pf_status": "present", "gratuity_status": "unknown", "notice_period_days": 90}),
        ("Good product company", 75.0, 25.0, 6, ["health", "equity", "pf", "gratuity"], False, 0, "mid", "tech",
         {"pf_status": "present", "gratuity_status": "present", "notice_period_days": 60}),
        ("No data at all", None, None, 0, [], False, 0, "entry", "tech",
         {"pf_status": "unknown", "gratuity_status": "unknown"}),
        ("Only salary extracted", 50.0, None, 0, [], False, 0, "entry", "tech",
         {"pf_status": "unknown", "gratuity_status": "unknown"}),
    ]
    
    print("\n" + "="*80)
    print("SCORING ENGINE AUDIT")
    print("="*80)
    
    for name, sal, not_pct, ben_cnt, benefits, nc, nc_mo, role, ind, kwargs in test_cases:
        result = engine.compute_score(
            salary_percentile=sal,
            notice_percentile=not_pct,
            benefits_count=ben_cnt,
            benefits_list=benefits,
            non_compete=nc,
            non_compete_months=nc_mo,
            role_level=role,
            industry=ind,
            **kwargs
        )
        
        print(f"\n{'─'*60}")
        print(f"  {name}")
        print(f"  Score: {result.score}/100 ({result.grade})")
        print(f"  Confidence: {result.confidence:.0%}")
        print(f"  Raw: {result.raw_score} × {result.multiplier} → calibrated: {result.score}")
        if result.badges:
            print(f"  Badges: {', '.join(result.badges)}")
        if result.risk_factors:
            print(f"  Risks: {', '.join(result.risk_factors)}")
        if result.legal_violations:
            print(f"  Legal: {', '.join(result.legal_violations)}")
        for k, v in result.breakdown.items():
            print(f"    {k:12s}: {v['score']:5.1f}/100 (weight: {v['weight']:.0%})")
        
        # Assertions
        assert 0 <= result.score <= 100, f"{name}: score {result.score} out of bounds!"
        assert 0 < result.confidence <= 1.0, f"{name}: confidence {result.confidence} out of bounds!"
        
        # Check weight sum
        total_weight = sum(v['weight'] for v in result.breakdown.values())
        assert abs(total_weight - 1.0) < 0.01, f"{name}: weights sum to {total_weight}, expected 1.0!"
    
    print(f"\n{'='*80}")
    print("  ALL ASSERTIONS PASSED")
    print(f"{'='*80}\n")


def test_score_ordering():
    """Better contracts should score higher than worse ones"""
    engine = PsychologicalScoringEngine()
    
    good = engine.compute_score(
        salary_percentile=80.0, notice_percentile=20.0,
        benefits_count=6, benefits_list=["health", "equity", "pf", "gratuity"],
        non_compete=False, non_compete_months=0,
        role_level="mid", industry="tech",
        pf_status="present", gratuity_status="present", notice_period_days=30
    )
    
    bad = engine.compute_score(
        salary_percentile=10.0, notice_percentile=85.0,
        benefits_count=1, benefits_list=["health"],
        non_compete=True, non_compete_months=18,
        role_level="entry", industry="tech",
        training_bond=True, training_bond_months=24, training_bond_amount=200000,
        pf_status="absent", gratuity_status="absent", notice_period_days=90
    )
    
    print(f"\n  Good contract: {good.score}/100 ({good.grade})")
    print(f"  Bad contract:  {bad.score}/100 ({bad.grade})")
    assert good.score > bad.score, f"Good ({good.score}) should score higher than bad ({bad.score})!"
    assert good.score >= 70, f"Good contract should be at least 70, got {good.score}"
    assert bad.score <= 50, f"Bad contract should be at most 50, got {bad.score}"
    print("  Score ordering: CORRECT")


def test_no_data_penalty():
    """Contract with no data should NOT be penalized heavily — just neutral"""
    engine = PsychologicalScoringEngine()
    
    result = engine.compute_score(
        salary_percentile=None, notice_percentile=None,
        benefits_count=0, benefits_list=[],
        non_compete=False, non_compete_months=0,
        role_level="entry", industry="tech",
        pf_status="unknown", gratuity_status="unknown"
    )
    
    print(f"\n  No-data contract: {result.score}/100 ({result.grade})")
    print(f"  Confidence: {result.confidence:.0%}")
    # Should be around neutral (40-60), not unfairly penalized
    assert 35 <= result.score <= 65, f"No-data score should be neutral (35-65), got {result.score}"
    # Confidence should be low since we have no data
    assert result.confidence <= 0.60, f"No-data confidence should be low, got {result.confidence}"
    print("  No-data neutrality: CORRECT")


if __name__ == "__main__":
    test_score_ranges()
    test_score_ordering()
    test_no_data_penalty()
    print("\n✅ ALL AUDIT TESTS PASSED\n")
