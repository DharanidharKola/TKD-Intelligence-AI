
import os
import hashlib
from pathlib import Path

from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore

from backend.rag.embeddings import get_embeddings


ROOT_DIR = Path(__file__).resolve().parents[2]

TERMINOLOGY_DIR = ROOT_DIR / "data" / "terminology"

PDF_FILES = [
    "TKD-Kims-Terminology-Guide.pdf",
    "terminology-full-guide.pdf"
]

NAMESPACE = "tkd-terminology"

load_dotenv(ROOT_DIR / ".env")


def load_terminology():

    documents = []

    for filename in PDF_FILES:

        pdf_path = TERMINOLOGY_DIR / filename

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"Terminology PDF not found: {pdf_path}"
            )

        print(f"\nReading: {filename}")

        reader = PdfReader(str(pdf_path))

        for page_number, page in enumerate(
            reader.pages, start=1
        ):

            text = (page.extract_text() or "").strip()

            if not text:
                print(f"Page {page_number}: No extractable text")
                continue

            documents.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": filename,
                        "page": page_number,
                        "document_type": "taekwondo_terminology"
                    }
                )
            )

        print(f"Pages: {len(reader.pages)}")

    print(f"\nTotal extracted pages: {len(documents)}")

    return documents


def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(documents)

    print(f"Total chunks created: {len(chunks)}")

    return chunks


def upload_to_pinecone(chunks):

    index_name = os.getenv("PINECONE_INDEX_NAME")

    if not index_name:
        raise ValueError(
            "PINECONE_INDEX_NAME missing from .env"
        )

    if not os.getenv("PINECONE_API_KEY"):
        raise ValueError(
            "PINECONE_API_KEY missing from .env"
        )

    embeddings = get_embeddings()

    ids = []

    for chunk in chunks:

        unique_text = (
            f"{chunk.metadata['source']}-"
            f"{chunk.metadata['page']}-"
            f"{chunk.page_content}"
        )

        ids.append(
            hashlib.sha256(
                unique_text.encode("utf-8")
            ).hexdigest()
        )

    PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=index_name,
        namespace=NAMESPACE,
        ids=ids
    )

    print("\nTerminology ingestion completed!")
    print(f"Index: {index_name}")
    print(f"Namespace: {NAMESPACE}")
    print(f"Chunks uploaded: {len(chunks)}")


def main():

    documents = load_terminology()

    if not documents:
        raise ValueError(
            "No terminology text extracted."
        )

    chunks = split_documents(documents)

    upload_to_pinecone(chunks)


if __name__ == "__main__":
    main()
