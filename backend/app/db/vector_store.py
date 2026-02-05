from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import PGVector
from sqlalchemy import create_engine

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

    return PGVector(
        connection_string=settings.DATABASE_URL,
        embedding_function=embeddings,
        collection_name="coffee_documents",
        distance_strategy="cosine",
    )


def get_retriever(k: int = 5):
    """Get retriever for similarity search."""
    vector_store = get_vector_store()
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": k},
    )
