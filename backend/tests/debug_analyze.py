
import requests
import json
import time

def test_analyze():
    url = "http://127.0.0.1:8005/api/analyze"
    
    # Mock context
    context = {
        "role": "mid",
        "experience_level": 4,
        "company_type": "product",
        "industry": "tech",
        "location": "Bangalore"
    }

    # Mock PDF content
    files = {
        'file': ('test_contract.txt', b'This is a test contract for Amazon SDE 2. Salary is 18,00,000 INR. Notice period is 30 days. No non-compete. Provident fund is included.', 'text/plain')
    }
    
    data = {
        'context': json.dumps(context)
    }

    try:
        print(f"Sending request to {url}...")
        resp = requests.post(url, files=files, data=data) 
        print(f"Status Code: {resp.status_code}")
        if resp.status_code != 200:
            print("Response Text:", resp.text)
        else:
            print("Success!")
            # Check determinism
            data = resp.json()
            print(f"Determinism: {data.get('determinism')}")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_analyze()
