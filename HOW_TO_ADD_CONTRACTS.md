# How to Add Contracts to the Knowledge Base

## 📁 Where to Place Contracts

**Place your contract files here:**
```
data/raw_contracts/
```

**Supported formats:**
- `.pdf` (PDF files)
- `.docx` (Word documents)
- `.doc` (Older Word format)

## 🚀 Two Ways to Add Contracts

### Method 1: Place Files in Folder (Recommended for Bulk)

1. **Copy your contract files** to `data/raw_contracts/`:
   ```
   data/
   └── raw_contracts/
       ├── employment_contract_1.pdf
       ├── employment_contract_2.docx
       ├── consulting_agreement.pdf
       └── ...
   ```

2. **Run ingestion script**:
   ```bash
   cd backend
   python -c "from pathlib import Path; from app.services.ingestion_service import IngestionService; service = IngestionService(); results = service.ingest_directory(Path('../data/raw_contracts')); print(f'Ingested {len(results)} contracts')"
   ```

   Or use the test script:
   ```bash
   python test_rag_pipeline.py
   ```

### Method 2: Upload via API (For Individual Files)

1. **Start the backend server**:
   ```bash
   cd backend
   python -m uvicorn app.main:app --reload
   ```

2. **Use the API endpoint**:
   ```bash
   curl -X POST "http://localhost:8000/api/contracts/ingest" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -F "file=@/path/to/contract.pdf"
   ```

   Or use the frontend (if you add an admin upload interface).

## ✅ After Ingestion

- **Embeddings are stored** in `./chroma_db/` (persistent storage)
- **Metadata is saved** in `data/processed/` (JSON files)
- **Contracts are ready** for analysis and comparison

## 📊 Check Knowledge Base Status

```bash
# Via API
curl -X GET "http://localhost:8000/api/contracts/stats" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## ⚠️ Important Notes

- **File names** become contract IDs (use descriptive names)
- **Large files** may take time to process (embedding generation)
- **Once ingested**, contracts are permanently in the knowledge base
- **To re-ingest**, delete the ChromaDB collection first

