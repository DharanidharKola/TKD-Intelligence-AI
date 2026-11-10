
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
    """
    Reuse one WT Rules Pinecone vector store
    instead of creating a new instance per request.
    """
    index_name = os.getenv("PINECONE_INDEX_NAME")

    if not index_name:
        raise ValueError("PINECONE_INDEX_NAME missing from .env")

    return PineconeVectorStore(
        index_name=index_name,
        embedding=get_embeddings(),
        namespace="wt-rules-2026"
    )


def retrieve_rules(question: str, k: int = 3):
    vector_store = get_vector_store()

    search_queries = [
        question,
        "Article 14.2 prohibited acts shall be penalized with Gam-jeom",
        "Article 14.3 Gam-jeom counted as one point for opposing contestant",
        "Article 14.4.1.10 attacking the fallen opponent"
    ]

    unique_results = {}

    for query in search_queries:
        results = vector_store.similarity_search_with_score(
            query,
            k=k
        )

        for document, score in results:
            key = (
                document.metadata.get("page"),
                document.page_content.strip()
            )

            if key not in unique_results:
                unique_results[key] = {
                    "content": document.page_content,
                    "page": document.metadata.get("page"),
                    "source": document.metadata.get("source"),
                    "score": float(score)
                }

    return list(unique_results.values())


if __name__ == "__main__":
    question = "What are the prohibited acts and penalties in Taekwondo?"

    results = retrieve_rules(question)

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(f"Page: {result['page']}")
        print(f"Score: {result['score']:.4f}")
        print(result["content"])
