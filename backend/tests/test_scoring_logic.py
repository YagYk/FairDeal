
import sys
import os
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.psychological_scoring import PsychologicalScoringEngine

def test_scoring_logic():
    engine = PsychologicalScoringEngine()
    
    # Test Case 1: High Salary (25LPA), No PF, No Gratuity
    # Current behavior: 
    # - Salary > 21LPA -> No PF penalty (logic is < 2100000)
    # - No Gratuity -> Penalty -15
    print("\n--- Test Case 1: 25 LPA, No PF, No Gratuity ---")
    data_1 = {
        'salary_in_inr': 2500000.0,
        'has_provident_fund': False,
        'mentions_gratuity': False,
        'notice_period_days': 30
    }
    score_1, violations_1 = engine._score_legal_compliance(data_1)
    print(f"Score: {score_1}")
    print(f"Violations: {violations_1}")
    
    # Test Case 2: Mid Salary (18LPA), No PF, No Gratuity
    # Current behavior:
    # - Salary < 21LPA -> PF Penalty -25
    # - No Gratuity -> Penalty -15
    print("\n--- Test Case 2: 18 LPA, No PF, No Gratuity ---")
    data_2 = {
        'salary_in_inr': 1800000.0,
        'has_provident_fund': False,
        'mentions_gratuity': False,
        'notice_period_days': 30
    }
    score_2, violations_2 = engine._score_legal_compliance(data_2)
    print(f"Score: {score_2}")
    print(f"Violations: {violations_2}")
    
    # Test Case 3: Confirmed Absence (Hypothetical)
    # If we implement 'gratuity_status': 'absent'
    print("\n--- Test Case 3: Gratuity confirmed absent ---")
    data_3 = {
        'salary_in_inr': 2500000.0,
        'mentions_gratuity': False,
        'gratuity_status': 'absent'
    }
    # Currently this key isn't used, but we'll implement it
    score_3, violations_3 = engine._score_legal_compliance(data_3)
    print(f"Score: {score_3}")
    print(f"Violations: {violations_3}")

if __name__ == "__main__":
    test_scoring_logic()
