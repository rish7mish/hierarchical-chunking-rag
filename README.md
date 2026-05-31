# Hierarchical Chunking for RAG

This project demonstrates hierarchical chunking for a Retrieval-Augmented Generation (RAG) pipeline.

The goal is to split a PDF into:

- Parent chunks: larger context blocks
- Child chunks: smaller retrieval-focused chunks

During retrieval, the system first retrieves the most relevant child chunk and then fetches its parent chunk to provide broader context.

## Why Hierarchical Chunking?

Flat chunking treats every chunk independently. This can cause loss of context when a small chunk is retrieved.

Hierarchical chunking solves this by maintaining a relationship between child chunks and parent chunks.

Retrieval flow:

```text
User query
 ↓
Search child chunks
 ↓
Retrieve precise child chunk
 ↓
Use child.parent_id
 ↓
Fetch parent context
 ↓
Return child + parent

hierarchical-chunking-rag/
│
├── src/
│   └── hierarchical_chunking.py
│
├── data/
│   └── sample.pdf
│
├── requirements.txt
├── README.md
└── .gitignore