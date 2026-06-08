"""
Debug script to test OCR-based scoring with question paper and handwritten answers.
This will help identify why scores are zero and answers aren't being detected.
"""

import fitz  # PyMuPDF
from PIL import Image
import io
from pdf_processor import get_pdf_processor
from auto_ref_generator import get_reference_generator
from main import _ocr_fast, _ocr_with_easyocr


def debug_pdf_extraction(pdf_path: str):
    """Debug PDF text and image extraction."""
    print(f"\n{'='*60}")
    print(f"Debugging: {pdf_path}")
    print('='*60)
    
    try:
        with open(pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        # Try text extraction first
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        print(f"\n📄 PDF has {len(doc)} pages")
        
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text()
            print(f"\n--- Page {page_idx + 1} ---")
            print(f"Text length: {len(text)} characters")
            
            if len(text) > 50:
                print(f"Preview: {text[:200]}...")
            else:
                print(f"Content: '{text}'")
        
        doc.close()
        
        # Try OCR on first page
        print("\n\n🔍 Testing OCR on first page...")
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc[0]
        pix = page.get_pixmap(dpi=200)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data)).convert("RGB")
        
        # Test fast OCR
        print("\n⚡ Fast OCR (pytesseract):")
        fast_text = _ocr_fast(img)
        print(f"Extracted: {len(fast_text)} chars")
        if fast_text:
            print(f"Preview: {fast_text[:300]}...")
        
        # Test EasyOCR
        print("\n🎯 EasyOCR:")
        easy_result = _ocr_with_easyocr(img)
        easy_text = easy_result.get("best_text", "")
        print(f"Extracted: {len(easy_text)} chars")
        if easy_text:
            print(f"Preview: {easy_text[:300]}...")
        
        doc.close()
        
        return pdf_bytes
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def debug_question_parsing(question_pdf_path: str):
    """Debug question paper parsing."""
    print(f"\n{'='*60}")
    print("Testing Question Paper Parsing")
    print('='*60)
    
    try:
        with open(question_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        processor = get_pdf_processor()
        questions = processor.process_question_paper(pdf_bytes)
        
        print(f"\n✅ Found {len(questions)} questions:")
        for q in questions:
            print(f"\n  Q{q.number}: {q.text[:100]}...")
            print(f"     Marks: {q.marks}")
        
        return questions
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def debug_answer_extraction(answer_pdf_path: str, question_numbers: list):
    """Debug answer extraction from handwritten PDF."""
    print(f"\n{'='*60}")
    print("Testing Answer Extraction")
    print('='*60)
    
    try:
        with open(answer_pdf_path, 'rb') as f:
            pdf_bytes = f.read()
        
        processor = get_pdf_processor()
        
        # Process with OCR
        extracted_text = processor.process_answer_sheet(pdf_bytes, use_ocr_threshold=50)
        
        print(f"\n📝 Total extracted text: {len(extracted_text)} characters")
        print(f"\nPreview:\n{extracted_text[:500]}...\n")
        
        # Try to extract answers for each question
        for q_num in question_numbers:
            print(f"\n{'-'*40}")
            print(f"Looking for Answer to Question {q_num}")
            print('-'*40)
            
            # Extract answer
            next_q = q_num + 1 if q_num < max(question_numbers) else None
            answer = processor.answer_parser.extract_answer_for_question(
                extracted_text, 
                q_num, 
                next_q
            )
            
            if answer and len(answer) > 10:
                print(f"✅ Found answer ({len(answer)} chars):")
                print(f"{answer[:200]}...")
            else:
                print(f"❌ No answer detected!")
                print(f"   Trying alternative patterns...")
                
                # Try simpler pattern
                import re
                patterns = [
                    rf'(?i)q\.?\s*{q_num}[\s:.\)]+(.+?)(?=q\.?\s*{q_num + 1}|\Z)',
                    rf'(?i){q_num}[.):\s]+(.+?)(?={q_num + 1}[.):\s]|\Z)',
                    rf'(?i)^{q_num}\.?\s+(.+?)(?=^{q_num + 1}\.|\Z)',
                ]
                
                for i, pattern in enumerate(patterns):
                    match = re.search(pattern, extracted_text, re.DOTALL | re.MULTILINE)
                    if match:
                        print(f"  Pattern {i+1} matched: {match.group(1)[:100]}...")
                        break
                else:
                    print(f"  No patterns matched")
        
        return extracted_text
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None


def debug_reference_generation(questions):
    """Debug reference answer generation."""
    print(f"\n{'='*60}")
    print("Testing Reference Answer Generation")
    print('='*60)
    
    try:
        generator = get_reference_generator()
        ref_answers = generator.generate_references_for_questions(questions)
        
        print(f"\n✅ Generated {len(ref_answers)} reference answers:")
        for q_num, ref_ans in ref_answers.items():
            print(f"\n  Q{q_num}:")
            print(f"  Length: {len(ref_ans)} chars")
            print(f"  Preview: {ref_ans[:150]}...")
        
        return ref_answers
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}


def main():
    """Main debug function."""
    print("\n🔍 OCR SCORING DEBUG TOOL")
    print("="*60)
    
    # Test with sample files
    question_pdf = "sample_question_paper.pdf"
    answer_pdf = "sample_student_answers.pdf"
    ref_pdf = "sample_reference_answers.pdf"
    
    import os
    if not os.path.exists(question_pdf):
        print(f"\n❌ Sample files not found. Please provide file paths.")
        question_pdf = input("Enter question paper PDF path: ").strip()
        answer_pdf = input("Enter student answers PDF path: ").strip()
    
    # Step 1: Debug question paper
    questions = debug_question_parsing(question_pdf)
    
    if not questions:
        print("\n⚠️  No questions found. Cannot proceed with debugging.")
        return
    
    # Step 2: Debug answer extraction
    question_numbers = [q.number for q in questions]
    extracted_text = debug_answer_extraction(answer_pdf, question_numbers)
    
    if not extracted_text:
        print("\n⚠️  No text extracted from answers. Cannot proceed.")
        return
    
    # Step 3: Debug reference generation
    ref_answers = debug_reference_generation(questions)
    
    # Step 4: Summary
    print(f"\n{'='*60}")
    print("DEBUG SUMMARY")
    print('='*60)
    print(f"Questions found: {len(questions)}")
    print(f"Reference answers generated: {len(ref_answers)}")
    print(f"\nPotential issues to check:")
    print("1. Are question numbers in answers matching the question paper?")
    print("2. Is the handwriting clear enough for OCR?")
    print("3. Are answers labeled clearly (e.g., 'Q1', 'Question 1', '1.')?")
    print("4. Is there sufficient text extracted?")
    

if __name__ == "__main__":
    main()
