import json

from langchain_core.tools import tool

from app.db.vector_store import get_retriever


@tool
def search_coffee_knowledge(query: str) -> str:
    """
    Search the Brazilian coffee knowledge base for information about coffee.
    Use this tool for questions about:
    - Coffee history in Brazil
    - How to plant, harvest, treat, and roast coffee
    - Coffee classification and quality levels
    - Brewing methods and preparation
    - Coffee regions and farms in Brazil
    - ARAM method and specialty coffee

    Args:
        query: The search query about Brazilian coffee

    Returns:
        Relevant information from the knowledge base
    """
    retriever = get_retriever(k=5)
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant information found in the knowledge base."

    results = []
    seen_sources = set()
    sources_meta = []

    for doc in docs:
        content = doc.page_content[:500]
        results.append(content)

        source_name = doc.metadata.get("source", "Unknown")
        source_type = doc.metadata.get("type", "")

        if source_name not in seen_sources:
            seen_sources.add(source_name)
            if source_type == "web":
                url = source_name
            else:
                url = f"/pdfs/{source_name}"
            sources_meta.append({"name": source_name, "url": url})

    text = "\n\n---\n\n".join(results)
    text += f"\n\n[SOURCES_META]{json.dumps(sources_meta)}[/SOURCES_META]"
    return text
