# FIN-Advisor: Tech Stack Definition

---

## Stack Summary

| Layer | Technology | Version | License | Cost |
|---|---|---|---|---|
| Frontend | React.js | 18.x | MIT | Free |
| Backend | FastAPI | 0.100+ | MIT | Free |
| Agent Framework | LangChain | 0.2+ | MIT | Free |
| Local LLM Runtime | API-based (Gemini/HuggingFace/OpenAI/Groq) | Latest | Various | Free tiers available |
| LLM Model | gemini-1.5-flash (recommended) | Latest | Google ToS | Free tier: 1,500 req/day |
| Vector Database | ChromaDB | 0.4+ | Apache 2.0 | Free |
| Embedding Model | intfloat/multilingual-e5-small | - | Apache 2.0 | Free |
| Relational Database | SQLite | 3.x | Public Domain | Free |
| Language | Python | 3.11+ | PSF | Free |
| Package Manager (Python) | pip / uv | Latest | - | Free |
| Package Manager (JS) | npm | Latest | - | Free |

**Total infrastructure cost: $0 USD**

---

## Component Details

### Frontend: React.js

**Purpose:** Render the chat interface.

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
- `langchain_community.llms` — LLM provider integrations
- `langchain_community.vectorstores` — ChromaDB integration
- `langchain.text_splitter` — Document chunking (for ETL)

**Why LangChain over alternatives:**
- Most mature agent framework with extensive tool-calling support
- Native integration with ChromaDB and all supported LLM providers
- Large community, well-documented
- LlamaIndex is more retrieval-focused; LangChain is better for agent orchestration

---

### LLM: API-Based Providers (Configurable)

**Purpose:** Generate natural language responses based on enriched context.

**Configuration:** Switchable via environment variables (`LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL_NAME`). Strategy pattern enables provider switching without code changes.

**Provider Options:**

| Provider | Model | Free Tier | Paid Cost (per 1M tokens) | Spanish Quality | Context Window |
|---|---|---|---|---|---|
| **Gemini (recommended)** | `gemini-1.5-flash` | 1,500 req/day | $0.35 input / $1.05 output | Excellent | 1M tokens |
| **HuggingFace** | `Llama-3.1-70B-Instruct` | Rate-limited | Pay-as-you-go | Good | 8K tokens |
| **OpenAI** | `gpt-4o-mini` | $5-18 student credit | $0.15 input / $0.60 output | Best-in-class | 128K tokens |
| **Groq** | `llama-3.3-70b-versatile` | ~14,000 req/day | Very affordable | Good | 128K tokens |

**LangChain packages required (install only the one you use):**
- Gemini: `langchain-google-genai`
- HuggingFace: `langchain-huggingface`
- OpenAI: `langchain-openai`
- Groq: `langchain-groq`

**Why API-based over local Ollama:**
- No local GPU or 16GB RAM requirement
- Gemini free tier (1,500 req/day) is more than enough for development and demo
- Better Spanish quality from larger models (70B+ parameters)
- Faster response times (especially Groq at ≤400ms)
- Strategy pattern allows switching providers via a single env var

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

### Embedding Model: intfloat/multilingual-e5-small

**Purpose:** Convert text chunks and queries into vector representations for semantic search.

**Details:**
- Library: `sentence-transformers`
- Model: `intfloat/multilingual-e5-small`
- Model size: ~134 MB
- Embedding dimension: 384
- Speed: Fast on CPU (no GPU required)
- Language: Multilingual (optimized for Spanish and legal text)

**Alternatives (configurable via `EMBEDDING_MODEL_NAME` env var):**
- `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (~120MB)
- `intfloat/multilingual-e5-base` (~440MB, higher quality)

**Why this model:**
- Better Spanish and legal text support than all-MiniLM-L6-v2
- Small enough to run on any machine
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
  │     ├── langchain_google_genai (Gemini LLM connection)
  │     ├── langchain_huggingface (HuggingFace LLM connection)
  │     ├── langchain_openai (OpenAI LLM connection)
  │     ├── langchain_groq (Groq LLM connection)
  │     ├── langchain_community.vectorstores.chroma (vector search)
  │     ├── langchain.agents (ReAct agent)
  │     └── langchain.tools (tool definitions)
  ├── chromadb (vector store)
  ├── sentence-transformers (embeddings)
  │     └── intfloat/multilingual-e5-small (model)
  ├── sqlite3 (built-in, relational data)
  └── pydantic (data validation)
```

---

## Development Tools (Recommended)

| Tool | Purpose |
|---|---|
| Git | Version control |
| VS Code / Kiro | IDE |
| Postman or curl | API testing |
| DB Browser for SQLite | Inspect mock data |
