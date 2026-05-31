from pypdf import PdfReader
from dataclasses import dataclass, asdict
from typing import List, Dict
import re
import uuid

@dataclass
class ParentChunk:
    parent_id: str
    document_id: str
    title: str
    text: str
    metadata: Dict


@dataclass
class ChildChunk:
    child_id: str
    parent_id: str
    document_id: str
    text: str
    metadata: Dict

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a text-based PDF file.

    Note:
    This works for normal PDFs where text can be selected.
    Scanned image PDFs need OCR before this step.
    """
    reader = PdfReader(pdf_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append(f"\n\n[PAGE {page_number}]\n{text}")

    return "\n".join(pages)    

if __name__ == "__main__":
    pdf_path = "data/sample.pdf"
    text = extract_text_from_pdf(pdf_path)
    print(text[:1000])    