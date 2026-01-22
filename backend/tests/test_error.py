
import requests
import json

def test_error_handling():
    url = "http://127.0.0.1:8005/api/analyze"
    
    # MALFORMED REQUEST: Missing 'context' field
    # This should trigger RequestValidationError
    files = {
        'file': ('test.txt', b'dummy content', 'text/plain')
    }
    
    print(f"Sending MALFORMED request to {url}...")
    try:
        resp = requests.post(url, files=files) # No data=...
        print(f"Status: {resp.status_code}")
        print("Response Body:")
        print(json.dumps(resp.json(), indent=2))
        
        if resp.status_code == 422 and "error" in resp.json():
            print("\n✅ Validation Error Handler Verified")
        else:
            print("\n❌ Unexpected Response")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_error_handling()
