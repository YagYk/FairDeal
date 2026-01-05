# OCR Setup for Image-Based PDFs

## Overview

The system now supports OCR (Optical Character Recognition) for PDFs that contain images or scanned documents. This allows extraction of text from image-based contracts.

## Installation

### Step 1: Install Tesseract OCR

**Windows:**
1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer
3. Add Tesseract to PATH (usually `C:\Program Files\Tesseract-OCR`)
4. Restart your terminal/IDE

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### Step 2: Install Python Packages

The packages are already in `requirements.txt`. Install them:

```bash
pip install pytesseract Pillow
```

### Step 3: Verify Installation

```bash
# Check Tesseract is installed
tesseract --version

# Test Python import
python -c "import pytesseract; from PIL import Image; print('OCR ready!')"
```

## How It Works

1. **Text Extraction First**: The system tries normal text extraction first
2. **OCR Fallback**: If a page has little/no text (< 50 characters), OCR is attempted
3. **Automatic Detection**: No manual configuration needed
4. **Graceful Fallback**: If OCR fails, the system continues with available text

## Limitations

- **Accuracy**: OCR accuracy depends on image quality
- **Speed**: OCR is slower than text extraction (~2-5 seconds per page)
- **Language**: Currently supports English only
- **Complex Layouts**: May not preserve exact formatting

## Testing

To test OCR with a scanned PDF:

```python
from pathlib import Path
from app.parsers.pdf_parser import PDFParser

parser = PDFParser()
text = parser.extract_text(Path("scanned_contract.pdf"))
print(f"Extracted {len(text)} characters")
```

## Troubleshooting

### "TesseractNotFoundError"
- **Solution**: Make sure Tesseract is installed and in PATH
- **Windows**: Add `C:\Program Files\Tesseract-OCR` to system PATH
- **Verify**: Run `tesseract --version` in terminal

### "No text extracted from images"
- **Solution**: Check image quality (should be 300+ DPI)
- **Solution**: Ensure PDF pages are actual images, not just low-quality text

### "OCR is slow"
- **Normal**: OCR takes 2-5 seconds per page
- **Optimization**: Only used when text extraction fails

