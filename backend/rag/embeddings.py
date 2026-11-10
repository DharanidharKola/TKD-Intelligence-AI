
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings


@lru_cache(maxsize=1)
def get_embeddings():
    """
    Load the embedding model once and reuse it across
    the WT Rules and Taekwondo Terminology retrievers.
    """
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
