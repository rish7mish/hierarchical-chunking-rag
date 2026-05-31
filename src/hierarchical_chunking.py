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

def split_parent_into_child_chunks(
    parent: ParentChunk,
    max_words: int = 120,
    overlap_words: int = 20
) -> List[ChildChunk]:
    """
    Split one parent chunk into smaller child chunks.

    Child chunks are used for precise retrieval.
    Parent chunks are used later to provide broader context.
    """
    words = parent.text.split()
    child_chunks = []

    if not words:
        return child_chunks

    start = 0
    child_index = 0

    while start < len(words):
        end = start + max_words
        child_words = words[start:end]
        child_text = " ".join(child_words)

        child_id = f"child-{uuid.uuid4().hex[:8]}"

        child_chunks.append(
            ChildChunk(
                child_id=child_id,
                parent_id=parent.parent_id,
                document_id=parent.document_id,
                text=child_text,
                metadata={
                    "level": "child",
                    "child_index": child_index,
                    "parent_id": parent.parent_id,
                    "parent_title": parent.title,
                    "start_word": start,
                    "end_word": min(end, len(words))
                }
            )
        )

        child_index += 1
        start += max_words - overlap_words

    return child_chunks    

def build_hierarchical_chunks(pdf_path: str) -> Dict:
    """
    Build the full hierarchical chunk structure from a PDF.

    Flow:
    PDF -> raw text -> cleaned text -> parent chunks -> child chunks

    Returns:
    - document_id
    - parent chunks
    - child chunks
    - parent lookup dictionary
    """
    document_id = f"doc-{uuid.uuid4().hex[:8]}"

    raw_text = extract_text_from_pdf(pdf_path)
    cleaned_text = clean_text(raw_text)

    parent_chunks = split_into_parent_chunks(cleaned_text, document_id)

    child_chunks = []
    for parent in parent_chunks:
        child_chunks.extend(split_parent_into_child_chunks(parent))

    parent_lookup = {
        parent.parent_id: parent
        for parent in parent_chunks
    }

    return {
        "document_id": document_id,
        "parents": parent_chunks,
        "children": child_chunks,
        "parent_lookup": parent_lookup
    }    

def simple_keyword_search(
    query: str,
    child_chunks: List[ChildChunk],
    top_k: int = 3
):
    """
    Simple keyword-based retrieval over child chunks.

    This is only for demonstrating hierarchical retrieval.
    In a real RAG system, this would be replaced by:
    - embeddings
    - vector database
    - cosine similarity
    - hybrid search
    """
    query_terms = set(query.lower().split())
    scored_chunks = []

    for child in child_chunks:
        child_terms = set(child.text.lower().split())
        score = len(query_terms.intersection(child_terms))

        if score > 0:
            scored_chunks.append((score, child))

    scored_chunks.sort(key=lambda item: item[0], reverse=True)

    return scored_chunks[:top_k]    

def retrieve_with_parent_context(
    query: str,
    hierarchy: Dict,
    top_k: int = 3
):
    """
    Retrieve child chunks first, then fetch their parent chunks.

    This demonstrates hierarchical retrieval:
    - child chunk gives precision
    - parent chunk gives broader context
    """
    results = simple_keyword_search(
        query=query,
        child_chunks=hierarchy["children"],
        top_k=top_k
    )

    final_results = []

    for score, child in results:
        parent = hierarchy["parent_lookup"][child.parent_id]

        final_results.append({
            "score": score,
            "child_chunk": asdict(child),
            "parent_context": asdict(parent)
        })

    return final_results    

if __name__ == "__main__":
    pdf_path = "data/sample.pdf"

    hierarchy = build_hierarchical_chunks(pdf_path)

    print("Document ID:", hierarchy["document_id"])
    print("Total Parent Chunks:", len(hierarchy["parents"]))
    print("Total Child Chunks:", len(hierarchy["children"]))

    query = "attention mechanism architecture"

    results = retrieve_with_parent_context(
        query=query,
        hierarchy=hierarchy,
        top_k=3
    )

    print("\nQuery:", query)
    print("\nHierarchical Retrieval Results:")

    for result in results:
        print("=" * 80)
        print("Score:", result["score"])

        print("\nChild Chunk:")
        print("Child ID:", result["child_chunk"]["child_id"])
        print("Parent ID:", result["child_chunk"]["parent_id"])
        print(result["child_chunk"]["text"][:500])

        print("\nParent Context:")
        print("Parent ID:", result["parent_context"]["parent_id"])
        print("Title:", result["parent_context"]["title"])
        print(result["parent_context"]["text"][:800])