"""
PDF parser for extracting text from contract PDFs.
Uses pdfplumber for better text extraction quality.
Supports OCR for image-based PDFs using Tesseract.
"""
import re
import os
import glob
import shutil
from pathlib import Path
from typing import Optional
import pdfplumber
from loguru import logger
import io

# Optional OCR support for image-based PDFs
try:
    import pytesseract
    from PIL import Image, ImageEnhance
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR libraries not installed. Image-based PDFs may not be fully processed. Install with: pip install pytesseract Pillow")

# Optional pdf2image for better PDF to image conversion
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    logger.warning("pdf2image not installed. OCR may be limited. Install with: pip install pdf2image")


def _find_poppler_path() -> Optional[str]:
    """
    Find Poppler installation path by checking common locations.
    Returns the path to the bin directory containing pdftoppm.exe
    """
    # Common Poppler installation paths
    poppler_paths = [
        r"C:\Program Files\poppler-*\Library\bin",
        r"C:\Program Files (x86)\poppler-*\Library\bin",
        r"C:\poppler\Library\bin",
        r"C:\poppler\bin",
        os.path.expanduser(r"~\poppler\Library\bin"),
        os.path.expanduser(r"~\poppler\bin"),
    ]
    
    # Also check if it's already in PATH
    if shutil.which("pdftoppm"):
        return None  # Already in PATH, no need to specify
    
    # Check common installation locations
    for pattern in poppler_paths:
        # Handle wildcards
        if '*' in pattern:
            matches = glob.glob(pattern)
            for match in matches:
                if os.path.exists(os.path.join(match, "pdftoppm.exe")):
                    logger.debug(f"Found Poppler at: {match}")
                    return match
        else:
            if os.path.exists(os.path.join(pattern, "pdftoppm.exe")):
                logger.debug(f"Found Poppler at: {pattern}")
                return pattern
    
    return None


def _find_tesseract_path() -> Optional[str]:
    """
    Find Tesseract OCR installation path by checking common locations.
    Returns the path to tesseract.exe
    """
    # Common Tesseract installation paths
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expanduser(r"~\AppData\Local\Tesseract-OCR\tesseract.exe"),
        r"C:\Tesseract-OCR\tesseract.exe",
    ]
    
    # Also check if it's already in PATH
    tesseract_in_path = shutil.which("tesseract")
    if tesseract_in_path:
        logger.debug(f"Tesseract found in PATH at: {tesseract_in_path}")
        return tesseract_in_path
    
    # Check common installation locations
    for tesseract_exe in tesseract_paths:
        if os.path.exists(tesseract_exe):
            logger.debug(f"Found Tesseract at: {tesseract_exe}")
            return tesseract_exe
    
    return None


# Find Poppler path at module load time
POPPLER_PATH = _find_poppler_path()
if POPPLER_PATH:
    logger.info(f"Auto-detected Poppler at: {POPPLER_PATH}")
    # Add to PATH for this process
    os.environ['PATH'] = POPPLER_PATH + os.pathsep + os.environ.get('PATH', '')

# Find Tesseract path at module load time and configure pytesseract
TESSERACT_PATH = None
if OCR_AVAILABLE:
    TESSERACT_PATH = _find_tesseract_path()
    if TESSERACT_PATH:
        logger.info(f"Auto-detected Tesseract at: {TESSERACT_PATH}")
        # Configure pytesseract to use the found path
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        # Also add Tesseract directory to PATH
        tesseract_dir = os.path.dirname(TESSERACT_PATH)
        os.environ['PATH'] = tesseract_dir + os.pathsep + os.environ.get('PATH', '')
    else:
        logger.warning("Tesseract not found. OCR will not work. Install Tesseract and add to PATH.")


class PDFParser:
    """
    Extracts text from PDF files with header/footer removal.
    
    Design choice: pdfplumber over PyPDF2 because it:
    - Better preserves text structure
    - Handles tables and complex layouts
    - More reliable for legal documents
    """
    
    def __init__(self):
        self.header_footer_patterns = [
            r"Page \d+ of \d+",
            r"\d+/\d+",
            r"CONFIDENTIAL",
            r"Page \d+",
        ]
    
    def extract_text(self, file_path: Path) -> str:
        """
        Extract raw text from PDF file with robust OCR support for rotated/scanned documents.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid PDF
        """
        if not file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.suffix.lower() == ".pdf":
            raise ValueError(f"File is not a PDF: {file_path}")
        
        logger.info(f"Extracting text from PDF: {file_path.name}")
        
        full_text = []
        
        try:
            with pdfplumber.open(file_path) as pdf:
                total_pages = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Try text extraction first
                    text = page.extract_text()
                    
                    # If no text found or very little text, try OCR for image-based PDFs
                    # Only attempt OCR if text is very minimal (< 50 chars) to avoid unnecessary processing
                    if not text or len(text.strip()) < 50:
                        if OCR_AVAILABLE:
                            # Only log for first few pages to avoid spam
                            if page_num <= 3 or page_num % 10 == 0:
                                logger.info(f"Page {page_num}/{total_pages} has little/no text, attempting fast OCR...")
                            ocr_text = self._extract_text_with_ocr_robust(file_path, page_num, total_pages)
                            if ocr_text and len(ocr_text.strip()) > 10:
                                text = ocr_text
                                if page_num <= 3 or page_num % 10 == 0:
                                    logger.info(f"OCR extracted {len(text)} characters from page {page_num}")
                            else:
                                if page_num <= 3:
                                    logger.debug(f"OCR returned minimal text for page {page_num}")
                        else:
                            if page_num <= 3:
                                logger.warning(f"Page {page_num} has no extractable text and OCR is not available")
                    
                    if text:
                        # Remove common headers/footers
                        cleaned_text = self._remove_headers_footers(text)
                        full_text.append(cleaned_text)
                        logger.debug(f"Extracted {len(text)} chars from page {page_num}")
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            raise ValueError(f"Failed to parse PDF: {e}")
        
        result = "\n\n".join(full_text)
        logger.info(f"Extracted {len(result)} total characters from PDF")
        
        return result
    
    def _extract_text_with_ocr_robust(self, file_path: Path, page_num: int, total_pages: int) -> Optional[str]:
        """
        Extract text from PDF page using OCR with rotation detection and correction.
        Tries multiple orientations (0°, 90°, 180°, 270°) and picks the best result.
        
        Args:
            file_path: Path to PDF file
            page_num: Page number (1-indexed)
            total_pages: Total number of pages
            
        Returns:
            Extracted text or None if OCR fails
        """
        if not OCR_AVAILABLE:
            return None
        
        try:
            # Get page image using pdf2image (preferred) or pdfplumber fallback
            pil_image = self._get_page_image(file_path, page_num)
            if pil_image is None:
                return None
            
            # Quick check: Skip OCR if image is too small (likely blank/empty)
            width, height = pil_image.size
            if width < 100 or height < 100:
                logger.debug(f"Page {page_num}: Image too small ({width}x{height}), skipping OCR")
                return None
            
            # Enhance image quality for better OCR
            pil_image = self._enhance_image_for_ocr(pil_image)
            
            # Optimized OCR: Try 0° first (most common), then other rotations only if needed
            # Use fewer PSM modes for speed
            best_text = ""
            best_confidence = 0
            best_rotation = 0
            
            # Simplified config - no whitelist for speed (let Tesseract handle it)
            char_whitelist = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,;:!?()- /&%$#@*+=|<>'
            
            # Try rotations in order: 0° (most common), then 90°, 180°, 270° only if needed
            rotations = [0, 90, 180, 270]
            # Try PSM 6 first (uniform block - fastest and most common), then 3 if needed
            psm_modes = [6, 3]  # Reduced from 3 to 2 modes for speed
            
            for rotation in rotations:
                try:
                    # Rotate image only if needed
                    if rotation == 0:
                        rotated_image = pil_image
                    else:
                        rotated_image = pil_image.rotate(-rotation, expand=True)
                    
                    # Try PSM modes
                    for psm in psm_modes:
                        try:
                            ocr_config = f'--psm {psm}'
                            
                            # Fast OCR - just get text, skip confidence check initially
                            ocr_text = pytesseract.image_to_string(
                                rotated_image,
                                lang='eng',
                                config=ocr_config
                            )
                            
                            text_length = len(ocr_text.strip())
                            
                            # Quick check: if we got substantial text, use it
                            if text_length > 200:
                                # Good result - get confidence for verification
                                try:
                                    ocr_data = pytesseract.image_to_data(
                                        rotated_image,
                                        lang='eng',
                                        config=ocr_config,
                                        output_type=pytesseract.Output.DICT
                                    )
                                    confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
                                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                                    
                                    # If confidence is reasonable, use this result immediately
                                    if avg_confidence > 50:
                                        logger.info(f"Page {page_num}: Fast OCR success at {rotation}° (PSM {psm}, {text_length} chars, {avg_confidence:.1f}% confidence)")
                                        return ocr_text
                                except:
                                    # If confidence check fails but we have text, use it
                                    if text_length > 300:
                                        logger.info(f"Page {page_num}: Fast OCR success at {rotation}° (PSM {psm}, {text_length} chars)")
                                        return ocr_text
                            
                            # Track best result so far
                            score = text_length
                            if score > best_confidence:
                                best_text = ocr_text
                                best_confidence = score
                                best_rotation = rotation
                                
                        except Exception as e:
                            logger.debug(f"OCR failed for page {page_num} at {rotation}° with PSM {psm}: {e}")
                            continue
                    
                    # Early exit: if we got good text at 0°, don't try other rotations
                    if rotation == 0 and len(best_text.strip()) > 150:
                        logger.debug(f"Page {page_num}: Good result at 0°, skipping other rotations")
                        break
                        
                except Exception as e:
                    logger.debug(f"Rotation {rotation}° failed for page {page_num}: {e}")
                    continue
            
            if best_text and len(best_text.strip()) > 10:
                if best_rotation > 0:
                    logger.info(f"Page {page_num}: OCR successful with {best_rotation}° rotation correction")
                return best_text
            else:
                logger.warning(f"Page {page_num}: OCR failed to extract meaningful text")
                return None
                
        except Exception as e:
            logger.warning(f"OCR extraction failed for page {page_num}: {e}")
            return None
    
    def _get_page_image(self, file_path: Path, page_num: int) -> Optional[Image.Image]:
        """
        Get PIL Image from PDF page using pdf2image (preferred) or pdfplumber fallback.
        
        Args:
            file_path: Path to PDF file
            page_num: Page number (1-indexed)
            
        Returns:
            PIL Image or None if conversion fails
        """
        try:
            # Try pdf2image first (better quality)
            if PDF2IMAGE_AVAILABLE:
                try:
                    # Use poppler_path if we found it, otherwise rely on PATH
                    convert_kwargs = {
                        'first_page': page_num,
                        'last_page': page_num,
                        'dpi': 300,  # High DPI for better OCR accuracy
                        'fmt': 'RGB'
                    }
                    if POPPLER_PATH:
                        convert_kwargs['poppler_path'] = POPPLER_PATH
                    
                    images = convert_from_path(str(file_path), **convert_kwargs)
                    if images:
                        return images[0]
                except Exception as e:
                    error_msg = str(e)
                    if "poppler" in error_msg.lower() or "path" in error_msg.lower():
                        logger.warning(f"Poppler not found for page {page_num}. Install Poppler and add to PATH, or use pdfplumber fallback.")
                        if POPPLER_PATH:
                            logger.debug(f"Tried Poppler path: {POPPLER_PATH}")
                    else:
                        logger.debug(f"pdf2image failed for page {page_num}, trying fallback: {e}")
            
            # Fallback: Use pdfplumber's to_image
            try:
                with pdfplumber.open(file_path) as pdf:
                    if page_num <= len(pdf.pages):
                        page = pdf.pages[page_num - 1]
                        im = page.to_image(resolution=300)
                        return im.original
            except Exception as e:
                logger.debug(f"pdfplumber image conversion failed: {e}")
            
            return None
        except Exception as e:
            logger.warning(f"Failed to get image for page {page_num}: {e}")
            return None
    
    def _enhance_image_for_ocr(self, image: Image.Image) -> Image.Image:
        """
        Enhance image quality for better OCR accuracy.
        
        Args:
            image: PIL Image
            
        Returns:
            Enhanced PIL Image
        """
        try:
            # Convert to grayscale if needed (OCR works better on grayscale)
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)  # Increase contrast by 50%
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)  # Increase sharpness by 20%
            
            return image
        except Exception as e:
            logger.debug(f"Image enhancement failed: {e}")
            return image
    
    def _remove_headers_footers(self, text: str) -> str:
        """
        Remove common header/footer patterns from text.
        
        Args:
            text: Raw text from page
            
        Returns:
            Text with headers/footers removed
        """
        lines = text.split("\n")
        cleaned_lines = []
        
        for line in lines:
            # Skip lines matching header/footer patterns
            is_header_footer = any(
                re.search(pattern, line, re.IGNORECASE)
                for pattern in self.header_footer_patterns
            )
            
            # Skip very short lines that are likely page numbers
            if not is_header_footer and len(line.strip()) > 3:
                cleaned_lines.append(line)
        
        return "\n".join(cleaned_lines)
    
    def extract_metadata(self, file_path: Path) -> dict:
        """
        Extract basic metadata from PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with file metadata
        """
        metadata = {
            "filename": file_path.name,
            "file_size": file_path.stat().st_size,
            "file_type": "pdf",
        }
        
        try:
            with pdfplumber.open(file_path) as pdf:
                metadata["num_pages"] = len(pdf.pages)
        except Exception:
            metadata["num_pages"] = 0
        
        return metadata

