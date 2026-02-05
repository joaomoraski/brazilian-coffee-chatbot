import httpx
from langchain_core.tools import tool

from app.settings import settings

PLACES_API_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"


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

    try:
        response = httpx.get(
            PLACES_API_URL,
            params={
                "query": f"coffee shop in {location}",
                "key": settings.GPLACES_API_KEY,
                "language": "pt-BR",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("status") != "OK":
            return f"No coffee shops found in {location}."

        results = data.get("results", [])[:10]

        if not results:
            return f"No coffee shops found in {location}."

        # Format results
        formatted = []
        for place in results:
            name = place.get("name", "Unknown")
            address = place.get("formatted_address", "Address not available")
            rating = place.get("rating", "N/A")
            total_ratings = place.get("user_ratings_total", 0)
            
            formatted.append(
                f"**{name}**\n"
                f"📍 {address}\n"
                f"⭐ {rating}/5 ({total_ratings} reviews)"
            )

        return "\n\n---\n\n".join(formatted)

    except httpx.TimeoutException:
        return "Request timed out. Please try again."
    except Exception as e:
        return f"Error searching for coffee shops: {str(e)}"
