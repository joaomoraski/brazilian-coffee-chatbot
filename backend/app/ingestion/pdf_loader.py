import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from unstructured.partition.pdf import partition_pdf


def load_pdf(file_path: str) -> List[Document]:
    """
    Load a PDF file and extract text content.

    Args:
        file_path: Path to the PDF file

    Returns:
        List of Document objects with extracted content
    """
    file_name = Path(file_path).name

    elements = partition_pdf(
        filename=file_path,
        strategy="fast",  # Fast strategy for text-based PDFs
        languages=["por", "eng"],  # Portuguese and English
        infer_table_structure=False,  # Disable for speed
        extract_images_in_pdf=False,
    )

    # Group elements into documents
    documents = []
    current_text = []

    for element in elements:
        text = str(element)
        if text.strip():
            current_text.append(text)

        # Create a new document every ~1000 characters or at section breaks
        if len("\n".join(current_text)) > 1000:
            documents.append(
                Document(
                    page_content="\n".join(current_text),
                    metadata={"source": file_name, "type": "pdf"},
                )
            )
            current_text = []

    # Add remaining content
    if current_text:
        documents.append(
            Document(
                page_content="\n".join(current_text),
                metadata={"source": file_name, "type": "pdf"},
            )
        )

    return documents


def load_all_pdfs(pdf_dir: str) -> List[Document]:
    """
    Load all PDFs from a directory.

    Args:
        pdf_dir: Path to directory containing PDFs

    Returns:
        List of all Document objects from all PDFs
    """
    all_documents = []
    pdf_path = Path(pdf_dir)


    for pdf_file in sorted(pdf_path.glob("*.pdf")):

        print(f"Processing: {pdf_file.name}")

        try:
            docs = load_pdf(str(pdf_file))
            all_documents.extend(docs)
            print(f"  ✓ Extracted {len(docs)} documents")
        except Exception as e:
            print(f"  ✗ Error processing {pdf_file.name}: {e}")

    return all_documents
