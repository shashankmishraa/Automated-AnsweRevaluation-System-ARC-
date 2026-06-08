"""
Demo mode data for OCR and Batch evaluation.
Provides realistic preset scores and feedback for demonstrations.
"""

from typing import Dict, List, Any


# Demo OCR Evaluation Results (Preset)
DEMO_OCR_RESULTS = {
    "general": {
        "question": "Explain the process of photosynthesis in plants.",
        "student_answer": "Photosynthesis is how plants make their own food using sunlight, water and carbon dioxide. They convert light energy into chemical energy stored in glucose. The process happens in chloroplasts which contain chlorophyll that gives plants their green color.",
        "reference_answer": "Photosynthesis is the biochemical process by which green plants convert light energy into chemical energy. Using chlorophyll, they absorb sunlight and combine carbon dioxide from the air with water to produce glucose and oxygen. This process occurs primarily in the leaves within specialized structures called chloroplasts.",
        "scores": {
            "similarity": 0.782,
            "coverage": 0.845,
            "grammar": 0.890,
            "relevance": 0.920,
            "final_score": 8.35
        },
        "grade": "A",
        "percentage": 83.5,
        "feedback": "Good answer with solid understanding. You correctly identified key concepts like chloroplasts, chlorophyll, and energy conversion. Could improve by mentioning the two stages (light and dark reactions) and the chemical equation.",
        "gap_analysis": {
            "matched": [
                {"concept": "photosynthesis", "status": "correct"},
                {"concept": "light energy", "status": "correct"},
                {"concept": "chemical energy", "status": "correct"},
                {"concept": "glucose", "status": "correct"},
                {"concept": "chloroplasts", "status": "correct"},
                {"concept": "chlorophyll", "status": "correct"},
                {"concept": "carbon dioxide", "status": "correct"}
            ],
            "missing": [
                {"concept": "oxygen production", "importance": "high"},
                {"concept": "light-dependent reactions", "importance": "medium"},
                {"concept": "Calvin cycle", "importance": "medium"}
            ],
            "coverage_percentage": 84.5
        }
    },
    
    "physics": {
        "question": "State Newton's three laws of motion and explain each with an example.",
        "student_answer": "First law: An object at rest stays at rest unless acted on by force. Example: book on table. Second law: F=ma, force equals mass times acceleration. Example: pushing car. Third law: Every action has equal opposite reaction. Example: rocket propulsion.",
        "reference_answer": "Newton's First Law (Law of Inertia): An object at rest remains at rest, and an object in motion remains in motion at constant velocity, unless acted upon by a net external force. Example: A hockey puck sliding on ice eventually stops due to friction. Newton's Second Law: The acceleration of an object is directly proportional to the net force acting on it and inversely proportional to its mass (F=ma). Example: It takes more force to push a truck than a bicycle. Newton's Third Law: For every action, there is an equal and opposite reaction. Example: When you jump, your legs apply force to the ground, and the ground applies equal force back, propelling you upward.",
        "scores": {
            "similarity": 0.695,
            "coverage": 0.780,
            "grammar": 0.720,
            "relevance": 0.890,
            "final_score": 7.45
        },
        "grade": "B",
        "percentage": 74.5,
        "feedback": "Good understanding of all three laws. Your examples are relevant and demonstrate practical application. Improve by providing more detailed explanations and using complete sentences.",
        "gap_analysis": {
            "matched": [
                {"concept": "First Law", "status": "correct"},
                {"concept": "Second Law", "status": "correct"},
                {"concept": "F=ma", "status": "correct"},
                {"concept": "Third Law", "status": "correct"},
                {"concept": "action-reaction", "status": "correct"}
            ],
            "missing": [
                {"concept": "inertia", "importance": "high"},
                {"concept": "constant velocity", "importance": "medium"},
                {"concept": "net external force", "importance": "high"}
            ],
            "coverage_percentage": 78.0
        }
    },
    
    "history": {
        "question": "What were the main causes of World War I?",
        "student_answer": "WWI was caused by militarism, alliances between countries, imperialism and competition for colonies, and nationalism. The assassination of Archduke Franz Ferdinand in Sarajevo by Gavrilo Princip was the trigger that started the war in 1914.",
        "reference_answer": "World War I was caused by four main factors known by the acronym MAIN: Militarism (arms race and military buildup between European powers), Alliances (complex system of treaties dividing Europe into two camps), Imperialism (competition for colonies and resources in Africa and Asia), and Nationalism (extreme pride in one's nation and desire for independence among ethnic groups). The immediate trigger was the assassination of Archduke Franz Ferdinand of Austria-Hungary on June 28, 1914, in Sarajevo by Gavrilo Princip, a Serbian nationalist.",
        "scores": {
            "similarity": 0.825,
            "coverage": 0.890,
            "grammar": 0.850,
            "relevance": 0.940,
            "final_score": 8.75
        },
        "grade": "A+",
        "percentage": 87.5,
        "feedback": "Excellent answer! You correctly identified all four MAIN causes and provided specific details about the assassination. Very good historical accuracy.",
        "gap_analysis": {
            "matched": [
                {"concept": "militarism", "status": "correct"},
                {"concept": "alliances", "status": "correct"},
                {"concept": "imperialism", "status": "correct"},
                {"concept": "nationalism", "status": "correct"},
                {"concept": "Archduke Franz Ferdinand", "status": "correct"},
                {"concept": "Gavrilo Princip", "status": "correct"},
                {"concept": "Sarajevo", "status": "correct"}
            ],
            "missing": [
                {"concept": "MAIN acronym", "importance": "low"},
                {"concept": "June 28, 1914", "importance": "low"}
            ],
            "coverage_percentage": 89.0
        }
    },
    
    "computer_science": {
        "question": "Explain the difference between RAM and ROM in computers.",
        "student_answer": "RAM is Random Access Memory, it's volatile and temporary, used for running programs. ROM is Read Only Memory, non-volatile and permanent, stores boot instructions. RAM can be read and written, ROM only read. RAM is faster but loses data when power off.",
        "reference_answer": "RAM (Random Access Memory) is volatile memory that temporarily stores data and programs currently being used by the CPU. It can be both read from and written to, and loses all data when power is turned off. ROM (Read-Only Memory) is non-volatile memory that permanently stores critical system instructions like the BIOS/boot firmware. It can only be read, not written to during normal operation, and retains data even without power. RAM is much faster and has larger capacity than ROM.",
        "scores": {
            "similarity": 0.758,
            "coverage": 0.825,
            "grammar": 0.780,
            "relevance": 0.910,
            "final_score": 8.05
        },
        "grade": "A-",
        "percentage": 80.5,
        "feedback": "Very good explanation of the key differences. You covered volatility, read/write capabilities, and purpose accurately. Could mention BIOS and give more specific use cases.",
        "gap_analysis": {
            "matched": [
                {"concept": "volatile", "status": "correct"},
                {"concept": "non-volatile", "status": "correct"},
                {"concept": "temporary", "status": "correct"},
                {"concept": "permanent", "status": "correct"},
                {"concept": "read and write", "status": "correct"},
                {"concept": "power off", "status": "correct"}
            ],
            "missing": [
                {"concept": "BIOS", "importance": "medium"},
                {"concept": "boot firmware", "importance": "high"},
                {"concept": "CPU", "importance": "low"}
            ],
            "coverage_percentage": 82.5
        }
    }
}


# Demo Batch Evaluation Results (Preset)
DEMO_BATCH_RESULTS = {
    "evaluation_id": "batch_demo_001",
    "exam_name": "Biology Mid-Term Exam - Photosynthesis & Cell Biology",
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
            "student_id": "2024-BIO-001",
            "final_score": 9.15,
            "percentage": 91.5,
            "grade": "A+",
            "feedback": "Excellent work! Outstanding understanding of cellular processes.",
            "question_scores": [
                {"question": 1, "marks": 9.2, "max": 10},
                {"question": 2, "marks": 9.0, "max": 10},
                {"question": 3, "marks": 9.3, "max": 10},
                {"question": 4, "marks": 9.0, "max": 10},
                {"question": 5, "marks": 4.6, "max": 5}
            ]
        },
        {
            "rank": 2,
            "student_name": "Bob Smith",
            "student_id": "2024-BIO-002",
            "final_score": 8.45,
            "percentage": 84.5,
            "grade": "A",
            "feedback": "Good answer with solid understanding. Minor improvements needed.",
            "question_scores": [
                {"question": 1, "marks": 8.5, "max": 10},
                {"question": 2, "marks": 8.2, "max": 10},
                {"question": 3, "marks": 8.6, "max": 10},
                {"question": 4, "marks": 8.4, "max": 10},
                {"question": 5, "marks": 4.2, "max": 5}
            ]
        },
        {
            "rank": 3,
            "student_name": "Carol White",
            "student_id": "2024-BIO-003",
            "final_score": 7.60,
            "percentage": 76.0,
            "grade": "B+",
            "feedback": "Satisfactory answer but needs improvement in key areas.",
            "question_scores": [
                {"question": 1, "marks": 7.8, "max": 10},
                {"question": 2, "marks": 7.5, "max": 10},
                {"question": 3, "marks": 7.4, "max": 10},
                {"question": 4, "marks": 7.6, "max": 10},
                {"question": 5, "marks": 3.8, "max": 5}
            ]
        },
        {
            "rank": 4,
            "student_name": "David Brown",
            "student_id": "2024-BIO-004",
            "final_score": 6.85,
            "percentage": 68.5,
            "grade": "B-",
            "feedback": "Basic understanding shown but significant improvements needed.",
            "question_scores": [
                {"question": 1, "marks": 7.0, "max": 10},
                {"question": 2, "marks": 6.5, "max": 10},
                {"question": 3, "marks": 7.2, "max": 10},
                {"question": 4, "marks": 6.8, "max": 10},
                {"question": 5, "marks": 3.4, "max": 5}
            ]
        },
        {
            "rank": 5,
            "student_name": "Emma Davis",
            "student_id": "2024-BIO-005",
            "final_score": 5.80,
            "percentage": 58.0,
            "grade": "C-",
            "feedback": "Answer requires substantial revision. Please review the topic.",
            "question_scores": [
                {"question": 1, "marks": 6.0, "max": 10},
                {"question": 2, "marks": 5.5, "max": 10},
                {"question": 3, "marks": 6.2, "max": 10},
                {"question": 4, "marks": 5.8, "max": 10},
                {"question": 5, "marks": 2.9, "max": 5}
            ]
        }
    ],
    "statistics": {
        "pass_rate": 100.0,
        "excellence_rate": 40.0,
        "average_by_question": [
            {"question": 1, "average": 7.7, "max": 10},
            {"question": 2, "average": 7.34, "max": 10},
            {"question": 3, "average": 7.74, "max": 10},
            {"question": 4, "average": 7.52, "max": 10},
            {"question": 5, "average": 3.78, "max": 5}
        ],
        "grade_distribution": {
            "A+": 1,
            "A": 1,
            "B+": 1,
            "B": 0,
            "B-": 1,
            "C+": 0,
            "C": 0,
            "C-": 1,
            "D": 0,
            "F": 0
        }
    }
}


def get_demo_ocr_result(subject: str = "general") -> Dict[str, Any]:
    """Get preset OCR evaluation result for demo mode."""
    return DEMO_OCR_RESULTS.get(subject, DEMO_OCR_RESULTS["general"])


def get_demo_batch_result() -> Dict[str, Any]:
    """Get preset batch evaluation result for demo mode."""
    return DEMO_BATCH_RESULTS


def generate_demo_ocr_response(subject: str = "general") -> Dict[str, Any]:
    """Generate complete demo OCR API response."""
    result = get_demo_ocr_result(subject)
    
    return {
        "question": result["question"],
        "student_answer": result["student_answer"],
        "reference_answer": result["reference_answer"],
        "extracted_text": result["student_answer"],  # Simulated OCR output
        "similarity": result["scores"]["similarity"],
        "coverage": result["scores"]["coverage"],
        "grammar": result["scores"]["grammar"],
        "relevance": result["scores"]["relevance"],
        "final_score": result["scores"]["final_score"],
        "grade": result["grade"],
        "feedback": result["feedback"],
        "gap_analysis": result["gap_analysis"],
        "evaluation_id": f"ocr_demo_{subject}",
        "processing_time_ms": 1250,  # Simulated processing time
        "ocr_mode": "accurate",
        "llm_enhanced_ocr": False,
        "llm_scoring_used": False,
        "demo_mode": True
    }


def generate_demo_batch_response() -> Dict[str, Any]:
    """Generate complete demo batch API response."""
    result = get_demo_batch_result()
    
    return {
        "evaluation_id": result["evaluation_id"],
        "exam_name": result["exam_name"],
        "total_students": result["total_students"],
        "average_score": result["average_score"],
        "average_percentage": result["average_percentage"],
        "class_grade": result["class_grade"],
        "highest_score": result["highest_score"],
        "lowest_score": result["lowest_score"],
        "results": [
            {
                "student_name": student["student_name"],
                "student_id": student["student_id"],
                "final_score": student["final_score"],
                "grade": student["grade"],
                "feedback": student["feedback"],
                "question_scores": student["question_scores"]
            }
            for student in result["students"]
        ],
        "statistics": result["statistics"],
        "processing_time_ms": 3500,  # Simulated processing time
        "demo_mode": True
    }


if __name__ == "__main__":
    print("🎭 Demo Mode Data Generator")
    print("="*60)
    
    print("\n📊 Available Demo Subjects for OCR:")
    for subject in DEMO_OCR_RESULTS.keys():
        print(f"  - {subject.replace('_', ' ').title()}")
    
    print("\n📦 Batch Demo:")
    print(f"  - Total Students: {DEMO_BATCH_RESULTS['total_students']}")
    print(f"  - Average Score: {DEMO_BATCH_RESULTS['average_score']}/10")
    print(f"  - Class Grade: {DEMO_BATCH_RESULTS['class_grade']}")
    
    print("\n💡 Usage:")
    print("  from demo_data import get_demo_ocr_result, get_demo_batch_result")
    print("  ocr_result = get_demo_ocr_result('physics')")
    print("  batch_result = get_demo_batch_result()")


# Demo PDF Handwritten Evaluation Results (Preset)
DEMO_PDF_RESULTS = {
    "questions_results": [
        {
            "question_number": 1,
            "question_text": "What is photosynthesis? Explain the process in detail. [10 marks]",
            "extracted_answer": "Photosynthesis is how plants make food using sunlight. They take in carbon dioxide and water, and use chlorophyll in their leaves to convert these into glucose and oxygen. The process has two stages: light reactions that capture energy from sunlight, and dark reactions (Calvin cycle) that make glucose.",
            "generated_reference": "Photosynthesis is a fundamental anabolic process by which plants use light energy to synthesise glucose from CO2 and water, releasing oxygen as a byproduct. It occurs in two stages: light-dependent reactions in the thylakoid membranes and the Calvin cycle in the stroma.",
            "max_marks": 10,
            "obtained_marks": 7.5,
            "similarity_score": 0.78,
            "coverage_score": 0.72,
            "feedback": "Good"
        },
        {
            "question_number": 2,
            "question_text": "Describe the structure and function of mitochondria. [10 marks]",
            "extracted_answer": "Mitochondria are the powerhouse of the cell. They have two membranes - outer and inner. The inner membrane has folds called cristae. Inside is the matrix which has enzymes. Mitochondria make ATP energy through respiration. They have their own DNA.",
            "generated_reference": "Mitochondria are double-membraned organelles, often called the powerhouses of the cell. The outer membrane is smooth while the inner membrane is folded into cristae, increasing surface area for ATP synthesis. The matrix contains enzymes for the Krebs cycle.",
            "max_marks": 10,
            "obtained_marks": 8.2,
            "similarity_score": 0.85,
            "coverage_score": 0.80,
            "feedback": "Excellent!"
        },
        {
            "question_number": 3,
            "question_text": "Explain the process of cellular respiration and its importance. [15 marks]",
            "extracted_answer": "Cellular respiration breaks down glucose to make ATP energy. It happens in three steps: glycolysis in the cytoplasm, Krebs cycle in mitochondria, and electron transport chain which makes lots of ATP. Overall about 36-38 ATP molecules are made from one glucose.",
            "generated_reference": "Cellular respiration is a catabolic process by which cells break down glucose to produce ATP. It involves glycolysis (cytoplasm), the Krebs cycle (mitochondrial matrix), and oxidative phosphorylation via the electron transport chain, yielding ~36-38 ATP per glucose molecule.",
            "max_marks": 15,
            "obtained_marks": 11.25,
            "similarity_score": 0.82,
            "coverage_score": 0.75,
            "feedback": "Good"
        },
        {
            "question_number": 4,
            "question_text": "What are enzymes? Discuss their role in biological reactions. [10 marks]",
            "extracted_answer": "Enzymes are proteins that speed up reactions in the body. They have active sites where substrates bind. They lower activation energy so reactions can happen faster. Different enzymes work at different pH and temperature. Without enzymes, reactions would be too slow to support life.",
            "generated_reference": "Enzymes are biological catalysts, primarily protein macromolecules, that accelerate chemical reactions by lowering activation energy. They are highly specific, with each enzyme binding to a particular substrate at its active site. Factors like pH and temperature affect enzyme activity.",
            "max_marks": 10,
            "obtained_marks": 8.5,
            "similarity_score": 0.88,
            "coverage_score": 0.83,
            "feedback": "Excellent!"
        },
        {
            "question_number": 5,
            "question_text": "Describe the structure of DNA and its significance in heredity. [5 marks]",
            "extracted_answer": "DNA is genetic material that carries hereditary information. It has a double helix shape with two strands. The strands have nucleotides with bases A, T, G, C. A pairs with T and G pairs with C. DNA stores information in the sequence of bases.",
            "generated_reference": "DNA is a double helix polymer of two antiparallel polynucleotide strands. Each nucleotide contains a deoxyribose sugar, phosphate group, and one of four nitrogenous bases (A, T, G, C). Base pairing (A-T, G-C) ensures faithful replication and transmission of genetic information.",
            "max_marks": 5,
            "obtained_marks": 4.1,
            "similarity_score": 0.80,
            "coverage_score": 0.76,
            "feedback": "Good"
        }
    ],
    "total_score": 39.55,
    "total_marks": 50,
    "percentage": 79.1,
    "grade": "B+",
    "processing_time_ms": 4200,
    "llm_used": False,
    "demo_mode": True
}

# Demo Text Evaluation Results (Preset)
DEMO_TEXT_RESULTS = {
    "general": {
        "question": "Explain the process of photosynthesis in plants.",
        "student_answer": "Photosynthesis is how plants make their own food using sunlight, water and carbon dioxide. They convert light energy into chemical energy stored in glucose. The process happens in chloroplasts which contain chlorophyll.",
        "reference_answer": "Photosynthesis is the biochemical process by which green plants convert light energy into chemical energy using chlorophyll. They combine CO2 and water to produce glucose and oxygen in two stages: light-dependent reactions and the Calvin cycle.",
        "similarity": 0.782,
        "coverage": 0.845,
        "grammar": 0.890,
        "relevance": 0.920,
        "final_score": 8.35,
        "grade": "A",
        "percentage": 83.5,
        "feedback": "Good answer with solid understanding. You correctly identified key concepts like chloroplasts, chlorophyll, and energy conversion. Consider mentioning the two stages (light and dark reactions).",
        "gap_analysis": {
            "matched": [
                {"concept": "photosynthesis", "status": "correct"},
                {"concept": "light energy", "status": "correct"},
                {"concept": "glucose", "status": "correct"},
                {"concept": "chloroplasts", "status": "correct"},
                {"concept": "chlorophyll", "status": "correct"}
            ],
            "missing": [
                {"concept": "oxygen production", "importance": "high", "marks_worth": 2},
                {"concept": "Calvin cycle", "importance": "medium", "marks_worth": 2}
            ],
            "coverage_percentage": 84.5,
            "total_reference_concepts": 8,
            "matched_concepts": 5,
            "missing_concepts": 2,
            "vague": [],
            "visual_highlights": []
        },
        "matched_concepts": ["photosynthesis", "glucose", "chlorophyll", "light energy", "chloroplasts"],
        "missing_concepts": ["Calvin cycle", "light-dependent reactions", "oxygen"]
    },
    "physics": {
        "question": "State Newton's Second Law of Motion and provide an example.",
        "student_answer": "F=ma. Force equals mass times acceleration. If you apply 10N to a 2kg object it accelerates at 5 m/s². A heavier object needs more force to achieve the same acceleration.",
        "reference_answer": "Newton's Second Law states F=ma. The acceleration of an object is directly proportional to net force and inversely proportional to mass. Example: 10N on 2kg gives 5 m/s² acceleration.",
        "similarity": 0.875,
        "coverage": 0.820,
        "grammar": 0.860,
        "relevance": 0.930,
        "final_score": 8.80,
        "grade": "A",
        "percentage": 88.0,
        "feedback": "Excellent answer! You correctly stated the law and provided a clear numerical example demonstrating the relationship between force, mass and acceleration.",
        "gap_analysis": {
            "matched": [
                {"concept": "F=ma", "status": "correct"},
                {"concept": "force", "status": "correct"},
                {"concept": "mass", "status": "correct"},
                {"concept": "acceleration", "status": "correct"}
            ],
            "missing": [
                {"concept": "net force", "importance": "medium", "marks_worth": 1},
                {"concept": "inversely proportional", "importance": "low", "marks_worth": 1}
            ],
            "coverage_percentage": 82.0,
            "total_reference_concepts": 6,
            "matched_concepts": 4,
            "missing_concepts": 2,
            "vague": [],
            "visual_highlights": []
        },
        "matched_concepts": ["F=ma", "force", "mass", "acceleration", "example"],
        "missing_concepts": ["net force", "inversely proportional"]
    },
    "history": {
        "question": "What were the main causes of World War I?",
        "student_answer": "WWI was caused by militarism, alliances, imperialism, and nationalism (MAIN). The assassination of Archduke Franz Ferdinand in Sarajevo by Gavrilo Princip in 1914 was the immediate trigger.",
        "reference_answer": "World War I was caused by four MAIN factors: Militarism, Alliances, Imperialism, and Nationalism. The immediate trigger was the assassination of Archduke Franz Ferdinand on June 28, 1914.",
        "similarity": 0.925,
        "coverage": 0.910,
        "grammar": 0.880,
        "relevance": 0.960,
        "final_score": 9.20,
        "grade": "A+",
        "percentage": 92.0,
        "feedback": "Excellent answer! You correctly identified all four MAIN causes and provided accurate details about the assassination trigger. Outstanding historical accuracy.",
        "gap_analysis": {
            "matched": [
                {"concept": "militarism", "status": "correct"},
                {"concept": "alliances", "status": "correct"},
                {"concept": "imperialism", "status": "correct"},
                {"concept": "nationalism", "status": "correct"},
                {"concept": "Franz Ferdinand", "status": "correct"},
                {"concept": "Sarajevo", "status": "correct"}
            ],
            "missing": [
                {"concept": "arms race", "importance": "low", "marks_worth": 1}
            ],
            "coverage_percentage": 91.0,
            "total_reference_concepts": 7,
            "matched_concepts": 6,
            "missing_concepts": 1,
            "vague": [],
            "visual_highlights": []
        },
        "matched_concepts": ["militarism", "alliances", "imperialism", "nationalism", "Franz Ferdinand"],
        "missing_concepts": ["arms race"]
    },
    "computer_science": {
        "question": "Explain the difference between RAM and ROM in computers.",
        "student_answer": "RAM is volatile memory used for running programs temporarily. ROM is non-volatile and stores permanent boot instructions like BIOS. RAM can be read and written, ROM is read-only. RAM loses data when powered off.",
        "reference_answer": "RAM is volatile temporary memory for active programs, readable and writable. ROM is non-volatile permanent memory storing BIOS/firmware, read-only. RAM is faster with larger capacity.",
        "similarity": 0.858,
        "coverage": 0.875,
        "grammar": 0.820,
        "relevance": 0.940,
        "final_score": 8.65,
        "grade": "A",
        "percentage": 86.5,
        "feedback": "Very good explanation covering all key differences. You mentioned volatility, read/write capabilities, BIOS and power-off behaviour accurately.",
        "gap_analysis": {
            "matched": [
                {"concept": "volatile", "status": "correct"},
                {"concept": "non-volatile", "status": "correct"},
                {"concept": "BIOS", "status": "correct"},
                {"concept": "read-only", "status": "correct"},
                {"concept": "temporary", "status": "correct"}
            ],
            "missing": [
                {"concept": "CPU", "importance": "low", "marks_worth": 1},
                {"concept": "capacity", "importance": "low", "marks_worth": 1}
            ],
            "coverage_percentage": 87.5,
            "total_reference_concepts": 7,
            "matched_concepts": 5,
            "missing_concepts": 2,
            "vague": [],
            "visual_highlights": []
        },
        "matched_concepts": ["volatile", "non-volatile", "BIOS", "read-only", "temporary"],
        "missing_concepts": ["CPU", "capacity"]
    }
}


def generate_demo_pdf_response() -> dict:
    """Generate complete demo PDF handwritten evaluation response."""
    return DEMO_PDF_RESULTS


def generate_demo_text_response(subject: str = "general") -> dict:
    """Generate complete demo text evaluation response."""
    data = DEMO_TEXT_RESULTS.get(subject, DEMO_TEXT_RESULTS["general"])
    return {
        "question": data["question"],
        "student_answer": data["student_answer"],
        "reference_answer": data["reference_answer"],
        "similarity": data["similarity"],
        "coverage": data["coverage"],
        "grammar": data["grammar"],
        "relevance": data["relevance"],
        "final_score": data["final_score"],
        "grade": data["grade"],
        "percentage": data["percentage"],
        "feedback": data["feedback"],
        "gap_analysis": data["gap_analysis"],
        "matched_concepts": data["matched_concepts"],
        "missing_concepts": data["missing_concepts"],
        "evaluation_id": f"text_demo_{subject}",
        "processing_time_ms": 850,
        "llm_enhanced": True,
        "demo_mode": True
    }


# Demo CS PDF Evaluation Results (Preset)
DEMO_CS_PDF_RESULTS = {
    "questions_results": [
        {
            "question_number": 1,
            "question_text": "What is the difference between a compiler and an interpreter? Give one example of each. [5 marks]",
            "extracted_answer": "A compiler translates the entire source code into machine code before execution, e.g. GCC for C. An interpreter executes code line by line without producing a separate executable, e.g. Python interpreter. Compilers are faster at runtime; interpreters are easier to debug.",
            "generated_reference": "A compiler translates entire source code to machine code before execution (e.g. GCC). An interpreter executes code line-by-line at runtime (e.g. Python). Compilers produce standalone executables; interpreters do not.",
            "max_marks": 5,
            "obtained_marks": 4.2,
            "similarity_score": 0.84,
            "coverage_score": 0.80,
            "feedback": "Good",
            "gap_analysis": {
                "matched": [
                    {"concept": "compiler", "status": "correct"},
                    {"concept": "interpreter", "status": "correct"},
                    {"concept": "machine code", "status": "correct"},
                    {"concept": "GCC", "status": "correct"},
                    {"concept": "Python", "status": "correct"}
                ],
                "missing": [
                    {"concept": "standalone executable", "importance": "medium", "marks_worth": 1}
                ],
                "coverage_percentage": 83.0
            }
        },
        {
            "question_number": 2,
            "question_text": "Explain the concept of Object-Oriented Programming and its four main principles. [10 marks]",
            "extracted_answer": "OOP organises software around objects. Its four principles are: 1) Encapsulation - bundling data and methods, hiding internal details. 2) Inheritance - child class inherits from parent, promoting reuse. 3) Polymorphism - same method behaves differently by object type. 4) Abstraction - hiding complex implementation through interfaces.",
            "generated_reference": "OOP organises software around objects. Four principles: Encapsulation (data hiding), Inheritance (code reuse via parent-child classes), Polymorphism (same interface, different behaviour), Abstraction (hiding complexity via interfaces/abstract classes).",
            "max_marks": 10,
            "obtained_marks": 9.1,
            "similarity_score": 0.92,
            "coverage_score": 0.90,
            "feedback": "Excellent!",
            "gap_analysis": {
                "matched": [
                    {"concept": "encapsulation", "status": "correct"},
                    {"concept": "inheritance", "status": "correct"},
                    {"concept": "polymorphism", "status": "correct"},
                    {"concept": "abstraction", "status": "correct"},
                    {"concept": "objects", "status": "correct"},
                    {"concept": "interfaces", "status": "correct"}
                ],
                "missing": [
                    {"concept": "abstract classes", "importance": "low", "marks_worth": 1}
                ],
                "coverage_percentage": 90.0
            }
        },
        {
            "question_number": 3,
            "question_text": "What is a binary search algorithm? Write its time complexity and explain how it works. [10 marks]",
            "extracted_answer": "Binary search works on a sorted array. It checks the middle element and if the target is smaller it searches the left half, otherwise the right half. It keeps dividing until found. Time complexity is O(log n).",
            "generated_reference": "Binary search finds an element in a sorted array by repeatedly halving the search space. Compare target with middle element; search left half if smaller, right if larger. Time complexity O(log n), space O(1) iterative.",
            "max_marks": 10,
            "obtained_marks": 6.5,
            "similarity_score": 0.75,
            "coverage_score": 0.60,
            "feedback": "Satisfactory",
            "gap_analysis": {
                "matched": [
                    {"concept": "sorted array", "status": "correct"},
                    {"concept": "middle element", "status": "correct"},
                    {"concept": "O(log n)", "status": "correct"},
                    {"concept": "halving", "status": "correct"}
                ],
                "missing": [
                    {"concept": "space complexity O(1)", "importance": "high", "marks_worth": 2},
                    {"concept": "iterative vs recursive", "importance": "medium", "marks_worth": 2},
                    {"concept": "pseudocode or code example", "importance": "high", "marks_worth": 2}
                ],
                "coverage_percentage": 60.0
            }
        },
        {
            "question_number": 4,
            "question_text": "Differentiate between a stack and a queue data structure with examples. [5 marks]",
            "extracted_answer": "A stack follows LIFO order. Elements are pushed and popped from the top. Example: browser back button. A queue follows FIFO order. Elements added at rear, removed from front. Example: print job queue.",
            "generated_reference": "Stack: LIFO (Last In First Out), push/pop from top, e.g. function call stack. Queue: FIFO (First In First Out), enqueue at rear, dequeue from front, e.g. CPU scheduling.",
            "max_marks": 5,
            "obtained_marks": 4.5,
            "similarity_score": 0.88,
            "coverage_score": 0.85,
            "feedback": "Excellent!",
            "gap_analysis": {
                "matched": [
                    {"concept": "LIFO", "status": "correct"},
                    {"concept": "FIFO", "status": "correct"},
                    {"concept": "push pop", "status": "correct"},
                    {"concept": "rear front", "status": "correct"},
                    {"concept": "example", "status": "correct"}
                ],
                "missing": [
                    {"concept": "function call stack example", "importance": "low", "marks_worth": 1}
                ],
                "coverage_percentage": 85.0
            }
        },
        {
            "question_number": 5,
            "question_text": "What is an operating system? Describe its main functions. [10 marks]",
            "extracted_answer": "An operating system manages the computer hardware and software. It provides a user interface and runs programs. Examples are Windows and Linux.",
            "generated_reference": "An OS is system software managing hardware and software resources. Functions: process management, memory management, file system management, device management, security, and providing a user interface.",
            "max_marks": 10,
            "obtained_marks": 3.5,
            "similarity_score": 0.45,
            "coverage_score": 0.30,
            "feedback": "Needs improvement",
            "gap_analysis": {
                "matched": [
                    {"concept": "hardware management", "status": "correct"},
                    {"concept": "user interface", "status": "correct"}
                ],
                "missing": [
                    {"concept": "process management", "importance": "high", "marks_worth": 2},
                    {"concept": "memory management", "importance": "high", "marks_worth": 2},
                    {"concept": "file system", "importance": "high", "marks_worth": 2},
                    {"concept": "device management", "importance": "medium", "marks_worth": 1},
                    {"concept": "security", "importance": "medium", "marks_worth": 1}
                ],
                "coverage_percentage": 30.0
            }
        },
        {
            "question_number": 6,
            "question_text": "Explain the difference between TCP and UDP protocols. [5 marks]",
            "extracted_answer": "TCP is connection-oriented. It establishes a connection via three-way handshake and guarantees delivery, ordering, and error checking. Used for web browsing and email. UDP is connectionless, does not guarantee delivery or order. Faster, used for video streaming, gaming, and DNS.",
            "generated_reference": "TCP: connection-oriented, three-way handshake, reliable delivery, ordered, error-checked. Used for HTTP, email. UDP: connectionless, no delivery guarantee, faster, lower overhead. Used for DNS, streaming, VoIP.",
            "max_marks": 5,
            "obtained_marks": 4.8,
            "similarity_score": 0.93,
            "coverage_score": 0.92,
            "feedback": "Excellent!",
            "gap_analysis": {
                "matched": [
                    {"concept": "connection-oriented", "status": "correct"},
                    {"concept": "three-way handshake", "status": "correct"},
                    {"concept": "reliable delivery", "status": "correct"},
                    {"concept": "connectionless", "status": "correct"},
                    {"concept": "UDP faster", "status": "correct"},
                    {"concept": "use cases", "status": "correct"}
                ],
                "missing": [
                    {"concept": "VoIP", "importance": "low", "marks_worth": 0}
                ],
                "coverage_percentage": 92.0
            }
        },
        {
            "question_number": 7,
            "question_text": "What is database normalization? Explain 1NF, 2NF and 3NF with examples. [10 marks]",
            "extracted_answer": "Database normalization reduces data redundancy. 1NF: atomic values, unique rows. Example: splitting multi-valued phone column. 2NF: in 1NF, non-key attributes depend on whole primary key. Could not remember 3NF.",
            "generated_reference": "Normalization organises data to reduce redundancy. 1NF: atomic values, no repeating groups. 2NF: 1NF + no partial dependencies. 3NF: 2NF + no transitive dependencies (non-key attributes depend only on primary key).",
            "max_marks": 10,
            "obtained_marks": 5.5,
            "similarity_score": 0.62,
            "coverage_score": 0.55,
            "feedback": "Satisfactory",
            "gap_analysis": {
                "matched": [
                    {"concept": "redundancy", "status": "correct"},
                    {"concept": "1NF atomic values", "status": "correct"},
                    {"concept": "2NF partial dependency", "status": "correct"}
                ],
                "missing": [
                    {"concept": "3NF transitive dependency", "importance": "high", "marks_worth": 3},
                    {"concept": "3NF example", "importance": "high", "marks_worth": 2},
                    {"concept": "repeating groups", "importance": "medium", "marks_worth": 1}
                ],
                "coverage_percentage": 55.0
            }
        },
        {
            "question_number": 8,
            "question_text": "What is recursion in programming? Write a recursive function to calculate factorial. [10 marks]",
            "extracted_answer": "Recursion is when a function calls itself to solve a smaller version of the same problem. It must have a base case. def factorial(n): if n==0 or n==1: return 1; return n * factorial(n-1). factorial(5) = 120.",
            "generated_reference": "Recursion: a function calling itself with a smaller input until a base case is reached. factorial(n) = n * factorial(n-1), base case factorial(0)=1. Each call is placed on the call stack.",
            "max_marks": 10,
            "obtained_marks": 9.0,
            "similarity_score": 0.91,
            "coverage_score": 0.88,
            "feedback": "Excellent!",
            "gap_analysis": {
                "matched": [
                    {"concept": "function calls itself", "status": "correct"},
                    {"concept": "base case", "status": "correct"},
                    {"concept": "factorial code", "status": "correct"},
                    {"concept": "correct output", "status": "correct"}
                ],
                "missing": [
                    {"concept": "call stack explanation", "importance": "medium", "marks_worth": 1}
                ],
                "coverage_percentage": 88.0
            }
        },
        {
            "question_number": 9,
            "question_text": "Explain the concept of virtual memory and how it works in modern operating systems. [5 marks]",
            "extracted_answer": "(No answer attempted)",
            "generated_reference": "Virtual memory allows a computer to use disk space as an extension of RAM. The OS uses paging to swap memory pages between RAM and disk. Enables running programs larger than physical RAM.",
            "max_marks": 5,
            "obtained_marks": 0.0,
            "similarity_score": 0.0,
            "coverage_score": 0.0,
            "feedback": "No answer detected",
            "gap_analysis": {
                "matched": [],
                "missing": [
                    {"concept": "virtual memory definition", "importance": "high", "marks_worth": 2},
                    {"concept": "paging", "importance": "high", "marks_worth": 2},
                    {"concept": "disk as RAM extension", "importance": "high", "marks_worth": 1}
                ],
                "coverage_percentage": 0.0
            }
        },
        {
            "question_number": 10,
            "question_text": "What is the difference between HTTP and HTTPS? Why is HTTPS important? [5 marks]",
            "extracted_answer": "HTTP transfers data in plain text. HTTPS uses SSL/TLS encryption to protect data in transit. HTTPS prevents attackers from intercepting passwords and credit card numbers, and improves trust and SEO ranking.",
            "generated_reference": "HTTP is plain-text protocol for web communication. HTTPS adds SSL/TLS encryption, ensuring data confidentiality and integrity. Important for protecting sensitive data, authentication, and SEO.",
            "max_marks": 5,
            "obtained_marks": 4.6,
            "similarity_score": 0.90,
            "coverage_score": 0.87,
            "feedback": "Excellent!",
            "gap_analysis": {
                "matched": [
                    {"concept": "plain text", "status": "correct"},
                    {"concept": "SSL/TLS", "status": "correct"},
                    {"concept": "encryption", "status": "correct"},
                    {"concept": "sensitive data", "status": "correct"},
                    {"concept": "SEO", "status": "correct"}
                ],
                "missing": [
                    {"concept": "authentication", "importance": "low", "marks_worth": 0}
                ],
                "coverage_percentage": 87.0
            }
        },
    ],
    "total_score": 51.7,
    "total_marks": 75,
    "percentage": 68.9,
    "grade": "B-",
    "processing_time_ms": 5200,
    "llm_used": False,
    "demo_mode": True
}


def generate_demo_cs_pdf_response() -> dict:
    """Generate complete demo CS PDF evaluation response."""
    return DEMO_CS_PDF_RESULTS
