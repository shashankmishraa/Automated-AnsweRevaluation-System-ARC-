import os
import random
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from auto_ref_generator import get_reference_generator
from pdf_processor import get_pdf_processor


ROOT = Path(__file__).resolve().parent
QUESTION_PDF = ROOT / "sample_question_paper.pdf"
OUTPUT_PDF = ROOT / "sample_handwritten_answers_generated.pdf"


def load_handwriting_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        r"C:\Windows\Fonts\segoesc.ttf",   # Segoe Script
        r"C:\Windows\Fonts\BRADHITC.TTF",  # Bradley Hand
        r"C:\Windows\Fonts\comic.ttf",     # Comic Sans (fallback handwriting-like)
        r"C:\Windows\Fonts\calibri.ttf",   # General fallback
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def main() -> None:
    if not QUESTION_PDF.exists():
        raise FileNotFoundError(f"Question paper not found: {QUESTION_PDF}")

    processor = get_pdf_processor()
    generator = get_reference_generator()

    question_bytes = QUESTION_PDF.read_bytes()
    questions = processor.process_question_paper(question_bytes)
    if not questions:
        raise RuntimeError("No questions could be parsed from sample_question_paper.pdf")

    page_w, page_h = 1654, 2339  # A4-ish at ~150-200dpi
    margin_x = 120
    top_y = 140
    line_h = 48
    max_chars = 75

    title_font = load_handwriting_font(44)
    body_font = load_handwriting_font(36)

    pages = []
    img = Image.new("RGB", (page_w, page_h), "white")
    draw = ImageDraw.Draw(img)
    y = top_y

    draw.text((margin_x, y), "Student Answer Sheet", fill="black", font=title_font)
    y += 90
    draw.text((margin_x, y), "Name: Demo Student    Roll: 24A-017", fill="black", font=body_font)
    y += 80

    for q in questions:
        generated = generator.generate_reference_answer(q.text, max_length=500).generated_answer
        answer_text = generated if generated else "Answer not available."

        block_lines = [f"Q{q.number}. {q.text}"]
        wrapped = textwrap.wrap(answer_text, width=max_chars)
        block_lines.extend(["Ans:"] + wrapped + [""])

        required_h = (len(block_lines) + 1) * line_h
        if y + required_h > page_h - 140:
            pages.append(img)
            img = Image.new("RGB", (page_w, page_h), "white")
            draw = ImageDraw.Draw(img)
            y = top_y

        for line in block_lines:
            jitter_x = margin_x + random.randint(-6, 8)
            draw.text((jitter_x, y), line, fill="black", font=body_font)
            y += line_h + random.randint(-3, 5)

    pages.append(img)

    pages[0].save(
        OUTPUT_PDF,
        save_all=True,
        append_images=pages[1:],
        resolution=150.0,
    )
    print(f"Generated handwritten-style answer PDF: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()

