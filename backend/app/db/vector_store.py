from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

from app.settings import settings


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Get Gemini embeddings model. Uses gemini-embedding-001 (models/embedding-001 is deprecated)."""
    return GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        google_api_key=settings.GOOGLE_API_KEY,
    )


@lru_cache(maxsize=1)
def get_vector_store() -> PGVector:
    """
    Get PGVector store instance (cached).
    Single instance per process avoids SQLAlchemy 'Table already defined' errors
    when the RAG tool is called multiple times.
    """
    embeddings = get_embeddings()
    connection = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")
    return PGVector(
        embeddings=embeddings,
        collection_name="coffee_documents",
        connection=connection,
        use_jsonb=True,
    )


def get_retriever(k: int = 5):
    """Get retriever for similarity search."""
    vector_store = get_vector_store()
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
