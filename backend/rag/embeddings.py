
from functools import lru_cache

from langchain_community.embeddings import FastEmbedEmbeddings


@lru_cache(maxsize=1)
def get_embeddings():
    """
    Lightweight ONNX embedding model.
    Reuses one instance across both Pinecone retrievers.
    """
    return FastEmbedEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        threads=1,
        batch_size=16,
        parallel=1
    )
