"""
PDF processing module for Answer Evaluation System.
Handles text extraction, OCR, and answer parsing.
"""

import re
import io
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

import fitz  # PyMuPDF
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import numpy as np

from config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


@dataclass
class ExtractedQuestion:
    """Represents an extracted question."""
    number: int
    text: str
    marks: int


@dataclass
class ParsedAnswer:
    """Represents a parsed student answer."""
    question_number: int
    text: str
    confidence: float = 1.0


class PDFTextExtractor:
    """Extract text from PDF files."""
    
    @staticmethod
    def extract_text(pdf_bytes: bytes) -> Dict[int, str]:
        """Extract text from PDF pages."""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages_text = {}
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                pages_text[page_num + 1] = text
            
            doc.close()
            return pages_text
            
        except Exception as e:
            logger.error(f"PDF text extraction error: {e}")
            raise PDFProcessingError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def extract_images(pdf_bytes: bytes, dpi: int = 300) -> Dict[int, List[Image.Image]]:
        """Extract images from PDF pages for OCR."""
        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            pages_images = {}
            
            zoom = dpi / 72  # Convert DPI to zoom factor
            mat = fitz.Matrix(zoom, zoom)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))
                pages_images[page_num + 1] = [image]
            
            doc.close()
            return pages_images
            
        except Exception as e:
            logger.error(f"PDF image extraction error: {e}")
            raise PDFProcessingError(f"Failed to extract images from PDF: {str(e)}")


class OCRProcessor:
    """Process images with OCR."""
    
    PSM_MODES = [6, 3, 4, 11]  # Page segmentation modes to try
    _easyocr_reader = None

    @staticmethod
    def _quality_score(text: str) -> float:
        """Heuristic quality score to reject gibberish OCR outputs."""
        if not text:
            return -1e9
        t = text.strip()
        if len(t) < 10:
            return -1e6

        total = len(t)
        alpha = sum(1 for c in t if c.isalpha())
        alnum = sum(1 for c in t if c.isalnum())
        spaces = sum(1 for c in t if c.isspace())
        punct = total - alnum - spaces
        words = len([w for w in t.split() if w])

        alpha_ratio = alpha / total
        punct_ratio = punct / total

        return (
            min(total, 2000) * 0.001
            + alpha_ratio * 3.0
            + min(words, 250) * 0.01
            - punct_ratio * 2.0
        )
    
    @classmethod
    def preprocess_image(cls, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR results."""
        try:
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too small
            min_width = 1500
            if image.size[0] < min_width:
                ratio = min_width / image.size[0]
                new_size = (min_width, int(image.size[1] * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to grayscale
            gray = image.convert('L')
            
            # Apply median filter to reduce noise
            for _ in range(2):
                gray = gray.filter(ImageFilter.MedianFilter(size=3))
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(gray)
            contrasted = enhancer.enhance(2.5)
            
            # Enhance sharpness
            sharpness_enhancer = ImageEnhance.Sharpness(contrasted)
            sharpened = sharpness_enhancer.enhance(2.0)
            
            # Auto contrast
            thresholded = ImageOps.autocontrast(sharpened, cutoff=2)
            
            # Slight brightness increase
            brightness_enhancer = ImageEnhance.Brightness(thresholded)
            final_image = brightness_enhancer.enhance(1.2)
            
            return final_image
            
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            # Return original image as fallback
            return image.convert('L') if image.mode != 'L' else image
    
    @classmethod
    def perform_ocr(cls, image: Image.Image, configs: List[str] = None) -> Tuple[str, float]:
        """Perform OCR with multiple configurations and return best result."""
        if configs is None:
            configs = [f'--psm {psm} --oem 3' for psm in cls.PSM_MODES]
        
        preprocessed = cls.preprocess_image(image)
        candidates: List[Tuple[str, float]] = []

        # Try EasyOCR first (works better on many handwritten cases)
        try:
            import easyocr
            if cls._easyocr_reader is None:
                cls._easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)

            for variant in [image.convert("RGB"), preprocessed.convert("RGB")]:
                arr = np.array(variant)
                for kwargs in [
                    {"paragraph": True},
                    {"paragraph": True, "decoder": "beamsearch"},
                    {"paragraph": False},
                ]:
                    try:
                        result = cls._easyocr_reader.readtext(arr, **kwargs)
                    except TypeError:
                        result = cls._easyocr_reader.readtext(arr)
                    except Exception:
                        continue

                    chunks = [r[1].strip() for r in result if len(r) >= 2 and isinstance(r[1], str) and r[1].strip()]
                    confs = [float(r[2]) for r in result if len(r) >= 3 and isinstance(r[2], (float, int))]
                    text = " ".join(chunks).strip()
                    if text:
                        avg_conf = sum(confs) / len(confs) if confs else 0.5
                        combined = cls._quality_score(text) + avg_conf
                        candidates.append((text, combined))
        except Exception:
            pass
        
        for config in configs:
            try:
                # Extract text
                extracted = pytesseract.image_to_string(preprocessed, config=config)
                
                # Get confidence data
                try:
                    data = pytesseract.image_to_data(
                        preprocessed, 
                        config=config, 
                        output_type=pytesseract.Output.DICT
                    )
                    confidences = [int(conf) for conf in data['conf'] if conf != '-1']
                    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                except Exception:
                    avg_confidence = 50  # Default if confidence extraction fails
                
                cleaned = extracted.strip()
                if cleaned:
                    combined = cls._quality_score(cleaned) + (avg_confidence / 100.0)
                    candidates.append((cleaned, combined))
                    
            except Exception as e:
                logger.warning(f"OCR with config '{config}' failed: {e}")
                continue

        if not candidates:
            return "", 0.0

        best_text, best_score = max(candidates, key=lambda x: x[1])
        near_best = [text for text, score in candidates if score >= (best_score - 0.25)]
        if near_best:
            longest_near_best = max(near_best, key=len)
            if len(longest_near_best) > len(best_text):
                best_text = longest_near_best
        # Map heuristic score into a rough 0-1 confidence band.
        confidence = max(0.0, min(1.0, (best_score + 1.0) / 5.0))
        return best_text, confidence
    
    @classmethod
    def detect_diagram(cls, image: Image.Image) -> bool:
        """Detect if image contains a diagram."""
        try:
            # Try OpenCV first
            import cv2
            cv_img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            lines = cv2.HoughLinesP(
                edges, rho=1, theta=np.pi/180, threshold=50,
                minLineLength=30, maxLineGap=10
            )
            line_count = len(lines) if lines is not None else 0
            edge_density = (edges > 0).sum() / edges.size
            
            return (line_count >= 15) or (edge_density >= 0.04)
            
        except ImportError:
            # Fallback to PIL
            try:
                edge_img = image.convert("L").filter(ImageFilter.FIND_EDGES)
                bw = edge_img.point(lambda p: 255 if p > 30 else 0)
                pixels = list(bw.getdata())
                dark = sum(1 for p in pixels if p == 0)
                edge_density = dark / len(pixels)
                return edge_density >= 0.04
            except Exception as e:
                logger.warning(f"Diagram detection failed: {e}")
                return False


class TextCleaner:
    """Clean and normalize extracted text."""
    
    CHEMICAL_PATTERNS = [
        (r'(?i)c\s*o\s*2', 'CO2'),
        (r'(?i)h\s*2\s*o', 'H2O'),
        (r'(?i)o\s*2', 'O2'),
        (r'(?i)c\s*o', 'CO'),
        (r'(?i)n\s*2', 'N2'),
        (r'(?i)h\s*2', 'H2'),
    ]
    
    @classmethod
    def clean(cls, text: str) -> str:
        """Clean extracted text."""
        if not text:
            return ""
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix chemical formulas
        for pattern, replacement in cls.CHEMICAL_PATTERNS:
            text = re.sub(pattern, replacement, text)
        
        # Fix punctuation spacing
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        text = re.sub(r'([.,!?;:])\s*', r'\1 ', text)
        
        # Capitalize sentence starts
        sentences = re.split(r'([.!?])\s*', text)
        cleaned_sentences = []
        for i, part in enumerate(sentences):
            if part and part not in '.!?':
                if i == 0 or (i > 0 and sentences[i-1] in '.!?'):
                    part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
            cleaned_sentences.append(part)
        
        text = ''.join(cleaned_sentences)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()


class AnswerParser:
    """Parse answers from extracted text."""
    
    QUESTION_PATTERNS = [
        r'(?i)(?:q(?:uestion)?\.?\s*(\d+))[.):\s]+(.+)',
        r'(?i)(\d+)[.):\s]+(.+)',
    ]
    
    MARKS_PATTERNS = [
        r'(?i)\[(\d+)\s*(?:marks?|m)\]',
        r'(?i)\((\d+)\s*(?:marks?|m)\)',
        r'(?i)marks?\s*[:=]?\s*(\d+)',
        r'(?i)(\d+)\s*marks?',
    ]
    
    @classmethod
    def parse_questions(cls, text: str) -> List[ExtractedQuestion]:
        """Extract questions and marks from question paper text."""
        questions = []
        lines = text.split('\n')
        current_q = None
        current_marks_found = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to match question pattern
            q_match = None
            for pattern in cls.QUESTION_PATTERNS:
                q_match = re.match(pattern, line)
                if q_match:
                    break

            # Try to match marks pattern on this line
            marks = None
            for pattern in cls.MARKS_PATTERNS:
                marks_match = re.search(pattern, line)
                if marks_match:
                    marks = int(marks_match.group(1))
                    break

            if q_match:
                if current_q:
                    questions.append(current_q)
                current_q = ExtractedQuestion(
                    number=int(q_match.group(1)),
                    text=q_match.group(2).strip(),
                    marks=marks if marks is not None else 5  # default
                )
                current_marks_found = marks is not None
            elif current_q and line:
                # Append continuation line to current question text
                current_q.text += ' ' + line
                # Update marks if found on a continuation line and not yet found
                if not current_marks_found and marks is not None:
                    current_q.marks = marks
                    current_marks_found = True
                elif marks is not None:
                    # Always take the last marks value found (overrides default)
                    current_q.marks = marks

        if current_q:
            questions.append(current_q)

        return questions
    
    @classmethod
    def extract_answer_for_question(
        cls,
        all_text: str,
        question_num: int,
        next_question_num: Optional[int] = None
    ) -> str:
        """Extract student answer for specific question number."""
        # End boundary: start of next question or end of string
        if next_question_num:
            pattern_end = (
                rf'(?:q\.?\s*{next_question_num}[\s:.\)]'
                rf'|question\s*{next_question_num}[\s:.\)]'
                rf'|(?:^|\s){next_question_num}[.:\)]\s)'
            )
        else:
            pattern_end = r'\Z'

        # Patterns ordered from most specific to least
        # Handles: Q1. Q1: Q1) Q 1. question 1. 1. 1)
        # Also skips the question text itself and captures from Ans: onward if present
        q_header = (
            rf'(?i)(?:q\.?\s*{question_num}|question\s*{question_num}'
            rf'|(?:^|\n)\s*{question_num}[.:\)])'
            rf'[^\n]*\n'  # skip the question line
        )
        # Try to find "Ans:" marker after question header
        ans_pattern = rf'{q_header}(?:ans\s*[:\-]?\s*\n?)?(.+?)(?={pattern_end})'
        match = re.search(ans_pattern, all_text, re.DOTALL | re.IGNORECASE)
        if match:
            answer = match.group(1).strip()
            # Strip leading "Ans:" if OCR merged it onto the same line
            answer = re.sub(r'^(?i)ans\s*[:\-]?\s*', '', answer).strip()
            if len(answer) >= 10:
                return TextCleaner.clean(answer)

        # Fallback: line-by-line parsing
        lines = all_text.split('\n')
        in_answer = False
        skip_next = False  # skip the "Ans:" line itself
        answer_lines = []

        q_patterns = [
            rf'(?i)^\s*q\.?\s*{question_num}[\s:.\)]',
            rf'(?i)^\s*question\s*{question_num}[\s:.\)]',
            rf'(?i)^\s*{question_num}[.:\)]\s',
        ]
        next_q_patterns = []
        if next_question_num:
            next_q_patterns = [
                rf'(?i)^\s*q\.?\s*{next_question_num}[\s:.\)]',
                rf'(?i)^\s*question\s*{next_question_num}[\s:.\)]',
                rf'(?i)^\s*{next_question_num}[.:\)]\s',
            ]

        for line in lines:
            # Check if we've hit the next question
            if next_q_patterns and any(re.search(p, line) for p in next_q_patterns):
                break
            if not in_answer:
                if any(re.search(p, line) for p in q_patterns):
                    in_answer = True
                    skip_next = False
                    continue
            else:
                # Skip standalone "Ans:" lines
                if re.match(r'(?i)^\s*ans\s*[:\-]?\s*$', line):
                    continue
                # Strip inline "Ans:" prefix
                line = re.sub(r'(?i)^\s*ans\s*[:\-]?\s*', '', line)
                answer_lines.append(line)

        return TextCleaner.clean(' '.join(answer_lines))
    
    @classmethod
    def parse_reference_answers(
        cls,
        ref_text: str,
        questions: List[ExtractedQuestion]
    ) -> Dict[int, str]:
        """Parse reference answers for given questions."""
        ref_answers = {}
        
        for i, q in enumerate(questions):
            q_num = q.number
            next_q_num = questions[i + 1].number if i + 1 < len(questions) else None
            
            patterns = [
                rf'(?i)q\.?\s*{q_num}[\s:.\)]+(.+?)(?=q\.?\s*{q_num + 1}|\Z)',
                rf'(?i)question\s*{q_num}[\s:.\)]+(.+?)(?=question\s*{q_num + 1}|\Z)',
                rf'(?i){q_num}[.):\s]+(.+?)(?={q_num + 1}[.):\s]|\Z)',
            ]
            
            ref_ans = ""
            for pattern in patterns:
                match = re.search(pattern, ref_text, re.DOTALL)
                if match:
                    ref_ans = TextCleaner.clean(match.group(1))
                    break
            
            ref_answers[q_num] = ref_ans if ref_ans else "Reference answer not found"
        
        return ref_answers


class PDFProcessingError(Exception):
    """Custom exception for PDF processing errors."""
    pass


class PDFProcessor:
    """Main PDF processing class."""
    
    def __init__(self):
        self.text_extractor = PDFTextExtractor()
        self.ocr_processor = OCRProcessor()
        self.text_cleaner = TextCleaner()
        self.answer_parser = AnswerParser()
    
    def process_answer_sheet(
        self,
        pdf_bytes: bytes,
        use_ocr_threshold: int = None
    ) -> str:
        """Process student answer sheet, using OCR if needed."""
        use_ocr_threshold = use_ocr_threshold or settings.OCR_MIN_TEXT_LENGTH
        
        # Extract text
        pages = self.text_extractor.extract_text(pdf_bytes)
        total_text = ' '.join(pages.values())

        # If extracted text looks low-quality (common for scanned handwritten PDFs),
        # fall back to OCR even if length passes the threshold.
        try:
            extracted_quality = self.ocr_processor._quality_score(total_text)
        except Exception:
            extracted_quality = -1e9
        
        # Use OCR if text is too sparse
        if len(total_text.strip()) < use_ocr_threshold or extracted_quality < 0.5:
            logger.info("Text extraction yielded sparse results, running OCR...")
            images = self.text_extractor.extract_images(pdf_bytes, dpi=300)
            
            ocr_texts = []
            for page_num, page_images in images.items():
                for img in page_images:
                    text, confidence = self.ocr_processor.perform_ocr(img)
                    if text.strip():
                        ocr_texts.append(text)
            
            total_text = ' '.join(ocr_texts)
            logger.info(f"OCR extracted {len(total_text)} characters")
        
        return self.text_cleaner.clean(total_text)
    
    def process_question_paper(self, pdf_bytes: bytes) -> List[ExtractedQuestion]:
        """Process question paper and extract questions."""
        pages = self.text_extractor.extract_text(pdf_bytes)
        text = ' '.join(pages.values())
        return self.answer_parser.parse_questions(text)
    
    def process_reference_answers(
        self,
        pdf_bytes: bytes,
        questions: List[ExtractedQuestion]
    ) -> Dict[int, str]:
        """Process reference answers PDF."""
        pages = self.text_extractor.extract_text(pdf_bytes)
        text = ' '.join(pages.values())
        return self.answer_parser.parse_reference_answers(text, questions)


# Convenience function
def get_pdf_processor() -> PDFProcessor:
    """Get PDF processor instance."""
    return PDFProcessor()
