# 🚀 How to Run the App

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js 18+** and npm installed
3. **Google API Key** (already configured in `.env`)
4. **Tesseract OCR** (optional, for image-based PDFs - see `SETUP_OCR.md`)

## Quick Start

### Step 1: Start the Backend Server

Open a terminal in the project root and run:

```bash
cd backend
pip install -r requirements.txt
```

Then start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

**Note:** If `uvicorn` is not found after installation, try:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

The backend will start at: **http://localhost:8000**

You can verify it's running by visiting:
- http://localhost:8000/docs (API documentation)
- http://localhost:8000/health (health check)

### Step 2: Start the Frontend Server

Open a **new terminal** in the project root and run:

```bash
cd frontend
npm install  # Only needed the first time
npm run dev
```

The frontend will start at: **http://localhost:5173**

### Step 3: Open the App

Open your browser and navigate to:
**http://localhost:5173**

---

## Detailed Instructions

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```
   
   **Note:** If you get permission errors, try:
   ```bash
   pip install --user -r requirements.txt
   ```

3. **Verify environment variables:**
   - Check that `.env` file exists in the project root (one level up from `backend/`)
   - Ensure `GOOGLE_API_KEY` is set (already configured)

4. **Start the FastAPI server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   
   **Alternative if uvicorn command not found:**
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   
   The `--reload` flag enables auto-reload on code changes.

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node dependencies** (only needed the first time):
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **The app will open automatically** at http://localhost:5173

---

## Running Both Servers

You need **two terminal windows**:

**Terminal 1 (Backend):**
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

**Or use the provided script (Windows):**
```bash
cd backend
.\start_server.ps1
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

---

## First Time Setup

### 1. Ingest Sample Contracts (Optional)

Before analyzing contracts, you may want to ingest some sample contracts to build the knowledge base:

```bash
cd backend
python test_rag_pipeline.py
```

This will:
- Parse contracts from `data/raw_contracts/`
- Extract metadata
- Store embeddings in ChromaDB
- Make them available for comparison

**Note:** Place your sample contracts in `data/raw_contracts/` directory.

### 2. Create a User Account

1. Open the app at http://localhost:5173
2. Click the user icon (top-right) or navigate to `/login`
3. Click "Sign Up" to create an account
4. Log in with your credentials

---

## Troubleshooting

### Backend Issues

**"Module not found" errors:**
```bash
cd backend
pip install -r requirements.txt
```

**"GOOGLE_API_KEY not set":**
- Check that `.env` file exists in project root
- Verify the API key is correct

**Port 8000 already in use:**
```bash
python -m uvicorn app.main:app --reload --port 8001
```
Then update `frontend/src/services/api.ts` to use port 8001.

### Frontend Issues

**"Cannot find module" errors:**
```bash
cd frontend
npm install
```

**Port 5173 already in use:**
Vite will automatically use the next available port (5174, 5175, etc.)

**Backend connection errors:**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/app/main.py`
- Verify API URL in `frontend/src/services/api.ts`

### Database Issues

**SQLite database errors:**
- The database is automatically created on first run
- If issues occur, delete `backend/app.db` and restart the server

**ChromaDB errors:**
- Delete `chroma_db/` directory and re-run ingestion
- Ensure you have write permissions in the project directory

---

## Production Build

### Build Frontend:
```bash
cd frontend
npm run build
```

The built files will be in `frontend/dist/`

### Run Backend in Production:
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## API Endpoints

Once the backend is running, you can access:

- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Root:** http://localhost:8000/

---

## Need Help?

- Check `QUICKSTART.md` for RAG pipeline setup
- Check `SYSTEM_ARCHITECTURE.md` for system overview
- Check `SETUP_OCR.md` for OCR setup (if needed)

