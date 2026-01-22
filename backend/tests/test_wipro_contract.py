
import sys
import os
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.psychological_scoring import PsychologicalScoringEngine

def test_wipro_contract():
    engine = PsychologicalScoringEngine()
    
    # Contract Details (Wipro Project Engineer)
    # This is a classic "Service-Based" entry profile.
    data = {
        'salary_percentile': 25.0, # 3.5 LPA is lower end of market
        'notice_percentile': 95.0, # 90 days is very long
        'benefits_count': 8,
        'benefits_list': ['health_insurance', 'pf', 'gratuity'],
        'non_compete': True,
        'non_compete_months': 6,
        'role_level': 'entry',
        'industry': 'service', # Important context
        # Kwargs
        'salary_in_inr': 350004.0,
        'notice_period_days': 90,
        'has_provident_fund': True,
        'gratuity_status': 'present',
        'probation_months': 12, # Assuming probation matches bond occasionally, or standard 6
        'working_hours_per_week': 45,
        'training_bond': True,
        'training_bond_months': 12,
        'training_bond_amount': 75000,
        'has_legal_violations': False 
    }

    print(f"\nAnalyzing Contract: Wipro (Project Engineer)")
    print("-" * 50)
    
    result = engine.compute_score(**data)
    
    print(f"Final Score: {result.score}")
    print(f"Grade: {result.grade}")
    print(f"Multipliers applied: {result.multiplier:.2f}")
    print(f"Badges: {[b.encode('ascii', 'replace').decode() for b in result.badges]}")
    print("\nViolations/Risks:")
    for v in result.legal_violations:
        print(f"- [Legal] {v}")
    for r in result.risk_factors:
        print(f"- [Risk] {r}")
        
    print("\nBreakdown:")
    for k, v in result.breakdown.items():
        print(f"{k.capitalize()}: {v['score']:.1f} (Weight: {v['weight']:.2f})")

if __name__ == "__main__":
    test_wipro_contract()
