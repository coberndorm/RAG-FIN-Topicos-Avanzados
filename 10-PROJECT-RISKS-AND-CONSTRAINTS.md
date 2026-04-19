# FIN-Advisor: Risks, Constraints & Assumptions

---

## Constraints

| ID | Constraint | Impact | Mitigation |
|---|---|---|---|
| C-01 | $0 budget — no paid APIs or cloud services | Limits model quality (no GPT-4, no cloud vector DBs) | Use Ollama + Llama 3 locally. All tools are open-source |
| C-02 | Fully local deployment | No internet required at runtime, but limits accessibility | All components run on localhost. Acceptable for academic demo |
| C-03 | Academic timeline (single semester) | Limits feature scope | Focus on MVP with 6 user stories. No Phase 2 features |
| C-04 | Team experience level (first project) | Slower development, potential architectural mistakes | Clear documentation, simple architecture, well-known tools |
| C-05 | Hardware variability across team | Some machines may not run Llama 3 8B efficiently | Provide Mistral 7B as fallback. Test on lowest-spec machine early |
| C-06 | Mock data only (no real financial records) | Cannot validate real-world accuracy | Design data to be realistic. Document that this is a proof of concept |

---

## Risks

| ID | Risk | Probability | Impact | Mitigation Strategy |
|---|---|---|---|---|
| R-01 | LLM hallucinations in tax calculations | High | Critical — incorrect tax advice could undermine the project's credibility | Use calculator_engine for all math. System prompt explicitly forbids inventing numbers. Retrieval quality validation before demo |
| R-02 | Poor retrieval quality (wrong chunks returned) | Medium | High — agent gives irrelevant answers | Careful chunking strategy, metadata tagging, and test queries during development. Adjust chunk size and overlap if needed |
| R-03 | Ollama performance too slow on team hardware | Medium | Medium — bad demo experience | Test early on the weakest machine. Use Mistral 7B if Llama 3 is too slow. Reduce max_tokens in responses |
| R-04 | LangChain version incompatibilities | Medium | Medium — blocks development | Pin all dependency versions in requirements.txt. Use a virtual environment |
| R-05 | Spanish language quality in LLM responses | Low | Medium — responses may mix languages or use awkward phrasing | Test with Spanish prompts early. Llama 3 has good multilingual support. System prompt enforces Spanish |
| R-06 | Scope creep (team wants to add more features) | High | Medium — delays core delivery | Strict adherence to the 6 defined user stories. Phase 2 features are documented but not committed |
| R-07 | ChromaDB data corruption or loss | Low | High — requires re-ingestion | Use persistent mode with a known directory. Include the ETL script in the repo so re-ingestion is a single command |
| R-08 | Team member unavailability | Medium | Medium — delays tasks | Clear task ownership and documentation so any member can pick up another's work |

---

## Assumptions

| ID | Assumption | If Invalid... |
|---|---|---|
| A-01 | At least one team member's machine has 16GB RAM | If all machines have 8GB, use Mistral 7B and reduce context window |
| A-02 | The Estatuto Tributario PDF is publicly available from DIAN | If not, create a simplified mock version based on publicly known articles |
| A-03 | Llama 3 8B can reason adequately over Spanish financial text | If quality is poor, try Mistral 7B or a Spanish-fine-tuned model |
| A-04 | SQLite is sufficient for the mock data volume | If queries become complex, upgrade to PostgreSQL (minimal code change) |
| A-05 | The team has basic Python and React knowledge | If not, allocate first 1-2 weeks for onboarding with tutorials |
| A-06 | Single-user operation is acceptable for the demo | If the professor requires multi-user, add session management (minor change) |
| A-07 | The EverGreen FIN module's data model is stable | If the case study changes, update the SQLite schema and mock data accordingly |

---

## Definition of Done (Project Level)

The project is considered complete when:

1. All 6 user stories pass their Confirmation criteria
2. The ETL pipeline successfully ingests all knowledge base documents into ChromaDB
3. The ReAct agent correctly routes queries to the appropriate tools
4. The system runs entirely on a local machine without internet access
5. A live demo can be performed showing at least 3 different query types (legal, financial, combined)
6. All project documentation is complete and in the repository
7. The mock data is realistic enough to demonstrate meaningful responses
