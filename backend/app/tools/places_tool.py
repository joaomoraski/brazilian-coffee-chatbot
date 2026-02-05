from langchain_core.tools import tool
from langchain_google_community import GooglePlacesAPIWrapper

from app.settings import settings


@tool
def find_coffee_shops(location: str) -> str:
    """
    Find coffee shops in a specific city or location.
    Use this tool when the user asks where to find or buy coffee in a specific place.
    Examples: "Where can I get coffee in São Paulo?", "Coffee shops near me in Rio"

    Args:
        location: The city or location to search for coffee shops

    Returns:
        List of coffee shops with their details
    """
    if not settings.GPLACES_API_KEY:
        return "Google Places API key not configured. Cannot search for coffee shops."

    places = GooglePlacesAPIWrapper(
        gplaces_api_key=settings.GPLACES_API_KEY,
        top_k_results=10,
    )

    query = f"coffee shop in {location}"

    try:
        results = places.run(query)
        return results
    except Exception as e:
        return f"Error searching for coffee shops: {str(e)}"
