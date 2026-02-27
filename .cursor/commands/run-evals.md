# /run-evals

Run the eval suite against the coffee chatbot, fetch results from LangSmith, analyze failures, and improve the agent. **Loop:** run evals → read results (MCP) → improve chatbot → run evals again → repeat until correctness >= 90%.

**Quick re-run after a change:** from `backend/` run `make eval` (uses the same venv below). To sync the dataset first, run `make dataset` then `make eval`.

## Virtualenv (mkvirtualenv)

Use the virtualenv **brazil-coffee-chatbot**. virtualenvwrapper (mkvirtualenv) stores envs in `$WORKON_HOME` (default `~/.virtualenvs/`). Use that env's Python explicitly so the script runs with the correct dependencies:

- **Path**: `$HOME/.virtualenvs/brazil-coffee-chatbot/bin/python` (or, if the project has a local `.virtualenvs/brazil-coffee-chatbot`, use `./.virtualenvs/brazil-coffee-chatbot/bin/python` from repo root).

Do not assume `workon` is available in non-interactive shells; call the venv's `python` binary directly.

## Steps

### 1. Run the eval script

From the **backend** directory, run the eval module with the virtualenv's Python (same as `make eval` when using the default venv):

```bash
cd backend && make eval
```

Or explicitly: `cd backend && $HOME/.virtualenvs/brazil-coffee-chatbot/bin/python -m app.evals.eval`. If your venv is under the project, use `../.virtualenvs/brazil-coffee-chatbot/bin/python` or set `PY` when calling make: `make eval PY=../.virtualenvs/brazil-coffee-chatbot/bin/python`.

Wait for the script to finish. The output will include the experiment name (e.g. `first-offline-eval-<hash>`).

### 2. Fetch results via LangSmith MCP

Once the script finishes, use the LangSmith MCP tools to get the results:

**Step 2a — Get experiment metrics:**

Call `list_experiments` with:
- `reference_dataset_name = "coffee-chatbot-eval"`
- `limit = 1`

This returns the latest experiment name and aggregated `feedback_stats` (correctness score, tool_correctness score, latency, cost).

**Step 2b — Get per-example run details:**

Call `fetch_runs` with:
- `project_name = "<experiment_name_from_step_2a>"`
- `limit = 20`

This returns each run's `inputs` (the question), `outputs` (agent's answer + tools_used), and evaluator feedback scores (correctness, tool_correctness).

**Step 2c — If needed, review dataset expectations:**

Call `list_examples` with:
- `dataset_name = "coffee-chatbot-eval"`

Use this to cross-reference what the expected answers are for failing cases.

### 3. Analyze failures

For each run with `correctness < 1` or `tool_correctness < 1`:
- Read the question, the agent's actual answer, and the expected answer criteria
- Identify the root cause:
  - **Prompt issue**: agent did not follow an instruction in `SYSTEM_PROMPT`
  - **Wrong tool**: agent used the wrong tool or no tool when one was required
  - **Tool description**: tool description is unclear, causing wrong tool selection
  - **Missing knowledge**: RAG did not return relevant content
  - **Off-topic handling**: agent incorrectly answered or refused an on-topic question

### 4. Apply minimal improvements

Improve only what is needed. Priority order:

1. **`backend/app/agents/coffee_agent.py`** — update `SYSTEM_PROMPT` to add or clarify instructions that fix the failures. Do NOT rewrite unchanged instructions.
2. **`backend/app/tools/`** — update tool descriptions (`rag_tool.py`, `places_tool.py`, `search_tool.py`) if tool selection was wrong.
3. **`backend/app/evals/dataset.py`** or **`backend/app/evals/eval.py`** — only if the eval expectation or evaluator itself is clearly wrong (last resort).

### 5. Check score and decide

- If `feedback_stats` shows overall correctness >= 90%: report success and stop.
- If < 90%: **loop** — apply changes to the chatbot, then run the eval again (Step 1). From `backend/` you can run `make eval` to re-run with the same venv. Repeat until >= 90% or the user asks to stop.

## Constraints

- Make patch-style edits only — never rewrite entire files.
- Do NOT change eval examples to match wrong agent behavior; fix the agent instead.
- Do NOT modify `eval.py` logic unless the evaluator itself is producing wrong scores.
- Stop the loop if the user says so, even if target is not reached.
- After each iteration, report: experiment name, correctness %, tool_correctness %, and which files were changed.
