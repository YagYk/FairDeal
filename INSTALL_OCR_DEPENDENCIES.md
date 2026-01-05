# Installing OCR Dependencies (Tesseract & Poppler)

## Issue
Chocolatey installation failed due to permission issues. Here are alternative methods:

## Method 1: Manual Installation (Recommended)

### Step 1: Install Tesseract OCR

1. **Download Tesseract:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.x.x.exe`)

2. **Install:**
   - Run the installer as Administrator
   - **Important:** During installation, check "Add to PATH" option
   - Default installation path: `C:\Program Files\Tesseract-OCR`

3. **Verify Installation:**
   ```powershell
   tesseract --version
   ```

### Step 2: Install Poppler

1. **Download Poppler:**
   - Go to: https://github.com/oschwartz10612/poppler-windows/releases/
   - Download the latest `Release-x.x.x.zip` file

2. **Extract and Setup:**
   - Extract the zip file to a permanent location (e.g., `C:\poppler`)
   - Add `C:\poppler\Library\bin` to your system PATH:
     - Open "Environment Variables" (search in Start menu)
     - Edit "Path" under "System variables"
     - Add: `C:\poppler\Library\bin`
     - Click OK and restart your terminal/IDE

3. **Verify Installation:**
   ```powershell
   pdftoppm -h
   ```

## Method 2: Fix Chocolatey and Retry

If you want to use Chocolatey, you need to:

1. **Run PowerShell as Administrator:**
   - Right-click PowerShell → "Run as Administrator"

2. **Remove the lock file:**
   ```powershell
   Remove-Item "C:\ProgramData\chocolatey\lib\4e648a20689ec7f5cb6f6c83f5e3238954966173" -Force -ErrorAction SilentlyContinue
   ```

3. **Try installation again:**
   ```powershell
   choco install tesseract -y
   choco install poppler -y
   ```

## Method 3: Use Conda/Mamba (If Available)

If you have Anaconda/Miniconda installed:

```bash
conda install -c conda-forge tesseract poppler
```

## Verification

After installation, verify both are working:

```powershell
# Check Tesseract
tesseract --version

# Check Poppler
pdftoppm -h
```

Then restart your backend server and test OCR again.

## Quick Test

After installation, you can test OCR with:

```python
# Test script
from app.parsers.pdf_parser import PDFParser
from pathlib import Path

parser = PDFParser()
# Test with a PDF file
test_file = Path("data/raw_contracts/your_test_file.pdf")
if test_file.exists():
    text = parser.extract_text(test_file)
    print(f"Extracted {len(text)} characters")
    if "OCR" in text or len(text) > 1000:
        print("✓ OCR appears to be working!")
```

## Troubleshooting

### Tesseract not found
- Make sure it's added to PATH
- Restart terminal/IDE after adding to PATH
- Try: `$env:Path += ";C:\Program Files\Tesseract-OCR"` (temporary)

### Poppler not found
- Verify the bin folder is in PATH
- Check: `C:\poppler\Library\bin\pdftoppm.exe` exists
- Restart terminal after adding to PATH

### Still not working?
- Check if both are in PATH: `$env:Path -split ';' | Select-String -Pattern 'tesseract|poppler'`
- Restart your computer (sometimes needed for PATH changes)
- Check backend logs for specific error messages

