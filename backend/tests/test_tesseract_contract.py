
import sys
import os
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.psychological_scoring import PsychologicalScoringEngine

def test_tesseract_contract():
    engine = PsychologicalScoringEngine()
    
    # Extracted data based on user text
    data = {
        'salary_percentile': 50.0, # 10LPA is roughly median for 0-2y
        'notice_percentile': 95.0, # 90 days is very long
        'benefits_count': 7, # PF, Gratuity, GHI, GPAI, GTLI, HRA, LTA
        'benefits_list': ['pf', 'gratuity', 'health_insurance', 'accident_insurance', 'life_insurance'],
        'non_compete': True,
        'non_compete_months': 36, # 3 years!
        'role_level': 'entry',
        'industry': 'tech',
        # Kwargs
        'salary_in_inr': 1000000.0,
        'notice_period_days': 90,
        'has_provident_fund': True,
        'gratuity_status': 'present',
        'probation_months': 3,
        'working_hours_per_week': 45, # 9 hours/day * 5 days assumed
        # "Backout Penalty" isn't standard in our current extraction, but "Recovery" is like a bond
        'training_bond': True, # Treating the 1 year recovery as a bond for scoring purpose
        'training_bond_months': 12,
        'training_bond_amount': 0, # Amount is "all expenses", undefined number, but the clause exists
        'has_legal_violations': False 
    }

    print(f"\nAnalyzing Contract: Tesseract Imaging (SDE)")
    print("-" * 50)
    
    result = engine.compute_score(**data)
    
    print(f"Final Score: {result.score}")
    print(f"Grade: {result.grade}")
    print(f"Multipliers applied: {result.multiplier}")
    print(f"Badges: {result.badges}")
    print("\nViolations/Risks:")
    for v in result.legal_violations:
        print(f"- [Legal] {v}")
    for r in result.risk_factors:
        print(f"- [Risk] {r}")
        
    print("\nBreakdown:")
    for k, v in result.breakdown.items():
        print(f"{k.capitalize()}: {v['score']:.1f} (Weight: {v['weight']:.2f})")

if __name__ == "__main__":
    test_tesseract_contract()
