"""
OCR Service using Gemini Vision API.
Provides robust text extraction from scanned PDFs and images.
"""
from __future__ import annotations

import base64
from io import BytesIO
from typing import List, Optional
import httpx

from ..config import settings
from ..logging_config import get_logger

log = get_logger("service.ocr")


class GeminiVisionOCR:
    """
    Uses Gemini 2.0 Flash's vision capabilities for OCR.
    This is the best available OCR for scanned documents.
    """
    
    def __init__(self) -> None:
        self.api_key = settings.llm_api_key
        self.model = "gemini-2.0-flash"
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            log.warning("OCR disabled: No Gemini API key configured")
    
    async def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> Optional[str]:
        """
        Extract text from a PDF using Gemini Vision.
        Converts PDF pages to images and sends to Gemini for OCR.
        """
        if not self.enabled:
            return None
        
        try:
            # Convert PDF to images
            images = self._pdf_to_images(pdf_bytes)
            if not images:
                log.warning("Failed to convert PDF to images")
                return None
            
            # Extract text from each page
            all_text = []
            for i, img_bytes in enumerate(images):
                page_text = await self._extract_text_from_image(img_bytes, page_num=i+1)
                if page_text:
                    all_text.append(f"[Page {i+1}]\n{page_text}")
            
            if not all_text:
                return None
            
            return "\n\n".join(all_text)
            
        except Exception as exc:
            log.error(f"OCR extraction failed: {exc}")
            return None
    
    def _pdf_to_images(self, pdf_bytes: bytes, dpi: int = 150) -> List[bytes]:
        """
        Convert PDF pages to PNG images.
        Uses pdf2image which requires poppler.
        Falls back to PyMuPDF if available.
        """
        images = []
        
        # Try PyMuPDF (fitz) first - no external dependencies
        try:
            import fitz  # PyMuPDF
            pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            for page_num in range(min(len(pdf), 10)):  # Limit to 10 pages
                page = pdf[page_num]
                # Render at 150 DPI
                mat = fitz.Matrix(dpi/72, dpi/72)
                pix = page.get_pixmap(matrix=mat)
                img_bytes = pix.tobytes("png")
                images.append(img_bytes)
            
            pdf.close()
            log.info(f"Converted {len(images)} PDF pages to images using PyMuPDF")
            return images
            
        except ImportError:
            log.warning("PyMuPDF not installed, trying pdf2image")
        except Exception as e:
            log.error(f"PyMuPDF failed: {e}")
        
        # Fallback to pdf2image (requires poppler)
        try:
            from pdf2image import convert_from_bytes
            pil_images = convert_from_bytes(pdf_bytes, dpi=dpi, first_page=1, last_page=10)
            
            for pil_img in pil_images:
                buf = BytesIO()
                pil_img.save(buf, format='PNG')
                images.append(buf.getvalue())
            
            log.info(f"Converted {len(images)} PDF pages to images using pdf2image")
            return images
            
        except ImportError:
            log.error("pdf2image not installed. Install with: pip install pdf2image")
        except Exception as e:
            log.error(f"pdf2image failed: {e}")
        
        return images
    
    async def _extract_text_from_image(self, image_bytes: bytes, page_num: int = 1) -> Optional[str]:
        """
        Send image to Gemini Vision API for OCR.
        """
        if not self.enabled:
            return None
        
        try:
            # Encode image as base64
            b64_image = base64.b64encode(image_bytes).decode('utf-8')
            
            # Prepare request
            url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {
                            "text": """Extract ALL text from this document image. This is an employment contract or offer letter.

Rules:
1. Extract every word exactly as it appears
2. Preserve paragraph structure with line breaks
3. Include all numbers, dates, and amounts exactly
4. If you see tables, format them as readable text
5. Do NOT summarize or interpret - just extract the raw text

Return ONLY the extracted text, nothing else."""
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": b64_image
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 8192,
                }
            }
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                result = response.json()
            
            # Extract text from response
            candidates = result.get("candidates", [])
            if candidates:
                content = candidates[0].get("content", {})
                parts = content.get("parts", [])
                if parts:
                    text = parts[0].get("text", "")
                    log.info(f"OCR extracted {len(text)} chars from page {page_num}")
                    return text
            
            return None
            
        except httpx.HTTPStatusError as e:
            log.error(f"Gemini API error: {e.response.status_code} - {e.response.text[:200]}")
            return None
        except Exception as exc:
            log.error(f"OCR API call failed: {exc}")
            return None
    
    async def extract_text_from_image_bytes(self, image_bytes: bytes) -> Optional[str]:
        """
        Extract text directly from an image (PNG, JPG, etc.)
        """
        return await self._extract_text_from_image(image_bytes)


# Singleton instance
_ocr_instance: Optional[GeminiVisionOCR] = None

def get_ocr_service() -> GeminiVisionOCR:
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = GeminiVisionOCR()
    return _ocr_instance
