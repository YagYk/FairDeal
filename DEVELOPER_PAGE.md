# Developer Dashboard

A comprehensive developer/debug page that provides real-time visibility into the backend operations, RAG model activity, and data flow.

## Access

1. **Login** to your account
2. Click on your **user icon** in the top-right corner
3. Select **"Developer"** from the dropdown menu
4. Or navigate directly to `/developer` (requires authentication)

## Features

### 1. System Health
- **ChromaDB Status**: Shows total chunks in the vector database
- **Knowledge Base**: Number of processed contracts
- **Raw Contracts**: Number of contract files in the data folder
- **Embedding Service**: Status of the embedding generation service
- **Recommendations**: System suggestions for improving the knowledge base

### 2. Knowledge Base
- **Total Chunks**: Number of text chunks stored in ChromaDB
- **Processed Contracts**: List of contracts that have been ingested
- **Raw Contracts**: Count of PDF/DOCX files ready for processing
- Shows metadata for each processed contract (type, industry, chunk count)

### 3. RAG Model Test
- **Interactive Query Testing**: Test the RAG retrieval system with custom queries
- **Query Input**: Enter any text query (e.g., "employment contract software engineer")
- **Results Count**: Adjust how many similar contracts to retrieve (1-20)
- **Detailed Results**: Shows:
  - Contract IDs
  - Similarity scores (percentage match)
  - Clause types
  - Text previews of retrieved chunks
  - Metadata (contract type, industry, etc.)
  - Embedding dimensions

### 4. Market Statistics
- **Field Analysis**: View statistics for specific fields (e.g., salary, notice period)
- **Data Overview**:
  - Total values in database
  - Valid values (non-null, > 0)
  - Median and mean calculations
- **Sample Values**: See actual data points used in calculations
- **Percentile Examples**: See how percentiles are computed for sample values

### 5. Analysis Pipeline
- **Pipeline Steps**: Visual breakdown of the 7-step analysis process
- **Configuration**: Shows current settings:
  - LLM model being used
  - Embedding model
  - Database paths
  - Contract storage paths
- **Capabilities**: Check which features are enabled:
  - OCR support
  - Rotation detection
  - RAG retrieval
  - Statistical analysis
  - LLM explanations
  - Transparency features

### 6. Recent Analyses
- **Analysis History**: View your recent contract analyses
- **Details Shown**:
  - Filename
  - Fairness score
  - Contract type, industry
  - Number of similar contracts found
  - Red flags count
  - Favorable terms count

## Use Cases

### Verifying Data Ingestion
1. Go to **System Health** → Check if "Knowledge Base" shows processed contracts > 0
2. Go to **Knowledge Base** → Verify contracts are listed with correct metadata
3. If empty, you need to ingest contracts using `test_rag_pipeline.py`

### Testing RAG Retrieval
1. Go to **RAG Model Test**
2. Enter a query like "software engineer employment contract"
3. Click **Test**
4. Review the similarity scores and retrieved chunks
5. Verify that the results are relevant to your query

### Verifying Statistics
1. Go to **Market Statistics**
2. Check if "Total Values" > 0
3. Review median/mean calculations
4. Verify sample values are reasonable

### Debugging Analysis Issues
1. Check **System Health** for any error indicators
2. Review **Recent Analyses** to see if analyses are being stored
3. Test **RAG Model Test** to verify retrieval is working
4. Check **Analysis Pipeline** configuration matches your expectations

## API Endpoints

The developer page uses these backend endpoints:

- `GET /api/debug/knowledge-base` - Knowledge base information
- `POST /api/debug/test-rag?query=...&n_results=5` - Test RAG retrieval
- `GET /api/debug/stats?field_name=salary` - Market statistics
- `GET /api/debug/analysis-pipeline` - Pipeline configuration
- `GET /api/debug/recent-analyses?limit=5` - Recent analyses
- `GET /api/debug/system-health` - System health check

All endpoints require authentication (JWT token).

## Tips

1. **Refresh Data**: Click "Refresh All" button to reload all sections
2. **Test Queries**: Try different query formats in RAG Test to see how retrieval works
3. **Monitor Health**: Check System Health regularly to ensure all components are working
4. **Verify Ingestion**: After ingesting new contracts, refresh Knowledge Base to see them appear

## Troubleshooting

### "No results found" in RAG Test
- **Solution**: Ingest contracts using `test_rag_pipeline.py` first

### "Knowledge base needs ingestion"
- **Solution**: Run the ingestion script to process contracts from `data/raw_contracts/`

### "Embedding service error"
- **Solution**: Check that `GOOGLE_API_KEY` is set in `.env` file

### Empty statistics
- **Solution**: Ensure contracts have been ingested and contain the field you're querying (e.g., salary)

