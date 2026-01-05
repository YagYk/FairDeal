# GitHub Repository Setup Guide

This document outlines what has been excluded from the GitHub repository for security and privacy reasons.

## Files Excluded from Repository

### 1. Environment Variables & Secrets
- `.env` - Contains API keys and secrets (NEVER commit this)
- Use `.env.example` as a template for your local setup

### 2. Contract Documents
- All PDF files (`*.pdf`)
- All DOC files (`*.doc`)
- All DOCX files (`*.docx`)
- Located in `data/raw_contracts/` and `data/processed/`

**Reason**: Contract documents may contain sensitive personal information and should not be publicly available.

### 3. Database Files
- `*.db`, `*.sqlite`, `*.sqlite3` files
- `chroma_db/` directory (vector database)
- Contains user data and analysis results

**Reason**: Database files contain user data and should remain private.

### 4. Training Data
- Test scripts that may contain training data
- Sample datasets
- Model weights and checkpoints

### 5. Log Files
- `*.log` files
- May contain sensitive information from debugging

### 6. Build Artifacts
- `node_modules/` (frontend dependencies)
- `dist/` and `build/` directories
- Python `__pycache__/` directories

## Setup Instructions for New Contributors

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd final_year_project
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

3. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Install Node.js dependencies (Frontend)**
   ```bash
   cd frontend
   npm install
   ```

5. **Set up database**
   ```bash
   cd backend
   python -m app.db.database init_db
   ```

6. **Add sample contracts** (optional)
   - Place PDF/DOCX files in `data/raw_contracts/`
   - Run ingestion: `python ingest_contracts.py`

## What IS Included in Repository

✅ Source code (Python, TypeScript, React)  
✅ Configuration files (package.json, requirements.txt)  
✅ Documentation (README, architecture docs)  
✅ Example environment file (.env.example)  
✅ Directory structure (.gitkeep files)

## Security Notes

- **Never commit** `.env` files
- **Never commit** contract documents (PDF/DOCX)
- **Never commit** database files
- **Never commit** API keys or secrets
- Review `.gitignore` before committing

## Verifying Before Commit

Before committing, verify that sensitive files are excluded:

```bash
# Check what will be committed
git status

# Verify .env is ignored
git check-ignore .env

# Verify PDFs are ignored
git check-ignore data/raw_contracts/*.pdf
```

## If You Accidentally Commit Sensitive Data

If you accidentally commit sensitive files:

1. **Remove from git history** (if not pushed):
   ```bash
   git rm --cached .env
   git commit --amend
   ```

2. **If already pushed**, you need to:
   - Rotate all API keys immediately
   - Use `git filter-branch` or BFG Repo-Cleaner to remove from history
   - Force push (coordinate with team)

## Contact

If you have questions about what should/shouldn't be committed, contact the project maintainer.

