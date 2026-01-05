# Backend Setup

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   If you get permission errors:
   ```bash
   pip install --user -r requirements.txt
   ```

2. **Start the server:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   
   **Windows PowerShell:**
   ```powershell
   .\start_server.ps1
   ```
   
   **Windows CMD:**
   ```cmd
   start_server.bat
   ```

3. **Verify it's running:**
   - Open http://localhost:8000/health
   - Should return: `{"status": "healthy"}`
   - API docs: http://localhost:8000/docs

## Important Notes

- The `.env` file should be in the **project root** (one level up from `backend/`)
- The server looks for `.env` at: `../.env` (relative to this directory)
- All dependencies are listed in `requirements.txt`

## Troubleshooting

### "uvicorn: command not found"
Use: `python -m uvicorn app.main:app --reload --port 8000`

### "Module not found"
Make sure you installed dependencies:
```bash
pip install -r requirements.txt
```

### "GOOGLE_API_KEY not set"
Check that `.env` exists in the project root with `GOOGLE_API_KEY` set.

