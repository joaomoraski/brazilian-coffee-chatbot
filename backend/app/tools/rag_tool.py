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

    # Format results
    results = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        content = doc.page_content[:500]  # Limit content length
        results.append(f"[Source {i}: {source}]\n{content}")

    return "\n\n---\n\n".join(results)
