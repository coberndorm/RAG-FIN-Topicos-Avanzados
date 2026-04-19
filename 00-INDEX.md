# FIN-Advisor: Project Definition Index

## Asistente Inteligente de Optimización Tributaria y Flujo de Caja
### EverGreen — Finance Module (FIN)

---

## Document Map

| # | Document | Description |
|---|---|---|
| 01 | [Project Overview](./01-PROJECT-OVERVIEW.md) | Problem statement, value proposition, constraints, and glossary |
| 02 | [Customer Journey](./02-CUSTOMER-JOURNEY.md) | End-to-end user journey through the 5 phases, scope boundaries, and actor definitions |
| 03 | [User Stories (3 C's)](./03-USER-STORIES.md) | 6 user stories with Card, Conversation, and Confirmation for each |
| 04 | [Knowledge Base Definition](./04-KNOWLEDGE-BASE-DEFINITION.md) | KB elements, chunking strategy, metadata schema, and quality criteria |
| 05 | [Inputs & Outputs](./05-INPUTS-AND-OUTPUTS.md) | Detailed definition of all system inputs (5) and outputs (5) with schemas and conditions |
| 06 | [Architecture](./06-ARCHITECTURE.md) | Layered architecture diagram, data flow, justification table, NFRs, and deployment topology |
| 07 | [Tech Stack](./07-TECH-STACK.md) | Complete technology inventory with versions, licenses, justifications, and dependency map |
| 08 | [Agent & Tools](./08-AGENT-AND-TOOLS.md) | ReAct agent definition, system prompt, 3 tool specifications, interaction patterns, and error handling |
| 09 | [Data Requirements](./09-DATA-REQUIREMENTS.md) | Document inventory, mock data table schemas, sample data, generation plan, and task ownership |
| 10 | [Risks & Constraints](./10-PROJECT-RISKS-AND-CONSTRAINTS.md) | 6 constraints, 8 risks with mitigations, 7 assumptions, and Definition of Done |

---

## Quick Reference

**What are we building?** A RAG-based AI assistant for the EverGreen Finance module that helps Colombian agricultural producers with tax optimization and cash flow management.

**Who is it for?** Agricultural producers and farm administrators using the EverGreen platform.

**What does it cost?** $0 — fully open-source, fully local.

**Core tech:** React + FastAPI + LangChain + Ollama (Llama 3) + ChromaDB + SQLite

**How many user stories?** 6 stories covering tax inquiries, cash flow diagnosis, investment viability, tax calendars, concept explanations, and expense optimization.
