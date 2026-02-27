# ☕ Brazilian Coffee Chatbot

An AI-powered chatbot that answers questions about Brazilian coffee — from its rich history to brewing methods, from plantation techniques to finding the best coffee shops near you.

Built with **RAG (Retrieval-Augmented Generation)** architecture using LangChain, Gemini, and PostgreSQL with pgvector.

![Architecture](https://img.shields.io/badge/Architecture-RAG%20Agent-blue)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green)
![Frontend](https://img.shields.io/badge/Frontend-Next.js-black)
![LLM](https://img.shields.io/badge/LLM-Gemini%203%20Pro-orange)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [RAG Deep Dive](#-rag-deep-dive)
- [Tech Stack & Decisions](#-tech-stack--decisions)
- [Project Structure](#-project-structure)
- [Setup](#-setup)
- [Usage](#-usage)
- [Evaluation](#-evaluation)
- [API Reference](#-api-reference)

---

## ✨ Features

- **Educational Q&A**: Answer questions about coffee history, cultivation, harvesting, roasting, and brewing
- **Coffee Classification**: Explain quality levels and specialty coffee standards
- **Location Search**: Find coffee shops in any city using Google Places API
- **Web Search Fallback**: Search the web when local knowledge isn't enough
- **Multilingual**: Responds in the same language the user writes (Portuguese, English, etc.)
- **Real-time Streaming**: See responses appear word-by-word like ChatGPT
- **Source Citations**: Every answer links to sources (PDFs, ARAM site, web search, Google Maps)
- **MLOps Ready**: LangSmith integration for tracing and monitoring
- **Eval feedback loop**: Offline evals on a 59-example LangSmith dataset with regression checks and failing-case summary to guide agent improvements

---

## 🏗 Architecture

```mermaid
graph TD
    User([User]) --> Frontend[Next.js Frontend]
    
    subgraph Frontend["Frontend (Next.js)"]
        ChatContainer --> useChat[useChat Hook]
        useChat -->|Stream/JSON| API[API Client]
    end
    
    Frontend -->|HTTP Request| Backend[FastAPI Backend]
    Frontend -->|PDF links| PdfApi
    
    subgraph Backend["Backend (FastAPI)"]
        Agent[LangChain Agent]
        
        subgraph Tools
            RAG["RAG Tool<br/>(Knowledge Base)"]
            Places["Places Tool<br/>(Google Maps)"]
            Tavily["Tavily Tool<br/>(Web Search)"]
        end
        
        Agent -->|Decides| Tools
        RAG -->|Similarity Search| VectorDB
    end
    
    subgraph Database["Database"]
        VectorDB[(PostgreSQL + pgvector)]
    end
    
    subgraph PdfApi["PDF API (optional separate deploy)"]
        Serve["GET /pdfs/{filename}"]
    end

    style User fill:#f9f,stroke:#333,stroke-width:2px
    style Frontend fill:#E8C593,stroke:#6F4E37,stroke-width:2px,color:#6F4E37
    style Backend fill:#6F4E37,stroke:#E8B946,stroke-width:2px,color:white
    style Database fill:#E8B946,stroke:#6F4E37,stroke-width:2px
    style Agent fill:#E8CD46,stroke:#333,stroke-width:2px
    style Tools fill:#fff,stroke:#333,stroke-width:1px,color:#333
```

### Component Responsibilities

| Component | Responsibility |
|-----------|---------------|
| **Next.js Frontend** | Chat UI with streaming support, coffee-themed design |
| **FastAPI Backend** | REST API, request handling, CORS |
| **LangChain Agent** | Decision-making: which tool to use based on user intent |
| **RAG Tool** | Search knowledge base for coffee information |
| **Places Tool** | Find coffee shops via Google Places API |
| **Tavily Tool** | Web search for current/missing information |
| **PostgreSQL + pgvector** | Store document embeddings for similarity search |
| **PDF API** | Lightweight separate service that serves PDFs (avoids Vercel 250MB limit on main backend) |

---

## 🔍 RAG Deep Dive

### What is RAG?

**RAG (Retrieval-Augmented Generation)** combines:
1. **Retrieval**: Find relevant documents from a knowledge base
2. **Augmented**: Add those documents to the LLM prompt
3. **Generation**: LLM generates answer using the context

```mermaid
sequenceDiagram
    actor User
    participant App as RAG Pipeline
    participant DB as Vector DB
    participant LLM as Gemini Model
    
    User->>App: "How is coffee harvested?"
    
    rect rgb(232, 197, 147)
        Note over App: 1. Embed Question
        App->>App: Convert to Vector<br/>[0.23, -0.12, ...]
    end
    
    rect rgb(232, 185, 70)
        Note over App, DB: 2. Similarity Search
        App->>DB: Query Top-K Vectors
        DB-->>App: Return Relevant Docs
    end
    
    rect rgb(111, 78, 55)
        Note over App, LLM: 3. Augmented Generation
        App->>LLM: System Prompt + <br/>Context + Question
        LLM-->>App: Generated Answer
    end
    
    App-->>User: "Coffee is harvested by..."
```

### Why RAG Instead of Fine-tuning?

| Approach | Pros | Cons |
|----------|------|------|
| **Fine-tuning** | Knowledge baked into model | Expensive, outdated quickly, hallucinations |
| **RAG** | Up-to-date, verifiable sources, cheaper | Requires vector DB, retrieval latency |

**We chose RAG because:**
1. Coffee information can be updated without retraining
2. Responses can cite sources
3. No expensive GPU training required
4. Works with any LLM (Gemini, GPT, Claude)

### Ingestion Pipeline

```mermaid
graph TD
    subgraph Sources["Data Sources"]
        PDF["PDF Files<br/>(Books, Reports)"]
        Web["ARAM Website<br/>(Scraped History)"]
    end

    subgraph Processing["Processing Pipeline"]
        Loader["Document Loaders<br/>(Unstructured + OCR)"]
        Chunker["Text Splitter<br/>(1000 chars, 200 overlap)"]
        Embedder["Gemini Embeddings<br/>(768 dimensions)"]
    end

    subgraph Storage["Storage"]
        VectorDB[("PostgreSQL<br/>+ pgvector")]
    end

    PDF --> Loader
    Web --> Loader
    Loader --> Chunker
    Chunker --> Embedder
    Embedder --> VectorDB

    style Sources fill:#E8C593,stroke:#6F4E37,stroke-width:2px
    style Processing fill:#E8B946,stroke:#6F4E37,stroke-width:2px
    style Storage fill:#6F4E37,stroke:#333,stroke-width:2px,color:white
    style PDF fill:#fff,stroke:#333
    style Web fill:#fff,stroke:#333
    style Loader fill:#fff,stroke:#333
    style Chunker fill:#fff,stroke:#333
    style Embedder fill:#fff,stroke:#333
```

### Why These Chunking Parameters?

```python
chunk_size=1000    # ~250 tokens, fits well in context
chunk_overlap=200  # Preserves context at boundaries
```

- **Too small** (100 chars): Loses context, fragments sentences
- **Too large** (5000 chars): Retrieves irrelevant content, wastes tokens
- **1000 chars**: Good balance for Q&A retrieval

---

## 🛠 Tech Stack & Decisions

### LLM: Gemini 3 Pro

**Why Gemini?**
- Excellent multilingual support (Portuguese/English)
- Competitive pricing
- Good reasoning for tool selection
- Native streaming support

### Vector DB: PostgreSQL + pgvector

**Why pgvector over Pinecone/Chroma?**
- **Self-hosted**: No vendor lock-in, data stays local
- **SQL familiar**: Easy to query, backup, maintain
- **Production-ready**: PostgreSQL is battle-tested
- **Free**: No per-query costs

### PDF Processing: Unstructured + Tesseract

**Why Unstructured?**
- Handles mixed content (text + images + tables)
- OCR support for scanned documents
- Preserves document structure
- Portuguese language support

### Frontend: Next.js + Tailwind

**Why Next.js?**
- React with built-in optimizations
- Easy deployment (Vercel)
- TypeScript support
- Fast development

---

## 📁 Project Structure

```
brazilian-coffee-chatbot/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   └── coffee_agent.py    # LangChain agent (create_agent)
│   │   ├── db/
│   │   │   └── vector_store.py    # pgvector connection
│   │   ├── ingestion/
│   │   │   ├── pdf_loader.py      # PDF processing with OCR
│   │   │   ├── web_scraper.py     # ARAM website scraper
│   │   │   └── embedder.py        # Embedding pipeline (reads from pdf-api/pdfs/)
│   │   ├── tools/
│   │   │   ├── rag_tool.py        # Knowledge base search
│   │   │   ├── places_tool.py     # Google Places API
│   │   │   └── search_tool.py     # Tavily web search
│   │   ├── evals/
│   │   │   ├── dataset.py         # Eval examples (LangSmith dataset)
│   │   │   └── eval.py            # Eval runner, regression check, failing-case summary
│   │   ├── main.py                # FastAPI application (no PDF route)
│   │   └── settings.py            # Environment config
│   ├── docker-compose.yml         # PostgreSQL + pgvector
│   └── requirements.txt
├── pdf-api/
│   ├── main.py                    # Minimal FastAPI app: GET /pdfs/{filename}
│   ├── pdfs/                      # Knowledge base PDFs (single source of truth)
│   └── requirements.txt           # fastapi, uvicorn only (light for Vercel)
├── frontend/
│   ├── src/
│   │   ├── app/                   # Next.js App Router
│   │   ├── components/Chat/       # Chat UI + source citation pills
│   │   ├── hooks/useChat.ts       # Streaming chat hook
│   │   └── lib/api.ts             # Backend API client
│   └── tailwind.config.ts         # Coffee color theme
└── docs/
    └── ARCHITECTURE.md            # Technical deep dive
```

---

## 🚀 Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for PostgreSQL)
- Tesseract OCR (`brew install tesseract` on macOS)

### 1. Clone & Environment

```bash
git clone <repo-url>
cd brazilian-coffee-chatbot

# Backend
cd backend
cp .env.example .env
# Fill in your API keys in .env
```

### 2. Environment Variables

**Backend** (`backend/.env`):

```env
# Required
GOOGLE_API_KEY=your-gemini-api-key

# Optional (for full features)
TAVILY_API_KEY=your-tavily-key
GPLACES_API_KEY=your-google-places-key
LANGSMITH_API_KEY=your-langsmith-key   # Required for evals
```

**Frontend** (`frontend/.env`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_PDF_API_URL=http://localhost:8001
```

### 3. Start Database

```bash
cd backend
docker-compose up -d
```

### 4. Install & Run Backend

```bash
cd backend
pip install -r requirements.txt

# Ingest documents (one-time; reads from pdf-api/pdfs/)
python -m app.ingestion.embedder

# Start server
python -m app.main
```

### 4b. (Optional) Run PDF API

Citation links to PDFs point at a separate lightweight service so the main backend stays under Vercel’s size limit. Locally, run it on port 8001:

```bash
cd pdf-api
pip install -r requirements.txt
make run
# or: uvicorn main:app --reload --port 8001
```

**💡 Tip**: Add PDFs to `pdf-api/pdfs/` before running ingestion. The embedder reads from that folder. For production, deploy `pdf-api/` as a second Vercel project and set `NEXT_PUBLIC_PDF_API_URL` to its URL.

### 5. Install & Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

---

## 📖 Usage

### Chat Examples

| Question | Tool Used |
|----------|-----------|
| "Como o café chegou ao Brasil?" | RAG (knowledge base) |
| "What are the best brewing methods?" | RAG (knowledge base) |
| "Onde posso tomar café em São Paulo?" | Google Places |
| "What's the current coffee price in 2025?" | Tavily (web search) |

### CLI: Ingest Documents

```bash
cd backend
python -m app.ingestion.embedder
```

### Evaluation

Run evals against the coffee chatbot using a LangSmith dataset. Requires a virtualenv with dependencies from `requirements-local.txt` (e.g. `brazil-coffee-chatbot`). From the **backend** directory:

```bash
make dataset   # Sync dataset to LangSmith (once)
make eval      # Run full eval; prints summary and failing cases if correctness < 90%
```

Results appear in the terminal (experiment name, score %, tool_correctness %) and on LangSmith. The script compares against the previous experiment for regression detection.

### CLI: Test Web Scraper

```bash
cd backend
python -c "
from app.ingestion.web_scraper import scrape_aram_history_sync
docs = scrape_aram_history_sync()
print(f'Scraped {len(docs)} documents')
"
```

---

## 📚 API Reference

### POST /chat/stream

Streaming chat (Server-Sent Events). Frontend uses this for real-time responses.

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "How to brew coffee?", "session_id": "<uuid>"}'
```

**Response:** SSE stream (`event: message` with text chunks; `event: done` when finished).

### GET /sessions/{session_id}/messages

Load chat history for a session.

### DELETE /sessions/{session_id}

Clear all messages for a session.

### PDF API (separate service)

If you run the `pdf-api` service (e.g. `http://localhost:8001`):

- **GET /pdfs/{filename}** — Serves a PDF from `pdf-api/pdfs/`. Used by the frontend for source citation links.

---

## 🔮 Future Improvements

- **Cloud Storage Integration**: Use Google Drive, S3, or other cloud storage to maintain PDFs instead of storing them locally. This would enable dynamic document updates without redeployment and better scalability.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- Coffee PDFs sourced from Brazilian agricultural research institutions
- [ARAM Brasil](https://arambrasil.coffee) for coffee history content
- Built with [LangChain](https://langchain.com)
