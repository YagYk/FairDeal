
import sys
import os
from pathlib import Path
import json

sys.path.append(str(Path(__file__).parent.parent))

from app.services.benchmark_service import BenchmarkService

def test_benchmark_failures():
    service = BenchmarkService()
    
    print("--- Test 1: Unknown Role ---")
    # "Underwater Basket Weaver" likely doesn't exist in our tech-focused dataset
    result = service.compare_salary(
        ctc_inr=1000000,
        role="Underwater Basket Weaver",
        yoe=5,
        company_type="product",
        location="Atlantis"
    )
    print(f"Result for Unknown Role: {result}")
    
    print("\n--- Test 2: Low Data Cohort ---")
    # "CEO" in "Mars" might exist but have < 5 records
    result = service.compare_salary(
        ctc_inr=5000000,
        role="CEO",
        yoe=15,
        company_type="startup",
        location="Mars"
    )
    print(f"Result for Low Data: {result}")

    # Verify result structure safety
    if result.percentile_salary is None:
        print("\n[SUCCESS] Graceful degradation: percentile_salary is None as expected.")
    else:
        print(f"\n❓ Percentile found: {result.percentile_salary}")

if __name__ == "__main__":
    test_benchmark_failures()
