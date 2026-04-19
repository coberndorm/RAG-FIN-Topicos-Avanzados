# FIN-Advisor: Customer Journey

## Actors

| Actor | Description |
|---|---|
| **Producer** | The primary user — an agricultural producer or farm administrator who manages the finances of their operation through EverGreen |
| **FIN-Advisor** | The AI assistant system that processes queries, retrieves knowledge, and generates recommendations |

---

## Journey Phases

### Phase 1: Discovery & Entry
The producer logs into the EverGreen platform and navigates to the Finance module. They notice the FIN-Advisor chat interface available as a persistent component in the FIN dashboard.

**Trigger:** The producer has a financial question they cannot answer by looking at raw transaction tables alone.

**Examples of triggering situations:**
- Tax filing deadline approaching and unsure about applicable deductions
- Considering purchasing new equipment but uncertain about cash flow impact
- Received a large payment and wants to understand optimal allocation
- Confused about a specific tax article's applicability to their operation

---

### Phase 2: Query Formulation (Input)
The producer types a natural-language question into the FIN-Advisor chat. The system accepts free-text queries in Spanish.

**User interaction:**
- The producer writes their question in conversational Spanish
- The system displays a loading/thinking indicator
- No special syntax or structured input is required

**Example queries:**
- "¿Puedo descontar el IVA del tractor que quiero comprar?"
- "¿Cómo está mi flujo de caja este trimestre?"
- "¿Qué beneficios tributarios tengo como pequeño productor de hortalizas?"
- "Si compro una cosechadora este mes, ¿comprometo mi liquidez?"

---

### Phase 3: Processing (The "Brain")
This phase is invisible to the user but represents the core RAG pipeline:

```
Step 1 — Intent Classification
   The ReAct agent analyzes the query and determines which tools are needed.
   
Step 2 — Tool Selection & Execution
   The agent may call one or more tools in sequence:
   
   Path A: Legal Query
   → Agent calls get_tax_knowledge
   → ChromaDB returns relevant law fragments
   → Agent has legal context
   
   Path B: Financial Query  
   → Agent calls query_evergreen_finances
   → Database returns user's current financial state
   → Agent has financial context
   
   Path C: Combined Query (most common)
   → Agent calls both tools
   → Agent calls calculator_engine if math is needed
   → Agent has full context
   
Step 3 — Response Generation
   The LLM synthesizes all retrieved context into a coherent,
   personalized recommendation.
```

**What the user sees:** A brief "Analyzing your query..." message followed by the response appearing in the chat.

---

### Phase 4: Response Delivery (Output)
The system presents the answer in the chat interface. Responses are structured and may include:

- A direct answer to the question
- References to specific tax articles (with article numbers)
- Relevant financial figures from the user's own data
- A recommended course of action
- Caveats or disclaimers when information is incomplete

**Example response:**
> "Según el Artículo 258-1 del Estatuto Tributario, los bienes de capital adquiridos para actividades agropecuarias permiten descontar el IVA pagado. Revisando tu flujo de caja actual, tienes un saldo disponible de $12.500.000 COP y cuentas por cobrar de $8.000.000 COP con vencimiento en 15 días. La compra de la cosechadora ($18.000.000 COP) sería viable en la semana 3 del mes, una vez se materialicen los cobros pendientes. Además, el descuento del IVA representaría un ahorro de $3.420.000 COP en tu declaración."

---

### Phase 5: Follow-up & Iteration
The producer can:
- Ask follow-up questions in the same conversation thread
- Request clarification on specific parts of the response
- Ask the system to recalculate with different assumptions
- Start a new query on a different topic

The conversation context is maintained within the session to allow coherent multi-turn interactions.

---

## Journey Map (Visual Summary)

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  DISCOVERY   │     │  QUERY           │     │  PROCESSING             │
│              │────>│  FORMULATION     │────>│                         │
│ Producer     │     │                  │     │  ┌─────────────────┐    │
│ opens FIN    │     │ Types question   │     │  │ ReAct Agent     │    │
│ module       │     │ in natural       │     │  │ reasons about   │    │
│              │     │ language         │     │  │ which tools     │    │
└─────────────┘     └──────────────────┘     │  │ to call         │    │
                                              │  └────────┬────────┘    │
                                              │           │             │
                                              │  ┌────────▼────────┐    │
                                              │  │ Tool Execution  │    │
                                              │  │ - Tax KB search │    │
                                              │  │ - Finance query │    │
                                              │  │ - Calculator    │    │
                                              │  └────────┬────────┘    │
                                              │           │             │
                                              └───────────┼─────────────┘
                                                          │
                                                          ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  FOLLOW-UP   │     │  RESPONSE        │     │  LLM GENERATION         │
│              │<────│  DELIVERY        │<────│                         │
│ Producer     │     │                  │     │  Synthesizes legal +    │
│ asks more    │     │ Structured       │     │  financial context      │
│ questions    │     │ recommendation   │     │  into personalized      │
│ or starts    │     │ with references  │     │  recommendation         │
│ new topic    │     │ and data         │     │                         │
└─────────────┘     └──────────────────┘     └─────────────────────────┘
```

---

## Scope Boundaries

### In-Scope (FIN-Advisor WILL respond to)
- Queries about the Colombian Estatuto Tributario applicable to agriculture
- Summaries of expenses and income registered in EverGreen
- Tax projections based on the user's real financial data
- Explanation of basic accounting and tax concepts
- Requirements for accessing government agricultural benefits
- Fixed asset purchase viability analysis

### Out-of-Scope (FIN-Advisor WILL NOT respond to)
- Stock market or cryptocurrency investment advice
- Human or veterinary health topics
- Political or social opinions
- Hardware or machinery technical support (unrelated to software)
- Guaranteed financial success promises
- Legal advice beyond tax information (e.g., labor law, contracts)
