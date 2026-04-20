# Implementation Plan: FIN-Advisor RAG

## Overview

Incremental implementation of the FIN-Advisor RAG system — a financial assistant for Colombian agricultural producers. The plan builds from foundational infrastructure (project structure, data models, environment config) through core components (calculation tools, ETL pipeline, agent, backend API) to the React frontend, Kiro IDE integration, and optional Docker orchestration. Each task builds on previous steps; testing is integrated alongside implementation.

## Tasks

- [x] 1. Project scaffolding, dependencies, and environment configuration
  - [x] 1.1 Create the folder structure under `RAG-FIN-Topicos-Avanzados/` with `agent/`, `agent/tools/`, `backend/`, `frontend/`, `scripts/`, `knowledge_base/`, and `tests/` directories, including `__init__.py` files for Python packages
    - _Requirements: 13.1, 13.8_
  - [x] 1.2 Create `requirements.txt` with all Python dependencies: `fastapi`, `uvicorn`, `pydantic`, `langchain`, `langchain-community`, `langchain-google-genai`, `langchain-huggingface`, `langchain-openai`, `langchain-groq`, `chromadb`, `sentence-transformers`, `hypothesis`, `pytest`, `pytest-asyncio`, `httpx`, `python-dotenv`
    - _Requirements: 14.5_
  - [x] 1.3 Create `.env.example` with all environment variables documented: `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL_NAME`, `EMBEDDING_MODEL_NAME`, `SIMILARITY_THRESHOLD`, `CHROMA_PERSIST_DIR`, `SQLITE_DB_PATH`
    - _Requirements: 12.2, 21.1_
  - [x] 1.4 Initialize the React frontend with `package.json` including `react`, `react-dom`, `react-markdown`, and dev dependencies; create minimal `src/index.jsx` and `src/App.jsx` entry points
    - _Requirements: 13.4_

- [x] 2. Pydantic data models and calculation tool implementations
  - [x] 2.1 Create `backend/models.py` with `ChatRequest`, `ChatResponse`, `SourceReference`, and `HealthStatus` Pydantic models with validation constraints (message min_length=1, max_length=2000)
    - Include type hints and Google-style docstrings in Spanish
    - _Requirements: 3.1, 3.2, 14.1, 14.2_
  - [x] 2.2 Create calculation tool input/output Pydantic models in `agent/tools/` — `VATDiscountInput/Output`, `NetLiquidityInput/Output`, `InvestmentViabilityInput/Output`, `TaxLiabilityInput/Output`, `DepreciationInput/Output` with Field validators
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 14.1_
  - [x] 2.3 Implement `agent/tools/calculate_vat_discount.py`: compute `discount_amount = purchase_price * vat_rate`, `effective_cost = purchase_price - discount_amount`, return Spanish explanation. Handle invalid inputs (negative price, invalid rate) with descriptive Spanish error messages
    - _Requirements: 7.1, 7.6, 7.7_
  - [x] 2.4 Implement `agent/tools/calculate_net_liquidity.py`: compute `net_liquidity_now = balance - payables`, `net_liquidity_projected = balance - payables + receivables`, return Spanish explanation. Handle invalid inputs
    - _Requirements: 7.2, 7.6, 7.7_
  - [x] 2.5 Implement `agent/tools/assess_investment_viability.py`: compute `effective_cost`, `available_funds_now/projected`, `viable_now`, `viable_in_days` (funding gap / avg daily receivable inflow, rounded up). Handle invalid inputs
    - _Requirements: 7.3, 7.6, 7.7_
  - [x] 2.6 Implement `agent/tools/project_tax_liability.py`: compute `taxable_income = max(0, gross_income - deductions)`, `estimated_tax = taxable_income * tax_rate`, return Spanish explanation. Handle invalid inputs
    - _Requirements: 7.4, 7.6, 7.7_
  - [x] 2.7 Implement `agent/tools/calculate_depreciation.py`: compute `annual_depreciation = purchase_value / useful_life_years`, `accumulated = min(annual * years_elapsed, purchase_value)`, `current_value = purchase_value - accumulated` (never negative). Handle invalid inputs
    - _Requirements: 7.5, 7.6, 7.7_
  - [x] 2.8 Write property tests for calculation tools in `tests/test_calculation_tools.py`
    - **Property 1: VAT Discount Arithmetic Invariant** — verify `discount_amount + effective_cost == purchase_price` and `discount_amount == purchase_price * vat_rate` for any positive price and valid rate
    - **Validates: Requirements 7.1**
  - [x] 2.9 Write property test for net liquidity invariant
    - **Property 2: Net Liquidity Arithmetic Invariant** — verify `net_liquidity_now == balance - payables` and `net_liquidity_projected == balance - payables + receivables`
    - **Validates: Requirements 7.2**
  - [x] 2.10 Write property test for investment viability invariant
    - **Property 3: Investment Viability Arithmetic Invariant** — verify `effective_cost == purchase_cost - tax_benefit`, `available_funds_now == balance - payables`, `viable_now == (available_funds_now >= effective_cost)`
    - **Validates: Requirements 7.3**
  - [x] 2.11 Write property test for tax liability invariant
    - **Property 4: Tax Liability Arithmetic Invariant** — verify `taxable_income == max(0, gross_income - deductions)` and `estimated_tax == taxable_income * tax_rate`
    - **Validates: Requirements 7.4**
  - [x] 2.12 Write property test for depreciation invariant
    - **Property 5: Depreciation Arithmetic Invariant** — verify `annual_depreciation == purchase_value / useful_life_years`, `accumulated == min(annual * years_elapsed, purchase_value)`, `current_value >= 0`
    - **Validates: Requirements 7.5**
  - [x] 2.13 Write property test for invalid input rejection across all calculation tools
    - **Property 6: Calculation Tools Reject Invalid Inputs** — verify descriptive Spanish error message returned (no unhandled exceptions) for negative prices, zero useful_life_years, negative payables, etc.
    - **Validates: Requirements 7.6**

- [x] 3. Shared test fixtures and conftest
  - [x] 3.1 Create `tests/conftest.py` with shared pytest fixtures: temporary SQLite test database pre-populated with mock data, temporary ChromaDB test collection with sample embeddings, FastAPI TestClient instance
    - _Requirements: 14.5, 14.6_

- [x] 4. Checkpoint — Verify calculation tools
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Mock data generation and financial data retrieval tool
  - [x] 5.1 Implement `scripts/generate_mock_data.py`: verify `sqlite3` availability, create `fin.db` with 5 tables (`perfil_productor`, `movimientos`, `facturas_venta`, `cuentas_por_pagar`, `activos_fijos`) following the exact schemas from the design. Generate 1 producer profile, 30+ movements over 6 months, 15+ invoices (60/30/10% PAID/PENDING/OVERDUE ±5%), 10+ payables, 5-8 fixed assets with realistic Colombian agricultural data
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_
  - [x] 5.2 Implement `agent/tools/query_evergreen_finances.py`: accept `query_type` enum (`current_balance`, `recent_movements`, `pending_receivables`, `pending_payables`, `fixed_assets`, `expense_summary`, `producer_profile`) and optional `period_days`. Execute parameterized read-only SQL queries, return structured JSON with COP values. `current_balance` = sum(INGRESO) - sum(EGRESO). Default period = current quarter
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  - [x] 5.3 Write property test for mock data generation invariants in `tests/test_mock_data_generation.py`
    - **Property 11: Mock Data Generation Invariants** — verify row counts (30+ movimientos, 15+ facturas, 10+ payables, 5-8 assets), 6-month span, and PAID/PENDING/OVERDUE distribution within ±5% of 60/30/10%
    - **Validates: Requirements 9.2, 9.3, 9.4**
  - [x] 5.4 Write property test for financial data retrieval in `tests/test_query_finances.py`
    - **Property 8: Financial Data Retrieval Returns Valid JSON for All Query Types** — verify valid structured JSON with COP values for each of the 7 query types against a populated test database
    - **Validates: Requirements 6.1, 6.2, 6.4, 6.5**
  - [x] 5.5 Write unit tests for each query type in `tests/test_query_finances.py` with a pre-populated test database fixture
    - _Requirements: 14.5_

- [x] 6. Knowledge base documents and ETL pipeline
  - [x] 6.1 Create knowledge base Markdown documents in `knowledge_base/`: `beneficios_compra_maquinaria.md`, `exenciones_pequeno_productor.md`, `programas_gobierno_agro.md`, `calendario_tributario_2024.md`, `estatuto_tributario_libro1.md`, `estatuto_tributario_libro3.md`. Written in Spanish with `##`/`###` headers, article numbers, realistic percentages and thresholds
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 20.2_
  - [x] 6.2 Implement `scripts/init_chromadb.py`: initialize ChromaDB persistent collection with cosine similarity metric
    - _Requirements: 8.4_
  - [x] 6.3 Implement `scripts/etl_ingest.py`: read Markdown files from `knowledge_base/`, split with `RecursiveCharacterTextSplitter` (800 chars default, 10% overlap, separators `["\n## ", "\n### ", "\n\n", "\n", " "]`), preserve article numbers as metadata, generate embeddings via configurable `EMBEDDING_MODEL_NAME` (default `intfloat/multilingual-e5-small`), store in ChromaDB with metadata (`source_document`, `article_number`, `topic_tags`, `document_type`, `date_ingested`, `chunk_index`, `total_chunks_in_article`). Implement dedup by `source_document`. Log documents processed, chunks created, errors
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 21.1, 21.3_
  - [x] 6.4 Implement `agent/tools/get_tax_knowledge.py`: convert query to embedding using configured model, cosine similarity search on ChromaDB, return top 5 chunks with metadata (`article_number`, `source_document`, `topic_tags`), filter by `SIMILARITY_THRESHOLD` (default 0.35). Return empty result with descriptive message if no chunks pass threshold. Read-only access
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 21.1, 21.3_
  - [x] 6.5 Write property test for ETL chunking in `tests/test_etl_pipeline.py`
    - **Property 9: ETL Chunking Preserves Metadata and Respects Size Constraints** — verify chunks are 500-1000 chars, carry required metadata fields, and article numbers are preserved
    - **Validates: Requirements 8.2, 8.3, 8.4**
  - [x] 6.6 Write property test for ETL idempotence in `tests/test_etl_pipeline.py`
    - **Property 10: ETL Ingestion Idempotence** — verify running ETL twice on the same document produces no duplicate chunks
    - **Validates: Requirements 8.6**
  - [x] 6.7 Write property test for knowledge retrieval in `tests/test_get_tax_knowledge.py`
    - **Property 7: Knowledge Retrieval Returns Bounded Results with Metadata** — verify at most 5 chunks returned, each with required metadata, sorted by descending similarity, below-threshold chunks excluded
    - **Validates: Requirements 5.1, 5.2**

- [x] 7. Checkpoint — Verify ETL pipeline and retrieval tools
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. LLM provider abstraction and ReAct agent
  - [x] 8.1 Implement `agent/llm_providers.py` with Strategy pattern: base interface and concrete providers for `HuggingFaceProvider`, `GeminiProvider`, `ChatGPTProvider`, `GroqProvider`. Factory function reads `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL_NAME` from env. Default to HuggingFace. Fail with clear error if API key missing for providers that require it
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_
  - [x] 8.2 Create `agent/prompt.md` — system prompt in Spanish instructing the agent to: respond in Spanish, cite article numbers, format COP with thousand separators, include financial disclaimers, define scope (Colombian agricultural taxation, EverGreen data, basic accounting), list out-of-scope topics (stocks, health, politics, hardware, legal advice beyond tax)
    - _Requirements: 4.3, 4.8_
  - [x] 8.3 Implement `agent/agent_config.py`: create ReAct agent via `create_react_agent` with max 5 iterations, `handle_parsing_errors=True`, register all 7 tools, load system prompt from `prompt.md`. Wire the configured LLM provider
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 8.4 Create `agent/tools/__init__.py` exporting all 7 tools as LangChain-compatible tool definitions with proper names, descriptions, and input schemas
    - _Requirements: 4.2_

- [x] 9. FastAPI backend server
  - [x] 9.1 Implement `backend/app.py`: FastAPI application factory with startup event that initializes ChromaDB, SQLite, and LLM provider connections. If LLM unreachable → log warning, start in degraded mode. If API key missing → fail to start with clear error
    - _Requirements: 3.4, 3.5, 12.4_
  - [x] 9.2 Implement `backend/middleware.py`: CORS middleware allowing requests from `http://localhost:3000`
    - _Requirements: 3.6_
  - [x] 9.3 Implement `backend/routes.py`: `POST /api/v1/chat` endpoint — validate request via `ChatRequest` model, invoke ReAct agent, return `ChatResponse` with `response`, `sources`, `tools_used`. Implement session management: if `session_id` provided, maintain in-memory conversation history; otherwise single-turn. `GET /api/v1/health` endpoint returning `HealthStatus` with status of backend, vector_store, financial_database, llm_connection
    - _Requirements: 3.1, 3.2, 3.3, 3.7_
  - [x] 9.4 Write property test for API request validation in `tests/test_api_validation.py`
    - **Property 13: API Request Validation** — verify HTTP 422 with descriptive error for missing `message`, non-string `message`, empty `message`
    - **Validates: Requirements 3.2**
  - [x] 9.5 Write property test for session context preservation in `tests/test_session_management.py`
    - **Property 14: Session Context Preservation** — verify conversation history is maintained across messages with the same `session_id`
    - **Validates: Requirements 3.7**
  - [x] 9.6 Write unit tests for health endpoint and valid chat request/response cycle in `tests/test_api_validation.py`
    - _Requirements: 14.5_

- [x] 10. Checkpoint — Verify backend API and agent integration
  - Ensure all tests pass, ask the user if questions arise.

- [x] 11. React chat frontend
  - [x] 11.1 Implement `frontend/src/components/ChatUI.jsx`: main chat container with message thread, text input with 500-char soft limit character counter, submit button disabled when input is empty/whitespace, loading indicator while awaiting response
    - _Requirements: 1.1, 1.5, 1.8_
  - [x] 11.2 Implement `frontend/src/components/SuggestionChips.jsx`: display 3+ clickable example queries (e.g., "¿Qué beneficios tributarios tengo?", "¿Cómo está mi flujo de caja?", "¿Puedo comprar un tractor?"). Clicking populates input and auto-submits
    - _Requirements: 1.2, 1.3_
  - [x] 11.3 Implement `frontend/src/components/ResponseRenderer.jsx`: render markdown-formatted agent responses using `react-markdown`, display sources and tools_used metadata
    - _Requirements: 1.6_
  - [x] 11.4 Implement `frontend/src/components/Logo.jsx`: display FIN-Advisor logo in top-right; render placeholder SVG/text "FIN" if no logo file exists
    - _Requirements: 1.4_
  - [x] 11.5 Wire `App.jsx` to compose all components, connect to `POST /api/v1/chat` via fetch, handle network/HTTP errors with Spanish error message and retry button
    - _Requirements: 1.5, 1.6, 1.7_
  - [x] 11.6 Implement centered greeting display: "Hola, soy FIN Advisor." on one line and "¿En qué puedo ayudarte hoy?" on the next line
    - _Requirements: 1.1_

- [x] 12. Checkpoint — Verify frontend renders and communicates with backend
  - Ensure all tests pass, ask the user if questions arise.

- [x] 13. README files and project documentation
  - [x] 13.1 Create root `RAG-FIN-Topicos-Avanzados/README.md` in Spanish: project overview, setup instructions (Python deps, SQLite, Node.js), how to run each component (`uvicorn`, `npm start`), knowledge base setup section listing each document source and preparation steps, links to folder READMEs
    - _Requirements: 13.7, 13.9, 20.1, 20.3_
  - [x] 13.2 Create folder-level `README.md` files in Spanish for `agent/`, `backend/`, `frontend/`, `scripts/`, and `knowledge_base/` — each describing contents, how components work, relationships to other parts, and setup/run instructions
    - _Requirements: 13.6, 13.9_

- [x] 14. Kiro IDE integration — skills, steering files, and hooks
  - [x] 14.1 Create `.kiro/skills/fin-advisor-project-context.md` with YAML frontmatter (`name`, `description`) and body covering: project identity, architecture summary, folder structure, key technical decisions, environment variable reference, external document list
    - _Requirements: 22.1, 22.3, 22.4_
  - [x] 14.2 Create `.kiro/skills/fin-advisor-code-standards.md` with YAML frontmatter and body covering: Python code rules (type hints, docstrings, PEP 8, classes, Pydantic, parameterized SQL), testing requirements (unit + property-based), React/frontend rules, documentation rules, Docker conventions
    - _Requirements: 22.2, 22.3, 22.4_
  - [x] 14.3 Create steering files in `.kiro/steering/`: `agent-folder.md`, `backend-folder.md`, `frontend-folder.md`, `scripts-folder.md`, `knowledge-base-folder.md` — each with YAML frontmatter (`name`, `description`, `inclusion: fileMatch`, `fileMatchPattern`) and body describing folder purpose, module layout, relationships, and constraints
    - _Requirements: 23.1, 23.2, 23.3, 23.4, 23.5, 23.6_
  - [x] 14.4 Create Kiro hooks in `.kiro/hooks/`: `python-edit-lint.hook.json`, `python-create-check.hook.json`, `post-task-tests.hook.json`, `kb-markdown-lint.hook.json`, `docker-config-check.hook.json` — each following the required JSON schema with `name`, `version`, `description`, `when`, `then` fields
    - _Requirements: 24.1, 24.2, 24.3, 24.4, 24.5, 24.6_

- [x] 15. Docker Compose orchestration (optional)
  - [x] 15.1 Create `Dockerfile.frontend` (build React production bundle, serve on port 3000), `Dockerfile.backend` (install Python deps, run uvicorn on port 8000), and `docker-compose.yml` defining both services with port mappings and environment variable support
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [x] 16. Frontend input validation tests
  - [x] 16.1 Write tests for chat input validation in `tests/test_frontend_validation.py`
    - **Property 12: Chat Input Validation** — verify that empty/whitespace-only strings disable the submit button, strings exceeding 500 characters trigger the soft warning counter, and strings exceeding 2000 characters are rejected by the backend with HTTP 422
    - **Validates: Requirements 1.8**

- [x] 17. User story smoke tests and agent behavior validation
  - [x] 17.1 Write integration smoke tests in `tests/test_user_stories.py` that invoke the ReAct agent with representative queries for each user story and validate response structure and tool usage:
    - **US-01 (Tax Benefit Inquiry):** Query about tax benefits → verify `get_tax_knowledge` was invoked, response contains at least one article number, response includes a disclaimer
    - **US-02 (Cash Flow Diagnosis):** Query about cash flow → verify `query_evergreen_finances` was invoked with `recent_movements` or `current_balance`, response contains COP-formatted monetary figures
    - **US-03 (Fixed Asset Purchase):** Query about buying a tractor → verify `calculate_vat_discount` and `assess_investment_viability` were invoked, response states viability conclusion
    - **US-04 (Tax Calendar):** Query about upcoming tax deadlines → verify `query_evergreen_finances` with `producer_profile` and `get_tax_knowledge` were invoked, response contains chronological dates
    - **US-05 (Concept Explanation):** Query about a financial concept (e.g., "¿Qué es la depreciación?") → verify response is under 200 words for simple concepts, uses agricultural context
    - **US-06 (Expense Optimization):** Query about expense analysis → verify `query_evergreen_finances` with `expense_summary` was invoked, response identifies top expense categories
    - _Requirements: 15.1, 15.2, 15.3, 15.6, 16.1, 16.2, 16.3, 16.6, 17.1, 17.2, 17.3, 17.4, 17.6, 18.1, 18.2, 18.5, 19.1, 19.2, 19.5, 25.1, 25.2, 25.3, 25.6_
  - [x] 17.2 Write out-of-scope rejection test: send queries about stocks, health, politics → verify agent declines politely in Spanish and lists topics it can help with
    - _Requirements: 4.8_

- [x] 18. Performance benchmarks and non-functional validation
  - [x] 18.1 Write a performance benchmark script `tests/test_performance.py` that measures and logs response times for: a simple single-tool query (target ≤30s), a complex multi-tool query (target ≤45s). Log results as warnings if targets are exceeded (soft benchmarks, not hard failures). Verify the loading indicator remains active (no timeout disconnect) for long responses
    - _Requirements: 26.1, 26.2, 26.3, 26.4_

- [x] 19. Final checkpoint — Full integration verification
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation after each major component
- Property tests validate universal correctness properties from the design document (Properties 1-14)
- Unit tests validate specific examples and edge cases
- Requirements 2 (SSE streaming) and 11 (Docker) are deferred/optional per the requirements document
- User story requirements (15-19, 25) are validated via integration smoke tests in Task 17
- Performance benchmarks (Req 26) are soft targets validated in Task 18
- Shared test fixtures (conftest.py) are created early in Task 3 so all subsequent test tasks can use them
- All code, comments, docstrings, and documentation are in Spanish
- All implementation resides inside `RAG-FIN-Topicos-Avanzados/`
