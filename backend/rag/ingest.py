
import os
import hashlib
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

from backend.rag.embeddings import get_embeddings


# Project paths
ROOT_DIR = Path(__file__).resolve().parents[2]

PDF_PATH = ROOT_DIR / "data" / "rules" / "2026-01_WT_Rules_Kyorugi.pdf"

# Load environment variables
load_dotenv(ROOT_DIR / ".env")


def load_pdf():

    print("\n1. Loading WT Rules PDF...")

    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found: {PDF_PATH}")

    reader = PdfReader(str(PDF_PATH))

    documents = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""
        text = text.strip()

        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": PDF_PATH.name,
                    "page": page_number,
                    "document_title": "WT Competition Rules & Interpretation",
                    "effective_date": "2026-01-01"
                }
            )
        )

    print(f"Total PDF pages: {len(reader.pages)}")
    print(f"Pages containing extractable text: {len(documents)}")

    return documents


def split_documents(documents):

    print("\n2. Splitting PDF into chunks...")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        add_start_index=True
    )

    chunks = splitter.split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    return chunks


def upload_to_pinecone(chunks):

    print("\n3. Generating embeddings...")

    embeddings = get_embeddings()

    print("\n4. Connecting to Pinecone...")

    index_name = os.getenv("PINECONE_INDEX_NAME")

    if not index_name:
        raise ValueError("PINECONE_INDEX_NAME missing from .env")

    if not os.getenv("PINECONE_API_KEY"):
        raise ValueError("PINECONE_API_KEY missing from .env")

    # Stable IDs prevent duplicate records when ingestion is rerun.
    ids = []

    for chunk in chunks:
        unique_text = (
            f"{chunk.metadata['source']}-"
            f"{chunk.metadata['page']}-"
            f"{chunk.metadata['start_index']}-"
            f"{chunk.page_content}"
        )

        ids.append(
            hashlib.sha256(unique_text.encode("utf-8")).hexdigest()
        )

    print("\n5. Uploading chunks to Pinecone...")

    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=index_name,
        namespace="wt-rules-2026",
        ids=ids
    )

    print(f"\nSuccessfully uploaded {len(chunks)} chunks!")
    print(f"Pinecone index: {index_name}")
    print("Namespace: wt-rules-2026")


def main():

    documents = load_pdf()

    if not documents:
        raise ValueError("No extractable text found in the PDF.")

    chunks = split_documents(documents)

    upload_to_pinecone(chunks)

    print("\n===================================")
    print("WT RULES INGESTION COMPLETED!")
    print("===================================")


if __name__ == "__main__":
    main()
