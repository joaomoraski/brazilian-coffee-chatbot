import json
import re
from typing import AsyncGenerator

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

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

5. **Source Attribution:** When using information from any tool, naturally mention the source in your answer:
   - For knowledge base results: mention the document name. Example: 'According to *metodos-de-preparo.pdf*, the V60 method...'
   - For web search results: mention the article or website title. Example: 'According to Reuters, Starbucks sources...'
   - For coffee shop results: mention the place name naturally in your response.
   - Do not list all sources at the end; weave them naturally into the text.

6. **IMPORTANT - Stay on Topic:**
   - You ONLY answer questions about coffee, specifically Brazilian coffee.
   - If the user asks about unrelated topics (fruits like mango, animals like monkeys, politics, sports, etc.), politely decline and redirect to coffee.
   - Do NOT use any tools (web search, places, knowledge base) for off-topic questions.
   - For off-topic requests, respond with something like: "I'm specialized in Brazilian coffee! I can't help with [topic], but I'd love to tell you about coffee. What would you like to know about Brazilian coffee?"
   - Only use tools when the question is clearly about coffee or finding coffee shops.

7. Always answer in Markdown format.
"""


def _make_gemini_llm(model: str) -> ChatGoogleGenerativeAI:
    """Create a Gemini LLM with shared config."""
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=1.0,
        max_tokens=None,
        timeout=20,
        max_retries=4,
        streaming=True,
        convert_system_message_to_human=True,
    )


def get_llm():
    """Get the Gemini LLM with fallback for traffic spikes (429/503)."""
    primary = _make_gemini_llm("gemini-3-pro-preview")
    fallback = _make_gemini_llm("gemini-3-flash-preview")
    flash_fallback = _make_gemini_llm("gemini-2.5-flash")
    return primary.with_fallbacks(
        [fallback, flash_fallback],
        exceptions_to_handle=(Exception,),
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

    agent = create_agent(
        llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent


async def chat(message: str, session_id: str) -> AsyncGenerator[str | dict, None]:
    """
    Chat with the coffee agent using session history.

    Streams response chunks directly from the model as they are generated,
    providing true real-time streaming without buffering.

    Args:
        message: User's message
        session_id: Session ID for history management

    Yields:
        Streamed response chunks directly from the LLM

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

            # Stream response directly from agent using astream
            # Filter to only stream the FINAL AI response, not intermediate tool results
            response_parts = []
            collected_sources = []

            async for chunk in agent.astream(
                {"messages": messages},
                stream_mode="messages",
            ):
                if isinstance(chunk, tuple):
                    msg, metadata = chunk
                else:
                    msg = chunk

                from langchain_core.messages import (
                    AIMessage as AIMessageType,
                    ToolMessage,
                )

                if isinstance(msg, ToolMessage):
                    tool_content = msg.content if isinstance(msg.content, str) else ""
                    match = re.search(
                        r"\[SOURCES_META\](.*?)\[/SOURCES_META\]",
                        tool_content,
                        re.DOTALL,
                    )
                    if match:
                        try:
                            collected_sources.extend(json.loads(match.group(1)))
                        except json.JSONDecodeError:
                            pass
                    continue

                if not isinstance(msg, AIMessageType):
                    continue

                if hasattr(msg, "content") and msg.content:
                    content = msg.content

                    if isinstance(content, str) and content.strip():
                        response_parts.append(content)
                        yield content
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and "text" in item:
                                text = item["text"]
                                if text and text.strip():
                                    response_parts.append(text)
                                    yield text
                            elif isinstance(item, str) and item.strip():
                                response_parts.append(item)
                                yield item

            if collected_sources:
                yield {"sources": collected_sources}

            # Save messages to history after streaming completes
            complete_response = "".join(response_parts)
            if complete_response:  # Only save if we got a response
                history_manager.add_user_message(message)
                history_manager.add_ai_message(complete_response)
            # Connection automatically returned to pool when context exits

    except Exception as e:
        logger.error(f"Error in chat for session {session_id}: {str(e)}", exc_info=True)
        raise
