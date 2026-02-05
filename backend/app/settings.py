import json
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_cors_origins() -> list[str]:
    """Parse CORS_ORIGINS from environment variable."""
    default = ["http://localhost:3000", "http://127.0.0.1:3000"]
    value = os.getenv("CORS_ORIGINS", "")
    
    if not value:
        return default
    
    # Try JSON first
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        # Fall back to comma-separated
        return [origin.strip() for origin in value.split(",") if origin.strip()]


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Google AI
    GOOGLE_API_KEY: str

    # PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/coffee_chatbot"

    # Tavily
    TAVILY_API_KEY: str | None = None

    # Google Places
    GPLACES_API_KEY: str | None = None

    # LangSmith
    LANGSMITH_TRACING: bool = True
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str = "Brazilian Coffee"


settings = Settings()
