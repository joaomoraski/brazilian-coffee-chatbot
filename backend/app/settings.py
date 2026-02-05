from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

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
