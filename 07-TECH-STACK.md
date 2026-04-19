# FIN-Advisor: Tech Stack Definition

---

## Stack Summary

| Layer | Technology | Version | License | Cost |
|---|---|---|---|---|
| Frontend | React.js | 18.x | MIT | Free |
| Backend | FastAPI | 0.100+ | MIT | Free |
| Agent Framework | LangChain | 0.2+ | MIT | Free |
| Local LLM Runtime | Ollama | Latest | MIT | Free |
| LLM Model | Llama 3 (8B) | 8B-instruct | Llama 3 License | Free |
| Vector Database | ChromaDB | 0.4+ | Apache 2.0 | Free |
| Embedding Model | all-MiniLM-L6-v2 | - | Apache 2.0 | Free |
| Relational Database | SQLite | 3.x | Public Domain | Free |
| Language | Python | 3.11+ | PSF | Free |
| Package Manager (Python) | pip / uv | Latest | - | Free |
| Package Manager (JS) | npm | Latest | - | Free |

**Total infrastructure cost: $0 USD**

---

## Component Details

### Frontend: React.js

**Purpose:** Render the chat interface and FIN dashboard.

**Key libraries:**
- `react` — Core UI framework
- `axios` or `fetch` — HTTP client for API calls
- `react-markdown` — Render markdown-formatted responses from the LLM
- CSS framework (optional): Tailwind CSS or plain CSS modules

**Why React over alternatives:**
- Most widely known among university students
- Massive ecosystem and documentation
- Simple component model for a chat interface
- No need for SSR (rules out Next.js complexity)

---

### Backend: FastAPI

**Purpose:** Serve the API, manage the agent lifecycle, handle request/response.

**Key libraries:**
- `fastapi` — Web framework
- `uvicorn` — ASGI server
- `langchain` — Agent orchestration
- `chromadb` — Vector store client
- `sentence-transformers` — Local embedding generation
- `sqlite3` (built-in) — Database access
- `pydantic` — Request/response validation

**Why FastAPI over alternatives:**
- Native async support (important for LLM inference which is I/O-bound)
- Automatic OpenAPI documentation (useful for team collaboration)
- First-class Pydantic integration for data validation
- De facto standard for Python AI/ML APIs

---

### Agent Framework: LangChain

**Purpose:** Define the ReAct agent, manage tools, orchestrate the reasoning loop.

**Key modules:**
- `langchain.agents` — ReAct agent implementation
- `langchain.tools` — Tool definition and registration
- `langchain_community.llms` — Ollama LLM integration
- `langchain_community.vectorstores` — ChromaDB integration
- `langchain.text_splitter` — Document chunking (for ETL)

**Why LangChain over alternatives:**
- Most mature agent framework with extensive tool-calling support
- Native integration with both Ollama and ChromaDB
- Large community, well-documented
- LlamaIndex is more retrieval-focused; LangChain is better for agent orchestration

---

### LLM: Ollama + Llama 3 (8B)

**Purpose:** Generate natural language responses based on enriched context.

**Configuration:**
- Runtime: Ollama (manages model download, serving, and API)
- Model: `llama3:8b-instruct` (instruction-tuned variant)
- Fallback: `mistral:7b-instruct` (lighter, for machines with less RAM)
- API endpoint: `http://localhost:11434/api/generate`
- Context window: 8,192 tokens (Llama 3 8B)

**Hardware requirements:**
| Resource | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB |
| GPU | Not required | NVIDIA with 6GB+ VRAM (dramatically faster) |
| Disk | 5 GB (for model weights) | 10 GB |

**Why Ollama over alternatives:**
- One-command model download and serving (`ollama pull llama3`)
- REST API compatible with LangChain out of the box
- No Python dependency conflicts (runs as a separate process)
- Supports model switching without code changes

---

### Vector Database: ChromaDB

**Purpose:** Store and query document embeddings for semantic search.

**Configuration:**
- Mode: Persistent local (data survives restarts)
- Collections: `tax_laws`, `sector_guides`
- Distance metric: Cosine similarity (default)
- Index: HNSW (default, efficient for small-to-medium datasets)

**Why ChromaDB over alternatives:**
- Zero cost, no cloud account needed
- Python-native client, integrates directly with LangChain
- Persistent mode with a simple directory path
- Metadata filtering (filter by `topic_tags`, `document_type`, etc.)
- FAISS was considered but lacks built-in metadata support

---

### Embedding Model: all-MiniLM-L6-v2

**Purpose:** Convert text chunks and queries into vector representations for semantic search.

**Details:**
- Library: `sentence-transformers`
- Model size: ~80 MB
- Embedding dimension: 384
- Speed: Fast on CPU (no GPU required)
- Language: Multilingual (supports Spanish)

**Why this model:**
- Small enough to run on any machine
- Good quality for document retrieval tasks
- No API key or internet connection needed after initial download
- Well-tested with ChromaDB and LangChain

---

### Relational Database: SQLite

**Purpose:** Store mock EverGreen FIN data (movements, invoices, payables, assets).

**Why SQLite:**
- Zero configuration — it's a single file (`fin.db`)
- Built into Python's standard library
- Perfect for mock/synthetic data
- Can be replaced with PostgreSQL without changing query logic (if using SQLAlchemy)

---

## Dependency Map

```
React.js (Frontend)
  └── axios (HTTP client)
  └── react-markdown (response rendering)

FastAPI (Backend)
  ├── uvicorn (server)
  ├── langchain (agent framework)
  │     ├── langchain_community.llms.ollama (LLM connection)
  │     ├── langchain_community.vectorstores.chroma (vector search)
  │     ├── langchain.agents (ReAct agent)
  │     └── langchain.tools (tool definitions)
  ├── chromadb (vector store)
  ├── sentence-transformers (embeddings)
  │     └── all-MiniLM-L6-v2 (model)
  ├── sqlite3 (built-in, relational data)
  └── pydantic (data validation)

Ollama (External process)
  └── llama3:8b-instruct (LLM model)
```

---

## Development Tools (Recommended)

| Tool | Purpose |
|---|---|
| Git | Version control |
| VS Code / Kiro | IDE |
| Postman or curl | API testing |
| DB Browser for SQLite | Inspect mock data |
| Ollama CLI | Model management (`ollama list`, `ollama pull`) |
