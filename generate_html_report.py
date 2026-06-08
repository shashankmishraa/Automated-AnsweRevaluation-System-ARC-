"""
Generate a beautiful HTML report for the OCR-based scoring.
This creates a visual, shareable report card.
"""

import json
from datetime import datetime


def load_scoring_data():
    """Load the scoring report JSON."""
    with open("static_scoring_report.json", 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_html_report(data):
    """Generate HTML report from scoring data."""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Biology Exam - Score Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .student-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 3px solid #e9ecef;
        }}
        
        .info-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .info-card h3 {{
            color: #667eea;
            font-size: 0.9em;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        
        .info-card p {{
            font-size: 1.3em;
            color: #333;
            font-weight: 600;
        }}
        
        .overall-score {{
            text-align: center;
            padding: 40px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        
        .score-circle {{
            width: 200px;
            height: 200px;
            border-radius: 50%;
            background: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0 auto 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .percentage {{
            font-size: 3.5em;
            font-weight: bold;
            color: #f5576c;
        }}
        
        .grade {{
            font-size: 1.5em;
            font-weight: 600;
            color: #667eea;
            margin-top: 10px;
        }}
        
        .total-marks {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .questions {{
            padding: 40px;
        }}
        
        .questions h2 {{
            color: #333;
            margin-bottom: 30px;
            font-size: 2em;
        }}
        
        .question-card {{
            background: #f8f9fa;
            border-left: 5px solid #667eea;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .question-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }}
        
        .question-number {{
            font-size: 1.3em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .question-score {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 25px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .score-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .metric {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .metric-name {{
            font-size: 0.85em;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .feedback {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        
        .feedback strong {{
            color: #856404;
        }}
        
        .keywords {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 15px;
        }}
        
        .keyword-tag {{
            background: #d4edda;
            color: #155724;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.85em;
        }}
        
        .keyword-tag.missing {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .answers-section {{
            padding: 40px;
            background: #f8f9fa;
            border-top: 3px solid #e9ecef;
        }}
        
        .answers-section h2 {{
            color: #333;
            margin-bottom: 30px;
        }}
        
        .answer-comparison {{
            background: white;
            border-radius: 10px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .answer-text {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            line-height: 1.6;
        }}
        
        .answer-label {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            background: #333;
            color: white;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Biology Examination Results</h1>
            <p>Cell Biology and Genetics</p>
        </div>
        
        <div class="student-info">
            <div class="info-card">
                <h3>Student Name</h3>
                <p>{data['student_name']}</p>
            </div>
            <div class="info-card">
                <h3>Roll Number</h3>
                <p>{data['roll_number']}</p>
            </div>
            <div class="info-card">
                <h3>Evaluation Date</h3>
                <p>{data['evaluation_date'][:10]}</p>
            </div>
            <div class="info-card">
                <h3>Total Questions</h3>
                <p>{data['total_questions']}</p>
            </div>
        </div>
        
        <div class="overall-score">
            <div class="score-circle">
                <div class="percentage">{data['overall_percentage']}%</div>
                <div class="grade">Grade: {data['overall_grade']}</div>
            </div>
            <div class="total-marks">
                Total Marks: {data['total_obtained_marks']}/{data['total_max_marks']}
            </div>
        </div>
        
        <div class="questions">
            <h2>📊 Question-by-Question Analysis</h2>
            
"""
    
    # Add each question
    for q in data['questions']:
        html += f"""
            <div class="question-card">
                <div class="question-header">
                    <div class="question-number">Question {q['question_number']}</div>
                    <div class="question-score">
                        {q['obtained_marks']}/{q['max_marks']} marks ({q['scores']['final_score']}/10)
                    </div>
                </div>
                
                <div class="score-grid">
                    <div class="metric">
                        <div class="metric-name">Similarity</div>
                        <div class="metric-value">{q['scores']['similarity']*100:.1f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-name">Coverage</div>
                        <div class="metric-value">{q['scores']['coverage']*100:.1f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-name">Grammar</div>
                        <div class="metric-value">{q['scores']['grammar']*100:.1f}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-name">Relevance</div>
                        <div class="metric-value">{q['scores']['relevance']*100:.1f}%</div>
                    </div>
                </div>
                
                <div class="feedback">
                    <strong>Feedback:</strong> {q['feedback']}
                </div>
                
                <div>
                    <strong>✅ Matched Keywords ({len(q['matched_keywords'])}):</strong>
                    <div class="keywords">
"""
        
        for keyword in q['matched_keywords'][:8]:
            html += f'<span class="keyword-tag">{keyword}</span>'
        
        html += """
                    </div>
                </div>
                
                <div>
                    <strong>❌ Missing Keywords:</strong>
                    <div class="keywords">
"""
        
        for keyword in q['missing_keywords'][:8]:
            html += f'<span class="keyword-tag missing">{keyword}</span>'
        
        html += """
                    </div>
                </div>
            </div>
"""
    
    # Add detailed answers section
    html += """
        </div>
        
        <div class="answers-section">
            <h2>📝 Detailed Answer Comparison</h2>
"""
    
    for i, q in enumerate(data['questions']):
        q_num = str(q['question_number'])
        student_answer = data['student_answers'].get(q_num, "Not available")
        ref_answer = data['reference_answers_used'].get(q_num, "Not available")
        
        html += f"""
            <div class="answer-comparison">
                <h3>Question {q_num}</h3>
                
                <div class="answer-label">Student Answer:</div>
                <div class="answer-text">{student_answer}</div>
                
                <div class="answer-label">Reference Answer (Excerpt):</div>
                <div class="answer-text">{ref_answer[:500]}...</div>
            </div>
"""
    
    html += f"""
        </div>
        
        <div class="footer">
            <p>Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
            <p>OCR-Based Automated Evaluation System</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


if __name__ == "__main__":
    print("📄 Generating HTML Report...")
    data = load_scoring_data()
    html = generate_html_report(data)
    
    with open("score_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("✅ HTML report generated: score_report.html")
    print("\n💡 Open this file in your web browser to view the beautiful score report!")
    print("   You can also print it or save it as PDF.")
