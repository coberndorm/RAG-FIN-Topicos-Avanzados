# Requirements Document

## Introduction

FIN-Advisor is a RAG-based (Retrieval-Augmented Generation) AI financial assistant for Colombian agricultural producers, embedded in the EverGreen Finance (FIN) module. The system retrieves relevant tax law fragments from a vectorized knowledge base (ChromaDB), queries the user's real-time financial data from a SQLite database, and reasons over both data sources using a LangChain ReAct agent backed by an LLM (HuggingFace, Gemini, or ChatGPT) to produce personalized, grounded financial advice in Spanish. The system includes a React chat frontend, a FastAPI backend with standard HTTP request/response (SSE streaming deferred to Phase 2), a full ETL pipeline for knowledge base ingestion, optional Docker Compose orchestration, and synthetic mock data generation.

## Glossary

- **FIN_Advisor**: The complete RAG-based AI financial assistant system
- **Chat_Interface**: The React frontend component providing the conversational UI
- **Backend_API**: The FastAPI server that receives user queries and returns agent responses
- **ReAct_Agent**: The LangChain-based Reasoning and Acting agent that orchestrates tool calls and generates responses
- **Knowledge_Base**: The collection of tax law documents and agricultural benefit guides stored as embeddings in ChromaDB
- **Vector_Store**: ChromaDB instance storing document embeddings for semantic similarity search
- **Financial_Database**: The SQLite database containing mock EverGreen FIN module data (movements, invoices, payables, assets, producer profile)
- **ETL_Pipeline**: The Extract-Transform-Load pipeline that ingests documents, chunks them, generates embeddings, and stores them in ChromaDB
- **Calculation_Tools**: The five deterministic computation tools (VAT discount, net liquidity, investment viability, tax projection, depreciation). Note: the ReAct_Agent has 7 tools total (2 retrieval + 5 calculation)
- **SSE_Stream**: Server-Sent Events stream used to deliver incremental LLM responses to the frontend (Phase 2 — not required for MVP)
- **Embedding_Model**: The primary embedding model is `intfloat/multilingual-e5-small` (~134MB, optimized for Spanish/legal text). Alternatives: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (~120MB) or `intfloat/multilingual-e5-base` (~440MB, higher quality). All are free, unlimited, and ChromaDB-compatible
- **Project_Root**: All implementation lives inside the `RAG-FIN-Topicos-Avanzados/` directory, which is the Git repository root
- **Producer**: The primary user — a Colombian agricultural producer or farm administrator

## Requirements

### Requirement 1: Chat Interface Presentation

**User Story:** As a Producer, I want a simple, centered chat interface with a greeting and suggestion chips, so that I can quickly understand what FIN-Advisor does and start asking questions.

#### Acceptance Criteria

1. WHEN the Producer opens the Chat_Interface, THE Chat_Interface SHALL display a centered greeting with "Hola, soy FIN Advisor." on one line and "¿En qué puedo ayudarte hoy?" on the next line
2. WHEN the Chat_Interface loads, THE Chat_Interface SHALL display suggestion chips below the text input with at least 3 example queries relevant to agricultural finance (e.g., "¿Qué beneficios tributarios tengo?", "¿Cómo está mi flujo de caja?", "¿Puedo comprar un tractor?")
3. WHEN the Producer clicks a suggestion chip, THE Chat_Interface SHALL populate the text input with the chip's query text and submit it automatically
4. THE Chat_Interface SHALL display the FIN-Advisor logo in the top-right corner of the page. IF no logo file exists, THE Chat_Interface SHALL render a placeholder element (e.g., a styled text "FIN" or an SVG placeholder) in the logo position so it can be replaced later
5. WHEN the Producer submits a query, THE Chat_Interface SHALL display the user's message in the conversation thread and show a loading indicator while awaiting the response
6. WHEN the Backend_API returns a response, THE Chat_Interface SHALL render the complete response text in the conversation thread
7. IF the Backend_API request fails (network error or HTTP error), THEN THE Chat_Interface SHALL display an error message in Spanish and offer a retry option
8. THE Chat_Interface SHALL enforce a soft input length hint of 500 characters and display a character counter. THE Backend_API SHALL enforce a hard limit of 2000 characters via Pydantic validation. IF the input is empty or whitespace-only, THE Chat_Interface SHALL disable the submit button

### Requirement 2: Streaming Response Delivery (Phase 2 — Optional)

**User Story:** As a Producer, I want to see the assistant's response appear progressively as it is generated, so that I do not have to wait for the full response before reading.

**Note:** This requirement is deferred to Phase 2. For MVP, the Backend_API returns the complete response as a single JSON payload via `POST /api/v1/chat`. The acceptance criteria below define the Phase 2 target.

#### Acceptance Criteria

1. WHEN the Backend_API receives a chat request with `stream=true`, THE Backend_API SHALL open an SSE_Stream connection and send response tokens incrementally as the ReAct_Agent generates them
2. WHILE the ReAct_Agent is processing a query, THE Backend_API SHALL send periodic heartbeat events on the SSE_Stream to keep the connection alive
3. WHEN the ReAct_Agent completes its response, THE Backend_API SHALL send a final event on the SSE_Stream indicating completion, including metadata about sources and tools used
4. IF the ReAct_Agent encounters an error during processing, THEN THE Backend_API SHALL send an error event on the SSE_Stream with a descriptive message in Spanish
5. THE Backend_API SHALL continue to support the non-streaming `POST /api/v1/chat` endpoint (MVP default) that returns the complete response as a single JSON payload

### Requirement 3: FastAPI Backend API

**User Story:** As a developer, I want a well-structured FastAPI backend with documented endpoints, so that the frontend can communicate reliably with the agent.

#### Acceptance Criteria

1. THE Backend_API SHALL expose a `POST /api/v1/chat` endpoint that accepts a JSON body with `message` (string, required) and `session_id` (string, optional) fields. This is the single chat endpoint; for MVP it returns a complete JSON response `{ "response": "string", "sources": [...], "tools_used": [...] }`
2. THE Backend_API SHALL validate incoming requests using Pydantic models and return HTTP 422 with descriptive errors for invalid payloads
3. THE Backend_API SHALL expose a `GET /api/v1/health` endpoint that returns a JSON object with keys `backend`, `vector_store`, `financial_database`, and `llm_connection`, each with a value of `"ok"`, `"degraded"`, or `"unavailable"`
4. WHEN the Backend_API starts, THE Backend_API SHALL initialize connections to the Vector_Store, Financial_Database, and the configured LLM provider
5. IF the LLM provider is unreachable at startup, THEN THE Backend_API SHALL log a warning and start in degraded mode, returning an appropriate error when chat requests are received
6. THE Backend_API SHALL include CORS middleware configured to allow requests from the Chat_Interface origin
7. WHEN a `session_id` is provided in the chat request, THE Backend_API SHALL maintain conversation context (message history) within that session for multi-turn interactions. Session context SHALL be stored in-memory (no cross-restart persistence required for MVP). IF no `session_id` is provided, THE Backend_API SHALL treat the request as a single-turn interaction

### Requirement 4: LangChain ReAct Agent

**User Story:** As a Producer, I want the assistant to reason about my query and decide which data sources and calculations to use, so that I receive accurate, personalized financial advice.

#### Acceptance Criteria

1. THE ReAct_Agent SHALL be implemented using LangChain `create_react_agent` with a maximum of 5 reasoning iterations per query
2. THE ReAct_Agent SHALL have access to 7 tools: get_tax_knowledge, query_evergreen_finances, calculate_vat_discount, calculate_net_liquidity, assess_investment_viability, project_tax_liability, and calculate_depreciation
3. THE ReAct_Agent SHALL use a system prompt that instructs it to respond in Spanish, cite article numbers when referencing tax laws, format monetary values as COP with thousand separators, and include disclaimers for financial advice. The system prompt SHALL define the agent's scope boundaries (Colombian agricultural taxation, EverGreen financial data, basic accounting concepts) and explicitly list out-of-scope topics (stocks, health, politics, hardware support, legal advice beyond tax). See `RAG-FIN-Topicos-Avanzados/project_documentation/08-AGENT-AND-TOOLS.md` for the full system prompt reference
4. WHEN the ReAct_Agent receives a query about tax laws or exemptions, THE ReAct_Agent SHALL invoke the get_tax_knowledge tool before generating a response
5. WHEN the ReAct_Agent receives a query about the Producer's financial data, THE ReAct_Agent SHALL invoke the query_evergreen_finances tool before generating a response
6. WHEN the ReAct_Agent receives a query requiring mathematical computation, THE ReAct_Agent SHALL use the appropriate Calculation_Tools instead of performing arithmetic within the LLM
7. IF the ReAct_Agent reaches the maximum iteration limit, THEN THE ReAct_Agent SHALL return the best available answer with a note indicating that the analysis may be incomplete
8. WHEN the Producer asks a question outside the defined scope (stocks, health, politics), THE ReAct_Agent SHALL politely decline in Spanish and list the topics it can help with

### Requirement 5: Knowledge Base Retrieval Tool (get_tax_knowledge)

**User Story:** As a Producer, I want the assistant to retrieve relevant tax law fragments when I ask about tax benefits, so that the advice I receive is grounded in actual legislation.

#### Acceptance Criteria

1. WHEN the get_tax_knowledge tool receives a search query, THE get_tax_knowledge tool SHALL convert the query to an embedding using the configured Embedding_Model (`intfloat/multilingual-e5-small` by default) and perform a cosine similarity search on the Vector_Store
2. THE get_tax_knowledge tool SHALL return the top 5 most similar document chunks along with metadata including article_number, source_document, and topic_tags
3. IF no chunks exceed the similarity threshold (default cosine similarity score of 0.35, configurable via `SIMILARITY_THRESHOLD` environment variable), THEN THE get_tax_knowledge tool SHALL return an empty result with a message indicating no relevant information was found
4. THE get_tax_knowledge tool SHALL have read-only access to the Vector_Store

### Requirement 6: Financial Data Retrieval Tool (query_evergreen_finances)

**User Story:** As a Producer, I want the assistant to access my financial records from EverGreen, so that the advice is based on my actual financial situation.

#### Acceptance Criteria

1. THE query_evergreen_finances tool SHALL accept a structured input with `query_type` (enum: `current_balance`, `recent_movements`, `pending_receivables`, `pending_payables`, `fixed_assets`, `expense_summary`, `producer_profile`) and an optional `period_days` (integer, default: current quarter) parameter. The `current_balance` query type SHALL be computed as the sum of all INGRESO amounts minus the sum of all EGRESO amounts from the `movimientos` table within the specified period
2. WHEN the query_evergreen_finances tool receives a query, THE query_evergreen_finances tool SHALL execute a parameterized SQL query against the Financial_Database and return structured JSON results
3. THE query_evergreen_finances tool SHALL have strictly read-only access to the Financial_Database
4. WHEN a period is not specified in the query, THE query_evergreen_finances tool SHALL default to the current quarter
5. THE query_evergreen_finances tool SHALL return all monetary values in COP

### Requirement 7: Calculation Tools

**User Story:** As a Producer, I want the assistant to perform precise financial calculations, so that I can trust the numbers in the advice I receive.

#### Acceptance Criteria

1. THE calculate_vat_discount tool SHALL accept purchase_price (decimal) and vat_rate (decimal, default 0.19) and return discount_amount, effective_cost, and a Spanish explanation
2. THE calculate_net_liquidity tool SHALL accept balance, receivables, and payables (all decimal) and return net_liquidity_now, net_liquidity_projected, and a Spanish explanation
3. THE assess_investment_viability tool SHALL accept balance, receivables, payables, purchase_cost (all decimal, required), and tax_benefit (decimal, optional, default 0) and return effective_cost, available_funds_now, available_funds_projected, viable_now (boolean), viable_in_days (integer), and a Spanish explanation. The `viable_in_days` value SHALL be estimated as 0 if `viable_now` is true; otherwise, it SHALL be calculated based on the ratio of the funding gap (`effective_cost - available_funds_now`) to the average daily receivable inflow (total `receivables` divided by 30 days), rounded up to the nearest integer
4. THE project_tax_liability tool SHALL accept gross_income, deductions, and tax_rate (all decimal) and return taxable_income, estimated_tax, and a Spanish explanation
5. THE calculate_depreciation tool SHALL accept purchase_value (decimal), useful_life_years (integer), and years_elapsed (decimal) and return annual_depreciation, accumulated_depreciation, current_value, and a Spanish explanation
6. IF any Calculation_Tools receives invalid input (negative values, zero useful_life_years, missing required fields), THEN THE Calculation_Tools SHALL return a descriptive error message in Spanish instead of a result
7. THE Calculation_Tools SHALL perform all computations deterministically without invoking the LLM

### Requirement 8: ETL Pipeline for Knowledge Base Ingestion

**User Story:** As a developer, I want an automated ETL pipeline that ingests knowledge base documents into ChromaDB, so that the retrieval tool has access to up-to-date tax law and benefit information.

#### Acceptance Criteria

1. THE ETL_Pipeline SHALL accept Markdown files from a designated knowledge base directory as input
2. WHEN the ETL_Pipeline processes a document, THE ETL_Pipeline SHALL split the document into chunks using RecursiveCharacterTextSplitter with a default chunk size of 800 characters (acceptable range: 500-1000 characters) and 10% overlap, using separators `["\n## ", "\n### ", "\n\n", "\n", " "]`
3. WHEN the ETL_Pipeline generates chunks, THE ETL_Pipeline SHALL preserve article numbers as metadata and avoid splitting mid-sentence within legal articles
4. THE ETL_Pipeline SHALL generate embeddings for each chunk using the Embedding_Model (`intfloat/multilingual-e5-small` as primary, with `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` and `intfloat/multilingual-e5-base` as configurable alternatives) and store them in the Vector_Store with metadata including source_document, article_number, topic_tags, document_type, date_ingested, chunk_index, and total_chunks_in_article
5. WHEN the ETL_Pipeline completes ingestion, THE ETL_Pipeline SHALL log the total number of documents processed, chunks created, and any errors encountered
6. IF a document has already been ingested (based on source_document metadata), THEN THE ETL_Pipeline SHALL skip or update the existing chunks rather than creating duplicates
7. THE ETL_Pipeline SHALL be executable as a standalone script from the `scripts/` directory

### Requirement 9: Mock Financial Data Generation

**User Story:** As a developer, I want a script that generates realistic synthetic financial data for the EverGreen FIN module, so that the system can be demonstrated without real financial records.

#### Acceptance Criteria

1. THE mock data generation script SHALL create a SQLite database with 5 tables: movimientos, facturas_venta, cuentas_por_pagar, activos_fijos, and perfil_productor. Column schemas for each table are defined in `RAG-FIN-Topicos-Avanzados/project_documentation/09-DATA-REQUIREMENTS.md` and SHALL be followed exactly
2. THE mock data generation script SHALL generate at least 30 movement records covering 6 months with realistic income categories (Venta cosecha, Venta ganado, Subsidio gobierno) and expense categories (Semillas, Abono/Fertilizante, Combustible, Mano de obra, Servicios públicos, Mantenimiento maquinaria, Transporte)
3. THE mock data generation script SHALL generate at least 15 sales invoice records with a distribution of 60% (±5%) PAID, 30% (±5%) PENDING, and 10% (±5%) OVERDUE
4. THE mock data generation script SHALL generate at least 10 accounts payable records and 5-8 fixed asset records with realistic Colombian agricultural data
5. THE mock data generation script SHALL generate 1 producer profile record with activity_type, nit, and tax_bracket fields populated
6. THE mock data generation script SHALL be executable as a standalone script from the `scripts/` directory and produce a `fin.db` SQLite file
7. THE mock data generation script SHALL verify that the Python `sqlite3` module is importable at the start, and if it is not available (e.g., a custom Python build without SQLite support), SHALL print clear instructions for the user's OS before exiting
8. THE project's `requirements.txt` (or equivalent) SHALL list all Python dependencies needed to interact with SQLite, including any ORM or driver packages if used beyond the built-in `sqlite3` module

### Requirement 10: Knowledge Base Document Creation

**User Story:** As a developer, I want a set of realistic knowledge base documents about Colombian agricultural tax law and benefits, so that the RAG pipeline has meaningful content to retrieve.

#### Acceptance Criteria

1. THE Knowledge_Base SHALL include at least 3 Markdown documents covering: agricultural machinery purchase benefits, small producer tax exemptions, and government agricultural programs
2. THE Knowledge_Base documents SHALL be written in Spanish with clear section headers (## and ###) suitable for effective chunking
3. THE Knowledge_Base documents SHALL include specific article numbers from the Estatuto Tributario, realistic percentages, monetary thresholds, and conditions
4. THE Knowledge_Base documents SHALL be stored in a designated `knowledge_base/` directory

### Requirement 11: Docker Compose Orchestration (Optional — Convenience)

**User Story:** As a developer, I want both the frontend and backend to be Dockerized and orchestrated with Docker Compose, so that the entire system can be started with a single command.

**Note:** Docker is not required for MVP. The system SHALL be runnable without Docker (direct `npm start` + `uvicorn` commands). Docker Compose is provided as a convenience for reproducible environments.

#### Acceptance Criteria

1. THE FIN_Advisor SHALL include a Dockerfile for the Chat_Interface (React frontend) that builds and serves the production bundle
2. THE FIN_Advisor SHALL include a Dockerfile for the Backend_API (FastAPI) that installs all Python dependencies and runs the server
3. THE FIN_Advisor SHALL include a `docker-compose.yml` file that defines services for the frontend and backend with appropriate port mappings (frontend on port 3000, backend on port 8000)
4. WHEN `docker-compose up` is executed, THE FIN_Advisor SHALL start both services and the Chat_Interface SHALL be able to communicate with the Backend_API
5. THE docker-compose configuration SHALL support environment variables for LLM provider selection and API keys

### Requirement 12: LLM Provider Configuration

**User Story:** As a developer, I want to configure the LLM provider (HuggingFace, Gemini API, or ChatGPT API) via environment variables, so that the system can switch between providers without code changes.

#### Acceptance Criteria

1. THE ReAct_Agent SHALL support four LLM provider options: HuggingFace (default), Gemini API (recommended for university), ChatGPT API, and Groq API
2. WHEN the Backend_API starts, THE Backend_API SHALL read the LLM provider configuration from environment variables (LLM_PROVIDER, LLM_API_KEY, LLM_MODEL_NAME)
3. IF the LLM_PROVIDER environment variable is not set, THEN THE Backend_API SHALL default to HuggingFace as the provider
4. IF the configured LLM provider requires an API key and the LLM_API_KEY is not set, THEN THE Backend_API SHALL fail to start with a clear error message indicating which API key is missing
5. THE Backend_API SHALL abstract the LLM provider behind a common interface (Strategy pattern) so that switching providers does not require changes to the ReAct_Agent or tool implementations
6. THE project SHALL include reference code in `scripts/llm_provider_reference.py` (provider factory functions with cost analysis) and `scripts/react_agent_reference.py` (ReAct agent setup with tool registration) for implementation guidance

### Requirement 13: Project Folder Structure

**User Story:** As a developer, I want a well-organized project folder structure, so that the codebase is maintainable and each component has a clear location.

#### Acceptance Criteria

1. THE FIN_Advisor project SHALL organize code into four top-level directories: `agent/` (agent implementation, system prompt, tools, LangChain ReAct agent), `frontend/` (React chat interface), `backend/` (FastAPI server), and `scripts/` (ETL ingestion, ChromaDB setup, mock data generation)
2. THE `agent/` directory SHALL contain the system prompt definition, tool implementations, and ReAct agent configuration as separate modules
3. THE `backend/` directory SHALL contain the FastAPI application, route definitions, Pydantic models, and middleware configuration
4. THE `frontend/` directory SHALL contain the React application with components for the chat interface, suggestion chips, and response rendering
5. THE `scripts/` directory SHALL contain standalone executable scripts for knowledge base ingestion, mock data generation, and ChromaDB initialization
6. EACH top-level directory (`agent/`, `frontend/`, `backend/`, `scripts/`, `knowledge_base/`) SHALL contain a `README.md` file written in Spanish describing: what the folder contains, how its components work, how it relates to other parts of the project, and any setup or run instructions specific to that folder
7. THE project root (`RAG-FIN-Topicos-Avanzados/`) SHALL contain a comprehensive `README.md` written in Spanish with project overview, setup instructions (including SQLite and Python dependency installation), how to run each component, and links to each folder's README
8. ALL implementation code, configuration files, Dockerfiles, and scripts SHALL reside inside the `RAG-FIN-Topicos-Avanzados/` directory, which is the Git repository root
9. ALL README.md files and project documentation (including code comments and docstrings) SHALL be written in Spanish, consistent with the application's target audience and the university project context

### Requirement 14: Code Quality Standards

**User Story:** As a developer, I want the codebase to follow consistent quality standards, so that the code is readable, maintainable, and testable.

#### Acceptance Criteria

1. THE FIN_Advisor codebase SHALL include type hints on all function parameters and return values in Python code
2. THE FIN_Advisor codebase SHALL include Google-style docstrings in Spanish on all public functions and classes
3. THE FIN_Advisor codebase SHALL follow PEP 8 formatting conventions
4. THE FIN_Advisor codebase SHALL use classes and inheritance where appropriate for tool definitions and data models
5. THE FIN_Advisor codebase SHALL include unit tests (using `pytest`) for each Calculation_Tools function, each query type in query_evergreen_finances, and the ETL_Pipeline chunking logic. Test files SHALL reside in a `tests/` directory at the project root, mirroring the source structure (e.g., `tests/test_calculation_tools.py`, `tests/test_query_finances.py`, `tests/test_etl_pipeline.py`)
6. THE FIN_Advisor codebase SHALL include property-based tests (using `hypothesis`) for Calculation_Tools to verify the correctness properties defined in the design document (Properties 1-6), including arithmetic invariants for all five calculation tools and invalid input rejection

### Requirement 15: User Story — Tax Benefit Inquiry (US-01)

**User Story:** As a Producer, I want to ask the assistant about tax benefits applicable to my type of agricultural operation, so that I can take advantage of deductions and exemptions I might not be aware of.

#### Acceptance Criteria

1. WHEN the Producer asks about tax benefits, THE ReAct_Agent SHALL invoke get_tax_knowledge to retrieve at least one relevant article from the Estatuto Tributario
2. WHEN the ReAct_Agent generates a tax benefit response, THE ReAct_Agent SHALL include the specific article number(s) referenced
3. THE ReAct_Agent SHALL explain the benefit in plain language understandable by a farm administrator
4. WHEN the Producer's activity type is available in the Financial_Database, THE ReAct_Agent SHALL personalize the response to the Producer's agricultural sector
5. IF the Producer's activity type is not available, THEN THE ReAct_Agent SHALL explicitly state this limitation in the response
6. THE ReAct_Agent SHALL include a disclaimer recommending professional validation for tax decisions

### Requirement 16: User Story — Cash Flow Diagnosis (US-02)

**User Story:** As a farm administrator, I want to ask the assistant to explain my current cash flow situation, so that I can understand why my available balance is what it is and plan accordingly.

#### Acceptance Criteria

1. WHEN the Producer asks about cash flow, THE ReAct_Agent SHALL invoke query_evergreen_finances to retrieve recent financial movements
2. THE ReAct_Agent SHALL identify the top 3 contributors to the cash flow change in the response
3. THE ReAct_Agent SHALL include actual monetary figures from the Producer's data in COP format
4. THE ReAct_Agent SHALL provide a semantic explanation of causes, not just a list of transactions
5. WHEN historical data exists for a previous period, THE ReAct_Agent SHALL include a comparison to the previous period
6. THE ReAct_Agent SHALL suggest actionable next steps in the response

### Requirement 17: User Story — Fixed Asset Purchase Viability (US-03)

**User Story:** As a Producer, I want to ask the assistant whether I can afford to buy a specific piece of equipment right now, so that I can make an informed investment decision without compromising my operation's liquidity.

#### Acceptance Criteria

1. WHEN the Producer asks about purchasing a fixed asset, THE ReAct_Agent SHALL retrieve the Producer's current balance, receivables, and payables from the Financial_Database
2. THE ReAct_Agent SHALL check the Knowledge_Base for applicable tax benefits on the asset type
3. THE ReAct_Agent SHALL invoke calculate_vat_discount and assess_investment_viability to compute the financial analysis
4. THE ReAct_Agent SHALL clearly state whether the purchase is viable at the current time
5. IF the purchase is not viable now, THEN THE ReAct_Agent SHALL suggest an estimated viable date based on projected receivables
6. THE ReAct_Agent SHALL quantify any applicable tax benefit in COP and include the assumptions used in the calculation

### Requirement 18: User Story — Accounting Concept Explanation (US-05)

**User Story:** As a Producer with limited accounting knowledge, I want to ask the assistant to explain financial or tax concepts in simple terms, so that I can better understand my own financial reports and obligations.

#### Acceptance Criteria

1. WHEN the Producer asks about a financial or tax concept, THE ReAct_Agent SHALL explain the concept without using unexplained jargon
2. THE ReAct_Agent SHALL make the explanation relevant to the agricultural context
3. WHEN the Producer has related data in the Financial_Database, THE ReAct_Agent SHALL include a concrete example from the Producer's data
4. IF no relevant Producer data exists, THEN THE ReAct_Agent SHALL provide a generic agricultural example
5. THE ReAct_Agent SHALL keep concept explanations concise, under 200 words for simple concepts

### Requirement 19: User Story — Expense Optimization (US-06)

**User Story:** As a farm administrator, I want to ask the assistant to analyze my recent expenses and suggest areas where I could save money, so that I can improve the profitability of my agricultural operation.

#### Acceptance Criteria

1. WHEN the Producer asks about expense optimization, THE ReAct_Agent SHALL retrieve and categorize the Producer's expenses from the Financial_Database
2. THE ReAct_Agent SHALL present at least the top 3 expense categories with their amounts
3. THE ReAct_Agent SHALL flag categories with disproportionate spending (above 40% of total expenses)
4. WHEN expenses qualify for tax deductions, THE ReAct_Agent SHALL mention the applicable deductions
5. THE ReAct_Agent SHALL provide actionable recommendations specific to the agricultural context
6. THE ReAct_Agent SHALL not recommend specific vendors or products in the response

### Requirement 20: External Document Sourcing

**User Story:** As a developer, I need to know exactly which external documents to download or source for the knowledge base, so that I can prepare them before running the ETL pipeline.

#### Acceptance Criteria

1. THE project documentation SHALL list the following documents that the developer must manually source and place in the `knowledge_base/` directory before running the ETL pipeline:
   - **Estatuto Tributario Nacional (Colombia)**: Download from the DIAN official portal (https://www.dian.gov.co/) or the Secretaría del Senado (https://www.secretariasenado.gov.co/). Focus on: Book I (Income Tax, agricultural sections — Art. 23, Art. 57-1) and Book III (VAT — Art. 258-1, VAT exemptions on agricultural inputs). Convert relevant sections from PDF to Markdown
   - **Calendario Tributario DIAN 2024/2025**: Available from https://www.dian.gov.co/. Contains filing deadlines by NIT bracket
   - **MinAgricultura guidelines on agricultural benefits**: Reference material from https://www.minagricultura.gov.co/ for creating the mock benefit guides (DOC-03 to DOC-06)
2. THE Knowledge_Base documents that are team-created (benefit guides, exemption guides, government programs) SHALL be clearly marked as mock/simplified versions inspired by real policy, not verbatim copies
3. THE project README SHALL include a "Knowledge Base Setup" section listing each document, where to find it, and how to prepare it for ingestion

### Requirement 21: Embedding Model Configuration

**User Story:** As a developer, I want the embedding model to be configurable so that I can switch between recommended models without code changes.

#### Acceptance Criteria

1. THE ETL_Pipeline and get_tax_knowledge tool SHALL read the embedding model name from an environment variable (`EMBEDDING_MODEL_NAME`, default: `intfloat/multilingual-e5-small`)
2. THE system SHALL support three embedding model options: `intfloat/multilingual-e5-small` (primary, ~134MB), `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (alternative, ~120MB), and `intfloat/multilingual-e5-base` (premium, ~440MB)
3. THE ETL_Pipeline SHALL use the same embedding model for both ingestion and query-time retrieval to ensure vector compatibility
4. THE project SHALL include a reference code snippet in `scripts/embedding_reference.py` demonstrating how to load and use each supported embedding model

### Requirement 22: Kiro Skills for Cross-Session Context

**User Story:** As a developer working across multiple chat sessions, I want Kiro to retain key project context (architecture, conventions, folder layout, tech decisions) so that every session starts with full awareness of the FIN-Advisor project.

#### Acceptance Criteria

1. THE project SHALL include a Kiro skill file at `.kiro/skills/fin-advisor-project-context.md` containing: project identity (name, repo root, type), architecture summary (frontend, backend, agent, vector store, database, LLM providers, embedding model), folder structure with descriptions, key technical decisions, environment variable reference, and the list of external documents the user must source
2. THE project SHALL include a Kiro skill file at `.kiro/skills/fin-advisor-code-standards.md` containing: Python code rules (type hints, docstrings, PEP 8, classes/inheritance, design patterns, Pydantic, parameterized SQL, read-only DB access), testing requirements (unit tests per function, property-based tests for calculation tools with specific invariants), React/frontend rules, documentation rules (README per folder), and Docker conventions
3. EACH skill file SHALL be written so that Kiro can load it at the start of any session and immediately understand the project's constraints, conventions, and structure without re-reading the full spec
4. EACH skill file SHALL include a YAML frontmatter block at the top with at minimum `name` and `description` fields, e.g.:
   ```yaml
   ---
   name: fin-advisor-project-context
   description: Core project context for the FIN-Advisor RAG system including architecture, folder layout, tech decisions, and environment variables
   ---
   ```

### Requirement 23: Kiro Steering Files for Folder-Level Guidance

**User Story:** As a developer, I want Kiro to automatically load detailed guidance about a specific folder when I'm working on files inside it, so that code generation follows the correct patterns and relationships for that part of the project.

#### Acceptance Criteria

1. THE project SHALL include a steering file at `.kiro/steering/agent-folder.md` with a YAML frontmatter block containing `inclusion: fileMatch` and `fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/agent/**'` plus `name` and `description` fields. The body describes: the agent folder's purpose (LangChain ReAct agent, system prompt, 7 tools), module layout (separate files for prompt, each tool, agent config), how the agent connects to the backend (imported by FastAPI routes), how tools access ChromaDB and SQLite, the Strategy pattern for LLM providers, and the 5-iteration max constraint. Example frontmatter:
   ```yaml
   ---
   name: agent-folder
   description: Guidance for the agent/ folder — LangChain ReAct agent, system prompt, tools, and LLM provider abstraction
   inclusion: fileMatch
   fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/agent/**'
   ---
   ```
2. THE project SHALL include a steering file at `.kiro/steering/backend-folder.md` with a YAML frontmatter block containing `name`, `description`, `inclusion: fileMatch`, and `fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/backend/**'` that describes: the backend folder's purpose (FastAPI server), module layout (app, routes, models, middleware), standard HTTP request/response for MVP (SSE streaming deferred to Phase 2), CORS configuration, health endpoint, how it initializes and calls the ReAct agent, Pydantic model conventions, and the relationship to the agent folder
3. THE project SHALL include a steering file at `.kiro/steering/frontend-folder.md` with a YAML frontmatter block containing `name`, `description`, `inclusion: fileMatch`, and `fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/frontend/**'` that describes: the frontend folder's purpose (React chat interface), component structure (chat UI, suggestion chips, response renderer, logo placeholder), how it connects to the backend via standard HTTP requests (SSE deferred to Phase 2), error handling for failed requests, input validation (2000-char backend limit, 500-char soft frontend hint), and styling approach
4. THE project SHALL include a steering file at `.kiro/steering/scripts-folder.md` with a YAML frontmatter block containing `name`, `description`, `inclusion: fileMatch`, and `fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/scripts/**'` that describes: the scripts folder's purpose (standalone utilities), each script's role (ETL ingestion, mock data generation, ChromaDB init, embedding reference, LLM provider reference, ReAct agent reference), how the ETL pipeline uses RecursiveCharacterTextSplitter and the configured embedding model, the SQLite schema for mock data, and how scripts relate to the agent and backend
5. THE project SHALL include a steering file at `.kiro/steering/knowledge-base-folder.md` with a YAML frontmatter block containing `name`, `description`, `inclusion: fileMatch`, and `fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/knowledge_base/**'` that describes: the knowledge base folder's purpose (Markdown source documents for RAG), the expected document list (Estatuto Tributario sections, benefit guides, tax calendar), formatting rules for effective chunking (section headers, article numbers preserved), metadata schema, and the relationship to the ETL pipeline
6. EVERY steering file SHALL include a complete YAML frontmatter block with at minimum: `name`, `description`, and `inclusion` (plus `fileMatchPattern` when `inclusion: fileMatch`). Missing frontmatter will cause the steering file to fail to load

### Requirement 24: Kiro Hooks for Automated Quality Enforcement

**User Story:** As a developer, I want automated checks to run whenever I edit or create files, so that the project stays consistent with the requirements without manual intervention.

#### Acceptance Criteria

1. THE project SHALL include a Kiro hook (`python-edit-lint.hook.json`) that triggers on Python file edits (`*.py`) inside `RAG-FIN-Topicos-Avanzados/` and asks the agent to verify: type hints are present on all function parameters and return values, Google-style docstrings in Spanish exist on public functions/classes, and PEP 8 formatting is followed. The hook JSON SHALL include `name`, `version`, `description`, `when.type`, `when.patterns`, and `then.type`/`then.prompt` fields
2. THE project SHALL include a Kiro hook (`python-create-check.hook.json`) that triggers on Python file creation (`*.py`) inside `RAG-FIN-Topicos-Avanzados/` and asks the agent to verify the new file includes proper module-level docstring in Spanish, follows the project's class/inheritance conventions, and has corresponding test stubs created. The hook JSON SHALL include `name`, `version`, `description`, `when.type`, `when.patterns`, and `then.type`/`then.prompt` fields
3. THE project SHALL include a Kiro hook (`post-task-tests.hook.json`) that triggers after each spec task is completed (`postTaskExecution`) and runs the project's test suite (`pytest`) to verify nothing is broken. The hook JSON SHALL include `name`, `version`, `description`, `when.type`, and `then.type`/`then.command` fields
4. THE project SHALL include a Kiro hook (`kb-markdown-lint.hook.json`) that triggers on Markdown file edits (`*.md`) inside `RAG-FIN-Topicos-Avanzados/knowledge_base/` and asks the agent to verify the document follows the chunking-friendly format (proper section headers, article numbers preserved, Spanish content). The hook JSON SHALL include `name`, `version`, `description`, `when.type`, `when.patterns`, and `then.type`/`then.prompt` fields
5. THE project SHALL include a Kiro hook (`docker-config-check.hook.json`) that triggers on Dockerfile or docker-compose.yml edits and asks the agent to verify the configuration is consistent with the project's port mappings (frontend 3000, backend 8000) and environment variable conventions. The hook JSON SHALL include `name`, `version`, `description`, `when.type`, `when.patterns`, and `then.type`/`then.prompt` fields
6. EVERY Kiro hook file SHALL follow this required JSON schema:
   ```json
   {
     "name": "string (required)",
     "version": "string (required, e.g. 1.0.0)",
     "description": "string (optional but recommended)",
     "when": {
       "type": "fileEdited | fileCreated | postTaskExecution | ...",
       "patterns": ["array of glob patterns (required for file events)"]
     },
     "then": {
       "type": "askAgent | runCommand",
       "prompt": "string (required for askAgent)",
       "command": "string (required for runCommand)"
     }
   }
   ```

### Requirement 25: User Story — Personalized Tax Calendar (US-04)

**User Story:** As a farm administrator, I want to receive a personalized tax calendar based on my operation's obligations, so that I never miss a filing deadline and can plan my cash reserves accordingly.

#### Acceptance Criteria

1. WHEN the Producer asks about upcoming tax deadlines, THE ReAct_Agent SHALL invoke query_evergreen_finances with `query_type: producer_profile` to identify the Producer's NIT bracket and tax obligations
2. THE ReAct_Agent SHALL invoke get_tax_knowledge to retrieve the official tax calendar from the Knowledge_Base
3. THE ReAct_Agent SHALL present at least the Producer's income tax and VAT obligations in chronological order, covering at least the next 3 months
4. EACH calendar entry SHALL include: date, obligation name, and estimated amount (if calculable from the Producer's financial data)
5. WHEN the Producer's projected balance on a deadline date is insufficient to cover the estimated obligation, THE ReAct_Agent SHALL flag that entry with a liquidity warning. The projected balance SHALL be calculated as: current balance + receivables due before the deadline date - payables due before the deadline date
6. THE ReAct_Agent SHALL specify that only national (DIAN) obligations are covered; municipal taxes are out of scope
7. THE ReAct_Agent SHALL invoke project_tax_liability when estimating tax amounts for calendar entries

### Requirement 26: Non-Functional Requirements — Performance

**User Story:** As a Producer, I want the assistant to respond within a reasonable time, so that the interaction feels conversational and I don't lose context while waiting.

#### Acceptance Criteria

1. THE FIN_Advisor SHALL target responses for simple queries (single tool call) within 30 seconds. These are soft performance benchmarks for demo purposes, not hard timeouts
2. THE FIN_Advisor SHALL target responses for complex queries (multi-tool calls, e.g., investment viability) within 45 seconds. These are soft performance benchmarks for demo purposes, not hard timeouts
3. THE FIN_Advisor SHALL target single-user operation for MVP; concurrent multi-user support is not required
4. IF a response exceeds the expected time, THE Chat_Interface SHALL continue displaying the loading indicator (no timeout disconnect for MVP)
