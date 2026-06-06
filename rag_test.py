from dotenv import load_dotenv
from openai import OpenAI

from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


load_dotenv()
client = OpenAI()


DISTANCE_THRESHOLD = 1.2


def load_markdown_file(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def build_chunks(markdown_text: str):
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )

    chunks = splitter.split_text(markdown_text)
    return chunks


def build_vector_store(chunks):
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(
        documents=chunks,
        embedding=embedding_model
    )

    vector_store.save_local("faiss_index")

    return vector_store


def format_context(docs):
    context_parts = []

    for doc in docs:
        header_1 = doc.metadata.get("Header 1", "")
        header_2 = doc.metadata.get("Header 2", "")

        context_parts.append(
            f"[Document: {header_1} | Section: {header_2}]\n"
            f"{doc.page_content}"
        )

    return "\n\n".join(context_parts)


def generate_answer(query: str, docs):
    context = format_context(docs)

    system_prompt = """
You are an airline cargo support assistant that answers questions using only the provided support SOP context.

Use clear technical language. Structure the answer with:
1. Issue summary
2. Relevant cause or rule found in the provided context
3. Recommended next check or action
4. Source citation

If the answer is not available in the provided context, reply exactly:
"I do not know based on the available airline cargo support documents."

Do not speculate. Do not invent root causes. Do not use general knowledge. Do not answer outside the provided context.
"""

    user_prompt = f"""
Context:
{context}

Question:
{query}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    return response.output_text


def run_retrieval_tests(vector_store):
    queries = [
        "What are the mandatory shipment message segments?",
        "Why is AWB not visible after message upload?",
        "What does customs information validation error mean?",
        "Why was AWB 618-12345675 delayed yesterday?",
        "What is the weather in Mumbai today?"
    ]

    for query in queries:
        print("\n" + "=" * 100)
        print("QUERY:", query)

        results = vector_store.similarity_search_with_score(query, k=3)
        best_doc, best_score = results[0]

        retrieved_docs = [
            doc for doc, score in results
            if score <= DISTANCE_THRESHOLD
        ]

        if best_score > DISTANCE_THRESHOLD:
            print("VERDICT: Out of domain / no reliable context")
            print(
                "LLM Answer: I do not know based on the available airline cargo support documents."
            )
        else:
            print("VERDICT: Relevant context found")

            answer = generate_answer(query, retrieved_docs)

            print("\nLLM Answer:")
            print(answer)

        print("\nRetrieved chunks:")

        for rank, (doc, score) in enumerate(results, start=1):
            print("\n--- Retrieved Chunk", rank, "---")
            print("Score:", score)
            print("Metadata:", doc.metadata)
            print("Content:")
            print(doc.page_content[:500])


def main():
    markdown_text = load_markdown_file("data/airline_support_sop.md")
    chunks = build_chunks(markdown_text)

    print("File loaded successfully")
    print("Total characters:", len(markdown_text))
    print("Total chunks created:", len(chunks))

    for index, chunk in enumerate(chunks, start=1):
        print("\n" + "-" * 80)
        print(f"Chunk {index}")
        print("Metadata:", chunk.metadata)
        print("Content preview:")
        print(chunk.page_content[:300])

    vector_store = build_vector_store(chunks)
    print("\nFAISS index created and saved successfully")

    run_retrieval_tests(vector_store)


if __name__ == "__main__":
    main()