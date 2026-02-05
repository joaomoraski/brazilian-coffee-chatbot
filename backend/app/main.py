import logging
from contextlib import asynccontextmanager
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.agents.coffee_agent import chat, chat_simple
from app.db.session_manager import get_session_history
from app.settings import get_cors_origins

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("🌱 Brazilian Coffee Chatbot starting up...")
    
    # Initialize database tables
    try:
        from app.db.session_manager import _ensure_table_exists
        _ensure_table_exists()
        logger.info("✅ Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
    
    yield
    logger.info("☕ Shutting down...")


app = FastAPI(
    title="Brazilian Coffee Chatbot",
    description="A RAG-based chatbot that answers questions about Brazilian coffee",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
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
    session_id: UUID  # Now required


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Brazilian Coffee Chatbot"}


@app.get("/sessions/{session_id}/messages")
async def get_session_messages_endpoint(session_id: UUID):
    """Get messages for a session from the database."""
    try:
        history = get_session_history(str(session_id))
        
        # Check if messages exist (new sessions will have empty history)
        try:
            messages = history.messages
        except Exception:
            # Session doesn't exist yet or table not created, return empty
            return {"messages": []}

        # Convert LangChain messages to API format
        formatted_messages = []
        for msg in messages:
            role = "user" if msg.type == "human" else "assistant"
            formatted_messages.append({"role": role, "content": msg.content})

        return {"messages": formatted_messages}
    except Exception as e:
        # Return empty array for non-existent sessions instead of error
        logger.debug(f"Session {session_id} not found or empty: {e}")
        return {"messages": []}


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Non-streaming chat endpoint.

    Args:
        request: Chat request with message and session_id

    Returns:
        Complete response
    """
    try:
        response = await chat_simple(request.message, str(request.session_id))
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Chat error for session {request.session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process chat request")


@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """
    Streaming chat endpoint.

    Args:
        request: Chat request with message and session_id

    Returns:
        Streamed response from the agent
    """
    import logging
    logger = logging.getLogger(__name__)

    async def generate():
        try:
            async for chunk in chat(request.message, str(request.session_id)):
                yield chunk
        except Exception as e:
            logger.error(f"Stream error for session {request.session_id}: {str(e)}", exc_info=True)
            # Don't yield error message - let frontend handle it
            raise

    try:
        return StreamingResponse(
            generate(),
            media_type="text/plain",
        )
    except Exception as e:
        logger.error(f"Failed to start stream: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process chat request")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
