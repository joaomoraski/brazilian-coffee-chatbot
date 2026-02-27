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


DATASET_NAME = "coffee-chatbot-eval"
REGRESSION_THRESHOLD = 5.0  # percentage points


def _compute_metrics(rows: list[dict]) -> dict[str, float]:
    totals: dict[str, list[float]] = {}
    for row in rows:
        for key, score in row["scores"].items():
            totals.setdefault(key, []).append(float(score) if score is not None else 0.0)
    return {k: sum(v) / len(v) * 100 for k, v in totals.items()}


def _metrics_from_project(project) -> dict[str, float]:
    stats = getattr(project, "feedback_stats", None) or {}
    result = {}
    for key, stat in stats.items():
        avg = stat.get("avg") if isinstance(stat, dict) else getattr(stat, "avg", None)
        if avg is not None:
            result[key] = float(avg) * 100
    return result


def _run_investigation(
    experiment_name: str,
    baseline_name: str,
    regressions: dict,
    failing_rows: list[dict],
) -> str:
    judge = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=settings.GOOGLE_API_KEY,
    )
    failing_text = "\n".join(
        f"- Q: {r['question']} | scores: {r['scores']}" for r in failing_rows
    )
    regression_text = "\n".join(
        f"  {k}: {v['current']:.1f}% vs baseline {v['baseline']:.1f}% (drop {v['drop']:.1f}pp)"
        for k, v in regressions.items()
    )
    prompt = (
        f"You are a QA analyst reviewing an AI chatbot evaluation.\n\n"
        f"Current experiment : {experiment_name}\n"
        f"Baseline experiment: {baseline_name}\n\n"
        f"Regressed metrics (dropped > {REGRESSION_THRESHOLD}pp):\n{regression_text}\n\n"
        f"Failing test cases (score < 1.0):\n{failing_text}\n\n"
        f"Please analyze:\n"
        f"1. Which specific test cases most likely caused the regressions.\n"
        f"2. Which evaluator scores dropped and why.\n"
        f"3. Likely root causes (prompt issue, wrong tool, missing RAG content, etc.).\n"
        f"4. Concrete suggested fixes (do NOT generate code, only describe changes)."
    )
    response = judge.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)


def main():
    import sys

    client = Client(api_key=settings.LANGSMITH_API_KEY, api_url=settings.LANGSMITH_ENDPOINT)

    # --- Run evals (all examples, no cap) ---
    experiment_results = client.evaluate(
        target,
        data=DATASET_NAME,
        evaluators=[correctness_evaluator, tool_correctness_evaluator],
        experiment_prefix="coffee-chatbot-eval",
        max_concurrency=6,
    )

    # --- Iterate ALL result rows ---
    rows: list[dict] = []
    for row in experiment_results:
        example = row["example"]
        scores = {
            er.key: er.score
            for er in row["evaluation_results"]["results"]
        }
        rows.append({
            "question": example.inputs.get("question", ""),
            "scores": scores,
        })

    current_metrics = _compute_metrics(rows)
    experiment_name: str = getattr(experiment_results, "experiment_name", "unknown")

    # --- Fetch previous experiment as baseline (no local file) ---
    # list_projects doesn't support order= in this SDK version; sort by start_time manually
    projects = sorted(
        client.list_projects(reference_dataset_name=DATASET_NAME),
        key=lambda p: getattr(p, "start_time", None) or "",
        reverse=True,
    )[:2]

    # projects[0] = current experiment (most recent), projects[1] = baseline
    baseline_metrics: dict[str, float] = {}
    baseline_name = "(none — first run)"
    if len(projects) >= 2:
        baseline_project = projects[1]
        baseline_name = baseline_project.name
        baseline_metrics = _metrics_from_project(baseline_project)

    # --- Regression check ---
    regressions: dict[str, dict] = {}
    for key, current_val in current_metrics.items():
        baseline_val = baseline_metrics.get(key)
        if baseline_val is not None and (baseline_val - current_val) > REGRESSION_THRESHOLD:
            regressions[key] = {
                "baseline": baseline_val,
                "current": current_val,
                "drop": baseline_val - current_val,
            }

    # --- Console summary ---
    print("\n" + "=" * 50)
    print("Eval Summary")
    print("=" * 50)
    print(f"Experiment : {experiment_name}")
    print(f"Baseline   : {baseline_name}")
    print(f"Dataset    : {DATASET_NAME} ({len(rows)} examples)")
    print("-" * 50)

    for key, current_val in sorted(current_metrics.items()):
        baseline_val = baseline_metrics.get(key)
        if baseline_val is not None:
            diff = current_val - baseline_val
            sign = "+" if diff >= 0 else ""
            status = f"<< REGRESSION {diff:.1f}pp" if key in regressions else f"OK ({sign}{diff:.1f}pp)"
            print(f"  {key:<22}: {current_val:5.1f}%  (baseline: {baseline_val:.1f}%)  {status}")
        else:
            print(f"  {key:<22}: {current_val:5.1f}%  (no baseline)")

    print("-" * 50)

    if not baseline_metrics:
        print("First run — no baseline to compare. Run again to enable regression checks.")
    # Print failing cases when correctness < 90% so agent can improve without MCP
    score_pct = current_metrics.get("score")
    if score_pct is not None and score_pct < 90.0:
        failing = [r for r in rows if (r["scores"].get("score") or 0) < 1.0]
        if failing:
            print("\nFailing cases (correctness < 1):")
            for r in failing[:25]:  # cap for console
                q = (r["question"] or "")[:80]
                s = r["scores"].get("score")
                print(f"  - {q!r}... -> score={s}")
            if len(failing) > 25:
                print(f"  ... and {len(failing) - 25} more")
    if not baseline_metrics:
        print("=" * 50 + "\n")
        sys.exit(0)

    if regressions:
        print(f"FAILED — {len(regressions)} metric(s) regressed > {REGRESSION_THRESHOLD}pp\n")
        failing_rows = [r for r in rows if any(s is None or s < 1.0 for s in r["scores"].values())]
        print("=== Investigation ===")
        investigation = _run_investigation(experiment_name, baseline_name, regressions, failing_rows)
        print(investigation)
        print("=" * 50 + "\n")
        sys.exit(1)
    else:
        print("PASSED")
        print("=" * 50 + "\n")
        sys.exit(0)


if __name__ == "__main__":
    main()