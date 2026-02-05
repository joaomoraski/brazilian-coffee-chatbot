from typing import AsyncGenerator

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from app.db.session_manager import get_session_history
from app.settings import settings
from app.tools.places_tool import find_coffee_shops
from app.tools.rag_tool import search_coffee_knowledge
from app.tools.search_tool import search_web

SYSTEM_PROMPT = """You are a helpful assistant specialized in Brazilian coffee.
You have access to a comprehensive knowledge base about:
- History of coffee in Brazil
- How to plant, harvest, treat, and roast coffee
- Coffee classification and quality levels (specialty coffee, commercial grades)
- Brewing methods and preparation techniques
- Coffee regions and major farms in Brazil
- ARAM method and specialty coffee culture

**Important Instructions:**
1. Always respond in the same language the user writes their question.
   - If the user asks in Portuguese, respond in Portuguese.
   - If the user asks in English, respond in English.
   - Detect the language automatically and match it in your response.

2. Use the appropriate tool based on the user's question:
   - Use 'search_coffee_knowledge' for educational questions about coffee
   - Use 'find_coffee_shops' when asked where to find/buy coffee in a location
   - Use 'search_web' when the knowledge base doesn't have enough info or for current events

3. Be friendly, informative, and passionate about coffee!

4. If you don't know something, say so honestly and use the web search tool.

5. **IMPORTANT - Stay on Topic:**
   - You ONLY answer questions about coffee, specifically Brazilian coffee.
   - If the user asks about unrelated topics (fruits like mango, animals like monkeys, politics, sports, etc.), politely decline and redirect to coffee.
   - Do NOT use any tools (web search, places, knowledge base) for off-topic questions.
   - For off-topic requests, respond with something like: "I'm specialized in Brazilian coffee! I can't help with [topic], but I'd love to tell you about coffee. What would you like to know about Brazilian coffee?"
   - Only use tools when the question is clearly about coffee or finding coffee shops.

6. Always answer in Markdown format.
"""


def get_llm() -> ChatGoogleGenerativeAI:
    """Get the Gemini LLM instance."""
    return ChatGoogleGenerativeAI(
        model="gemini-3-pro-preview",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=1.0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        streaming=True,
        convert_system_message_to_human=True,
    )


def get_tools() -> list:
    """Get all available tools for the agent."""
    return [
        search_coffee_knowledge,
        find_coffee_shops,
        search_web,
    ]


def create_coffee_agent():
    """Create the coffee chatbot agent with all tools."""
    llm = get_llm()
    tools = get_tools()

    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=SYSTEM_PROMPT,
    )

    return agent


async def chat(message: str, session_id: str) -> AsyncGenerator[str, None]:
    """
    Chat with the coffee agent using session history.

    Args:
        message: User's message
        session_id: Session ID for history management

    Yields:
        Streamed response chunks
    
    Raises:
        Exception: If any error occurs during chat processing
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        agent = create_coffee_agent()

        # Use context manager to properly manage database connection
        with get_session_history(session_id) as history_manager:
            # Get history from database
            chat_history: list[BaseMessage] = history_manager.messages

            # Build messages with context
            # Only use last 4 messages if there are more than 2 messages for context
            messages = []
            if chat_history and len(chat_history) >= 2:
                # Get last 4 messages (2 exchanges)
                context_messages = chat_history[-4:]
                messages.extend(context_messages)

            # Add current user message
            messages.append(HumanMessage(content=message))

            # Stream response
            response_parts = []
            async for event in agent.astream_events(
                {"messages": messages},
                version="v2",
            ):
                kind = event["event"]

                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]

                    # Get content from chunk (try different attributes)
                    content = None
                    if hasattr(chunk, "content"):
                        content = chunk.content
                    elif hasattr(chunk, "text"):
                        content = chunk.text

                    # Only yield if we have actual text content
                    if content:
                        # Handle string content
                        if isinstance(content, str):
                            if content.strip():  # Only yield non-empty strings
                                response_parts.append(content)
                                yield content
                        # Handle list of content blocks (from Gemini)
                        elif isinstance(content, list):
                            for item in content:
                                # Extract text from content blocks
                                if isinstance(item, dict) and "text" in item:
                                    text = item["text"]
                                    if text and text.strip():
                                        response_parts.append(text)
                                        yield text
                                elif isinstance(item, str) and item.strip():
                                    response_parts.append(item)
                                    yield item

            # Save messages to history after streaming completes
            complete_response = "".join(response_parts)
            if complete_response:  # Only save if we got a response
                history_manager.add_user_message(message)
                history_manager.add_ai_message(complete_response)
            # Connection automatically returned to pool when context exits
            
    except Exception as e:
        logger.error(f"Error in chat for session {session_id}: {str(e)}", exc_info=True)
        raise


async def chat_simple(message: str, session_id: str) -> str:
    """
    Non-streaming chat with the coffee agent.

    Args:
        message: User's message
        session_id: Session ID for history management

    Returns:
        Complete response
    """
    response_parts = []
    async for chunk in chat(message, session_id):
        response_parts.append(chunk)

    return "".join(response_parts)
