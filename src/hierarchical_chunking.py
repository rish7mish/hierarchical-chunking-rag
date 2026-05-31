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

def clean_text(text: str) -> str:
    """
    Clean extracted PDF text.

    This removes excessive blank lines and extra spaces
    while keeping basic paragraph/page structure.
    """
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()    

def split_into_parent_chunks(text: str, document_id: str) -> List[ParentChunk]:
    """
    Split cleaned text into parent chunks.

    In this simple version, each PDF page becomes one parent chunk.
    Parent chunks provide broader context during retrieval.
    """
    raw_sections = re.split(r"\[PAGE\s+\d+\]", text)
    parent_chunks = []

    for index, section_text in enumerate(raw_sections):
        section_text = section_text.strip()

        if not section_text:
            continue

        parent_id = f"parent-{uuid.uuid4().hex[:8]}"

        parent_chunks.append(
            ParentChunk(
                parent_id=parent_id,
                document_id=document_id,
                title=f"Page Section {index}",
                text=section_text,
                metadata={
                    "level": "parent",
                    "parent_index": index,
                    "chunk_type": "page_or_section"
                }
            )
        )

    return parent_chunks    

if __name__ == "__main__":
    pdf_path = "data/sample.pdf"
    document_id = f"doc-{uuid.uuid4().hex[:8]}"

    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)

    parent_chunks = split_into_parent_chunks(cleaned_text, document_id)

    print("Document ID:", document_id)
    print("Total Parent Chunks:", len(parent_chunks))

    for parent in parent_chunks[:2]:
        print("=" * 80)
        print("Parent ID:", parent.parent_id)
        print("Title:", parent.title)
        print("Metadata:", parent.metadata)
        print("Text Preview:", parent.text[:500])