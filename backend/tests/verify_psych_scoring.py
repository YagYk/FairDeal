
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

# Force utf-8 for Windows console
sys.stdout.reconfigure(encoding='utf-8')

from app.services.psychological_scoring import PsychologicalScoringEngine

def verify_scoring():
    scorer = PsychologicalScoringEngine()
    print(f"Verifying Psychological Scoring Engine v{scorer.version}...\n")

    # ---------------------------------------------------------
    # Example 1: Amazon SDE-2
    # ---------------------------------------------------------
    print("--- Amazon SDE-2 Test ---")
    amazon_data = {
        "salary_percentile": 57,
        "notice_percentile": 17,
        "benefits_count": 5,
        "benefits_list": ["health insurance", "provident fund", "gratuity", "paid leave", "bonus"],
        "non_compete": True,
        "non_compete_months": 6,
        "role_level": "mid",
        "industry": "tech",
        # Kwargs
        "salary_in_inr": 1800000,
        "notice_period_days": 30,
        "training_bond": False,
        "has_provident_fund": True,
        "mentions_gratuity": True
    }
    
    res1 = scorer.compute_score(**amazon_data)
    print(f"Score: {res1.score} ({res1.grade})")
    print(f"Breakdown: {res1.breakdown}")
    print(f"Badges: {res1.badges}")
    print(f"Risks: {res1.risk_factors}")
    
    # Expected: ~87, Excellent
    if 86 <= res1.score <= 88:
        print("✅ Amazon SDE-2 Passed")
    else:
        print(f"❌ Amazon SDE-2 Failed. Expected ~87, got {res1.score}")
    print("\n")

    # ---------------------------------------------------------
    # Example 2: Google L4 (Unicorn)
    # ---------------------------------------------------------
    print("--- Google L4 Test ---")
    google_data = {
        "salary_percentile": 92, # > 80
        "notice_percentile": 35, # Wait, user example said 35th percentile is good? 
                                 # User Logic: "Notice: 45 days (35th percentile) ✓"
                                 # Unicorn condition: notice_percentile <= 20. 
                                 # 35 is > 20, so technically not Unicorn by strict definition in code?
                                 # Let's adjust input to match the Unicorn condition (<= 20) if we want to test Unicorn Badge,
                                 # OR check if 35 yields Unicorn.
                                 # Code: if s_p >= 80 and n_p <= 20 ... -> Unicorn. 
                                 # So 35 won't trigger Unicorn badge in my code unless I change input.
                                 # Let's use user's exact input first.
        "benefits_count": 7,
        "benefits_list": ["health", "pf", "gratuity", "leave", "equity", "gym", "food"],
        "non_compete": False,
        "non_compete_months": 0,
        "role_level": "mid", # L4 is mid
        "industry": "tech",
        "salary_in_inr": 2800000,
        "notice_period_days": 45,
        "has_equity": True,
        "has_provident_fund": True,
        "mentions_gratuity": True
    }
    
    res2 = scorer.compute_score(**google_data)
    print(f"Score: {res2.score} ({res2.grade})")
    print(f"Badges: {res2.badges}")
    
    # ---------------------------------------------------------
    # Example 3: Infosys Trainee (Toxic/Poor)
    # ---------------------------------------------------------
    print("--- Infosys Trainee Test ---")
    infosys_data = {
        "salary_percentile": 18,
        "notice_percentile": 88,
        "benefits_count": 2,
        "benefits_list": ["pf", "health"],
        "non_compete": False,
        "non_compete_months": 0,
        "role_level": "entry",
        "industry": "service",
        "salary_in_inr": 350000,
        "notice_period_days": 90,
        "training_bond": True,
        "training_bond_amount": 150000,
        "training_bond_months": 24,
        "has_provident_fund": True,
        "mentions_gratuity": False # "Missing gratuity clause" in user ex
    }
    
    res3 = scorer.compute_score(**infosys_data)
    print(f"Score: {res3.score} ({res3.grade})")
    print(f"Badges: {res3.badges}")
    print(f"Risks: {res3.risk_factors}")
    print(f"Violations: {res3.legal_violations}")

if __name__ == "__main__":
    verify_scoring()
