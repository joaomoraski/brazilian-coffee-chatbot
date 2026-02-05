from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.coffee_agent import chat, chat_simple
from app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("🌱 Brazilian Coffee Chatbot starting up...")
    yield
    print("☕ Shutting down...")


app = FastAPI(
    title="Brazilian Coffee Chatbot",
    description="A RAG-based chatbot that answers questions about Brazilian coffee",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    """Chat message model."""

    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str
    history: Optional[List[Message]] = None


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Brazilian Coffee Chatbot"}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Non-streaming chat endpoint.

    Args:
        request: Chat request with message and optional history

    Returns:
        Complete response from the agent
    """
    try:
        history = [msg.model_dump() for msg in request.history] if request.history else None
        response = await chat_simple(request.message, history)
        return ChatResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint.

    Args:
        request: Chat request with message and optional history

    Returns:
        Streamed response from the agent
    """

    async def generate():
        try:
            history = [msg.model_dump() for msg in request.history] if request.history else None
            async for chunk in chat(request.message, history):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(
        generate(),
        media_type="text/plain",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
