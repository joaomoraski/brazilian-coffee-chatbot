# One command to run everything (DB + backend + pdf-api + frontend).
# Backend and pdf-api run in background; frontend runs in foreground (Ctrl+C to stop).
.PHONY: run

run:
	@echo "Starting database..."
	@cd backend && docker-compose up -d
	@sleep 2
	@echo "Starting backend API (port 8000)..."
	@(cd backend && uvicorn app.main:app --reload) &
	@echo "Starting PDF API (port 8001)..."
	@(cd pdf-api && uvicorn main:app --reload --port 8001) &
	@sleep 1
	@echo "Starting frontend (port 3000)..."
	@cd frontend && npm run dev
