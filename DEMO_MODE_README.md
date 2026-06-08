# 🎭 Demo Mode - OCR & Batch Processing

## Overview

Demo mode provides **preset, realistic evaluation results** for demonstrations without needing actual files or backend processing. Perfect for presentations, testing, and showcasing the system capabilities.

## Features ✨

### OCR Demo Mode
- **4 Subject Areas**: General Science, Physics, History, Computer Science
- **Realistic Scores**: Pre-calculated similarity, coverage, grammar, relevance metrics
- **Detailed Feedback**: Comprehensive feedback and gap analysis
- **Instant Results**: No file upload or OCR processing needed
- **Professional Quality**: Looks and feels like real evaluation

### Batch Demo Mode
- **5 Student Records**: Complete class evaluation dataset
- **Statistics Included**: Average, highest, lowest scores, grade distribution
- **Individual Reports**: Per-student breakdown with question-wise scores
- **Ranking System**: Students ranked by performance
- **Class Analytics**: Pass rate, excellence rate, question difficulty analysis

## How to Use 📝

### In the React UI

1. **Toggle Demo Mode**:
   - Look for the "Demo Mode / Live Mode" switch at the top
   - Switch to "DEMO" (purple badge appears)
   - Select subject from dropdown

2. **OCR Tab**:
   - Click on OCR tab
   - Enable Demo Mode
   - Choose subject (General, Physics, History, CS)
   - Click "Evaluate"
   - Get instant, realistic results!

3. **Batch Tab**:
   - Click on Batch tab  
   - Enable Demo Mode
   - Click "Evaluate"
   - See complete class evaluation with 5 students

### API Endpoints

#### OCR Demo
```bash
POST http://localhost:8000/evaluate/ocr-demo
Content-Type: application/x-www-form-urlencoded

subject=general  # Options: general, physics, history, computer_science
```

**Response:**
```json
{
  "question": "Explain the process of photosynthesis in plants.",
  "student_answer": "Photosynthesis is how plants make their own food...",
  "reference_answer": "Photosynthesis is the biochemical process...",
  "similarity": 0.782,
  "coverage": 0.845,
  "grammar": 0.890,
  "relevance": 0.920,
  "final_score": 8.35,
  "grade": "A",
  "percentage": 83.5,
  "feedback": "Good answer with solid understanding...",
  "gap_analysis": {
    "matched": [...],
    "missing": [...],
    "coverage_percentage": 84.5
  },
  "demo_mode": true
}
```

#### Batch Demo
```bash
POST http://localhost:8000/evaluate/batch-demo
```

**Response:**
```json
{
  "exam_name": "Biology Mid-Term Exam",
  "total_students": 5,
  "average_score": 7.42,
  "average_percentage": 74.2,
  "class_grade": "B",
  "highest_score": 9.15,
  "lowest_score": 5.80,
  "students": [
    {
      "rank": 1,
      "student_name": "Alice Johnson",
      "final_score": 9.15,
      "grade": "A+",
      ...
    },
    ...
  ],
  "statistics": {
    "pass_rate": 100.0,
    "excellence_rate": 40.0,
    "grade_distribution": {...},
    ...
  },
  "demo_mode": true
}
```

## Available Demo Subjects 📚

### OCR Subjects:

1. **General Science** - Photosynthesis
   - Question: Explain the process of photosynthesis in plants
   - Expected Score: 8.35/10 (83.5%) - Grade A
   
2. **Physics** - Newton's Laws
   - Question: State Newton's three laws of motion with examples
   - Expected Score: 7.45/10 (74.5%) - Grade B
   
3. **History** - World War I
   - Question: What were the main causes of WWI?
   - Expected Score: 8.75/10 (87.5%) - Grade A+
   
4. **Computer Science** - Memory Types
   - Question: Explain difference between RAM and ROM
   - Expected Score: 8.05/10 (80.5%) - Grade A-

### Batch Evaluation:

- **Subject**: Biology - Photosynthesis & Cell Biology
- **Students**: 5 (Alice, Bob, Carol, David, Emma)
- **Score Range**: 5.80 to 9.15 out of 10
- **Class Average**: 74.2% (Grade B)

## Demo Data Structure 📊

### Files Created:

```
d:\D down\bit\
├── demo_data.py              # All preset data and responses
├── DEMO_MODE_README.md       # This file
└── main.py                   # Updated with demo endpoints
```

### Code Usage:

```python
from demo_data import get_demo_ocr_result, get_demo_batch_result

# Get OCR demo result
ocr_result = get_demo_ocr_result('physics')
print(ocr_result['question'])
print(ocr_result['scores']['final_score'])

# Get batch demo result
batch_result = get_demo_batch_result()
print(f"Total students: {batch_result['total_students']}")
print(f"Average score: {batch_result['average_score']}")
```

## Benefits of Demo Mode 🎯

### For Presentations:
✅ **No Files Needed** - Instant results without uploads  
✅ **Consistent Output** - Same results every time  
✅ **Professional Quality** - Polished, realistic data  
✅ **Fast Demo** - 0.5-1.5 second response times  

### For Testing:
✅ **Predictable Results** - Know what to expect  
✅ **Edge Cases Covered** - Various score ranges  
✅ **No Dependencies** - Works without GPU/OCR engines  
✅ **Offline Capable** - No internet required  

### For Development:
✅ **Quick Iteration** - Test UI changes instantly  
✅ **Debug Friendly** - Known data makes bugs easier to spot  
✅ **API Contract** - Clear request/response format  

## Comparison: Demo vs Live 🔍

| Feature | Demo Mode | Live Mode |
|---------|-----------|-----------|
| **Speed** | 0.5-1.5s | 5-30s (OCR) |
| **Files Required** | ❌ No | ✅ Yes |
| **Internet** | ❌ Not needed | ✅ For Gemini API |
| **GPU/CPU** | ❌ Minimal | ✅ Intensive |
| **Results** | Preset, consistent | Varies by input |
| **Best For** | Demos, testing | Real evaluation |

## Sample Screenshots 📸

When you run demo mode, you'll see results like:

### OCR Demo (General Science):
```
Question: Explain the process of photosynthesis in plants.
Student Answer: Photosynthesis is how plants make their own food using sunlight...
Reference Answer: Photosynthesis is the biochemical process by which green plants...

Scores:
├─ Similarity: 78.2%
├─ Coverage: 84.5%
├─ Grammar: 89.0%
├─ Relevance: 92.0%
└─ Final Score: 8.35/10 (Grade: A)

Matched Concepts:
✅ photosynthesis, light energy, chemical energy, glucose, chloroplasts, chlorophyll

Missing Concepts:
❌ oxygen production, light-dependent reactions, Calvin cycle
```

### Batch Demo:
```
Biology Mid-Term Exam Results
═══════════════════════════════
Total Students: 5
Class Average: 74.2% (Grade: B)
Highest Score: Alice Johnson - 91.5%
Lowest Score: Emma Davis - 58.0%

Grade Distribution:
A+: ████░░░░░░ 1 student (20%)
A:  ████░░░░░░ 1 student (20%)
B+: ████░░░░░░ 1 student (20%)
B-: ████░░░░░░ 1 student (20%)
C-: ████░░░░░░ 1 student (20%)
```

## Technical Details ⚙️

### Backend Implementation:

**File**: `main.py`
```python
@app.post("/evaluate/ocr-demo")
async def evaluate_ocr_demo(subject: str = Form("general")):
    """DEMO MODE - Return preset OCR evaluation results."""
    await time.sleep(0.5)  # Simulate processing
    return generate_demo_ocr_response(subject)

@app.post("/evaluate/batch-demo")
async def evaluate_batch_demo():
    """DEMO MODE - Return preset batch evaluation results."""
    await time.sleep(1.0)  # Simulate processing
    return generate_demo_batch_response()
```

### Frontend Integration:

**File**: `ui-react/app/page.tsx`
```typescript
if (demoMode && activeTab === 'ocr') {
  formData.append('subject', selectedSubject);
  response = await fetch(`${API_BASE}/evaluate/ocr-demo`, {
    method: 'POST',
    body: formData
  });
}

if (demoMode && activeTab === 'batch') {
  response = await fetch(`${API_BASE}/evaluate/batch-demo`, {
    method: 'POST'
  });
}
```

## Customization 🔧

### Add New Demo Subjects:

Edit `demo_data.py`:

```python
DEMO_OCR_RESULTS["mathematics"] = {
    "question": "Solve quadratic equation ax² + bx + c = 0",
    "student_answer": "...",
    "reference_answer": "...",
    "scores": {
        "similarity": 0.85,
        "coverage": 0.90,
        "grammar": 0.88,
        "relevance": 0.92,
        "final_score": 8.85
    },
    ...
}
```

### Modify Batch Data:

Edit student records in `demo_data.py`:

```python
DEMO_BATCH_RESULTS["students"].append({
    "rank": 6,
    "student_name": "Your Name",
    "student_id": "2024-XXX-006",
    "final_score": 8.50,
    "grade": "A",
    ...
})
```

## Troubleshooting 💬

### Demo mode not working?

1. **Check Toggle**: Make sure demo mode switch is ON (purple badge visible)
2. **Select Subject**: For OCR, ensure a subject is selected
3. **Console Errors**: Check browser console for API errors
4. **Backend Running**: Ensure FastAPI server is running on port 8000

### Getting live results instead?

- Verify demo mode is enabled BEFORE clicking evaluate
- Refresh page if toggle doesn't respond
- Check network tab - should call `/ocr-demo` or `/batch-demo`

## Next Steps 🚀

1. **Try It Out**: 
   ```bash
   cd ui-react
   npm run dev
   ```
   
2. **Open Browser**: http://localhost:3000

3. **Enable Demo Mode**: Toggle switch at top

4. **Test OCR**: 
   - Go to OCR tab
   - Select "General Science"
   - Click Evaluate
   - See instant results!

5. **Test Batch**:
   - Go to Batch tab
   - Click Evaluate
   - See class results with 5 students!

---

**Created**: April 2, 2026  
**Status**: ✅ Fully Functional  
**Quality**: Production-Ready Demo Data
