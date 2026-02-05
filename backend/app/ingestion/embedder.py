from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.db.vector_store import get_vector_store
from app.ingestion.pdf_loader import load_all_pdfs
from app.ingestion.web_scraper import scrape_aram_history_sync


def chunk_documents(documents: List[Document]) -> List[Document]:
    """
    Split documents into smaller chunks for better retrieval.

    Args:
        documents: List of documents to chunk

    Returns:
        List of chunked documents
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return text_splitter.split_documents(documents)


def ingest_all_documents(pdf_dir: str) -> int:
    """
    Ingest all documents (PDFs and web content) into the vector store.

    Args:
        pdf_dir: Path to directory containing PDFs

    Returns:
        Number of documents ingested
    """
    print("Starting document ingestion...")

    # Load PDFs
    print("\n=== Loading PDFs ===")
    pdf_docs = load_all_pdfs(pdf_dir)
    print(f"Loaded {len(pdf_docs)} documents from PDFs")

    # Scrape web content
    print("\n=== Scraping ARAM Website ===")
    web_docs = scrape_aram_history_sync()
    print(f"Scraped {len(web_docs)} documents from web")

    # Combine all documents
    all_docs = pdf_docs + web_docs
    print(f"\nTotal documents before chunking: {len(all_docs)}")

    # Chunk documents
    print("\n=== Chunking Documents ===")
    chunked_docs = chunk_documents(all_docs)
    print(f"Total chunks after splitting: {len(chunked_docs)}")

    # Store in vector database
    print("\n=== Storing in Vector Database ===")
    vector_store = get_vector_store()
    vector_store.add_documents(chunked_docs)
    print("Documents stored successfully!")

    return len(chunked_docs)


if __name__ == "__main__":
    import os

    pdf_dir = os.path.join(os.path.dirname(__file__), "..", "..", "pdfs")
    count = ingest_all_documents(pdf_dir)
    print(f"\nIngestion complete! Total documents: {count}")
