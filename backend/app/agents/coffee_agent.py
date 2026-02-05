from typing import AsyncGenerator

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from app.settings import settings
from app.tools.rag_tool import search_coffee_knowledge
from app.tools.places_tool import find_coffee_shops
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


async def chat(message: str, history: list = None) -> AsyncGenerator[str, None]:
    """
    Chat with the coffee agent.

    Args:
        message: User's message
        history: Optional chat history

    Yields:
        Streamed response chunks
    """
    agent = create_coffee_agent()

    # Build messages
    messages = []
    if history:
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=message))

    # Stream response
    async for event in agent.astream_events(
        {"messages": messages},
        version="v2",
    ):
        kind = event["event"]

        if kind == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield content


async def chat_simple(message: str, history: list = None) -> str:
    """
    Non-streaming chat with the coffee agent.

    Args:
        message: User's message
        history: Optional chat history

    Returns:
        Complete response
    """
    response_parts = []
    async for chunk in chat(message, history):
        response_parts.append(chunk)

    return "".join(response_parts)
