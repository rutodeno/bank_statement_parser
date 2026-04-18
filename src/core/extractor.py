'''
This file handles PDF to text extraction
'''

import pdfplumber
from pathlib import Path

def extract_text_from_pdf(pdf_path: Path) -> str:
    text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)


