# FIN-Advisor: Project Overview

## Project Name
**Asistente Inteligente de Optimización Tributaria y Flujo de Caja (FIN-Advisor)**

## Context
EverGreen is a mock agricultural management platform used as a case study. The Finance (FIN) module currently handles invoicing, accounts payable/receivable, and taxation records. However, it lacks any intelligent decision-support capability — producers must manually interpret complex tax regulations and make financial decisions without data-driven guidance.

## Problem Statement
Colombian agricultural producers face three recurring challenges within the FIN module:

1. **Tax Complexity:** The Colombian Estatuto Tributario contains sector-specific exemptions and deductions (e.g., VAT discounts on capital goods for agriculture) that are difficult to interpret without professional advice.
2. **Cash Flow Blindness:** Producers register transactions but lack tools to understand the *why* behind their cash flow behavior or to project future liquidity.
3. **Investment Timing:** Deciding when to purchase fixed assets (tractors, harvesters, irrigation systems) requires cross-referencing current liquidity, pending receivables, and applicable tax benefits — a task that is error-prone when done manually.

## Proposed Solution
A RAG-based (Retrieval-Augmented Generation) AI assistant embedded in the EverGreen FIN module that:

- Retrieves relevant tax law fragments from a vectorized knowledge base
- Queries the user's real-time financial data from EverGreen's database
- Reasons over both data sources using a configurable LLM (via API-based providers: Gemini, HuggingFace, OpenAI, or Groq) to produce personalized, grounded financial advice
- Performs precise calculations when projections or tax computations are needed

## Value Proposition
FIN-Advisor transforms the Finance module from a passive record-keeping system into an **active decision-support tool**, reducing the risk of tax penalties, surfacing applicable benefits, and enabling data-informed investment decisions — all without requiring the producer to hire an external accountant for routine queries.

## Project Constraints

| Constraint | Detail |
|---|---|
| Budget | $0 USD — university project, all tools must be free or open-source. Free-tier cloud APIs (e.g., Gemini, Groq) are acceptable |
| Deployment | Local development with external LLM API calls — free-tier cloud APIs are used for inference, all other components run locally |
| Data | Mix of public legal documents and synthetic/mock financial data |
| Timeline | Academic semester scope |
| Team | University students (first mock project) |

## Glossary

| Term | Definition |
|---|---|
| RAG | Retrieval-Augmented Generation — a pattern where an LLM's response is grounded by retrieving relevant documents before generating |
| ReAct Agent | Reasoning and Acting — an agent architecture where the LLM iteratively reasons about what tool to call next |
| Chunking | The process of splitting large documents into smaller, semantically meaningful pieces for vector storage |
| Embeddings | Numerical vector representations of text that capture semantic meaning, enabling similarity search |
| Vector Store | A database optimized for storing and querying embedding vectors (ChromaDB in this project) |
| Estatuto Tributario | Colombia's national tax code |
| DIAN | Dirección de Impuestos y Aduanas Nacionales — Colombia's tax authority |
| EverGreen FIN Module | The Finance module of the EverGreen case study, managing invoices, accounts, and movements |
| Tool (Agent) | A function the AI agent can invoke to interact with external data sources or perform calculations |
| Overlap (Chunking) | The percentage of shared text between consecutive chunks to preserve context across boundaries |
