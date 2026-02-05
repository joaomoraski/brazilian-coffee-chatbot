from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_postgres import PGVector

from app.settings import settings


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Get Gemini embeddings model."""
    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.GOOGLE_API_KEY,
    )


def get_vector_store() -> PGVector:
    """Get PGVector store instance."""
    embeddings = get_embeddings()
    
    # Convert psycopg2 URL to psycopg3 format
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
