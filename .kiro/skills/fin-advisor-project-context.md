---
name: FIN-Advisor Project Context
description: Contexto central del proyecto FIN-Advisor RAG — arquitectura, estructura de carpetas, decisiones técnicas, variables de entorno y documentos externos requeridos.
---

# FIN-Advisor — Contexto del Proyecto

## Identidad del Proyecto

**FIN-Advisor** es un asistente financiero basado en RAG (Retrieval-Augmented Generation) para productores agropecuarios colombianos, integrado en el módulo EverGreen Finance (FIN). El sistema combina tres fuentes de datos — una base de conocimiento vectorizada de legislación tributaria colombiana (ChromaDB), datos financieros en tiempo real del productor (SQLite) y herramientas de cálculo determinísticas — orquestados por un agente LangChain ReAct respaldado por un LLM configurable.

- **Repositorio raíz:** `RAG-FIN-Topicos-Avanzados/`
- **Tipo:** Proyecto universitario — Tópicos Avanzados
- **Idioma de documentación:** Español (READMEs, docstrings, comentarios, respuestas del agente)
- **Audiencia objetivo:** Productores agropecuarios y administradores de finca colombianos

## Resumen de Arquitectura

```
React Frontend (:3000) → FastAPI Backend (:8000) → ReAct Agent (LangChain) → 7 Herramientas
                                                        ↓
                                          ChromaDB (base de conocimiento)
                                          SQLite (datos financieros)
                                          LLM Provider (HuggingFace/Gemini/ChatGPT/Groq)
```

| Capa | Tecnología | Descripción |
|---|---|---|
| Presentación | React + react-markdown | Chat UI con chips de sugerencia, renderizado Markdown |
| API | FastAPI + Pydantic | POST /api/v1/chat, GET /api/v1/health, CORS |
| Razonamiento | LangChain `create_react_agent` | Máx. 5 iteraciones, 7 herramientas, prompt en español |
| Conocimiento | ChromaDB (persistente local) | Embeddings con `intfloat/multilingual-e5-small` (384-dim) |
| Datos | SQLite (`fin.db`) | 5 tablas: perfil_productor, movimientos, facturas_venta, cuentas_por_pagar, activos_fijos |
| Inferencia | LLM configurable (Strategy pattern) | HuggingFace (default), Gemini (recomendado), ChatGPT, Groq |

## Estructura de Carpetas

```
RAG-FIN-Topicos-Avanzados/
├── agent/                    # Agente ReAct LangChain
│   ├── prompt.md             # Prompt del sistema (Markdown)
│   ├── agent_config.py       # Creación del agente y configuración LLM
│   ├── llm_providers.py      # Strategy pattern: HuggingFace, Gemini, ChatGPT, Groq
│   └── tools/                # 7 herramientas del agente
│       ├── get_tax_knowledge.py          # Búsqueda semántica en ChromaDB
│       ├── query_evergreen_finances.py   # Consultas SQL parametrizadas
│       ├── calculate_vat_discount.py     # Descuento IVA
│       ├── calculate_net_liquidity.py    # Liquidez neta
│       ├── assess_investment_viability.py # Viabilidad de inversión
│       ├── project_tax_liability.py      # Proyección tributaria
│       └── calculate_depreciation.py     # Depreciación de activos
├── backend/                  # Servidor FastAPI
│   ├── app.py                # Factory de la aplicación
│   ├── routes.py             # Endpoints /api/v1/chat y /api/v1/health
│   ├── models.py             # Modelos Pydantic (ChatRequest, ChatResponse, etc.)
│   └── middleware.py         # Configuración CORS
├── frontend/                 # Interfaz React
│   └── src/components/       # ChatUI, SuggestionChips, ResponseRenderer, Logo
├── scripts/                  # Utilidades independientes
│   ├── etl_ingest.py         # Pipeline ETL: MD → chunks → embeddings → ChromaDB
│   ├── generate_mock_data.py # Generación de datos sintéticos SQLite
│   ├── init_chromadb.py      # Inicialización de colección ChromaDB
│   └── *_reference.py        # Código de referencia (embeddings, LLM, agente)
├── knowledge_base/           # Documentos Markdown fuente para RAG
├── tests/                    # pytest + hypothesis
├── .env.example              # Plantilla de variables de entorno
└── requirements.txt          # Dependencias Python
```

## Decisiones Técnicas Clave

| Decisión | Elección | Justificación |
|---|---|---|
| Proveedores LLM | HuggingFace (default), Gemini, ChatGPT, Groq | Strategy pattern; cambio vía variables de entorno |
| Modelo de embeddings | `intfloat/multilingual-e5-small` (384-dim) | Optimizado para español/texto legal, ~134MB, CPU |
| Vector Store | ChromaDB persistente local | Gratuito, nativo Python, filtrado por metadatos |
| Base de datos relacional | SQLite | Zero-config, built-in Python, archivo único |
| Framework de agente | LangChain `create_react_agent` | Soporte ReAct maduro, tool calling nativo |
| Streaming | Diferido a Fase 2 | MVP usa POST → JSON; SSE agrega complejidad sin valor core |
| Docker | Opcional (conveniencia) | Sistema funciona sin Docker vía `npm start` + `uvicorn` |
| Herramientas de cálculo | 5 herramientas individuales (no monolíticas) | Razonamiento más claro, schemas simples, mejor aislamiento de errores |
| Idioma de documentación | Español | Consistente con audiencia objetivo y contexto universitario |
| Chunking ETL | RecursiveCharacterTextSplitter (800 chars, 10% overlap) | Separadores: `\n## `, `\n### `, `\n\n`, `\n`, ` ` |
| Umbral de similitud | 0.35 (coseno, configurable) | Balance entre recall y precisión para texto legal en español |

## Variables de Entorno

| Variable | Default | Requerida | Descripción |
|---|---|---|---|
| `LLM_PROVIDER` | `huggingface` | No | Proveedor: `gemini` (recomendado), `huggingface`, `chatgpt`, `groq` |
| `LLM_API_KEY` | — | Sí | API key del proveedor seleccionado |
| `LLM_MODEL_NAME` | Según proveedor | No | Identificador del modelo |
| `EMBEDDING_MODEL_NAME` | `intfloat/multilingual-e5-small` | No | Modelo de embeddings para ETL y retrieval |
| `SIMILARITY_THRESHOLD` | `0.35` | No | Similitud coseno mínima para retrieval |
| `CHROMA_PERSIST_DIR` | `./chroma_data` | No | Directorio de persistencia ChromaDB |
| `SQLITE_DB_PATH` | `./fin.db` | No | Ruta al archivo SQLite |

## Documentos Externos Requeridos

Antes de ejecutar el pipeline ETL, el desarrollador debe preparar estos documentos en `knowledge_base/`:

| Documento | Fuente | Tipo |
|---|---|---|
| Estatuto Tributario — Libro I (Renta, secciones agrícolas) | Portal DIAN / Secretaría del Senado | Externo (legal) |
| Estatuto Tributario — Libro III (IVA, secciones agrícolas) | Portal DIAN / Secretaría del Senado | Externo (legal) |
| Beneficios compra maquinaria | Creado por el equipo (mock) | Guía |
| Exenciones pequeño productor | Creado por el equipo (mock) | Guía |
| Programas gobierno agro | Creado por el equipo (mock) | Guía |
| Calendario tributario 2024 | Portal DIAN / creado por equipo | Calendario |
