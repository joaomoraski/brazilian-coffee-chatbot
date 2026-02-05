from typing import List

import httpx
from bs4 import BeautifulSoup
from langchain_core.documents import Document


async def scrape_aram_history() -> List[Document]:
    """
    Scrape the ARAM Brazil coffee history page.

    Returns:
        List of Document objects with scraped content
    """
    url = "https://arambrasil.coffee/historia/"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script and style elements
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    # Extract main content
    main_content = soup.find("main") or soup.find("article") or soup.find("body")

    if not main_content:
        return []

    # Get all text paragraphs
    paragraphs = []
    for element in main_content.find_all(["p", "h1", "h2", "h3", "h4", "li"]):
        text = element.get_text(strip=True)
        if text and len(text) > 20:  # Filter out very short content
            paragraphs.append(text)

    # Combine into documents (chunk by ~1000 chars)
    documents = []
    current_chunk = []
    current_length = 0

    for para in paragraphs:
        current_chunk.append(para)
        current_length += len(para)

        if current_length > 1000:
            documents.append(
                Document(
                    page_content="\n\n".join(current_chunk),
                    metadata={
                        "source": url,
                        "type": "web",
                        "title": "ARAM Brasil - História do Café",
                    },
                )
            )
            current_chunk = []
            current_length = 0

    # Add remaining content
    if current_chunk:
        documents.append(
            Document(
                page_content="\n\n".join(current_chunk),
                metadata={
                    "source": url,
                    "type": "web",
                    "title": "ARAM Brasil - História do Café",
                },
            )
        )

    return documents


def scrape_aram_history_sync() -> List[Document]:
    """Synchronous wrapper for scraping ARAM history."""
    import asyncio

    return asyncio.run(scrape_aram_history())
