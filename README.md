# Automated Answer Revaluation System (ARC)

This repository contains an automated answer evaluation system for handwritten and typed answer sheets. It includes backend scoring, PDF processing, reactive UI components, and report generation tools.

## Project structure

- `app.py`, `main.py`, `scoring.py`, `pdf_processor.py`, `generate_html_report.py`, etc. - core Python scoring and report generation logic
- `ui-react/` - React frontend for user interaction
- `batch_test/` - example test inputs and student answer cases
- `requirements.txt` - Python dependencies
- `.gitignore` - ignores generated artifacts, model files, and environment files

## Usage

1. Create a Python virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Run the backend service or scoring script as needed

## Notes

- The `.gitignore` already excludes generated files such as `*.db`, `*.h5`, `*.pkl`, `node_modules/`, and environment files.
- Do not commit secret or environment files like `.env`.
