# OCR Enhancement & Chatbot Implementation

## 🎯 Overview

This update adds:
1. **Robust OCR** with rotation detection for PDFs (handles 0°, 90°, 180°, 270° rotations)
2. **AI Chatbot** that answers questions about contract analysis results

---

## 🔧 OCR Enhancements

### Features Added

1. **Automatic Rotation Detection**
   - Tries OCR at 0°, 90°, 180°, and 270° rotations
   - Picks the best result based on confidence scores
   - Handles both portrait and landscape documents

2. **Image Quality Enhancement**
   - Converts to grayscale for better OCR accuracy
   - Enhances contrast (50% increase)
   - Sharpens images (20% increase)

3. **Multiple PSM Modes**
   - Tries different Page Segmentation Modes (PSM 6, 3, 1)
   - PSM 6: Uniform block of text
   - PSM 3: Fully automatic page segmentation
   - PSM 1: Automatic with OSD (Orientation and Script Detection)

4. **Better PDF to Image Conversion**
   - Uses `pdf2image` library (preferred method)
   - Falls back to `pdfplumber.to_image()` if pdf2image unavailable
   - High DPI (300) for better accuracy

### Files Modified

- `backend/app/parsers/pdf_parser.py` - Complete OCR rewrite
- `backend/requirements.txt` - Added `pdf2image==1.16.3`

### How It Works

```python
# 1. Try normal text extraction first
text = page.extract_text()

# 2. If no text, convert page to image
pil_image = convert_from_path(pdf_path, dpi=300)[page_num-1]

# 3. Enhance image quality
enhanced_image = enhance_image_for_ocr(pil_image)

# 4. Try OCR at different rotations
for rotation in [0, 90, 180, 270]:
    rotated_image = enhanced_image.rotate(-rotation, expand=True)
    ocr_text = pytesseract.image_to_string(rotated_image, config=ocr_config)
    # Calculate confidence score
    # Keep best result

# 5. Return best OCR result
```

---

## 💬 Chatbot Implementation

### Features

1. **Context-Aware Responses**
   - Uses full analysis results as context
   - Answers questions about fairness scores, red flags, percentiles, etc.

2. **Natural Language Understanding**
   - Handles questions like:
     - "What does my fairness score mean?"
     - "What are the main red flags?"
     - "How can I negotiate better terms?"
     - "What percentile is my salary at?"

3. **Professional & Helpful**
   - Explains technical terms in simple language
   - Provides specific numbers and percentages
   - References negotiation scripts when relevant

### Backend Changes

**New Files:**
- `backend/app/services/chatbot_service.py` - Chatbot logic

**Modified Files:**
- `backend/app/api/contracts.py` - Added `/api/contracts/chat` endpoint
- `backend/app/models/user.py` - Added `analysis_result_json` field to store full results

**Database Schema Update:**
```sql
ALTER TABLE contract_analyses ADD COLUMN analysis_result_json TEXT;
```

### Frontend Changes

**New Files:**
- `frontend/src/components/Chatbot.tsx` - Chatbot UI component

**Modified Files:**
- `frontend/src/services/api.ts` - Added `chat()` method
- `frontend/src/components/AnalysisDashboard.tsx` - Integrated chatbot
- `frontend/src/pages/Home.tsx` - Pass analysis_id to dashboard

### API Endpoint

**POST `/api/contracts/chat`**

Request:
```json
{
  "analysis_id": "uuid-here",
  "question": "What does my fairness score mean?"
}
```

Response:
```json
{
  "success": true,
  "response": "Your fairness score of 72% indicates...",
  "analysis_id": "uuid-here"
}
```

---

## 📦 Installation

### 1. Install New Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This will install `pdf2image==1.16.3`.

### 2. Install pdf2image System Dependencies

**Windows:**
- Install Poppler: https://github.com/oschwartz10612/poppler-windows/releases
- Add to PATH: `C:\Program Files\poppler\Library\bin`

**macOS:**
```bash
brew install poppler
```

**Linux:**
```bash
sudo apt-get install poppler-utils
```

### 3. Update Database Schema

The database needs a new column. Run this migration:

**Option 1: Automatic (on next server start)**
- The database will auto-update when you restart the server
- SQLAlchemy will add the column if it doesn't exist

**Option 2: Manual SQL**
```sql
ALTER TABLE contract_analyses ADD COLUMN analysis_result_json TEXT;
```

### 4. Restart Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

---

## 🧪 Testing

### Test OCR with Rotated PDF

1. Upload a scanned/rotated PDF
2. Check logs for OCR rotation attempts
3. Verify text extraction works correctly

### Test Chatbot

1. Upload and analyze a contract
2. Scroll to bottom of results page
3. Find the chatbot component
4. Ask questions like:
   - "What does my fairness score mean?"
   - "What are the red flags?"
   - "How can I negotiate?"

---

## 🐛 Troubleshooting

### OCR Issues

**"pdf2image not found"**
- Install Poppler (see Installation section)
- Verify Poppler is in PATH: `pdftoppm -h`

**"Tesseract not found"**
- Install Tesseract OCR (see SETUP_OCR.md)
- Verify: `tesseract --version`

**Poor OCR accuracy**
- Ensure PDF is high quality (300+ DPI)
- Check if text is actually in images (not selectable text)
- Try different PSM modes manually

### Chatbot Issues

**"Analysis result not available"**
- Old analyses don't have JSON stored
- Re-analyze the contract to get chatbot support

**"Analysis not found"**
- Ensure you're logged in
- Check that analysis_id is correct
- Verify analysis belongs to current user

---

## 📝 Notes

- **OCR Performance**: OCR takes 2-5 seconds per page (slower than text extraction)
- **Chatbot Accuracy**: Responses are based on analysis data - if data is incomplete, responses may be limited
- **Database Storage**: Full analysis results are now stored as JSON (increases database size slightly)

---

## ✅ What's Next

1. **Test with real rotated PDFs** from your sample data
2. **Verify chatbot responses** are accurate and helpful
3. **Monitor OCR performance** - may need optimization for large documents
4. **Consider caching** OCR results for repeated analyses

