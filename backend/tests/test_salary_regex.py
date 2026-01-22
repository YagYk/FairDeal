
import sys
import os
from pathlib import Path

# Add backend to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.rule_extraction_service import RuleExtractionService
from app.services.parser_service import ParsedDocument, PageText

def test_salary_regex():
    service = RuleExtractionService()
    
    test_cases = [
        # New pattern: Suffix
        ("Salary is 18,00,000 INR", 1800000.0),
        ("CTC is 15,00,000 INR", 1500000.0),
        
        # New pattern: Contextual
        ("The fixed Salary is 12,00,000", 1200000.0), # Assuming this matches the contextual pattern
        
        # Existing widespread patterns
        ("Total CTC: ₹20,00,000", 2000000.0),
        ("Annual CTC Rs. 2400000", 2400000.0),
        ("Offered CTC: 10 LPA", 1000000.0),
        
        # Monthly
        ("Salary: ₹50,000 per month", 600000.0),
        
        # Edge cases
        ("Gratuity limit is 20,00,000", None), # Should be ignored
    ]
    
    print(f"{'TEST INPUT':<40} | {'EXPECTED':<12} | {'ACTUAL':<12} | {'STATUS'}")
    print("-" * 80)
    
    passed = 0
    for text, expected in test_cases:
        # Mock logic directly or via private method if necessary, 
        # but _extract_ctc_logic is what we want to test.
        # It returns (value, source_text)
        
        val, source = service._extract_ctc_logic(text)
        
        status = "PASS" if val == expected else "FAIL"
        if val == expected:
            passed += 1
            
        # Sanitize for Windows console
        safe_text = text.encode('ascii', 'replace').decode()
        print(f"{safe_text:<40} | {str(expected):<12} | {str(val):<12} | {status}")

    print("-" * 80)
    print(f"Total Passed: {passed}/{len(test_cases)}")

if __name__ == "__main__":
    test_salary_regex()
