
import sys
import os
from pathlib import Path
import json

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.psychological_scoring import PsychologicalScoringEngine

def run_scenarios():
    engine = PsychologicalScoringEngine()
    
    scenarios = [
        {
            "name": "Scenario A: Service-Based (Toxic)",
            "desc": "Low salary, 2y bond, 90d notice, 6d work week",
            "data": {
                'salary_percentile': 20.0,
                'notice_percentile': 95.0, # Very long notice
                'benefits_count': 5,
                'benefits_list': ['health_insurance', 'pf'],
                'non_compete': True,
                'non_compete_months': 12,
                'role_level': 'entry',
                'industry': 'tech',
                # Kwargs
                'salary_in_inr': 350000.0,
                'notice_period_days': 90,
                'training_bond': True,
                'training_bond_months': 24,
                'training_bond_amount': 200000,
                'has_provident_fund': True,
                'gratuity_status': 'absent', # Confirmed absent
                'working_hours_per_week': 48,
                'probation_months': 6
            }
        },
        {
            "name": "Scenario B: Product-Based (Ideal)",
            "desc": "High salary, no bond, 30d notice, good benefits",
            "data": {
                'salary_percentile': 85.0,
                'notice_percentile': 30.0, # Short notice
                'benefits_count': 12,
                'benefits_list': ['health_insurance', 'stock_options', 'pf', 'gratuity', 'remote_work'],
                'non_compete': False,
                'non_compete_months': 0,
                'role_level': 'mid',
                'industry': 'tech',
                # Kwargs
                'salary_in_inr': 2500000.0,
                'notice_period_days': 30,
                'training_bond': False,
                'training_bond_months': 0,
                'training_bond_amount': 0,
                'has_provident_fund': True,
                'gratuity_status': 'present',
                'working_hours_per_week': 40,
                'probation_months': 3
            }
        },
        {
            "name": "Scenario C: No Notice Period (Ambiguous)",
            "desc": "Notice info missing used, standard salary",
            "data": {
                'salary_percentile': 50.0,
                'notice_percentile': None, # Missing
                'benefits_count': 8,
                'benefits_list': ['pf', 'medical'],
                'non_compete': False,
                'non_compete_months': 0,
                'role_level': 'mid',
                'industry': 'tech',
                # Kwargs
                'salary_in_inr': 1200000.0,
                'notice_period_days': None,
                'has_provident_fund': True,
                'working_hours_per_week': 40
            }
        },
        {
            "name": "Scenario D: Zero Notice (Immediate)",
            "desc": "0 days notice (could be good or bad depending on context)",
            "data": {
                'salary_percentile': 60.0,
                'notice_percentile': 0.0,
                'benefits_count': 8,
                'benefits_list': ['pf'],
                'non_compete': False,
                'non_compete_months': 0,
                'role_level': 'senior',
                'industry': 'tech',
                # Kwargs
                'salary_in_inr': 1500000.0,
                'notice_period_days': 0,
                'has_provident_fund': True
            }
        },
        {
            "name": "Scenario E: Bond Edge Case",
            "desc": "High salary but 1y bond (Retention bonus?)",
            "data": {
                'salary_percentile': 90.0,
                'notice_percentile': 50.0,
                'benefits_count': 10,
                'benefits_list': ['pf', 'stocks'],
                'non_compete': True,
                'non_compete_months': 6,
                'role_level': 'mid',
                'industry': 'tech',
                # Kwargs
                'salary_in_inr': 3000000.0,
                'notice_period_days': 60,
                'training_bond': True,
                'training_bond_months': 12,
                'training_bond_amount': 1000000, # Huge bond
                'bond_justification': 'Signing Bonus', # Context check
                'has_provident_fund': True
            }
        }
    ]

    print(f"{'SCENARIO':<40} | {'SCORE':<5} | {'GRADE':<10} | {'VIOLATIONS'}")
    print("-" * 100)
    
    reports = []

    for sc in scenarios:
        result = engine.compute_score(**sc['data'])
        
        # Format output
        violations_str = ", ".join([v.split(':')[0] for v in result.legal_violations]) if result.legal_violations else "None"
        print(f"{sc['name']:<40} | {result.score:<5} | {result.grade:<10} | {violations_str[:40]}...")
        
        # Store comprehensive report
        reports.append({
            "scenario": sc['name'],
            "description": sc['desc'],
            "score": result.score,
            "grade": result.grade,
            "breakdown": result.breakdown,
            "violations": result.legal_violations,
            "risk_factors": result.risk_factors,
            "badges": result.badges
        })

    # Save detailed report to JSON for analysis
    with open("scoring_report.json", "w") as f:
        json.dump(reports, f, indent=2)
    print("\nDetailed report saved to scoring_report.json")

if __name__ == "__main__":
    run_scenarios()
