# How to Ingest Sample Contracts

## 🎯 Overview

To get accurate analysis results, you need to ingest your sample contracts into the knowledge base first. This guide shows you exactly how to do that.

---

## 📋 Step-by-Step Guide

### Step 1: Place Contracts in Data Folder

Your contracts should already be in:
```
data/raw_contracts/
```

**Verify they're there:**
```bash
# Windows PowerShell
Get-ChildItem data\raw_contracts\*.pdf
Get-ChildItem data\raw_contracts\*.docx
```

You should see files like:
- `EMPLOYMENT_AGREEMENT_1.pdf`
- `CONSULTANCY_AGREEMENT_1.pdf`
- `Independent-Contractor_Freelancer_1.pdf`
- etc.

### Step 2: Run Ingestion Script

```bash
cd backend
python test_rag_pipeline.py
```

**What this does:**
1. ✅ Parses all PDF/DOCX files from `data/raw_contracts/`
2. ✅ Extracts metadata using LLM (contract type, industry, salary, etc.)
3. ✅ Chunks text by clauses
4. ✅ Generates embeddings (vector representations)
5. ✅ Stores in ChromaDB (vector database)
6. ✅ Saves metadata to `data/processed/`

**Expected output:**
```
Ingesting contracts from data/raw_contracts/
Processing: EMPLOYMENT_AGREEMENT_1.pdf
  ✓ Extracted metadata
  ✓ Generated 45 chunks
  ✓ Stored in ChromaDB
Processing: CONSULTANCY_AGREEMENT_1.pdf
  ...
```

### Step 3: Verify Ingestion

```bash
cd backend
python verify_data_sources.py
```

**You should see:**
```
📊 ChromaDB Statistics:
   Total chunks in vector database: 500+ (depends on your contracts)

📁 Processed Contracts:
   Total contracts in knowledge base: 12
   
   Contract Details:
   1. EMPLOYMENT_AGREEMENT_1_metadata.json
      Type: employment
      Industry: technology
      ...
```

### Step 4: Test Analysis

Now when you upload a contract for analysis:
- ✅ It will find similar contracts from your knowledge base
- ✅ It will show which contracts were used
- ✅ It will calculate accurate percentiles
- ✅ It will provide detailed explanations

---

## 🔍 How to Know Data is Being Used

### During Analysis

**Check the logs** (backend terminal):
```
INFO: Retrieving similar contracts for query: 'employment contract...'
INFO: Retrieved 15 similar chunks
INFO: Computing percentile for salary=800000
INFO: Found 12 similar contracts in knowledge base
```

### In Results

**Frontend shows:**
1. **Data Sources Section**:
   - "Contracts Used: 15"
   - "Total in Database: 12"
   - List of top similar contracts with similarity scores

2. **Percentile Explanations**:
   - "Based on 12 similar contracts in our knowledge base"
   - Market median, mean, quartiles

3. **Confidence Metrics**:
   - "High confidence" if sample size >= 20
   - "Medium confidence" if sample size >= 10
   - "Low confidence" if sample size < 10

---

## 📊 Understanding the Data Flow

```
Your Contract Upload
    ↓
Extract Metadata (LLM)
    ↓
Query Knowledge Base (RAG)
    ├─→ Find similar contracts by:
    │   • Contract type
    │   • Industry
    │   • Role
    │   • Location
    │   • Semantic similarity
    ↓
Calculate Statistics
    ├─→ Percentiles (salary, notice period)
    ├─→ Market averages
    └─→ Frequency analysis
    ↓
Generate Explanations
    ├─→ Show which contracts were used
    ├─→ Explain each percentile
    └─→ Justify recommendations
    ↓
Display Results
    ├─→ Data sources transparency
    ├─→ Detailed explanations
    └─→ Confidence metrics
```

---

## ✅ Verification Checklist

After ingestion, verify:

- [ ] `data/processed/` contains `*_metadata.json` files
- [ ] `verify_data_sources.py` shows contracts in knowledge base
- [ ] ChromaDB has chunks (check logs)
- [ ] Upload a contract and see "Contracts Used: X" in results
- [ ] Detailed report shows similar contracts with similarity scores
- [ ] Percentile explanations mention sample size

---

## 🐛 Troubleshooting

### "No contracts found in knowledge base"

**Solution:**
1. Check contracts are in `data/raw_contracts/`
2. Run `python test_rag_pipeline.py` to ingest
3. Verify `data/processed/` has metadata files

### "Low confidence" in results

**Solution:**
- Add more contracts to `data/raw_contracts/`
- More contracts = better accuracy
- Aim for 20+ contracts for high confidence

### "Contracts Used: 0"

**Solution:**
- Contracts might not match filters (contract_type, industry, location)
- Check if your contract metadata matches ingested contracts
- Try ingesting more diverse contracts

---

## 💡 Best Practices

1. **Diversity**: Include contracts from different:
   - Industries (tech, finance, consulting, etc.)
   - Roles (engineer, manager, consultant, etc.)
   - Contract types (employment, consulting, freelance)

2. **Quality**: Use real contracts (anonymized) for best results

3. **Quantity**: More contracts = better statistics:
   - 10+ contracts: Basic analysis
   - 20+ contracts: Good analysis
   - 50+ contracts: Excellent analysis

4. **Update**: Re-run ingestion when adding new contracts

---

## 📝 Example

**Before ingestion:**
```
Contracts Used: 0
Confidence: Low
Sample Size: 0
```

**After ingestion (12 contracts):**
```
Contracts Used: 12
Confidence: Medium
Sample Size: 12
Top Similar Contracts:
  - employment_agreement_1.pdf (87% match)
  - software_engineer_contract.pdf (82% match)
  ...
```

---

## 🎯 For Your Project Demo

**To impress the panel:**

1. **Show data sources**: "We used 12 similar contracts from our knowledge base"
2. **Show transparency**: "Here are the exact contracts we compared against"
3. **Show confidence**: "High confidence analysis based on 20+ similar contracts"
4. **Show accuracy**: "Percentiles calculated from real market data"

This demonstrates:
- ✅ Real data usage (not mock data)
- ✅ Transparency and credibility
- ✅ Sophisticated analysis system
- ✅ Production-ready implementation

