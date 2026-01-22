
import asyncio
import httpx
import time
import json

async def send_request(client, i):
    url = "http://127.0.0.1:8001/api/analyze"
    # Content that forces LLM usage (no regex match for salary)
    files = {
        'file': (f'test_doc_{i}.txt', b'The company offers a good compensation package. We expect a long term commitment.', 'text/plain')
    }
    context = {
        "role": "developer", 
        "experience_level": 2, 
        "company_type": "product",
        "industry": "tech",
        "location": "remote"
    }
    data = {'context': json.dumps(context)}
    
    print(f"[{time.strftime('%X')}] Request {i}: Sending...")
    try:
        start = time.time()
        response = await client.post(url, files=files, data=data, timeout=60.0)
        duration = time.time() - start
        print(f"[{time.strftime('%X')}] Request {i}: Completed in {duration:.2f}s | Status: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"[{time.strftime('%X')}] Request {i}: Failed - {str(e)}")
        return 0

async def main():
    print("Starting stress test to verify rate limiting queue...")
    async with httpx.AsyncClient() as client:
        # Send 3 concurrent requests
        # consistently hitting the 4s delay window
        tasks = [send_request(client, i) for i in range(1, 4)]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
