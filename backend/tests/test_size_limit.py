import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
import builtins
import io

client = TestClient(app)

def test_size_limit():
    # Create a dummy file larger than 10MB (10MB + 1 byte)
    # We don't need to actually write 10MB to disk, we can create a large bytes object
    # or a virtual file-like object if the server reads it into memory.
    # However, Starlette/FastAPI UploadFile spools to disk or memory.
    # Creating a real file is safer to mimic the upload behavior accurately.
    
    file_size = 10 * 1024 * 1024 + 1024  # 10MB + 1KB
    large_content = io.BytesIO(b"0" * file_size)
    large_content.name = "large_file.txt"

    response = client.post(
        "/api/analyze",
        files={"file": ("large_file.txt", large_content, "text/plain")},
        data={"context": '{"role": "SDE", "ctc": 1000000, "experience_level": 3, "company_type": "product", "industry": "tech", "location": "Bangalore"}'}
    )
    
    # We expect 413 Payload Too Large
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]

