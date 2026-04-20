# FIN-Advisor: Architecture Definition

---

## Architecture Overview

FIN-Advisor follows a **layered architecture** with four distinct layers, each with a single responsibility. Components run locally except for LLM inference, which uses external API-based providers (free-tier cloud APIs).

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                               │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    React.js Frontend                            │   │
│   │                                                                 │   │
│   │   ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │   │
│   │   │  Chat UI     │  │  Suggestion  │  │  Response          │   │   │
│   │   │  Component   │  │  Chips       │  │  Renderer          │   │   │
│   │   └──────────────┘  └──────────────┘  └────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                     │
│                              HTTP / REST                                 │
│                                    │                                     │
├────────────────────────────────────┼─────────────────────────────────────┤
│                        REASONING LAYER                                   │
│                                    │                                     │
│   ┌────────────────────────────────▼────────────────────────────────┐   │
│   │                    FastAPI Backend                               │   │
│   │                                                                 │   │
│   │   ┌──────────────────────────────────────────────────────┐     │   │
│   │   │              ReAct Agent (LangChain)                 │     │   │
│   │   │                                                      │     │   │
│   │   │   ┌─────────────┐ ┌──────────────┐                  │     │   │
│   │   │   │ Tool:       │ │ Tool:        │                  │     │   │
│   │   │   │ get_tax_    │ │ query_       │  Calculation     │     │   │
│   │   │   │ knowledge   │ │ evergreen_   │  Tools (x5):     │     │   │
│   │   │   │             │ │ finances     │  ┌────────────┐  │     │   │
│   │   │   │             │ │              │  │ vat_disc.  │  │     │   │
│   │   │   │             │ │              │  │ net_liq.   │  │     │   │
│   │   │   │             │ │              │  │ invest.    │  │     │   │
│   │   │   │             │ │              │  │ tax_proj.  │  │     │   │
│   │   │   │             │ │              │  │ deprec.    │  │     │   │
│   │   │   └──────┬──────┘ └──────┬───────┘  └────────────┘  │     │   │
│   │   │          │               │                          │     │   │
│   │   └──────────┼───────────────┼──────────────────────────┘     │   │
│   │              │               │                                 │   │
│   └──────────────┼───────────────┼─────────────────────────────────┘   │
│                  │               │                                     │
├──────────────────┼───────────────┼─────────────────────────────────────┤
│                  │  KNOWLEDGE LAYER          DATA LAYER                │
│                  │               │                                     │
│   ┌──────────────▼──────┐  ┌────▼──────────────────────────────┐     │
│   │    ChromaDB          │  │    SQLite / PostgreSQL            │     │
│   │    (Vector Store)    │  │    (EverGreen FIN Database)       │     │
│   │                      │  │                                   │     │
│   │  - Tax law chunks    │  │  - Movimientos (movements)       │     │
│   │  - Benefit guides    │  │  - Facturas (invoices)           │     │
│   │  - Sector docs       │  │  - Cuentas por pagar (payables)  │     │
│   │                      │  │  - Activos fijos (fixed assets)  │     │
│   │  Embeddings via      │  │                                   │     │
│   │  sentence-transformers│  │  Mock data (synthetic)           │     │
│   └──────────────────────┘  └───────────────────────────────────┘     │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                        INFERENCE LAYER                                │
│                                                                       │
│   ┌───────────────────────────────────────────────────────────────┐   │
│   │              API-Based LLM Providers (External)                │   │
│   │                                                               │   │
│   │   Gemini (recommended) / HuggingFace / OpenAI / Groq         │   │
│   │   Configured via: LLM_PROVIDER, LLM_API_KEY, LLM_MODEL_NAME  │   │
│   │   Role: Receives enriched prompt, generates final response    │   │
│   └───────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Layer Descriptions

### Layer 1: Presentation Layer

| Component | Technology | Responsibility |
|---|---|---|
| Chat UI | React.js | Renders the conversational interface where the user types queries and receives responses |
| Suggestion Chips | React.js | Displays clickable example queries to help the user get started |
| Response Renderer | React.js | Formats the agent's structured responses (tables, warnings, calendars) into readable UI components |
| Logo | React.js | FIN-Advisor logo in top-right; renders placeholder if no logo file exists |

**Note:** A FIN Dashboard component (displaying EverGreen FIN module views) is deferred to Phase 2. See [PHASE-2-BACKLOG.md](./PHASE-2-BACKLOG.md).

**Communication:** The frontend communicates with the backend via REST API calls. For MVP, standard HTTP request/response is used. Streaming (SSE) is planned for Phase 2 for a better UX during long responses.

**Key endpoint:**
```
POST /api/v1/chat
Body: { "message": "string", "session_id": "string" }
Response: { "response": "string", "sources": [...], "tools_used": [...] }
```

---

### Layer 2: Reasoning Layer

| Component | Technology | Responsibility |
|---|---|---|
| API Server | FastAPI (Python) | Receives HTTP requests, manages sessions, returns responses |
| ReAct Agent | LangChain | Orchestrates the reasoning loop: analyzes the query, decides which tools to call, synthesizes the final answer |
| Tool: get_tax_knowledge | Python function | Performs semantic search on ChromaDB and returns relevant law/guide chunks |
| Tool: query_evergreen_finances | Python function | Executes SQL queries against the EverGreen FIN database and returns structured financial data |
| Tool: calculate_vat_discount | Python function | Calculates VAT discount on capital good purchases |
| Tool: calculate_net_liquidity | Python function | Calculates available funds after pending obligations |
| Tool: assess_investment_viability | Python function | Determines if a purchase is viable and suggests optimal timing |
| Tool: project_tax_liability | Python function | Estimates tax liability for a period |
| Tool: calculate_depreciation | Python function | Calculates current depreciated value of a fixed asset |

**Note:** Calculation capabilities are split into 5 single-purpose tools instead of one monolithic calculator. This gives the agent clearer semantics when reasoning about which tool to call — the tool name itself describes the action. See [Agent & Tools](./08-AGENT-AND-TOOLS.md) for the full rationale.

**ReAct Loop (example: investment viability query):**
```
1. THOUGHT: "The user asks about VAT on tractors. I need legal info + their balance."
2. ACTION: Call get_tax_knowledge("IVA descuento bienes de capital agropecuario")
3. OBSERVATION: [Chunk from Art. 258-1 returned]
4. THOUGHT: "Now I need the user's financial state to assess viability."
5. ACTION: Call query_evergreen_finances("current_balance, pending_receivables")
6. OBSERVATION: [Balance: $12.5M, Receivables: $8M]
7. THOUGHT: "I should calculate the VAT discount first."
8. ACTION: Call calculate_vat_discount({ "purchase_price": 18000000 })
9. OBSERVATION: [Discount: $3.42M, Effective cost: $14.58M]
10. THOUGHT: "Now I can assess if the purchase is viable."
11. ACTION: Call assess_investment_viability({ balance, receivables, payables, purchase_cost, tax_benefit })
12. OBSERVATION: [Viable in 15 days]
13. FINAL ANSWER: [Synthesized recommendation with all data]
```

---

### Layer 3: Knowledge Layer (ChromaDB)

| Attribute | Detail |
|---|---|
| Technology | ChromaDB (persistent local mode) |
| Embedding Model | `intfloat/multilingual-e5-small` via sentence-transformers (runs locally, optimized for Spanish/legal text) |
| Collections | `tax_laws`, `sector_guides` |
| Index Type | HNSW (default in ChromaDB) |

**Why ChromaDB?**
- Zero cost, fully local
- Python-native, integrates seamlessly with LangChain
- Persistent mode survives restarts without re-indexing
- Simple API for both ingestion and querying

---

### Layer 4: Data Layer (Relational Database)

| Attribute | Detail |
|---|---|
| Technology | SQLite (development) or PostgreSQL (if team prefers) |
| Content | Mock financial data simulating EverGreen's FIN module |
| Access Pattern | Read-only queries from the agent's tools |

**Tables:**
- `movimientos` — Accounting movements (income/expenses)
- `facturas_venta` — Sales invoices
- `cuentas_por_pagar` — Accounts payable
- `activos_fijos` — Fixed asset inventory
- `perfil_productor` — Producer profile (activity type, tax bracket)

---

### Inference Layer (API-Based LLM Providers)

| Attribute | Detail |
|---|---|
| Technology | API-based: Gemini (recommended), HuggingFace, OpenAI, Groq |
| Primary Model | `gemini-1.5-flash` (free tier: 1,500 req/day) |
| Alternatives | `Llama-3.1-70B-Instruct` (HuggingFace), `gpt-4o-mini` (OpenAI), `llama-3.3-70b-versatile` (Groq) |
| API | Provider-specific REST APIs, abstracted via LangChain + Strategy pattern |
| Configuration | `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL_NAME` environment variables |

**Why API-based over Ollama + Llama 3?**
- No local GPU or 16GB RAM requirement
- Gemini free tier is more than enough for development and demo
- Better Spanish quality from larger models (70B+ parameters)
- Strategy pattern allows switching providers via a single env var
- Faster response times (especially Groq at ≤400ms)

---

## Data Flow Diagram

```
                    ┌──────────┐
                    │  User    │
                    │ (Browser)│
                    └────┬─────┘
                         │ 1. POST /api/v1/chat
                         │    { message: "¿Puedo descontar el IVA?" }
                         ▼
                    ┌──────────┐
                    │ FastAPI  │
                    │ Backend  │
                    └────┬─────┘
                         │ 2. Pass query to ReAct Agent
                         ▼
                    ┌──────────┐
                    │  ReAct   │
                    │  Agent   │◄─────────────────────────────┐
                    └────┬─────┘                              │
                         │                                    │
              ┌──────────┼──────────┐                         │
              │          │          │                          │
              ▼          ▼          ▼                          │
        ┌──────────┐ ┌──────────┐ ┌──────────────────┐       │
        │ ChromaDB │ │ SQLite/  │ │ Calculation      │       │
        │ (search) │ │ Postgres │ │ Tools (x5)       │       │
        │          │ │ (query)  │ │ - vat_discount   │       │
        │          │ │          │ │ - net_liquidity  │       │
        │          │ │          │ │ - invest_viab.   │       │
        │          │ │          │ │ - tax_projection │       │
        │          │ │          │ │ - depreciation   │       │
        └────┬─────┘ └────┬─────┘ └────────┬─────────┘       │
             │            │                │                  │
             │ 3. Return  │ 4. Return      │ 5. Return        │
             │ law chunks │ fin. data      │ calculation       │
             └────────────┴────────────────┴──────────────────┘
                         │
                         │ 6. Agent synthesizes context
                         ▼
                    ┌──────────┐
                    │  LLM API │
                    │ Provider │
                    └────┬─────┘
                         │ 7. Generated response
                         ▼
                    ┌──────────┐
                    │ FastAPI  │
                    │ Backend  │
                    └────┬─────┘
                         │ 8. JSON response
                         ▼
                    ┌──────────┐
                    │  User    │
                    │ (Browser)│
                    └──────────┘
```

---

## Architecture Justification

| Decision | Chosen | Alternatives Considered | Rationale |
|---|---|---|---|
| Frontend | React.js | Next.js, Vue.js | Simpler setup for a chat-focused UI. SSR (Next.js) is unnecessary for this use case |
| Backend | FastAPI | Flask, Django | Native async support, automatic OpenAPI docs, best Python framework for AI/ML serving |
| Agent Framework | LangChain | LlamaIndex, Smolagents | Most mature ecosystem for ReAct agents with tool calling. Extensive documentation and community |
| Vector DB | ChromaDB | Pinecone, Weaviate, FAISS | Free, local, Python-native, persistent mode. Pinecone/Weaviate require cloud. FAISS lacks metadata filtering |
| LLM | API-based (Gemini recommended) | Ollama (local), Hugging Face (local) | Gemini free tier (1,500 req/day) is sufficient for university project. Better Spanish quality from larger models. Strategy pattern allows switching providers |
| Relational DB | SQLite | PostgreSQL, MySQL | Zero configuration, file-based, perfect for mock data. Can upgrade to Postgres if needed |
| Embeddings | sentence-transformers (intfloat/multilingual-e5-small) | OpenAI embeddings, Cohere | Free, local, fast. Optimized for Spanish/legal text. Quality is sufficient for the document types in scope |

---

## Non-Functional Requirements

| Requirement | Target | Notes |
|---|---|---|
| Response Time | < 30 seconds (simple queries), < 45 seconds (multi-tool queries) | Depends on hardware. GPU significantly reduces LLM inference time |
| Availability | Local only — available when the machine is running | No SLA required for university project |
| Concurrency | Single user | MVP does not need to handle multiple simultaneous users |
| Data Privacy | Financial data stays local; queries sent to external LLM APIs | User queries and context are sent to the configured LLM provider (Gemini, HuggingFace, OpenAI, or Groq). Financial database and knowledge base remain local. No financial records are stored externally |
| Scalability | Not required for MVP | Architecture supports horizontal scaling if needed later |
| Security | Basic — no authentication for MVP | In production, would add JWT auth and role-based access |

---

## Deployment Topology

```
┌─────────────────────────────────────────────────┐
│              Developer's Machine                 │
│                                                  │
│  ┌────────────┐  ┌────────────┐                  │
│  │ React Dev  │  │ FastAPI    │                  │
│  │ Server     │  │ Server     │                  │
│  │ :3000      │  │ :8000      │                  │
│  └────────────┘  └────────────┘                  │
│                                                  │
│  ┌────────────┐  ┌────────────┐                  │
│  │ ChromaDB   │  │ SQLite     │                  │
│  │ (embedded) │  │ (file)     │                  │
│  │            │  │ fin.db     │                  │
│  └────────────┘  └────────────┘                  │
│                                                  │
│  External: LLM API Provider (Gemini/HF/OpenAI/Groq)
│                                                  │
└─────────────────────────────────────────────────┘
```

All services run on localhost. No Docker required for MVP, though a `docker-compose.yml` can be provided for convenience.
