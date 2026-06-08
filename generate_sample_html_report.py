"""
Generate HTML report for sample PDF scoring results.
"""

import json


def load_report():
    """Load the JSON scoring report."""
    with open("sample_pdf_scoring_report.json", "r", encoding="utf-8") as f:
        return json.load(f)


def generate_html(data):
    """Generate HTML report from scoring data."""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sample PDF Evaluation Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
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
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.2em; opacity: 0.9; }}
        .info-bar {{
            display: flex;
            justify-content: space-between;
            padding: 20px 40px;
            background: #f8f9fa;
            border-bottom: 3px solid #e9ecef;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .info-item {{
            background: white;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .info-item h3 {{
            color: #667eea;
            font-size: 0.85em;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .info-item p {{
            font-size: 1.1em;
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
            width: 220px;
            height: 220px;
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
            font-size: 1.8em;
            font-weight: 600;
            color: #667eea;
            margin-top: 10px;
        }}
        .marks {{
            font-size: 1.3em;
            opacity: 0.9;
            margin-top: 10px;
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
        .feedback strong {{ color: #856404; }}
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
        .answer-section {{
            margin-top: 20px;
        }}
        .answer-text {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            line-height: 1.6;
            font-size: 0.95em;
        }}
        .answer-label {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 8px;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            background: #333;
            color: white;
        }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; }}
            .overall-score {{ background: #f093fb; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Sample PDF Evaluation Report</h1>
            <p>OCR-Based Answer Scoring Results</p>
        </div>
        
        <div class="info-bar">
            <div class="info-item">
                <h3>Question Paper</h3>
                <p>📄 sample_question_paper.pdf</p>
            </div>
            <div class="info-item">
                <h3>Student Answers</h3>
                <p>✍️ sample_handwritten_answers_generated.pdf</p>
            </div>
            <div class="info-item">
                <h3>Evaluation Date</h3>
                <p>{data['evaluation_date'][:10]}</p>
            </div>
            <div class="info-item">
                <h3>Total Questions</h3>
                <p>{data['total_questions']}</p>
            </div>
        </div>
        
        <div class="overall-score">
            <div class="score-circle">
                <div class="percentage">{data['overall_percentage']}%</div>
                <div class="grade">Grade: {data['overall_grade']}</div>
            </div>
            <div class="marks">
                Total Marks: {data['total_obtained_marks']}/{data['total_max_marks']}
            </div>
        </div>
        
        <div class="questions">
            <h2>📝 Question-by-Question Analysis</h2>
"""
    
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
        for kw in q['matched_keywords']:
            html += f'<span class="keyword-tag">{kw}</span>'
        
        html += """
                    </div>
                </div>
                
                <div>
                    <strong>❌ Missing Keywords:</strong>
                    <div class="keywords">
"""
        for kw in q['missing_keywords']:
            html += f'<span class="keyword-tag missing">{kw}</span>'
        
        html += f"""
                    </div>
                </div>
                
                <div class="answer-section">
                    <div class="answer-label">Student Answer:</div>
                    <div class="answer-text">{q['student_answer']}</div>
                    
                    <div class="answer-label">Reference Answer (Excerpt):</div>
                    <div class="answer-text">{q['reference_answer'][:400]}...</div>
                </div>
            </div>
"""
    
    html += f"""
        </div>
        
        <div class="footer">
            <p>Generated on {data['evaluation_date'][:10]}</p>
            <p>OCR-Based Automated Evaluation System</p>
            <p>Files: sample_question_paper.pdf + sample_handwritten_answers_generated.pdf</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html


if __name__ == "__main__":
    print("📄 Generating HTML Report...")
    data = load_report()
    html = generate_html(data)
    
    with open("sample_pdf_score_report.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("✅ HTML report generated: sample_pdf_score_report.html")
    print("\n💡 Open this file in your web browser to view the report!")
