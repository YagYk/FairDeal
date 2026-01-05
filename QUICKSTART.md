# Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up API Keys

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Google API key:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   LLM_PROVIDER=gemini
   EMBEDDING_PROVIDER=gemini
   ```
   
   Get your API key from: https://makersuite.google.com/app/apikey

### Step 3: Add Sample Contracts

Place PDF or DOCX contract files in `data/raw_contracts/`:

```bash
# Example structure
data/raw_contracts/
  ├── contract1.pdf
  ├── contract2.docx
  └── employment_agreement.pdf
```

### Step 4: Run the Test Script

```bash
python test_rag_pipeline.py
```

This will:
1. ✅ Parse all contracts
2. ✅ Extract metadata using LLM
3. ✅ Chunk documents by clauses
4. ✅ Generate embeddings
5. ✅ Store in ChromaDB
6. ✅ Test retrieval with sample queries

## 📝 Example Usage

### Ingest a Single Contract

```python
from pathlib import Path
from app.services.ingestion_service import IngestionService

ingestion = IngestionService()
result = ingestion.ingest_contract(Path("data/raw_contracts/my_contract.pdf"))
print(f"Ingested {result['num_chunks']} chunks")
```

### Query Similar Contracts

```python
from app.services.rag_service import RAGService

rag = RAGService()

# Simple query
results = rag.retrieve_similar_contracts(
    query_text="90 day notice period employment contract",
    n_results=10
)

# With filters
results = rag.retrieve_similar_contracts(
    query_text="non-compete clause restrictions",
    n_results=20,
    filters={
        "contract_type": "employment",
        "industry": "technology"
    }
)

for result in results:
    print(f"Similarity: {result['similarity_score']:.4f}")
    print(f"Clause: {result['clause_type']}")
    print(f"Text: {result['text'][:200]}...")
```

## 🔍 Understanding the Output

The test script will show:

1. **Ingestion Summary**: Which contracts were processed successfully
2. **Retrieval Results**: Similar chunks with:
   - `similarity_score`: How similar (0-1, higher is better)
   - `clause_type`: Which clause the chunk belongs to
   - `metadata`: Contract-level metadata
   - `text`: The actual chunk text

## 🐛 Troubleshooting

### "No module named 'app'"
Make sure you're running from the project root directory.

### "GOOGLE_API_KEY not set"
Check your `.env` file exists and has a valid Google API key. Get one from https://makersuite.google.com/app/apikey

### "No PDF or DOCX files found"
Add contract files to `data/raw_contracts/` directory.

### ChromaDB errors
If you get ChromaDB errors, delete the `chroma_db/` directory and re-run ingestion.

## 📚 Next Steps

- Read the full [README.md](README.md) for architecture details
- Explore the code in `backend/app/services/` to understand the pipeline
- Customize chunking strategies in `backend/app/utils/chunking.py`
- Add more clause patterns for better chunking

## 💡 Tips

- Start with 2-3 sample contracts to test the pipeline
- Check `data/processed/` for extracted metadata JSON files
- Use filters to narrow down retrieval results
- Monitor `rag_test.log` for detailed logging
