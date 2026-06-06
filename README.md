# Hierarchical Chunking for RAG (Airline Cargo Support)

This project demonstrates a Retrieval-Augmented Generation (RAG) pipeline utilizing hierarchical chunking on a Markdown Standard Operating Procedure (SOP) document.

The pipeline splits structured Markdown text by section headers (e.g., `#`, `##`, `###`) to preserve context. During retrieval, we search for precise chunks matching user queries and synthesize context-aware answers using an LLM.

## Architecture & Flow

1. **Document Loading**: Parse structured Markdown containing Airline Cargo SOPs ([data/airline_support_sop.md](file:///C:/Projects/hierarchical-chunking-rag/data/airline_support_sop.md)).
2. **Hierarchical Chunking**: Use LangChain's `MarkdownHeaderTextSplitter` to partition content based on heading levels, preserving the document structure.
3. **Local Vector Indexing**:
   - Generate embeddings for each chunk using `sentence-transformers/all-MiniLM-L6-v2`.
   - Store the vectors locally in a [FAISS](file:///C:/Projects/hierarchical-chunking-rag/faiss_index) index.
4. **Semantic Retrieval**:
   - Compute similarity search score between query and document chunks.
   - Filter chunks using a distance threshold to identify out-of-domain queries.
5. **Context-Aware Synthesis**:
   - Format retrieved sections as structured context.
   - Run the query through the OpenAI GPT-4 mini model to produce source-cited, accurate answers.

---

## Directory Structure

```text
hierarchical-chunking-rag/
│
├── data/
│   ├── airline_support_sop.md   # Airline Cargo SOP document
│   └── sample.pdf                # Sample PDF reference document
│
├── faiss_index/                  # Local FAISS vector index files
│   ├── index.faiss
│   └── index.pkl
│
├── src/
│   └── hierarchical_chunking.py  # Page-based PDF chunking reference
│
├── .env                          # Local environment secrets (ignored)
├── .gitignore
├── rag_test.py                   # Main RAG script (LangChain, FAISS, OpenAI)
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Installation

Install all required packages:
```bash
pip install -r requirements.txt
pip install langchain-community sentence-transformers faiss-cpu openai python-dotenv
```

### 2. Configuration

Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key
```

### 3. Execution

Run the retrieval tests:
```bash
python rag_test.py
```