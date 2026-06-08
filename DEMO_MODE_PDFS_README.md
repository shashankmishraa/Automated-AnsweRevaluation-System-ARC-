# 🎭 OCR & Batch Demo Mode - Using Real Sample PDFs

## Overview

Demo mode now uses **actual sample PDF files** from your project directory for realistic OCR evaluation, instead of preset text data.

## What Changed ✅

### Before:
- ❌ Text tab had demo mode toggle (removed)
- ❌ OCR demo used preset text responses
- ❌ No real file processing

### After:
- ✅ Text tab always uses live backend (no demo)
- ✅ OCR demo processes actual sample PDFs
- ✅ Batch demo uses preset class data
- ✅ Real OCR, real scoring, real results!

## Sample PDFs Used 📄

The demo mode automatically loads these files from your project directory:

1. **sample_question_paper.pdf** - Contains 5 biology questions
2. **sample_student_answers.pdf** - Handwritten student answers

These files are already in your `d:\D down\bit\` folder.

## How to Use 📝

### Quick Start:

1. **Start Backend**:
   ```bash
   cd d:\D down\bit
   python app.py
   ```

2. **Start Frontend**:
   ```bash
   cd ui-react
   npm run dev
   ```

3. **Open Browser**: http://localhost:3000

4. **Go to OCR Tab**:
   - Toggle "Demo Mode" ON (green badge)
   - See the notice: "Using sample_question_paper.pdf and sample_student_answers.pdf"
   - Click "Evaluate"
   - Watch real OCR processing happen!

5. **Go to Batch Tab**:
   - Toggle "Demo Mode" ON
   - Click "Evaluate"
   - See preset class evaluation with 5 students

## Features by Mode 🎯

### OCR Demo Mode (PDF Processing):

**What Happens:**
1. Backend loads `sample_question_paper.pdf`
2. Backend loads `sample_student_answers.pdf`
3. Real OCR is performed on handwritten answers
4. Questions are extracted from question paper
5. Answers are matched to questions
6. Real scoring happens (similarity, coverage, grammar, relevance)
7. Results are displayed with actual extracted text

**Options Available:**
- ⚡ **Quick Mode**: Fast OCR (1-3 seconds)
- 🎯 **Accurate Mode**: Better quality (5-10 seconds)
- 🤖 **LLM Enhancement**: AI-powered text correction (optional)

**Results You'll See:**
- Real extracted text from handwritten answers
- Question-by-question breakdown
- Actual scores based on OCR output quality
- Gap analysis showing matched/missing concepts

### Batch Demo Mode:

**What Happens:**
- Uses preset data for 5 students
- Shows complete class statistics
- Individual student rankings
- Question-wise score breakdown

**Data Included:**
- 5 Students: Alice, Bob, Carol, David, Emma
- Scores range: 58% to 91.5%
- Class average: 74.2%
- Complete grade distribution

## API Endpoints 🔌

### OCR PDF Demo (Real Files):
```bash
POST http://localhost:8000/evaluate/pdf-handwritten-demo
Content-Type: application/x-www-form-urlencoded

use_llm=true|false
mode=fast|accurate
```

**Response:**
```json
{
  "questions_results": [
    {
      "question_number": 1,
      "extracted_answer": "Photosynthesis is how plants...",
      "obtained_marks": 8.5,
      "max_marks": 10,
      "similarity_score": 0.85,
      "coverage_score": 0.78
    }
  ],
  "total_score": 38.5,
  "total_marks": 45,
  "percentage": 85.6,
  "grade": "A",
  "extracted_text": "Full OCR text...",
  "demo_mode": true,
  "sample_pdfs_used": true
}
```

### Batch Demo (Preset Data):
```bash
POST http://localhost:8000/evaluate/batch-demo
```

Returns complete class evaluation with 5 students.

## File Structure 📁

```
d:\D down\bit\
├── sample_question_paper.pdf       ← Used by OCR demo
├── sample_student_answers.pdf      ← Used by OCR demo
├── main.py                         ← Backend with demo endpoints
├── DEMO_MODE_PDFS_README.md        ← This file
└── ui-react/app/page.tsx           ← Frontend with demo toggles
```

## Demo Mode Comparison 📊

| Feature | OCR Demo | Batch Demo |
|---------|----------|------------|
| **Data Source** | Real PDFs | Preset JSON |
| **Processing** | Real OCR | Simulated |
| **Files Used** | sample_*.pdf | demo_data.py |
| **Time** | 2-5 seconds | 1.5 seconds |
| **Results** | Varies by OCR | Always same |
| **Best For** | Showing OCR capability | Quick class demo |

## Benefits of Using Real PDFs ✨

### Authenticity:
✅ **Real Handwriting** - Actual scanned handwritten answers  
✅ **Real Questions** - Proper biology exam questions  
✅ **Real OCR** - Genuine text extraction challenges  
✅ **Real Scoring** - Actual similarity calculations  

### Educational:
✅ **See OCR Quality** - Understand extraction limitations  
✅ **Debug Friendly** - Know exactly what was processed  
✅ **Reproducible** - Same PDFs = consistent demo  
✅ **Professional** - Impressive live demonstrations  

## Troubleshooting 💬

### "No questions found in sample question paper"
- Check that `sample_question_paper.pdf` exists in project root
- Verify PDF contains readable text
- Try running: `python debug_ocr_scoring.py` to test

### "No text could be extracted from sample PDFs"
- OCR might be failing on handwriting
- Switch to "Accurate Mode" for better results
- Enable LLM enhancement for difficult handwriting

### Demo mode toggle not showing
- Make sure you're on OCR or Batch tab
- Text tab no longer has demo mode toggle
- Refresh page if needed

## Customization 🔧

### Use Your Own PDFs:

Edit `main.py`, find `/evaluate/pdf-handwritten-demo`:

```python
# Replace these file paths with your own
with open("your_question_paper.pdf", "rb") as f:
    question_pdf_bytes = f.read()

with open("your_student_answers.pdf", "rb") as f:
    answer_pdf_bytes = f.read()
```

### Change Sample PDFs:

Simply replace the files:
1. Backup original: `copy sample_question_paper.pdf backup.pdf`
2. Copy your PDF: `copy your_exam.pdf sample_question_paper.pdf`
3. Run demo - it will use your file!

## Next Steps 🚀

1. **Try OCR Demo**:
   - Go to OCR tab
   - Enable demo mode
   - Click Evaluate
   - See real results!

2. **Compare Modes**:
   - Try Quick vs Accurate mode
   - Enable/disable LLM
   - See difference in results

3. **Use Your Papers**:
   - Replace sample PDFs with your own
   - Show real student work
   - Perfect for presentations!

---

**Updated**: April 2, 2026  
**Status**: ✅ Fully Functional - Real PDF Processing  
**Files**: sample_question_paper.pdf + sample_student_answers.pdf
