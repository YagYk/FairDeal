
import argparse
import requests
import json
import os
import sys
from pathlib import Path

# Configuration
API_URL = "http://localhost:8000/api/analyze"

def analyze_contract(file_path: str, role: str, yoe: float, company_type: str):
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File not found at {file_path}")
        return

    print(f"--- Analyzing Contract: {path.name} ---")
    print(f"Role: {role} | Exp: {yoe} YOE | Type: {company_type}")
    print("Sending request to backend...")

    try:
        # Prepare valid context
        context = {
            "role": role,
            "experience_level": yoe,
            "company_type": company_type,
            "location": "Bangalore", # Default
            "industry": "tech"      # Default
        }

        with open(path, 'rb') as f:
            files = {'file': (path.name, f, 'application/pdf')}
            data = {'context': json.dumps(context)}
            
            response = requests.post(API_URL, files=files, data=data)

        if response.status_code == 200:
            result = response.json()
            display_results(result)
            
            # Save full JSON for inspection
            output_file = f"analysis_result_{path.stem}.json"
            with open(output_file, 'w') as out:
                json.dump(result, out, indent=2)
            print(f"\nFull JSON result saved to: {output_file}")
            
        else:
            print(f"\n[!] Analysis Failed (Status: {response.status_code})")
            try:
                print("Error Details:", response.json())
            except:
                print("Raw Response:", response.text)

    except requests.exceptions.ConnectionError:
        print("\n[!] Could not connect to backend server.")
        print("    Is it running? (Try: python -m uvicorn app.main:app ...)")
    except Exception as e:
        print(f"\n[!] An error occurred: {e}")

def display_results(data):
    print("\n" + "="*60)
    print(f" ANALYSIS RESULTS ")
    print("="*60)
    
    # Extraction Summary
    ext = data.get("extraction", {})
    ctc = ext.get("ctc_inr", {}).get("value")
    notice = ext.get("notice_period_days", {}).get("value")
    
    print(f"\n[EXTRACTION]")
    print(f"  • CTC:         ₹{ctc:,.0f}" if ctc else "  • CTC:         Not found")
    print(f"  • Notice:      {notice} days" if notice else "  • Notice:      Not found")
    
    # Scoring
    score = data.get("score")
    grade = data.get("grade")
    print(f"\n[SCORING]")
    print(f"  • Score:       {score}/100")
    print(f"  • Grade:       {grade}")
    
    # Market Comparison
    print(f"\n[MARKET BENCHMARK]")
    percentiles = data.get("percentiles", {})
    if "salary" in percentiles:
        sal_p = percentiles["salary"]
        print(f"  • Salary:      Better than {sal_p.get('value', 0):.0f}% of market")
    if "notice_period" in percentiles:
        not_p = percentiles["notice_period"]
        print(f"  • Notice:      Longer than {not_p.get('value', 0):.0f}% of market (Lower is better)")
        
    # Red Flags
    flags = data.get("red_flags", [])
    if flags:
        print(f"\n[RED FLAGS] ({len(flags)})")
        for i, flag in enumerate(flags, 1):
            print(f"  {i}. [{flag.get('severity', 'UNK').upper()}] {flag.get('rule')}")
            print(f"     -> Recommendation: {flag.get('recommendation')}")
    else:
        print("\n[RED FLAGS]")
        print("  None detected!")

    # RAG Evidence
    rag = data.get("rag", {})
    evidence_map = rag.get("evidence_by_clause_type", {})
    
    print(f"\n[RAG INTELLIGENCE]")
    if evidence_map:
        count = sum(len(v) for v in evidence_map.values())
        print(f"  • Retrieved {count} similar clauses from Vector DB")
        for c_type, chunks in evidence_map.items():
            print(f"  • {c_type.upper()}: Found {len(chunks)} precedent clauses")
    else:
        print("  • No retrieval triggers found (Clean contract or RAG skipped)")

    print("\n" + "="*60)

if __name__ == "__main__":
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        
    parser = argparse.ArgumentParser(description="Analyze a contract PDF via CLI")
    parser.add_argument("file", help="Path to the contract PDF file")
    parser.add_argument("--role", default="Software Engineer", help="Job Role (default: Software Engineer)")
    parser.add_argument("--yoe", type=float, default=2.0, help="Years of Experience (default: 2.0)")
    parser.add_argument("--type", default="product", choices=["product", "service", "startup"], help="Company Type (default: product)")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args = parser.parse_args()
    analyze_contract(args.file, args.role, args.yoe, args.type)
