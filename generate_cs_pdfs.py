# -*- coding: utf-8 -*-
"""
Generate CS question paper PDF and a student answer sheet PDF.
Answers are intentionally varied in quality (excellent, good, partial,
vague, blank) so the evaluator has realistic data to work with.
"""

import os
import random
import textwrap
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors

from PIL import Image, ImageDraw, ImageFont

ROOT         = Path(__file__).resolve().parent
QUESTION_PDF = ROOT / "cs_question_paper.pdf"
ANSWER_PDF   = ROOT / "cs_student_answers.pdf"

# --------------------------------------------------------------------------- #
# 10 CS Questions
# --------------------------------------------------------------------------- #
QUESTIONS = [
    {"number": 1,  "text": "What is the difference between a compiler and an interpreter? Give one example of each.", "marks": 5},
    {"number": 2,  "text": "Explain the concept of Object-Oriented Programming and its four main principles.", "marks": 10},
    {"number": 3,  "text": "What is a binary search algorithm? Write its time complexity and explain how it works.", "marks": 10},
    {"number": 4,  "text": "Differentiate between a stack and a queue data structure with examples.", "marks": 5},
    {"number": 5,  "text": "What is an operating system? Describe its main functions.", "marks": 10},
    {"number": 6,  "text": "Explain the difference between TCP and UDP protocols.", "marks": 5},
    {"number": 7,  "text": "What is database normalization? Explain 1NF, 2NF and 3NF with examples.", "marks": 10},
    {"number": 8,  "text": "What is recursion in programming? Write a recursive function to calculate factorial.", "marks": 10},
    {"number": 9,  "text": "Explain the concept of virtual memory and how it works in modern operating systems.", "marks": 5},
    {"number": 10, "text": "What is the difference between HTTP and HTTPS? Why is HTTPS important?", "marks": 5},
]

# --------------------------------------------------------------------------- #
# Student answers — intentionally varied quality
# Q1  good | Q2  excellent | Q3  partial | Q4  good | Q5  vague
# Q6  excellent | Q7  partial | Q8  excellent | Q9  blank | Q10 good
# --------------------------------------------------------------------------- #
ANSWERS = [
    # Q1 — good
    (
        "A compiler translates the entire source code into machine code before execution, e.g. GCC for C. "
        "An interpreter executes code line by line without producing a separate executable, e.g. Python interpreter. "
        "Compilers are faster at runtime; interpreters are easier to debug."
    ),

    # Q2 — excellent
    (
        "Object-Oriented Programming (OOP) organises software around objects rather than functions. "
        "Its four main principles are: "
        "1) Encapsulation - bundling data and methods together and hiding internal details (e.g. private fields in Java). "
        "2) Inheritance - a child class inherits properties from a parent class, promoting code reuse. "
        "3) Polymorphism - the same method name behaves differently depending on the object type. "
        "4) Abstraction - hiding complex implementation and showing only necessary details through interfaces or abstract classes."
    ),

    # Q3 — partial (missing space complexity and iterative comparison)
    (
        "Binary search works on a sorted array. It checks the middle element and if the target is smaller "
        "it searches the left half, otherwise the right half. It keeps dividing until found. "
        "Time complexity is O(log n)."
    ),

    # Q4 — good
    (
        "A stack follows LIFO (Last In First Out) order. Elements are pushed and popped from the top. "
        "Example: browser back button history. "
        "A queue follows FIFO (First In First Out) order. Elements are added at the rear and removed from the front. "
        "Example: print job queue in an operating system."
    ),

    # Q5 — vague / incomplete
    (
        "An operating system manages the computer hardware and software. "
        "It provides a user interface and runs programs. "
        "Examples are Windows and Linux."
    ),

    # Q6 — excellent
    (
        "TCP (Transmission Control Protocol) is connection-oriented. It establishes a connection via a "
        "three-way handshake before data transfer and guarantees delivery, ordering, and error checking. "
        "Used for web browsing and email. "
        "UDP (User Datagram Protocol) is connectionless. It sends packets without establishing a connection "
        "and does not guarantee delivery or order. It is faster and used for video streaming, gaming, and DNS."
    ),

    # Q7 — partial (misses 3NF)
    (
        "Database normalization reduces data redundancy and improves integrity. "
        "1NF: Each column must contain atomic values and each row must be unique. "
        "Example: splitting a multi-valued phone number column into separate rows. "
        "2NF: Must be in 1NF and every non-key attribute must depend on the whole primary key. "
        "I could not remember the exact definition of 3NF."
    ),

    # Q8 — excellent
    (
        "Recursion is when a function calls itself to solve a smaller version of the same problem. "
        "It must have a base case to stop the recursion. "
        "Factorial example: "
        "def factorial(n): "
        "    if n == 0 or n == 1: return 1 "
        "    return n * factorial(n - 1) "
        "factorial(5) = 5 * 4 * 3 * 2 * 1 = 120."
    ),

    # Q9 — blank
    "",

    # Q10 — good
    (
        "HTTP transfers data between browser and server in plain text. "
        "HTTPS is the secure version that uses SSL/TLS encryption to protect data in transit. "
        "HTTPS is important because it prevents attackers from intercepting sensitive data like passwords "
        "and credit card numbers, and it also improves trust and SEO ranking."
    ),
]


# --------------------------------------------------------------------------- #
# Font loader
# --------------------------------------------------------------------------- #
def load_font(size):
    candidates = [
        r"C:\Windows\Fonts\segoesc.ttf",
        r"C:\Windows\Fonts\BRADHITC.TTF",
        r"C:\Windows\Fonts\comic.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


# --------------------------------------------------------------------------- #
# Generate Question Paper PDF  (typed, ReportLab)
# --------------------------------------------------------------------------- #
def generate_question_paper():
    doc = SimpleDocTemplate(
        str(QUESTION_PDF),
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm,   bottomMargin=2*cm,
    )
    title_style = ParagraphStyle("title", fontSize=16, alignment=TA_CENTER,
                                 spaceAfter=6, fontName="Helvetica-Bold")
    sub_style   = ParagraphStyle("sub",   fontSize=11, alignment=TA_CENTER,
                                 spaceAfter=4, fontName="Helvetica")
    q_style     = ParagraphStyle("q",     fontSize=11, alignment=TA_LEFT,
                                 spaceAfter=6, fontName="Helvetica", leading=16)
    instr_style = ParagraphStyle("instr", fontSize=10, alignment=TA_LEFT,
                                 spaceAfter=4, fontName="Helvetica-Oblique",
                                 textColor=colors.grey)

    total_marks = sum(q["marks"] for q in QUESTIONS)
    story = [
        Paragraph("COMPUTER SCIENCE - MID-TERM EXAMINATION", title_style),
        Paragraph(
            "Subject: CS101 &nbsp;|&nbsp; Time: 2 Hours &nbsp;|&nbsp; "
            "Total Marks: %d" % total_marks,
            sub_style,
        ),
        HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=10),
        Paragraph(
            "Instructions: Answer ALL questions. Write clearly and show your working where applicable.",
            instr_style,
        ),
        Spacer(1, 0.4*cm),
    ]

    for q in QUESTIONS:
        story.append(Paragraph(
            "<b>Q%d.</b> %s &nbsp;&nbsp;<b>[%d marks]</b>" % (q["number"], q["text"], q["marks"]),
            q_style,
        ))
        story.append(Spacer(1, 0.3*cm))

    doc.build(story)
    print("Question paper saved: %s" % QUESTION_PDF)


# --------------------------------------------------------------------------- #
# Generate Answer Sheet PDF  (handwritten-style, PIL image)
# --------------------------------------------------------------------------- #
def generate_answer_sheet():
    page_w, page_h = 1654, 2339   # A4 at ~200 dpi
    margin_x = 120
    top_y    = 140
    line_h   = 50
    max_chars = 78

    title_font = load_font(46)
    body_font  = load_font(37)
    bold_font  = load_font(40)

    pages = []
    img   = Image.new("RGB", (page_w, page_h), "white")
    draw  = ImageDraw.Draw(img)
    y     = top_y

    # Header
    draw.text((margin_x, y), "Student Answer Sheet - CS101", fill="black", font=title_font)
    y += 90
    draw.text((margin_x, y),
              "Name: Alex Kumar    Roll No: CS-2024-042    Date: 17-Apr-2026",
              fill="black", font=body_font)
    y += 80
    draw.line([(margin_x, y), (page_w - margin_x, y)], fill="black", width=2)
    y += 30

    for idx, q in enumerate(QUESTIONS):
        answer_text = ANSWERS[idx]

        if not answer_text.strip():
            block_lines = [
                "Q%d. %s" % (q["number"], q["text"]),
                "Ans:",
                "(No answer attempted)",
                "",
            ]
        else:
            wrapped = textwrap.wrap(answer_text, width=max_chars)
            block_lines = ["Q%d. %s" % (q["number"], q["text"]), "Ans:"] + wrapped + [""]

        required_h = (len(block_lines) + 2) * line_h
        if y + required_h > page_h - 160:
            pages.append(img)
            img  = Image.new("RGB", (page_w, page_h), "white")
            draw = ImageDraw.Draw(img)
            y    = top_y

        for i, line in enumerate(block_lines):
            font  = bold_font if i == 0 else body_font
            color = (30, 30, 180) if i == 0 else "black"
            jitter = random.randint(-5, 7)
            draw.text((margin_x + jitter, y), line, fill=color, font=font)
            y += line_h + random.randint(-2, 4)

        draw.line([(margin_x, y), (page_w - margin_x, y)], fill=(200, 200, 200), width=1)
        y += 20

    pages.append(img)

    pages[0].save(
        str(ANSWER_PDF),
        save_all=True,
        append_images=pages[1:],
        resolution=150.0,
    )
    print("Answer sheet saved: %s" % ANSWER_PDF)


if __name__ == "__main__":
    print("Generating CS question paper...")
    generate_question_paper()
    print("Generating CS student answer sheet...")
    generate_answer_sheet()
    print("Done.")
    print("  Question paper : %s" % QUESTION_PDF)
    print("  Answer sheet   : %s" % ANSWER_PDF)
    print("Upload both in the OCR tab (PDF mode) to evaluate.")
