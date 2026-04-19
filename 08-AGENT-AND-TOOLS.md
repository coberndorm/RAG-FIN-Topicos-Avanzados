# FIN-Advisor: Agent & Tools Definition

---

## Agent Definition

| Attribute | Detail |
|---|---|
| Type | ReAct (Reasoning and Acting) |
| Framework | LangChain `create_react_agent` |
| LLM Backend | Ollama (Llama 3 8B) |
| Max Iterations | 5 (prevents infinite loops — note: with 7 tools, complex queries may use 4-5 iterations) |
| Tools Available | 7 (get_tax_knowledge, query_evergreen_finances, calculate_vat_discount, calculate_net_liquidity, assess_investment_viability, project_tax_liability, calculate_depreciation) |

### Agent Behavior

The ReAct agent operates in an iterative loop:

```
THOUGHT → ACTION → OBSERVATION → THOUGHT → ... → FINAL ANSWER
```

At each step, the agent:
1. Reasons about what information it still needs
2. Decides which tool to call (or whether to answer directly)
3. Observes the tool's output
4. Repeats until it has enough context to generate a complete answer

The agent does NOT follow a fixed pipeline. It dynamically decides the order and number of tool calls based on the query.

### Design Decision: Single-Purpose Calculation Tools

The calculation capabilities are split into 5 independent, single-purpose tools instead of a single monolithic `calculator_engine`. This is intentional:

1. **Clearer agent reasoning:** The tool name itself tells the agent what it does. The agent picks `assess_investment_viability` directly instead of picking `calculator_engine` and then figuring out which sub-operation to pass.
2. **Simpler input schemas:** Each tool has a narrow, well-defined set of parameters. No ambiguous "operation" field.
3. **Better error isolation:** If one calculation type has a bug, it doesn't affect the others.
4. **Easier testing:** Each tool can be unit-tested independently with its own fixtures.

---

## System Prompt

```
You are the Expert Financial Assistant of the EverGreen system. Your purpose is 
to help Colombian agricultural producers manage their finances and comply with 
their tax obligations.

REASONING RULES:
1. For questions about laws, taxes, exemptions, or government benefits, ALWAYS 
   use the get_tax_knowledge tool first.
2. For questions about the user's money, balances, expenses, invoices, or 
   financial records, ALWAYS use the query_evergreen_finances tool.
3. For calculations, use the specific calculation tool that matches the need:
   - VAT savings on a purchase → calculate_vat_discount
   - Available funds after obligations → calculate_net_liquidity
   - Whether a purchase is affordable → assess_investment_viability
   - Estimated tax for a period → project_tax_liability
   - Current value of an asset → calculate_depreciation
4. You may call multiple tools in sequence. Do not guess — retrieve data first.
5. If you cannot find relevant information in the knowledge base or the user's 
   data, say so explicitly. NEVER invent financial figures or legal references.

RESPONSE RULES:
- Respond in Spanish.
- Use a technical but accessible tone, suitable for a farm administrator.
- When citing tax laws, always include the article number.
- When presenting financial figures, use COP with thousand separators 
  (e.g., $12.500.000 COP).
- For any response that could be interpreted as financial or legal advice, 
  include a disclaimer recommending professional validation.

SCOPE:
- You ONLY answer questions related to Colombian agricultural taxation, 
  EverGreen financial data, and basic accounting concepts.
- If the user asks about topics outside this scope (investments in stocks, 
  health, politics, etc.), politely decline and explain what you can help with.
```

---

## Tool Definitions

### Tool 1: get_tax_knowledge

| Attribute | Detail |
|---|---|
| Purpose | Retrieve relevant fragments from the tax law and agricultural benefit knowledge base |
| Data Source | ChromaDB (collections: `tax_laws`, `sector_guides`) |
| Input | A natural language search query (string) |
| Output | List of relevant text chunks with metadata (article number, source, topic tags) |
| Access Pattern | Semantic similarity search (cosine distance) |

**Behavior:**
- Receives the agent's search query
- Converts it to an embedding using sentence-transformers
- Queries ChromaDB for the top-k most similar chunks (k=5 by default)
- Returns the chunk text along with metadata (article number, source document, tags)

**Example invocation:**
```
Agent THOUGHT: "I need to find what the law says about VAT discounts on agricultural machinery."
Agent ACTION: get_tax_knowledge("descuento IVA bienes de capital sector agropecuario")
OBSERVATION: [
  {
    "text": "Artículo 258-1. Descuento del IVA en la adquisición de bienes de capital...",
    "metadata": {
      "article_number": "258-1",
      "source_document": "estatuto_tributario_2024.md",
      "topic_tags": ["IVA", "bienes_de_capital", "maquinaria"]
    }
  },
  ...
]
```

**Constraints:**
- Read-only access to ChromaDB
- Returns a maximum of 5 chunks per query
- If no relevant chunks are found (similarity below threshold), returns an empty result with a message

---

### Tool 2: query_evergreen_finances

| Attribute | Detail |
|---|---|
| Purpose | Retrieve the user's financial data from the EverGreen FIN database |
| Data Source | SQLite database (`fin.db`) |
| Input | A structured query descriptor (what data is needed) |
| Output | Structured financial data (JSON) |
| Access Pattern | SQL queries (read-only) |

**Available query types:**

| Query Type | Description | Returns |
|---|---|---|
| `current_balance` | Current available cash balance | Single decimal value |
| `recent_movements` | Income and expenses for a given period | List of movement records |
| `pending_receivables` | Unpaid sales invoices | List of invoice records with amounts and due dates |
| `pending_payables` | Unpaid supplier debts | List of payable records with amounts and due dates |
| `fixed_assets` | Current asset inventory | List of asset records with values |
| `expense_summary` | Expenses grouped by category for a period | Aggregated category totals |
| `producer_profile` | User's activity type and tax bracket | Profile record |

**Example invocation:**
```
Agent THOUGHT: "I need to check if the user can afford the purchase."
Agent ACTION: query_evergreen_finances({
  "query_type": "current_balance"
})
OBSERVATION: { "current_balance": 12500000, "currency": "COP" }

Agent ACTION: query_evergreen_finances({
  "query_type": "pending_receivables",
  "period_days": 30
})
OBSERVATION: {
  "receivables": [
    { "invoice_id": 42, "client": "Cooperativa del Valle", "amount": 5000000, "due_date": "2024-07-15" },
    { "invoice_id": 43, "client": "Mercado Central", "amount": 3000000, "due_date": "2024-07-22" }
  ],
  "total": 8000000
}
```

**Constraints:**
- Strictly read-only — the agent cannot insert, update, or delete records
- All monetary values are in COP
- Date ranges default to the current quarter if not specified

---

### Tool 3: calculate_vat_discount

| Attribute | Detail |
|---|---|
| Purpose | Calculate the VAT discount applicable to a capital good purchase |
| Data Source | None (pure computation) |
| Input | `purchase_price` (decimal), `vat_rate` (decimal, default 0.19) |
| Output | `discount_amount`, `effective_cost`, `explanation` |

**Example invocation:**
```
Agent THOUGHT: "I need to know how much VAT the user saves on the tractor."
Agent ACTION: calculate_vat_discount({ "purchase_price": 18000000, "vat_rate": 0.19 })
OBSERVATION: {
  "discount_amount": 3420000,
  "effective_cost": 14580000,
  "explanation": "El descuento del IVA (19%) sobre $18.000.000 es de $3.420.000. 
                   El costo efectivo del bien sería $14.580.000."
}
```

---

### Tool 4: calculate_net_liquidity

| Attribute | Detail |
|---|---|
| Purpose | Calculate available funds after accounting for pending obligations |
| Data Source | None (pure computation) |
| Input | `balance` (decimal), `receivables` (decimal), `payables` (decimal) |
| Output | `net_liquidity_now`, `net_liquidity_projected`, `explanation` |

**Example invocation:**
```
Agent THOUGHT: "I need to know how much the user actually has available."
Agent ACTION: calculate_net_liquidity({ "balance": 12500000, "receivables": 8000000, "payables": 2000000 })
OBSERVATION: {
  "net_liquidity_now": 10500000,
  "net_liquidity_projected": 18500000,
  "explanation": "Liquidez actual: $12.500.000 - $2.000.000 (por pagar) = $10.500.000. 
                   Proyectada con cobros pendientes: $10.500.000 + $8.000.000 = $18.500.000."
}
```

---

### Tool 5: assess_investment_viability

| Attribute | Detail |
|---|---|
| Purpose | Determine if a fixed asset purchase is financially viable and suggest optimal timing |
| Data Source | None (pure computation) |
| Input | `balance` (decimal), `receivables` (decimal), `payables` (decimal), `purchase_cost` (decimal), `tax_benefit` (decimal, default 0) |
| Output | `effective_cost`, `available_funds_now`, `available_funds_projected`, `viable_now`, `viable_in_days`, `explanation` |

**Example invocation:**
```
Agent THOUGHT: "I need to determine if the harvester purchase is viable."
Agent ACTION: assess_investment_viability({
  "balance": 12500000,
  "receivables": 8000000,
  "payables": 2000000,
  "purchase_cost": 18000000,
  "tax_benefit": 3420000
})
OBSERVATION: {
  "effective_cost": 14580000,
  "available_funds_now": 10500000,
  "available_funds_projected": 18500000,
  "viable_now": false,
  "viable_in_days": 15,
  "explanation": "Fondos actuales ($10.5M) son insuficientes para el costo efectivo ($14.58M). 
                   Tras recibir pagos pendientes en ~15 días, los fondos disponibles ($18.5M) 
                   superarán el costo efectivo."
}
```

---

### Tool 6: project_tax_liability

| Attribute | Detail |
|---|---|
| Purpose | Estimate the tax liability for a given period based on income and deductions |
| Data Source | None (pure computation) |
| Input | `gross_income` (decimal), `deductions` (decimal), `tax_rate` (decimal) |
| Output | `taxable_income`, `estimated_tax`, `explanation` |

**Example invocation:**
```
Agent THOUGHT: "The user wants to know their estimated income tax."
Agent ACTION: project_tax_liability({ "gross_income": 50000000, "deductions": 12000000, "tax_rate": 0.25 })
OBSERVATION: {
  "taxable_income": 38000000,
  "estimated_tax": 9500000,
  "explanation": "Ingreso bruto: $50.000.000 - Deducciones: $12.000.000 = Base gravable: $38.000.000. 
                   Impuesto estimado (25%): $9.500.000."
}
```

---

### Tool 7: calculate_depreciation

| Attribute | Detail |
|---|---|
| Purpose | Calculate the current depreciated value of a fixed asset using straight-line method |
| Data Source | None (pure computation) |
| Input | `purchase_value` (decimal), `useful_life_years` (int), `years_elapsed` (decimal) |
| Output | `annual_depreciation`, `accumulated_depreciation`, `current_value`, `explanation` |

**Example invocation:**
```
Agent THOUGHT: "The user wants to know the current value of their tractor."
Agent ACTION: calculate_depreciation({ "purchase_value": 45000000, "useful_life_years": 10, "years_elapsed": 3 })
OBSERVATION: {
  "annual_depreciation": 4500000,
  "accumulated_depreciation": 13500000,
  "current_value": 31500000,
  "explanation": "Depreciación anual: $4.500.000/año. Tras 3 años, depreciación acumulada: 
                   $13.500.000. Valor actual del activo: $31.500.000."
}
```

---

### Shared Constraints (All Calculation Tools)

- Do not access any database — work only with provided numbers
- All calculations are deterministic (no LLM involvement)
- Return both the numeric result and a human-readable explanation in Spanish
- If any required input is missing or invalid (e.g., negative values, zero useful life), return an error message instead of a result

---

## Tool Summary

| # | Tool Name | Category | Inputs | Used By |
|---|---|---|---|---|
| 1 | get_tax_knowledge | Retrieval | search query (string) | US-01, US-03, US-04, US-06 |
| 2 | query_evergreen_finances | Retrieval | query descriptor (structured) | US-02, US-03, US-04, US-05, US-06 |
| 3 | calculate_vat_discount | Calculation | purchase_price, vat_rate | US-01, US-03 |
| 4 | calculate_net_liquidity | Calculation | balance, receivables, payables | US-02, US-03, US-04 |
| 5 | assess_investment_viability | Calculation | balance, receivables, payables, purchase_cost, tax_benefit | US-03 |
| 6 | project_tax_liability | Calculation | gross_income, deductions, tax_rate | US-04 |
| 7 | calculate_depreciation | Calculation | purchase_value, useful_life_years, years_elapsed | US-05 |

---

## Tool Interaction Patterns

### Pattern A: Simple Legal Query (1 tool)
```
User: "¿Qué dice la ley sobre exenciones de IVA para semillas?"
Agent: THOUGHT → get_tax_knowledge → FINAL ANSWER
```

### Pattern B: Simple Financial Query (1 tool)
```
User: "¿Cuánto he gastado en insumos este trimestre?"
Agent: THOUGHT → query_evergreen_finances → FINAL ANSWER
```

### Pattern C: Combined Analysis (3-4 tools)
```
User: "¿Puedo comprar un tractor sin quedarme sin liquidez?"
Agent: THOUGHT → get_tax_knowledge → query_evergreen_finances → calculate_vat_discount → assess_investment_viability → FINAL ANSWER
```

### Pattern D: Educational Query (0-1 tools)
```
User: "¿Qué es la depreciación?"
Agent: THOUGHT → FINAL ANSWER (from LLM's training knowledge)
```

### Pattern E: Tax Planning Query (2-3 tools)
```
User: "¿Cuánto voy a deber de renta este año?"
Agent: THOUGHT → query_evergreen_finances → get_tax_knowledge → project_tax_liability → FINAL ANSWER
```

---

## Error Handling

| Scenario | Agent Behavior |
|---|---|
| ChromaDB returns no relevant chunks | Agent states: "No encontré información específica sobre este tema en la base de conocimiento tributario." |
| Database query returns empty results | Agent states: "No hay registros de [X] en tu cuenta de EverGreen para el período consultado." |
| Calculation tool receives invalid inputs | Agent re-checks the data from previous tool calls before retrying with corrected values |
| Query is out of scope | Agent politely declines and lists what it CAN help with |
| Max iterations reached (5) | Agent returns the best answer it can with available data, noting any gaps |
