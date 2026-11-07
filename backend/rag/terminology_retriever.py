
import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from langchain_pinecone import PineconeVectorStore

from backend.rag.embeddings import get_embeddings


ROOT_DIR = Path(__file__).resolve().parents[2]

load_dotenv(ROOT_DIR / ".env")

NAMESPACE = "tkd-terminology"


@lru_cache(maxsize=1)
def get_terminology_vector_store():

    index_name = os.getenv("PINECONE_INDEX_NAME")

    if not index_name:
        raise ValueError(
            "PINECONE_INDEX_NAME missing from .env"
        )

    embeddings = get_embeddings()

    return PineconeVectorStore(
        index_name=index_name,
        embedding=embeddings,
        namespace=NAMESPACE
    )


def retrieve_terminology(question: str, k: int = 4):

    vector_store = get_terminology_vector_store()

    results = vector_store.similarity_search(
        question,
        k=k
    )

    return [
        {
            "content": doc.page_content,
            "source": doc.metadata.get("source"),
            "page": doc.metadata.get("page")
        }
        for doc in results
    ]


def format_terminology_context(question: str, k: int = 2):

    results = retrieve_terminology(question, k=k)

    if not results:
        return "No relevant terminology was retrieved."

    return "\n\n".join(
        item["content"]
        for item in results
    )
