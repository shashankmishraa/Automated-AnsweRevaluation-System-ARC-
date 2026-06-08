"""
Main FastAPI application for Answer Evaluation System.
Professional production-ready API with auto-reference generation and LLM scoring.
"""

import time
import asyncio
import logging
import re
from difflib import SequenceMatcher
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import modules
from config import get_settings
from security import sanitize_text
from models import get_model_manager
from scoring import ScoreCalculator, determine_grade, grammar_score, coverage_score, generate_feedback, perform_gap_analysis, GeminiEnhancedScorer
from database import get_db_manager
from pdf_processor import get_pdf_processor, OCRProcessor
from security import FileValidator
from auto_ref_generator import get_reference_generator
from demo_data import generate_demo_ocr_response, generate_demo_batch_response, generate_demo_pdf_response, generate_demo_text_response, generate_demo_cs_pdf_response

settings = get_settings()

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL), format=settings.LOG_FORMAT)
logger = logging.getLogger(__name__)

_easyocr_reader = None

REF_ANSWERS_LOG = "ref_answers_log.txt"

def _log_ref_answer(mode: str, question: str, reference_answer: str, eval_id: str = ""):
    """Append AI-generated reference answer to the log file."""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sep = "=" * 60
        entry = (
            f"\n{sep}\n"
            f"Timestamp  : {timestamp}\n"
            f"Mode       : {mode}\n"
            f"Eval ID    : {eval_id}\n"
            f"Question   : {question[:200]}\n"
            f"{'-' * 60}\n"
            f"Reference Answer:\n{reference_answer}\n"
            f"{sep}\n"
        )
        with open(REF_ANSWERS_LOG, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception as e:
        logger.warning(f"Failed to log ref answer: {e}")


def _get_llm_usage_stats() -> Dict[str, Any]:
    """Get current LLM API usage statistics."""
    from gemini_service import get_gemini_service
    llm = get_gemini_service()
    usage_count = getattr(llm, '_usage_count', 0)
    return {
        "llm_available": llm.is_available(),
        "session_api_calls": usage_count,
        "daily_limit": 1500,
        "remaining_calls": max(0, 1500 - usage_count)
    }



def _enhance_ocr_with_llm_vision(pil_img, ocr_text: str) -> str:
    """Use LLM Vision API to enhance and correct OCR-extracted text."""
    from gemini_service import get_gemini_service
    from PIL import Image
    import io
    
    llm = get_gemini_service()
    
    if not llm.is_available():
        return ocr_text
    
    try:
        import google.generativeai as genai
        
        if pil_img.size[0] > 800:
            ratio = 800 / pil_img.size[0]
            new_size = (800, int(pil_img.size[1] * ratio))
            pil_img = pil_img.resize(new_size, Image.Resampling.LANCZOS)
        
        img_bytes = io.BytesIO()
        pil_img.save(img_bytes, format='JPEG', quality=85)
        img_bytes.seek(0)
        
        prompt = f"""Fix OCR errors. Return corrected text only:
{ocr_text[:500]}"""

        uploaded_file = genai.upload_file(img_bytes, mime_type="image/jpeg")
        model = genai.GenerativeModel('models/gemini-2.0-flash')
        llm._usage_count += 1
        
        response = model.generate_content(
            [uploaded_file, prompt],
            generation_config={'max_output_tokens': 300}
        )
        
        if response and response.text:
            enhanced_text = response.text.strip()
            if len(enhanced_text) > len(ocr_text) * 0.5:
                return enhanced_text
        return ocr_text
            
    except Exception as e:
        logger.error(f"LLM enhancement error: {e}")
        return ocr_text


def _ocr_with_easyocr(pil_img) -> Dict[str, Any]:
    """Run EasyOCR and return best text."""
    import numpy as np

    global _easyocr_reader
    if _easyocr_reader is None:
        import easyocr
        _easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)

    arr = np.array(pil_img.convert("RGB"))
    
    try:
        results = _easyocr_reader.readtext(arr, paragraph=True)
        text_parts = []
        for item in results:
            if len(item) >= 2:
                text = item[1]
                if text and text.strip():
                    text_parts.append(text.strip())
        text = " ".join(text_parts)
        return {"best_text": text, "raw_text": text}
    except Exception as e:
        logger.error(f"EasyOCR error: {e}")
        return {"best_text": "", "raw_text": ""}


def _ocr_fast(pil_img) -> str:
    """Fast OCR using pytesseract."""
    try:
        import pytesseract
        from PIL import ImageEnhance
        
        # Simple preprocessing
        gray = pil_img.convert('L')
        enhancer = ImageEnhance.Contrast(gray)
        gray = enhancer.enhance(1.5)
        
        # OCR
        text = pytesseract.image_to_string(gray, config='--psm 6 --oem 3')
        return text.strip()
    except Exception as e:
        logger.error(f"Fast OCR error: {e}")
        return ""


# Pydantic models
class AnswerRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    reference_answer: Optional[str] = Field(None, max_length=5000)
    student_answer: str = Field(..., min_length=1, max_length=5000)
    model_name: Optional[str] = None
    student_name: Optional[str] = None


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Answer Evaluation API...")
    get_model_manager()
    get_db_manager()
    yield
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered answer evaluation system with OCR",
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper functions
def get_scoring_metrics(reference: str, student: str, question: str, model_name: Optional[str] = None, use_cnn: bool = False):
    model_manager = get_model_manager()
    metrics = {
        "similarity": model_manager.compute_similarity(reference, student, model_name),
        "coverage": coverage_score(reference, student),
        "grammar": grammar_score(student),
        "relevance": model_manager.compute_relevance(question, student, model_name)
    }
    
    if use_cnn:
        metrics["cnn_score"] = model_manager.compute_cnn_score(reference, student)

    return metrics


# ============= MAIN ENDPOINTS =============

@app.get("/")
async def root():
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}


@app.get("/health")
async def health_check():
    model_manager = get_model_manager()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "models": model_manager.health_check(),
        "version": settings.APP_VERSION,
        "llm_status": _get_llm_usage_stats()
    }


@app.post("/evaluate")
async def evaluate(request: Request, data: AnswerRequest):
    start_time = time.time()
    
    question = sanitize_text(data.question)
    student = sanitize_text(data.student_answer)
    
    use_auto_reference = request.query_params.get("auto_ref", "false").lower() == "true"
    use_cnn = request.query_params.get("use_cnn", "false").lower() == "true"
    use_llm = request.query_params.get("use_llm", "false").lower() == "true"
    
    if use_auto_reference and question:
        try:
            generator = get_reference_generator()
            generated_ref = generator.generate_reference_answer(question)
            reference = generated_ref.generated_answer if generated_ref else student
        except Exception as e:
            logger.warning(f"Auto-reference generation failed: {e}")
            reference = sanitize_text(data.reference_answer) or student
    else:
        reference = sanitize_text(data.reference_answer) if data.reference_answer else student
    
    metrics = get_scoring_metrics(reference, student, question, data.model_name, use_cnn)
    
    llm_scorer = GeminiEnhancedScorer()
    llm_result = None
    llm_used = False
    
    if use_llm:
        llm_result = llm_scorer.score_with_gemini(question, reference, student)
        if llm_result:
            llm_used = True
            if 'coverage' in llm_result:
                metrics['coverage'] = round(metrics['coverage'] * 0.7 + llm_result['coverage'] * 0.3, 3)
            if 'relevance' in llm_result:
                metrics['relevance'] = round(metrics['relevance'] * 0.7 + llm_result['relevance'] * 0.3, 3)
    
    calculator = ScoreCalculator(use_cnn=use_cnn)
    final_score = calculator.calculate_final_score(**metrics)
    grade = determine_grade(final_score)
    
    if llm_result and llm_result.get('feedback'):
        feedback = llm_result['feedback']
    else:
        feedback = generate_feedback(final_score, **{k: v for k, v in metrics.items() if k != 'cnn_score'})
    
    if llm_result and (llm_result.get('matched_concepts') or llm_result.get('missing_concepts')):
        gap_analysis = {
            'matched': [{'concept': c, 'status': 'correct'} for c in llm_result.get('matched_concepts', [])],
            'missing': [{'concept': c, 'importance': 'high', 'marks_worth': 2} for c in llm_result.get('missing_concepts', [])],
            'llm_enhanced': True
        }
    else:
        gap_analysis = perform_gap_analysis(reference, student)
    
    processing_time_ms = int((time.time() - start_time) * 1000)
    _log_ref_answer("text", question, reference, str(int(time.time())))

    db = get_db_manager()
    eval_id = db.save_evaluation(
        evaluation_type="single",
        student_name=data.student_name,
        question=question,
        student_answer=student,
        reference_answer=reference,
        similarity_score=metrics['similarity'],
        coverage_score=metrics['coverage'],
        grammar_score=metrics['grammar'],
        relevance_score=metrics['relevance'],
        final_score=final_score,
        grade=grade,
        feedback=feedback,
        processing_time_ms=processing_time_ms
    )
    
    response = {
        "question": question,
        "student_answer": student,
        "reference_answer": reference,
        "similarity": metrics["similarity"],
        "coverage": metrics["coverage"],
        "grammar": metrics["grammar"],
        "relevance": metrics["relevance"],
        "final_score": final_score,
        "grade": grade,
        "feedback": feedback,
        "gap_analysis": gap_analysis,
        "evaluation_id": eval_id,
        "processing_time_ms": processing_time_ms,
        "llm_usage": _get_llm_usage_stats()
    }
    
    if llm_used:
        response["llm_enhanced"] = True
        response["llm_scoring_details"] = {
            "overall_score": llm_result.get('overall', 0) * 10 if llm_result else None,
            "accuracy": llm_result.get('accuracy_score', 0) if llm_result else None,
            "clarity": llm_result.get('clarity_score', 0) if llm_result else None,
            "completeness": llm_result.get('completeness_score', 0) if llm_result else None
        }
        if llm_result and llm_result.get('matched_concepts'):
            response["matched_concepts"] = llm_result.get('matched_concepts', [])
            response["missing_concepts"] = llm_result.get('missing_concepts', [])
    else:
        response["llm_enhanced"] = False
    
    if use_cnn and "cnn_score" in metrics:
        response["cnn_score"] = metrics["cnn_score"]
    
    return response


@app.get("/models")
async def list_models():
    model_manager = get_model_manager()
    return model_manager.get_available_models()


@app.get("/statistics")
async def get_statistics():
    db = get_db_manager()
    return db.get_statistics()


# ============= OCR ENDPOINTS =============


def _normalize_reference_answer(question: str, reference_answer: str) -> str:
    """Ensure reference answer is not too generic, fallback to question-based template."""
    if not reference_answer or not reference_answer.strip():
        return f"A detailed answer to '{question}' should explain the main concepts with examples."

    cleaned = reference_answer.strip()
    if cleaned.lower().startswith("reference answer for") or len(cleaned) < 40:
        return f"A detailed answer to '{question}' should explain the main concepts with examples."

    return cleaned


@app.post("/evaluate/ocr")
async def evaluate_ocr(
    image: UploadFile = File(...),
    question_text: str = Form(None),
    use_llm: bool = Form(False)
):
    """OCR evaluation for single images (basic mode)."""
    from PIL import Image
    import io
    
    start_time = time.time()
    
    try:
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        image_bytes = await image.read()
        FileValidator.validate_file_size(image_bytes)
        FileValidator.validate_file_type(image_bytes)
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Try EasyOCR first
        try:
            ocr_result = _ocr_with_easyocr(pil_img)
            extracted_text = ocr_result.get("best_text", "")
        except:
            extracted_text = _ocr_fast(pil_img)
        
        if not extracted_text:
            extracted_text = "No text could be extracted from the image."
        
        question = question_text or "OCR-based question"
        student_answer = sanitize_text(extracted_text[:5000], max_length=5000)
        
        generator = get_reference_generator()
        generated_ref = generator.generate_reference_answer(question)
        reference_answer = generated_ref.generated_answer if generated_ref else f"Reference answer for: {question}"
        reference_answer = _normalize_reference_answer(question, reference_answer)
        
        model_manager = get_model_manager()
        metrics = {
            'similarity': model_manager.compute_similarity(reference_answer, student_answer),
            'coverage': coverage_score(reference_answer, student_answer),
            'grammar': grammar_score(student_answer),
            'relevance': model_manager.compute_relevance(question, student_answer)
        }
        
        llm_used = False
        if use_llm:
            llm_scorer = GeminiEnhancedScorer()
            llm_result = llm_scorer.score_with_gemini(question, reference_answer, student_answer)
            if llm_result:
                llm_used = True
                if 'coverage' in llm_result:
                    metrics['coverage'] = metrics['coverage'] * 0.7 + llm_result['coverage'] * 0.3
                if 'relevance' in llm_result:
                    metrics['relevance'] = metrics['relevance'] * 0.7 + llm_result['relevance'] * 0.3
        
        calculator = ScoreCalculator()
        final_score = calculator.calculate_final_score(**metrics)
        grade = determine_grade(final_score)
        feedback = generate_feedback(final_score, **metrics)
        gap_analysis = perform_gap_analysis(reference_answer, student_answer)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        _log_ref_answer("ocr", question, reference_answer, str(int(time.time())))

        db = get_db_manager()
        eval_id = db.save_evaluation(
            evaluation_type="ocr",
            question=question,
            student_answer=student_answer,
            reference_answer=reference_answer,
            similarity_score=metrics['similarity'],
            coverage_score=metrics['coverage'],
            grammar_score=metrics['grammar'],
            relevance_score=metrics['relevance'],
            final_score=final_score,
            grade=grade,
            feedback=feedback,
            processing_time_ms=processing_time_ms
        )
        
        return {
            "question": question,
            "student_answer": student_answer,
            "reference_answer": reference_answer,
            "extracted_text": extracted_text[:1000],
            "similarity": metrics["similarity"],
            "coverage": metrics["coverage"],
            "grammar": metrics["grammar"],
            "relevance": metrics["relevance"],
            "final_score": final_score,
            "grade": grade,
            "feedback": feedback,
            "gap_analysis": gap_analysis,
            "evaluation_id": eval_id,
            "processing_time_ms": processing_time_ms,
            "llm_used": llm_used,
            "llm_usage": _get_llm_usage_stats()
        }
        
    except Exception as e:
        logger.error(f"OCR evaluation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.post("/evaluate/ocr-fast")
async def evaluate_ocr_fast(
    image: UploadFile = File(...),
    question_text: str = Form(None),
    use_llm: bool = Form(False)
):
    """FAST OCR evaluation - optimized for speed (1-3 seconds)."""
    from PIL import Image
    import io
    
    start_time = time.time()
    
    try:
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        image_bytes = await image.read()
        FileValidator.validate_file_size(image_bytes)
        FileValidator.validate_file_type(image_bytes)
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Fast OCR using pytesseract
        extracted_text = _ocr_fast(pil_img)
        
        if not extracted_text:
            extracted_text = "No text could be extracted."
        
        question = question_text or "OCR-based question"
        student_answer = sanitize_text(extracted_text[:2000], max_length=2000)
        
        generator = get_reference_generator()
        generated_ref = generator.generate_reference_answer(question)
        reference_answer = generated_ref.generated_answer if generated_ref else student_answer
        reference_answer = _normalize_reference_answer(question, reference_answer)
        
        model_manager = get_model_manager()
        similarity = model_manager.compute_similarity(reference_answer, student_answer)
        coverage = coverage_score(reference_answer, student_answer)
        grammar = grammar_score(student_answer)
        relevance = model_manager.compute_relevance(question, student_answer)
        
        final_score = (similarity + coverage + grammar + relevance) / 4 * 10
        grade = determine_grade(final_score)
        feedback = generate_feedback(final_score, similarity, coverage, grammar, relevance)
        _log_ref_answer("ocr-fast", question, reference_answer, str(int(time.time())))

        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "question": question,
            "student_answer": student_answer,
            "reference_answer": reference_answer,
            "extracted_text": extracted_text[:1000],
            "similarity": round(similarity, 3),
            "coverage": round(coverage, 3),
            "grammar": round(grammar, 3),
            "relevance": round(relevance, 3),
            "final_score": round(final_score, 2),
            "grade": grade,
            "feedback": feedback,
            "processing_time_ms": processing_time_ms,
            "ocr_mode": "fast",
            "llm_usage": _get_llm_usage_stats()
        }
        
    except Exception as e:
        logger.error(f"Fast OCR error: {e}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


@app.post("/evaluate/ocr-accurate")
async def evaluate_ocr_accurate(
    image: UploadFile = File(...),
    question_text: str = Form(None),
    use_llm: bool = Form(True),
    preprocessing: str = Form("handwriting")
):
    """ACCURATE OCR evaluation - optimized for accuracy (5-10 seconds)."""
    from PIL import Image
    import io
    
    start_time = time.time()
    
    try:
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")

        image_bytes = await image.read()
        FileValidator.validate_file_size(image_bytes)
        FileValidator.validate_file_type(image_bytes)
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Preprocess based on mode
        if preprocessing == "handwriting":
            # Enhance contrast and sharpen for handwriting
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(pil_img)
            pil_img = enhancer.enhance(1.8)
            enhancer = ImageEnhance.Sharpness(pil_img)
            pil_img = enhancer.enhance(2.0)
        
        # Use EasyOCR for better accuracy
        ocr_result = _ocr_with_easyocr(pil_img)
        extracted_text = ocr_result.get("best_text", "")
        
        if not extracted_text:
            extracted_text = _ocr_fast(pil_img)
        
        # Enhance with LLM if enabled
        if use_llm and extracted_text:
            from gemini_service import get_gemini_service
            llm = get_gemini_service()
            if llm.is_available():
                enhanced = _enhance_ocr_with_llm_vision(pil_img, extracted_text)
                if enhanced != extracted_text:
                    extracted_text = enhanced
        
        if not extracted_text:
            extracted_text = "No text could be extracted."
        
        question = question_text or "OCR-based question"
        student_answer = sanitize_text(extracted_text[:5000], max_length=5000)
        
        generator = get_reference_generator()
        generated_ref = generator.generate_reference_answer(question)
        reference_answer = generated_ref.generated_answer if generated_ref else student_answer
        reference_answer = _normalize_reference_answer(question, reference_answer)
        
        model_manager = get_model_manager()
        metrics = {
            'similarity': model_manager.compute_similarity(reference_answer, student_answer),
            'coverage': coverage_score(reference_answer, student_answer),
            'grammar': grammar_score(student_answer),
            'relevance': model_manager.compute_relevance(question, student_answer)
        }
        
        # LLM scoring
        llm_used = False
        if use_llm:
            llm_scorer = GeminiEnhancedScorer()
            llm_result = llm_scorer.score_with_gemini(question, reference_answer, student_answer)
            if llm_result:
                llm_used = True
                if 'coverage' in llm_result:
                    metrics['coverage'] = metrics['coverage'] * 0.7 + llm_result['coverage'] * 0.3
                if 'relevance' in llm_result:
                    metrics['relevance'] = metrics['relevance'] * 0.7 + llm_result['relevance'] * 0.3
        
        calculator = ScoreCalculator()
        final_score = calculator.calculate_final_score(**metrics)
        grade = determine_grade(final_score)
        feedback = generate_feedback(final_score, **metrics)
        gap_analysis = perform_gap_analysis(reference_answer, student_answer)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        _log_ref_answer("ocr-accurate", question, reference_answer, str(int(time.time())))

        db = get_db_manager()
        eval_id = db.save_evaluation(
            evaluation_type="ocr_accurate",
            question=question,
            student_answer=student_answer,
            reference_answer=reference_answer,
            similarity_score=metrics['similarity'],
            coverage_score=metrics['coverage'],
            grammar_score=metrics['grammar'],
            relevance_score=metrics['relevance'],
            final_score=final_score,
            grade=grade,
            feedback=feedback,
            processing_time_ms=processing_time_ms
        )
        
        return {
            "question": question,
            "student_answer": student_answer,
            "reference_answer": reference_answer,
            "extracted_text": extracted_text[:1000],
            "similarity": metrics["similarity"],
            "coverage": metrics["coverage"],
            "grammar": metrics["grammar"],
            "relevance": metrics["relevance"],
            "final_score": final_score,
            "grade": grade,
            "feedback": feedback,
            "gap_analysis": gap_analysis,
            "evaluation_id": eval_id,
            "processing_time_ms": processing_time_ms,
            "ocr_mode": "accurate",
            "llm_enhanced_ocr": use_llm,
            "llm_scoring_used": llm_used,
            "llm_usage": _get_llm_usage_stats()
        }
        
    except Exception as e:
        logger.error(f"Accurate OCR error: {e}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")


# ============= DEMO MODE ENDPOINTS =============

@app.post("/evaluate/pdf-handwritten-demo")
async def evaluate_pdf_handwritten_demo(
    use_llm: bool = Form(False),
    mode: str = Form("fast")
):
    """DEMO MODE - Evaluate using sample PDFs from project directory."""
    import io
    import fitz
    from PIL import Image
    
    start_time = time.time()
    
    try:
        # Load sample PDFs from project directory
        with open("sample_student_answers.pdf", "rb") as f:
            answer_pdf_bytes = f.read()
        
        with open("sample_question_paper.pdf", "rb") as f:
            question_pdf_bytes = f.read()
        
        # Process question paper
        processor = get_pdf_processor()
        questions = processor.process_question_paper(question_pdf_bytes)
        
        if not questions:
            raise HTTPException(status_code=400, detail="No questions found in sample question paper")
        
        # OCR the handwritten answers
        doc = fitz.open(stream=answer_pdf_bytes, filetype="pdf")
        extracted_chunks = []
        
        dpi = 150 if mode == "fast" else 250
        
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            pix = page.get_pixmap(dpi=dpi)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            
            if mode == "fast":
                text = _ocr_fast(img)
            else:
                ocr_result = _ocr_with_easyocr(img)
                text = ocr_result.get("best_text", "")
                if use_llm and text:
                    text = _enhance_ocr_with_llm_vision(img, text)
            
            if text:
                extracted_chunks.append(text)
        
        doc.close()
        extracted_text = " ".join(extracted_chunks).strip()
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text could be extracted from sample PDFs")
        
        student_answer_text = sanitize_text(extracted_text[:10000], max_length=10000)
        
        # Generate references and score
        generator = get_reference_generator()
        ref_answers = generator.generate_references_for_questions(questions)
        
        llm_scorer = GeminiEnhancedScorer() if use_llm else None
        
        results = []
        total_obtained = 0.0
        total_marks = sum(q.marks for q in questions)
        llm_used_count = 0
        
        calculator = ScoreCalculator()
        
        for idx, q in enumerate(questions):
            next_q_num = questions[idx + 1].number if idx + 1 < len(questions) else None
            extracted_ans = processor.answer_parser.extract_answer_for_question(student_answer_text, q.number, next_q_num)
            ref_ans = ref_answers.get(q.number, "")
            
            if not extracted_ans or len(extracted_ans) < 10:
                similarity = coverage = obtained = 0.0
                feedback = "No answer detected"
            elif not ref_ans:
                similarity = coverage = 0.5
                obtained = q.marks * 0.5
                feedback = "Reference unavailable"
            else:
                similarity = get_model_manager().compute_similarity(ref_ans, extracted_ans)
                coverage = coverage_score(ref_ans, extracted_ans)
                grammar = grammar_score(extracted_ans)
                relevance = get_model_manager().compute_relevance(q.text, extracted_ans)
                
                llm_result = None
                if use_llm and llm_scorer:
                    llm_result = llm_scorer.score_with_gemini(q.text, ref_ans, extracted_ans)
                    if llm_result:
                        llm_used_count += 1
                        if 'coverage' in llm_result:
                            coverage = coverage * 0.7 + llm_result['coverage'] * 0.3
                        if 'relevance' in llm_result:
                            relevance = relevance * 0.7 + llm_result['relevance'] * 0.3
                
                final_score_normalized = calculator.calculate_final_score(similarity, coverage, grammar, relevance)
                obtained = (final_score_normalized / 10.0) * q.marks
                
                percentage = (obtained / q.marks) * 100 if q.marks > 0 else 0
                
                if percentage >= 90:
                    feedback = "Excellent!"
                elif percentage >= 75:
                    feedback = "Good"
                elif percentage >= 60:
                    feedback = "Satisfactory"
                else:
                    feedback = "Needs improvement"
            
            results.append({
                "question_number": q.number,
                "question_text": q.text[:200],
                "extracted_answer": extracted_ans[:500] if extracted_ans else "No answer",
                "generated_reference": ref_ans[:300] if ref_ans else "No reference",
                "max_marks": q.marks,
                "obtained_marks": round(obtained, 2),
                "similarity_score": round(similarity, 3),
                "coverage_score": round(coverage, 3),
                "feedback": feedback
            })
            total_obtained += obtained
        
        percentage = (total_obtained / total_marks) * 100 if total_marks > 0 else 0
        grade = determine_grade(percentage, max_score=100)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return {
            "questions_results": results,
            "total_score": round(total_obtained, 2),
            "total_marks": total_marks,
            "percentage": round(percentage, 2),
            "grade": grade,
            "extracted_text": student_answer_text,
            "processing_time_ms": processing_time_ms,
            "llm_used": llm_used_count > 0,
            "demo_mode": True,
            "sample_pdfs_used": True
        }
        
    except Exception as e:
        logger.error(f"Demo PDF evaluation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Demo processing failed: {str(e)}")


@app.post("/evaluate/ocr-demo")
async def evaluate_ocr_demo(
    subject: str = Form("general")
):
    """DEMO MODE - Return preset OCR evaluation results for demonstration."""
    await asyncio.sleep(0.5)
    return generate_demo_ocr_response(subject)


@app.post("/evaluate/batch-demo")
async def evaluate_batch_demo():
    """DEMO MODE - Return preset batch evaluation results for demonstration."""
    await asyncio.sleep(1.0)
    return generate_demo_batch_response()


@app.post("/evaluate/pdf-demo")
async def evaluate_pdf_demo():
    """DEMO MODE - Return preset PDF handwritten evaluation results."""
    await asyncio.sleep(1.0)
    return generate_demo_pdf_response()


@app.post("/evaluate/cs-pdf-demo")
async def evaluate_cs_pdf_demo():
    """DEMO MODE - Return preset CS PDF evaluation results with gap analysis."""
    await asyncio.sleep(1.0)
    return generate_demo_cs_pdf_response()


@app.post("/evaluate/text-demo")
async def evaluate_text_demo(
    subject: str = Form("general")
):
    """DEMO MODE - Return preset text evaluation results."""
    await asyncio.sleep(0.8)
    return generate_demo_text_response(subject)


# ============= PDF HANDWRITTEN ENDPOINTS =============

@app.post("/evaluate/pdf-handwritten")
async def evaluate_pdf_handwritten(
    pdf: UploadFile = File(...),
    question_paper: Optional[UploadFile] = File(None),
    question_text: str = Form(None),
    use_llm: bool = Form(False),
    mode: str = Form("fast")  # "fast" or "accurate"
):
    """Evaluate handwritten PDF with OCR."""
    import io
    import fitz
    from PIL import Image
    
    start_time = time.time()
    
    try:
        if not pdf.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")

        pdf_bytes = await pdf.read()
        FileValidator.validate_file_size(pdf_bytes)
        
        # OCR the handwritten PDF to get full text
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        extracted_chunks = []
        
        dpi = 150 if mode == "fast" else 250
        
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            pix = page.get_pixmap(dpi=dpi)
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data)).convert("RGB")
            
            if mode == "fast":
                text = _ocr_fast(img)
            else:
                ocr_result = _ocr_with_easyocr(img)
                text = ocr_result.get("best_text", "")
                if use_llm and text:
                    text = _enhance_ocr_with_llm_vision(img, text)
            
            if text:
                extracted_chunks.append(text)
        
        doc.close()
        extracted_text = " ".join(extracted_chunks).strip()
        
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No text could be extracted from PDF")
        
        student_answer_text = sanitize_text(extracted_text[:10000], max_length=10000)
        
        # Check if question_paper is provided for multi-question evaluation
        if question_paper:
            if not question_paper.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="Question paper must be a PDF")
            question_bytes = await question_paper.read()
            processor = get_pdf_processor()
            questions = processor.process_question_paper(question_bytes)
            
            if not questions:
                raise HTTPException(status_code=400, detail="No questions found in question paper")
            
            generator = get_reference_generator()
            ref_answers = generator.generate_references_for_questions(questions)
            for q in questions:
                if q.number in ref_answers:
                    _log_ref_answer("pdf-handwritten", q.text, ref_answers[q.number], str(int(time.time())))

            llm_scorer = GeminiEnhancedScorer() if use_llm else None
            
            results = []
            total_obtained = 0.0
            total_marks = sum(q.marks for q in questions)
            llm_used_count = 0
            
            calculator = ScoreCalculator()
            db = get_db_manager()
            
            for idx, q in enumerate(questions):
                next_q_num = questions[idx + 1].number if idx + 1 < len(questions) else None
                extracted_ans = processor.answer_parser.extract_answer_for_question(student_answer_text, q.number, next_q_num)
                ref_ans = ref_answers.get(q.number, "")
                
                if not extracted_ans or len(extracted_ans) < 10:
                    similarity = coverage = obtained = 0.0
                    feedback = "No answer detected"
                elif not ref_ans:
                    similarity = coverage = 0.5
                    obtained = q.marks * 0.5
                    feedback = "Reference unavailable"
                else:
                    similarity = get_model_manager().compute_similarity(ref_ans, extracted_ans)
                    coverage = coverage_score(ref_ans, extracted_ans)
                    grammar = grammar_score(extracted_ans)
                    relevance = get_model_manager().compute_relevance(q.text, extracted_ans)
                    
                    llm_result = None
                    if use_llm and llm_scorer:
                        llm_result = llm_scorer.score_with_gemini(q.text, ref_ans, extracted_ans)
                        if llm_result:
                            llm_used_count += 1
                            if 'coverage' in llm_result:
                                coverage = coverage * 0.7 + llm_result['coverage'] * 0.3
                            if 'relevance' in llm_result:
                                relevance = relevance * 0.7 + llm_result['relevance'] * 0.3
                    
                    final_score_normalized = calculator.calculate_final_score(similarity, coverage, grammar, relevance)
                    obtained = (final_score_normalized / 10.0) * q.marks
                    
                    percentage = (obtained / q.marks) * 100 if q.marks > 0 else 0
                    
                    if percentage >= 90:
                        feedback = "Excellent!"
                    elif percentage >= 75:
                        feedback = "Good"
                    elif percentage >= 60:
                        feedback = "Satisfactory"
                    else:
                        feedback = "Needs improvement"
                
                results.append({
                    "question_number": q.number,
                    "question_text": q.text[:200],
                    "extracted_answer": extracted_ans[:500] if extracted_ans else "No answer",
                    "generated_reference": ref_ans[:300] if ref_ans else "No reference",
                    "max_marks": q.marks,
                    "obtained_marks": round(obtained, 2),
                    "similarity_score": round(similarity, 3),
                    "coverage_score": round(coverage, 3),
                    "feedback": feedback
                })
                total_obtained += obtained
            
            percentage = (total_obtained / total_marks) * 100 if total_marks > 0 else 0
            grade = determine_grade(percentage, max_score=100)
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            db.save_evaluation(
                evaluation_type="pdf_handwritten_multi",
                question=f"Multi-question evaluation ({len(questions)} questions)",
                student_answer=student_answer_text[:2000],
                reference_answer=f"Multiple references generated",
                final_score=percentage,
                grade=grade,
                metrics={"total_questions": len(questions), "llm_used": llm_used_count > 0},
                processing_time_ms=processing_time_ms
            )
            
            return {
                "questions_results": results,
                "total_score": round(total_obtained, 2),
                "total_marks": total_marks,
                "percentage": round(percentage, 2),
                "grade": grade,
                "extracted_text": student_answer_text,
                "processing_time_ms": processing_time_ms,
                "llm_used": llm_used_count > 0,
                "llm_usage": _get_llm_usage_stats()
            }
        
        # Single question mode (fallback or when no question_paper)
        question = question_text or "Handwritten question"
        
        generator = get_reference_generator()
        generated_ref = generator.generate_reference_answer(question)
        reference_answer = generated_ref.generated_answer if generated_ref else student_answer_text
        
        model_manager = get_model_manager()
        metrics = {
            'similarity': model_manager.compute_similarity(reference_answer, student_answer_text),
            'coverage': coverage_score(reference_answer, student_answer_text),
            'grammar': grammar_score(student_answer_text),
            'relevance': model_manager.compute_relevance(question, student_answer_text)
        }
        
        llm_used = False
        if use_llm:
            llm_scorer = GeminiEnhancedScorer()
            llm_result = llm_scorer.score_with_gemini(question, reference_answer, student_answer_text)
            if llm_result:
                llm_used = True
                if 'coverage' in llm_result:
                    metrics['coverage'] = metrics['coverage'] * 0.7 + llm_result['coverage'] * 0.3
                if 'relevance' in llm_result:
                    metrics['relevance'] = metrics['relevance'] * 0.7 + llm_result['relevance'] * 0.3
        
        calculator = ScoreCalculator()
        final_score = calculator.calculate_final_score(**metrics)
        grade = determine_grade(final_score)
        feedback = generate_feedback(final_score, **metrics)
        gap_analysis = perform_gap_analysis(reference_answer, student_answer_text)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        db = get_db_manager()
        eval_id = db.save_evaluation(
            evaluation_type="pdf_handwritten_single",
            question=question,
            student_answer=student_answer_text,
            reference_answer=reference_answer,
            final_score=final_score,
            grade=grade,
            metrics=metrics,
            processing_time_ms=processing_time_ms
        )
        
        return {
            "score": final_score,
            "grade": grade,
            "percentage": round((final_score / 10.0) * 100, 2),
            "feedback": feedback,
            "metrics": {
                "similarity": round(metrics['similarity'], 3),
                "coverage": round(metrics['coverage'], 3),
                "grammar": round(metrics['grammar'], 3),
                "relevance": round(metrics['relevance'], 3)
            },
            "gap_analysis": gap_analysis,
            "extracted_text": student_answer_text,
            "question": question,
            "reference_answer": reference_answer,
            "processing_time_ms": processing_time_ms,
            "llm_used": llm_used,
            "llm_usage": _get_llm_usage_stats()
        }
        
    except Exception as e:
        logger.error(f"PDF handwritten evaluation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF processing failed: {str(e)}")


# ============= BATCH ENDPOINTS =============

@app.post("/evaluate/batch")
async def evaluate_batch(
    batch_file: UploadFile = File(...),
    reference_answer: str = Form(None),
    auto_ref: bool = Form(False),
    use_llm: bool = Form(False)
):
    start_time = time.time()
    
    try:
        if not batch_file.filename.lower().endswith('.zip'):
            raise HTTPException(status_code=400, detail="File must be a ZIP archive")

        import zipfile
        import io

        zip_content = await batch_file.read()
        FileValidator.validate_file_size(zip_content)
        
        with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
            file_list = zip_file.namelist()
            
            question_files = [f for f in file_list if 'question' in f.lower()]
            if not question_files:
                raise HTTPException(status_code=400, detail="No question file found")
            
            question_file = question_files[0]
            question_text = zip_file.read(question_file).decode('utf-8')
            
            student_files = [f for f in file_list if 'answer' in f.lower() and f.endswith('.txt')]
            if not student_files:
                raise HTTPException(status_code=400, detail="No student answer files found")
            
            student_files.sort()
            
            if auto_ref or not reference_answer:
                generator = get_reference_generator()
                generated_ref = generator.generate_reference_answer(question_text)
                reference = generated_ref.generated_answer if generated_ref else ""
            else:
                reference = reference_answer
            
            if not reference:
                raise HTTPException(status_code=400, detail="Reference answer required")
            _log_ref_answer("batch", question_text, reference, str(int(time.time())))

            llm_scorer = GeminiEnhancedScorer() if use_llm else None
            
            results = []
            calculator = ScoreCalculator()
            db = get_db_manager()
            llm_used_count = 0
            
            for student_file in student_files:
                student_name = student_file.replace('_answer.txt', '').replace('.txt', '')
                student_answer = zip_file.read(student_file).decode('utf-8')
                
                metrics = get_scoring_metrics(reference, student_answer, question_text, use_cnn=False)
                
                llm_result = None
                if use_llm and llm_scorer:
                    llm_result = llm_scorer.score_with_gemini(question_text, reference, student_answer)
                    if llm_result:
                        llm_used_count += 1
                        if 'coverage' in llm_result:
                            metrics['coverage'] = metrics['coverage'] * 0.7 + llm_result['coverage'] * 0.3
                        if 'relevance' in llm_result:
                            metrics['relevance'] = metrics['relevance'] * 0.7 + llm_result['relevance'] * 0.3
                
                final_score = calculator.calculate_final_score(**metrics)
                grade = determine_grade(final_score)
                
                if llm_result and llm_result.get('feedback'):
                    feedback = llm_result['feedback']
                else:
                    feedback = generate_feedback(final_score, **{k: v for k, v in metrics.items() if k != 'cnn_score'})
                
                results.append({
                    "student_name": student_name,
                    "student_answer": student_answer[:500],
                    "similarity": round(metrics["similarity"], 3),
                    "coverage": round(metrics["coverage"], 3),
                    "grammar": round(metrics["grammar"], 3),
                    "relevance": round(metrics["relevance"], 3),
                    "final_score": round(final_score, 2),
                    "grade": grade,
                    "feedback": feedback[:200]
                })
            
            total_students = len(results)
            avg_score = sum(r["final_score"] for r in results) / total_students if total_students > 0 else 0
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            eval_id = db.save_evaluation(
                evaluation_type="batch",
                exam_name=f"Batch Evaluation - {total_students} students",
                final_score=round(avg_score, 2),
                grade=determine_grade(avg_score),
                processing_time_ms=processing_time_ms
            )
            
            return {
                "evaluation_id": eval_id,
                "question": question_text[:500],
                "reference_answer": reference[:500],
                "total_students": total_students,
                "average_score": round(avg_score, 2),
                "results": results,
                "processing_time_ms": processing_time_ms,
                "llm_usage": _get_llm_usage_stats(),
                "llm_scoring_used": use_llm,
                "students_with_llm": llm_used_count if use_llm else 0
            }
            
    except Exception as e:
        logger.error(f"Batch evaluation error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch evaluation failed: {str(e)}")


# ============= PDF AUTO ENDPOINT =============

@app.post("/evaluate/pdf-auto")
async def evaluate_pdf_auto(
    answer_sheet: UploadFile = File(...),
    question_paper: UploadFile = File(...),
    student_name: str = Form(""),
    exam_name: str = Form("Auto-Evaluation"),
    use_llm: bool = Form(False)
):
    start_time = time.time()
    
    try:
        answer_content = await answer_sheet.read()
        question_content = await question_paper.read()
        
        processor = get_pdf_processor()
        generator = get_reference_generator()
        
        answer_text = processor.process_answer_sheet(answer_content)
        questions = processor.process_question_paper(question_content)
        
        if not questions:
            raise HTTPException(status_code=400, detail="No questions found")
        
        ref_answers = generator.generate_references_for_questions(questions)
        
        llm_scorer = GeminiEnhancedScorer() if use_llm else None
        
        results = []
        total_obtained = 0.0
        total_marks = sum(q.marks for q in questions)
        llm_used_count = 0
        
        calculator = ScoreCalculator()
        db = get_db_manager()
        
        for idx, q in enumerate(questions):
            next_q_num = questions[idx + 1].number if idx + 1 < len(questions) else None
            extracted_ans = processor.answer_parser.extract_answer_for_question(answer_text, q.number, next_q_num)
            ref_ans = ref_answers.get(q.number, "")
            
            if not extracted_ans or len(extracted_ans) < 10:
                similarity = coverage = obtained = 0.0
                feedback = "No answer detected"
            elif not ref_ans:
                similarity = coverage = 0.5
                obtained = q.marks * 0.5
                feedback = "Reference unavailable"
            else:
                similarity = get_model_manager().compute_similarity(ref_ans, extracted_ans)
                coverage = coverage_score(ref_ans, extracted_ans)
                grammar = grammar_score(extracted_ans)
                relevance = get_model_manager().compute_relevance(q.text, extracted_ans)
                
                llm_result = None
                if use_llm and llm_scorer:
                    llm_result = llm_scorer.score_with_gemini(q.text, ref_ans, extracted_ans)
                    if llm_result:
                        llm_used_count += 1
                        if 'coverage' in llm_result:
                            coverage = coverage * 0.7 + llm_result['coverage'] * 0.3
                        if 'relevance' in llm_result:
                            relevance = relevance * 0.7 + llm_result['relevance'] * 0.3
                
                final_score_normalized = calculator.calculate_final_score(similarity, coverage, grammar, relevance)
                obtained = (final_score_normalized / 10.0) * q.marks
                
                percentage = (obtained / q.marks) * 100 if q.marks > 0 else 0
                
                if percentage >= 90:
                    feedback = "Excellent!"
                elif percentage >= 75:
                    feedback = "Good"
                elif percentage >= 60:
                    feedback = "Satisfactory"
                else:
                    feedback = "Needs improvement"
            
            results.append({
                "question_number": q.number,
                "question_text": q.text[:200],
                "extracted_answer": extracted_ans[:500] if extracted_ans else "No answer",
                "generated_reference": ref_ans[:300] if ref_ans else "No reference",
                "max_marks": q.marks,
                "obtained_marks": round(obtained, 2),
                "similarity_score": round(similarity, 3),
                "coverage_score": round(coverage, 3),
                "feedback": feedback
            })
            total_obtained += obtained
        
        percentage = (total_obtained / total_marks) * 100 if total_marks > 0 else 0
        grade = determine_grade(percentage, max_score=100)
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        eval_id = db.save_evaluation(
            evaluation_type="pdf_auto",
            student_name=student_name or "Anonymous",
            exam_name=exam_name,
            final_score=round(total_obtained, 2),
            grade=grade,
            processing_time_ms=processing_time_ms
        )
        
        return {
            "evaluation_id": eval_id,
            "student_name": student_name or "Anonymous",
            "exam_name": exam_name,
            "total_max_marks": total_marks,
            "total_obtained_marks": round(total_obtained, 2),
            "percentage": round(percentage, 2),
            "grade": grade,
            "questions_results": results,
            "processing_time_ms": processing_time_ms,
            "reference_generation_note": "Reference answers were auto-generated from questions",
            "llm_usage": _get_llm_usage_stats(),
            "llm_scoring_used": use_llm,
            "questions_with_llm": llm_used_count if use_llm else 0
        }
        
    except Exception as e:
        logger.error(f"PDF evaluation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


class RefLogRequest(BaseModel):
    text: str

@app.post("/log-ref-answers")
async def log_ref_answers(data: RefLogRequest):
    """Append AI reference answers from demo mode to the log file."""
    try:
        with open(REF_ANSWERS_LOG, "a", encoding="utf-8") as f:
            f.write(data.text + "\n")
        return {"status": "ok"}
    except Exception as e:
        logger.warning(f"Failed to write ref log: {e}")
        return {"status": "error"}


@app.get("/history")
async def get_history(limit: int = 20, evaluation_type: Optional[str] = None):
    """Get recent evaluation history for score trend chart."""
    db = get_db_manager()
    records = db.get_evaluations(evaluation_type=evaluation_type, limit=limit)
    return [
        {
            "id": r["id"],
            "timestamp": r["timestamp"],
            "evaluation_type": r["evaluation_type"],
            "final_score": r["final_score"],
            "grade": r["grade"],
            "student_name": r["student_name"],
            "question": r["question"][:80] if r["question"] else None,
        }
        for r in records if r["final_score"] is not None
    ]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
