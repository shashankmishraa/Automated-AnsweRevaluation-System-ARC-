# ocr.py - Optimized Version
"""
Enhanced OCR Module for Answer Evaluation System - OPTIMIZED for speed.
"""

import io
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import pytesseract
from dataclasses import dataclass
import time

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Structured OCR result."""
    text: str
    confidence: float
    engine: str
    preprocessing_applied: List[str]
    processing_time_ms: float = 0.0
    word_confidences: Optional[List[Tuple[str, float]]] = None


class OptimizedOCR:
    """Optimized OCR processor with fast preprocessing."""
    
    def __init__(self):
        self.easyocr_reader = None
        self._init_easyocr()
        self.cache = {}  # Simple cache for image hashes
    
    def _init_easyocr(self):
        """Initialize EasyOCR reader if available (once)."""
        if self.easyocr_reader is None:
            try:
                import easyocr
                # Use GPU if available, otherwise CPU
                self.easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
                logger.info("✅ EasyOCR initialized")
            except Exception as e:
                logger.warning(f"EasyOCR not available: {e}")
                self.easyocr_reader = None
    
    def _get_image_hash(self, image: Image.Image) -> str:
        """Generate simple hash for caching."""
        import hashlib
        return hashlib.md5(image.tobytes()).hexdigest()[:16]
    
    def fast_preprocess(self, image: Image.Image, mode: str = "auto") -> Image.Image:
        """
        Fast preprocessing - only essential steps.
        """
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Convert to grayscale (fast)
            gray = image.convert('L')
            
            # Simple resize if too large (speed optimization)
            max_size = 1200
            if gray.size[0] > max_size:
                ratio = max_size / gray.size[0]
                new_size = (max_size, int(gray.size[1] * ratio))
                gray = gray.resize(new_size, Image.Resampling.LANCZOS)
            
            if mode == "handwriting":
                # Quick contrast enhancement
                enhancer = ImageEnhance.Contrast(gray)
                gray = enhancer.enhance(1.5)
                
                # Light sharpening
                gray = gray.filter(ImageFilter.SHARPEN)
                
            elif mode == "printed":
                # Simple binarization for printed text
                gray = gray.point(lambda x: 0 if x < 128 else 255, '1')
                
            elif mode == "auto":
                # Auto-detect: check if image has many edges (handwriting) or not
                img_np = np.array(gray)
                edges = cv2.Canny(img_np, 50, 150)
                edge_density = np.sum(edges > 0) / edges.size
                
                if edge_density > 0.05:  # Likely handwriting
                    enhancer = ImageEnhance.Contrast(gray)
                    gray = enhancer.enhance(1.5)
                    gray = gray.filter(ImageFilter.SHARPEN)
                else:  # Likely printed
                    gray = gray.point(lambda x: 0 if x < 128 else 255, '1')
            
            return gray
            
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            return image.convert('L')
    
    def extract_text_fast(self, image: Image.Image, use_gemini: bool = False,
                          gemini_service=None, timeout_ms: int = 3000) -> OCRResult:
        """
        Fast text extraction with timeout.
        """
        start_time = time.time()
        
        # Check cache
        img_hash = self._get_image_hash(image)
        if img_hash in self.cache:
            logger.info(f"Using cached OCR result for {img_hash}")
            return self.cache[img_hash]
        
        # Fast preprocessing (only one pass)
        processed = self.fast_preprocess(image, "auto")
        
        # Try Tesseract first (fastest)
        text, conf = self._extract_fast_tesseract(processed)
        
        # If Tesseract gives poor results, try EasyOCR
        if len(text) < 20 or conf < 0.3:
            if self.easyocr_reader:
                text_easy, conf_easy, word_confs = self._extract_fast_easyocr(processed)
                if len(text_easy) > len(text):
                    text = text_easy
                    conf = conf_easy
                    engine = "easyocr"
                else:
                    engine = "tesseract"
            else:
                engine = "tesseract"
        else:
            engine = "tesseract"
        
        # Quick Gemini enhancement (optional, with timeout)
        if use_gemini and gemini_service and gemini_service.is_available() and len(text) > 10:
            # Only enhance if we have time
            elapsed = (time.time() - start_time) * 1000
            if elapsed < timeout_ms:
                enhanced = self._fast_gemini_enhance(image, text, gemini_service)
                if enhanced and len(enhanced) > len(text):
                    text = enhanced
                    engine += "+gemini"
        
        processing_time = (time.time() - start_time) * 1000
        
        result = OCRResult(
            text=text.strip(),
            confidence=conf,
            engine=engine,
            preprocessing_applied=["fast_preprocessing"],
            processing_time_ms=processing_time,
            word_confidences=None
        )
        
        # Cache result
        if len(text) > 50:
            self.cache[img_hash] = result
        
        return result
    
    def _extract_fast_tesseract(self, image: Image.Image) -> Tuple[str, float]:
        """Fast Tesseract extraction with optimal settings."""
        try:
            # Use optimal PSM for speed
            config = '--psm 6 --oem 3'  # PSM 6 = uniform block of text
            text = pytesseract.image_to_string(image, config=config)
            
            # Quick confidence estimate
            data = pytesseract.image_to_data(image, config=config,
                                              output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if conf != '-1']
            avg_conf = sum(confidences) / len(confidences) / 100 if confidences else 0.5
            
            return text.strip(), avg_conf
            
        except Exception as e:
            logger.error(f"Tesseract error: {e}")
            return "", 0.0
    
    def _extract_fast_easyocr(self, image: Image.Image) -> Tuple[str, float, List]:
        """Fast EasyOCR extraction."""
        if not self.easyocr_reader:
            return "", 0.0, []
        
        try:
            img_np = np.array(image.convert('RGB'))
            # Use greedy decoder for speed
            result = self.easyocr_reader.readtext(
                img_np,
                paragraph=True,
                decoder='greedy'  # Faster than beamsearch
            )
            
            text_parts = []
            confidences = []
            word_confidences = []
            
            for item in result:
                bbox, text, conf = item
                text_parts.append(text)
                confidences.append(conf)
                word_confidences.append((text, conf))
            
            full_text = " ".join(text_parts)
            avg_conf = sum(confidences) / len(confidences) / 100 if confidences else 0
            
            return full_text, avg_conf, word_confidences
            
        except Exception as e:
            logger.error(f"EasyOCR error: {e}")
            return "", 0.0, []
    
    def _fast_gemini_enhance(self, image: Image.Image, ocr_text: str,
                            gemini_service) -> Optional[str]:
        """Quick Gemini enhancement with minimal prompt."""
        if not ocr_text or len(ocr_text) < 20:
            return None
        
        try:
            import google.generativeai as genai
            
            # Resize image for faster upload
            if image.size[0] > 800:
                ratio = 800 / image.size[0]
                new_size = (800, int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            # Short prompt for faster response
            prompt = f"""Fix OCR errors. Return corrected text only:
{ocr_text[:500]}"""

            uploaded_file = genai.upload_file(img_bytes, mime_type="image/jpeg")
            model = genai.GenerativeModel('models/gemini-2.0-flash')
            response = model.generate_content(
                [uploaded_file, prompt],
                generation_config={'max_output_tokens': 300}  # Limit tokens
            )
            
            if response and response.text:
                enhanced = response.text.strip()
                if len(enhanced) > len(ocr_text) * 0.5:
                    return enhanced
            
            return None
            
        except Exception as e:
            logger.error(f"Gemini enhancement error: {e}")
            return None


# Singleton instance
_optimized_ocr = None


def get_optimized_ocr() -> OptimizedOCR:
    """Get or create optimized OCR instance."""
    global _optimized_ocr
    if _optimized_ocr is None:
        _optimized_ocr = OptimizedOCR()
    return _optimized_ocr