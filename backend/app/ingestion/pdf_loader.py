import os
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from unstructured.partition.pdf import partition_pdf


def load_pdf(file_path: str, use_ocr: bool = False) -> List[Document]:
    """
    Load a PDF file and extract text content.

    Args:
        file_path: Path to the PDF file
        use_ocr: Whether to use OCR for scanned documents

    Returns:
        List of Document objects with extracted content
    """
    file_name = Path(file_path).name

    # Configure strategy based on OCR requirement
    strategy = "hi_res" if use_ocr else "auto"

    elements = partition_pdf(
        filename=file_path,
        strategy=strategy,
        languages=["por", "eng"],  # Portuguese and English
        infer_table_structure=True,
        extract_images_in_pdf=False,  # Skip image extraction for now
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

    # Files that need OCR (scanned documents)
    ocr_files = {"historia-no-brasil.pdf"}

    for pdf_file in pdf_path.glob("*.pdf"):
        print(f"Processing: {pdf_file.name}")
        use_ocr = pdf_file.name in ocr_files

        try:
            docs = load_pdf(str(pdf_file), use_ocr=use_ocr)
            all_documents.extend(docs)
            print(f"  Extracted {len(docs)} documents")
        except Exception as e:
            print(f"  Error processing {pdf_file.name}: {e}")

    return all_documents
