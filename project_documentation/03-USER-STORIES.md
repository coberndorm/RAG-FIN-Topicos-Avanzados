# FIN-Advisor: User Stories (3 C's Framework)

Each user story follows the **Card, Conversation, Confirmation** framework.

---

## US-01: Tax Benefit Inquiry

### Card
> **As a** agricultural producer,
> **I want to** ask the assistant about tax benefits applicable to my type of operation,
> **so that** I can take advantage of deductions and exemptions I might not be aware of.

### Conversation
The producer has heard that there are VAT discounts for purchasing agricultural machinery but doesn't know the specifics. They open FIN-Advisor and ask: "¿Qué beneficios tributarios tengo como productor de hortalizas para la compra de maquinaria?"

The system needs to:
- Search the vectorized Estatuto Tributario for articles related to VAT on capital goods for agriculture
- Identify the producer's registered activity type from EverGreen data
- Return the specific articles, conditions, and applicable percentages

Key discussion points:
- What if the producer's activity type isn't registered in the system? → The assistant should ask the user to clarify or state that it cannot personalize without that data.
- What if the law fragment is ambiguous? → The assistant should present the raw text and explain its interpretation, noting uncertainty.
- Should the assistant recommend consulting a professional? → Yes, for complex cases, it should always suggest professional validation.

### Confirmation
- [ ] The system retrieves at least one relevant article from the Estatuto Tributario
- [ ] The response includes the specific article number(s) referenced
- [ ] The response explains the benefit in plain language (understandable by a farm administrator)
- [ ] If the user's activity type is available, the response is personalized to their sector
- [ ] If the user's activity type is NOT available, the system explicitly states this limitation
- [ ] The response includes a disclaimer recommending professional validation for tax decisions
- [ ] Response time is under 30 seconds

---

## US-02: Cash Flow Diagnosis

### Card
> **As a** farm administrator,
> **I want to** ask the assistant to explain my current cash flow situation,
> **so that** I can understand why my available balance is what it is and plan accordingly.

### Conversation
The administrator notices their balance is lower than expected. They ask: "¿Por qué mi flujo de caja bajó tanto este mes?"

The system needs to:
- Query the EverGreen FIN database for recent movements (income and expenses)
- Identify the largest transactions or patterns that explain the change
- Present a semantic analysis — not just numbers, but the "why"

Key discussion points:
- How far back should the system look? → Default to current quarter, but the user can specify a different period.
- What if there are no significant anomalies? → The system should say so and present the normal distribution of expenses.
- Should it compare to previous periods? → Yes, if historical data is available, a comparison adds context.

### Confirmation
- [ ] The system queries the user's financial movements from the EverGreen database
- [ ] The response identifies the top 3 contributors to the cash flow change
- [ ] The response includes actual monetary figures from the user's data
- [ ] The explanation is semantic (explains causes, not just lists transactions)
- [ ] If historical data exists, a comparison to the previous period is included
- [ ] The response suggests actionable next steps (e.g., "consider following up on pending receivables")
- [ ] Response time is under 30 seconds

---

## US-03: Fixed Asset Purchase Viability

### Card
> **As a** agricultural producer,
> **I want to** ask the assistant whether I can afford to buy a specific piece of equipment right now,
> **so that** I can make an informed investment decision without compromising my operation's liquidity.

### Conversation
The producer is considering buying a harvester worth $18,000,000 COP. They ask: "Si compro una cosechadora este mes, ¿comprometo mi liquidez?"

The system needs to:
- Retrieve the user's current balance, pending receivables, and upcoming payables
- Check for applicable tax benefits on the purchase (VAT discount on capital goods)
- Run a calculation: available cash + expected receivables - upcoming payables - purchase cost
- Determine viability and suggest optimal timing

Key discussion points:
- What if the user doesn't specify the price? → The assistant should ask for the approximate cost.
- Should the system factor in tax benefits in the viability calculation? → Yes, if applicable benefits are found, they should reduce the effective cost.
- What if the purchase is not viable now? → The system should suggest when it could become viable based on projected receivables.

### Confirmation
- [ ] The system retrieves the user's current balance, receivables, and payables
- [ ] The system checks ChromaDB for applicable tax benefits on the asset type
- [ ] A calculation is performed using `calculate_vat_discount` and `assess_investment_viability` showing: available funds vs. total cost (net of tax benefits)
- [ ] The response clearly states whether the purchase is viable NOW
- [ ] If not viable now, the response suggests an estimated viable date based on projected income
- [ ] The tax benefit (if any) is quantified in COP
- [ ] The response includes the assumptions used in the calculation
- [ ] Response time is under 45 seconds (allows for multiple tool calls + calculation)

---

## US-04: Personalized Tax Calendar

### Card
> **As a** farm administrator,
> **I want to** receive a personalized tax calendar based on my operation's obligations,
> **so that** I never miss a filing deadline and can plan my cash reserves accordingly.

### Conversation
The administrator knows tax deadlines exist but can never remember which ones apply to their specific situation. They ask: "¿Cuáles son mis próximas fechas de pago de impuestos?"

The system needs to:
- Identify the producer's tax obligations based on their registered activity and size
- Retrieve the official tax calendar from the knowledge base
- Cross-reference with the user's cash flow to flag dates where liquidity might be tight

Key discussion points:
- How does the system know the user's NIT or tax ID bracket? → From the EverGreen user profile data (mocked).
- Should it include municipal taxes? → For MVP, only national taxes (DIAN). Municipal taxes are out of scope.
- What format should the calendar take? → A chronological list with dates, obligation names, and estimated amounts.

### Confirmation
- [ ] The system identifies at least the user's income tax and VAT obligations
- [ ] Dates are presented in chronological order
- [ ] Each entry includes: date, obligation name, and estimated amount (if calculable)
- [ ] Dates where the user's projected balance is insufficient are flagged with a warning
- [ ] The response specifies that only national (DIAN) obligations are covered
- [ ] The calendar covers at least the next 3 months
- [ ] Response time is under 30 seconds

---

## US-05: Accounting Concept Explanation

### Card
> **As a** agricultural producer with limited accounting knowledge,
> **I want to** ask the assistant to explain financial or tax concepts in simple terms,
> **so that** I can better understand my own financial reports and obligations.

### Conversation
The producer sees "depreciación acumulada" in their asset report and doesn't understand what it means. They ask: "¿Qué significa depreciación acumulada y cómo me afecta?"

The system needs to:
- Recognize this as an educational query (no tool calls needed, or minimal retrieval)
- Explain the concept in plain, accessible language
- If possible, illustrate with an example from the user's own data

Key discussion points:
- Should the system always try to use the user's data for examples? → Yes, when relevant data exists. Otherwise, use a generic agricultural example.
- How technical should the explanation be? → Targeted at a farm administrator, not an accountant. Avoid jargon.
- Should it link to further reading? → If a relevant section exists in the knowledge base, reference it.

### Confirmation
- [ ] The response explains the concept without using unexplained jargon
- [ ] The explanation is relevant to the agricultural context
- [ ] If the user has related data in EverGreen, a concrete example from their data is included
- [ ] If no user data is relevant, a generic agricultural example is provided
- [ ] The response is concise (under 200 words for simple concepts)
- [ ] Response time is under 30 seconds

---

## US-06: Expense Optimization Recommendation

### Card
> **As a** farm administrator,
> **I want to** ask the assistant to analyze my recent expenses and suggest areas where I could save money,
> **so that** I can improve the profitability of my agricultural operation.

### Conversation
The administrator feels like they're spending too much on inputs but can't pinpoint where. They ask: "¿En qué estoy gastando de más y cómo puedo optimizar mis costos?"

The system needs to:
- Query the user's expense records from EverGreen, categorized by type
- Identify categories with unusually high spending (compared to income ratio or historical patterns)
- Cross-reference with tax knowledge to suggest if any expenses qualify for deductions
- Provide actionable recommendations

Key discussion points:
- What counts as "unusually high"? → For MVP, compare expense categories as a percentage of total expenses. Flag any category above 40%.
- Should the system suggest specific vendors or alternatives? → No, that's out of scope. It should suggest categories to review.
- What if all expenses look normal? → The system should confirm that and suggest maintaining current patterns.

### Confirmation
- [ ] The system retrieves and categorizes the user's expenses from EverGreen
- [ ] At least the top 3 expense categories are presented with their amounts
- [ ] Categories with disproportionate spending are flagged
- [ ] If any expenses qualify for tax deductions, this is mentioned
- [ ] Recommendations are actionable and specific to the agricultural context
- [ ] The response does NOT recommend specific vendors or products
- [ ] Response time is under 30 seconds

---

## Summary Matrix

| ID | Story | Priority | Tools Used | Estimated Complexity |
|---|---|---|---|---|
| US-01 | Tax Benefit Inquiry | High | get_tax_knowledge, calculate_vat_discount | Medium |
| US-02 | Cash Flow Diagnosis | High | query_evergreen_finances, calculate_net_liquidity | Medium |
| US-03 | Fixed Asset Purchase Viability | High | get_tax_knowledge, query_evergreen_finances, calculate_vat_discount, assess_investment_viability | High |
| US-04 | Personalized Tax Calendar | Medium | get_tax_knowledge, query_evergreen_finances, project_tax_liability | Medium |
| US-05 | Accounting Concept Explanation | Low | get_tax_knowledge (optional), calculate_depreciation (optional) | Low |
| US-06 | Expense Optimization | Medium | query_evergreen_finances, get_tax_knowledge | Medium |
