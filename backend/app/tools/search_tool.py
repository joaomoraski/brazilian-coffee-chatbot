from langchain_core.tools import tool
from tavily import TavilyClient

from app.settings import settings


@tool
def search_web(query: str) -> str:
    """
    Search the web for current information about coffee.
    Use this tool when:
    - The knowledge base doesn't have enough information
    - The user asks about current events, prices, or news
    - The user asks about something not covered in the documents

    Args:
        query: The search query

    Returns:
        Search results from the web
    """
    if not settings.TAVILY_API_KEY:
        return "Tavily API key not configured. Cannot perform web search."

    client = TavilyClient(api_key=settings.TAVILY_API_KEY)

    try:
        response = client.search(
            query=f"{query} Brazilian coffee",
            search_depth="basic",
            max_results=5,
        )

        if not response.get("results"):
            return "No results found on the web."

        # Format results
        results = []
        for r in response["results"]:
            title = r.get("title", "No title")
            content = r.get("content", "")[:300]
            url = r.get("url", "")
            results.append(f"**{title}**\n{content}\nSource: {url}")

        return "\n\n---\n\n".join(results)

    except Exception as e:
        return f"Error performing web search: {str(e)}"
