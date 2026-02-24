# Virtualenv for evals (same as .cursor/commands/run-evals.md). Override if your venv is elsewhere.
PY ?= $(HOME)/.virtualenvs/brazil-coffee-chatbot/bin/python

run:
	uvicorn app.main:app --reload

ingest:
	python -m app.ingestion.embedder

# Sync eval dataset to LangSmith (create/update coffee-chatbot-eval from app/evals/dataset.py)
dataset:
	$(PY) -m app.evals.dataset

# Run offline evals. After changing the chatbot, run 'make eval' again to re-run the loop.
eval:
	$(PY) -m app.evals.eval