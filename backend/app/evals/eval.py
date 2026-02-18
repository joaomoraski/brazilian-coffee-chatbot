from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client, traceable
from openevals import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT

from app.agents.coffee_agent import create_coffee_agent
from app.settings import settings


def _extract_answer(content) -> str:
    if isinstance(content, str) and content.strip():
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        return "".join(parts).strip()
    return ""


def _extract_tools_used(messages: list) -> list[str]:
    """
    Extract tool names from agent output.
    Uses AIMessage.tool_calls (primary) since eval uses agent.invoke(), not chat().
    The streaming chat() filters ToolMessage for display, but invoke() returns full messages.
    """
    tools = []
    for msg in messages:
        if isinstance(msg, ToolMessage) and hasattr(msg, "name") and msg.name:
            tools.append(msg.name)
        elif isinstance(msg, AIMessage) and hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", None)
                if name:
                    tools.append(name)
    return list(dict.fromkeys(tools))  # preserve order, dedupe


@traceable(name="coffee_chatbot")
def target(inputs: dict) -> dict:
    question = inputs.get("question", "")
    if not question:
        return {"answer": "", "tools_used": []}

    agent = create_coffee_agent()
    result = agent.invoke({"messages": [HumanMessage(content=question)]})

    messages = result.get("messages", [])
    tools_used = _extract_tools_used(messages)

    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.content:
            answer = _extract_answer(msg.content)
            if answer:
                return {"answer": answer, "tools_used": tools_used}

    return {"answer": "", "tools_used": tools_used}


def correctness_evaluator(run, example):
    """LLM-as-judge for answer correctness."""
    judge = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.GOOGLE_API_KEY,
    )
    evaluator = create_llm_as_judge(prompt=CORRECTNESS_PROMPT, judge=judge)
    return evaluator(
        inputs=run.inputs,
        outputs=run.outputs,
        reference_outputs=example.outputs or {},
    )


def tool_correctness_evaluator(run, example):
    """Check that the agent called the expected tools for the question."""
    expected_tools = example.outputs.get("expected_tools") if example.outputs else []
    if not expected_tools:
        return {"key": "tool_correctness", "score": 1.0, "comment": "No expected_tools defined"}

    tools_used = run.outputs.get("tools_used") or []
    expected_set = set(expected_tools)
    used_set = set(tools_used)
    missing = expected_set - used_set
    score = 1.0 if not missing else 0.0

    return {
        "key": "tool_correctness",
        "score": score,
        "comment": f"Expected {expected_tools}, got {tools_used}. Missing: {list(missing) or 'none'}",
    }


def main():
    client = Client(api_key=settings.LANGSMITH_API_KEY, api_url=settings.LANGSMITH_ENDPOINT)

    experiment_results = client.evaluate(
        target,
        data="coffee-chatbot-eval",
        evaluators=[correctness_evaluator, tool_correctness_evaluator],
        experiment_prefix="first-offline-eval",
        max_concurrency=2)
    
    print(experiment_results)

if __name__ == "__main__":
    main()