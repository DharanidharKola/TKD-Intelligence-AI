
import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore

from backend.rag.embeddings import get_embeddings


ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")


@lru_cache(maxsize=1)
def get_vector_store():
    """Reuse the WT Rules Pinecone vector store."""

    index_name = os.getenv("PINECONE_INDEX_NAME")

    if not index_name:
        raise ValueError("PINECONE_INDEX_NAME missing from environment")

    return PineconeVectorStore(
        index_name=index_name,
        embedding=get_embeddings(),
        namespace="wt-rules-2026",
    )


def retrieve_rules(question: str, k: int = 4):
    """
    Retrieve a small number of relevant WT Rules passages.
    Keeps the LLM prompt compact.
    """

    if not question or not question.strip():
        return []

    vector_store = get_vector_store()

    results = vector_store.similarity_search_with_score(
        question.strip()[:1000],
        k=min(k, 4),
    )

    unique_results = []
    seen = set()

    for document, score in results:
        content = document.page_content.strip()

        key = (
            document.metadata.get("page"),
            content,
        )

        if key in seen:
            continue

        seen.add(key)

        unique_results.append({
            "content": content[:1200],
            "page": document.metadata.get("page"),
            "source": document.metadata.get("source"),
            "score": float(score),
        })

    return unique_results


if __name__ == "__main__":
    question = "What are the prohibited acts and penalties in Taekwondo?"

    results = retrieve_rules(question)

    print("Retrieved passages:", len(results))

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print("Page:", result["page"])
        print("Score:", result["score"])
        print(result["content"])
