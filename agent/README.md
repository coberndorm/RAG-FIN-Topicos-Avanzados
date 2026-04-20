# agent/ — Módulo del Agente ReAct

Este directorio contiene la implementación del agente de razonamiento de FIN-Advisor, basado en el patrón **ReAct** (Reasoning + Acting) de LangChain. El agente orquesta 7 herramientas para responder consultas financieras de productores agrícolas colombianos.

## Contenido

```
agent/
├── __init__.py            # Exportaciones del paquete
├── agent_config.py        # Creación y configuración del agente ReAct
├── llm_providers.py       # Patrón Strategy: proveedores de LLM
├── prompt.md              # Prompt del sistema en Markdown
└── tools/                 # Herramientas del agente (7 total)
    ├── __init__.py        # Exporta las 7 herramientas como tools de LangChain
    ├── models.py          # Modelos Pydantic de entrada/salida
    ├── get_tax_knowledge.py         # Recuperación de conocimiento tributario (ChromaDB)
    ├── query_evergreen_finances.py  # Consulta de datos financieros (SQLite)
    ├── calculate_vat_discount.py    # Cálculo de descuento IVA
    ├── calculate_net_liquidity.py   # Cálculo de liquidez neta
    ├── assess_investment_viability.py # Evaluación de viabilidad de inversión
    ├── project_tax_liability.py     # Proyección de obligación tributaria
    └── calculate_depreciation.py    # Cálculo de depreciación
```

## Componentes

### `llm_providers.py` — Proveedores de LLM (Patrón Strategy)

Implementa una clase base abstracta `ProveedorLLM` con proveedores concretos:

- **HuggingFaceProvider** — Usa `HuggingFaceEndpoint` (modelo por defecto: `meta-llama/Llama-3.1-70B-Instruct`)
- **GeminiProvider** — Usa `ChatGoogleGenerativeAI` (modelo por defecto: `gemini-2.5-flash`)
- **ChatGPTProvider** — Usa `ChatOpenAI` (modelo por defecto: `gpt-4o-mini`)
- **GroqProvider** — Usa `ChatGroq` (modelo por defecto: `llama-3.3-70b-versatile`)

La función factoría `crear_proveedor_llm()` lee las variables de entorno `LLM_PROVIDER`, `LLM_API_KEY` y `LLM_MODEL_NAME` para instanciar el proveedor correcto. Si falta la clave de API, lanza un error descriptivo.

### `agent_config.py` — Configuración del Agente

- `_cargar_prompt_sistema()` — Carga el prompt del sistema desde `prompt.md`
- `crear_agente()` — Crea el agente ReAct con `create_react_agent` de LangChain, registra las 7 herramientas, configura máximo 5 iteraciones y manejo de errores de parsing
- `obtener_config_invocacion()` — Retorna la configuración de invocación del agente

### `prompt.md` — Prompt del Sistema

Archivo Markdown que define el comportamiento del agente:
- Responder siempre en español
- Citar números de artículos al referenciar leyes tributarias
- Formatear valores monetarios como COP con separadores de miles
- Incluir disclaimers en asesoría financiera
- Definir alcance: tributación agrícola colombiana, datos EverGreen, conceptos contables básicos
- Rechazar temas fuera de alcance: acciones, salud, política, soporte técnico

### `tools/` — Herramientas del Agente

**Herramientas de recuperación (2):**

| Herramienta | Fuente | Descripción |
|-------------|--------|-------------|
| `get_tax_knowledge` | ChromaDB | Búsqueda semántica de fragmentos de legislación tributaria. Retorna top 5 chunks con metadatos (artículo, fuente, tags) |
| `query_evergreen_finances` | SQLite | Consultas parametrizadas a la base financiera. Soporta 7 tipos: `current_balance`, `recent_movements`, `pending_receivables`, `pending_payables`, `fixed_assets`, `expense_summary`, `producer_profile` |

**Herramientas de cálculo (5):**

| Herramienta | Entrada | Salida |
|-------------|---------|--------|
| `calculate_vat_discount` | precio, tasa IVA | descuento, costo efectivo, explicación |
| `calculate_net_liquidity` | saldo, cuentas por cobrar, cuentas por pagar | liquidez actual, liquidez proyectada, explicación |
| `assess_investment_viability` | saldo, cobrar, pagar, costo compra, beneficio fiscal | costo efectivo, fondos disponibles, viabilidad, días estimados |
| `project_tax_liability` | ingreso bruto, deducciones, tasa impositiva | ingreso gravable, impuesto estimado, explicación |
| `calculate_depreciation` | valor compra, vida útil, años transcurridos | depreciación anual, acumulada, valor actual, explicación |

Todas las herramientas de cálculo son determinísticas (no invocan el LLM) y retornan mensajes de error descriptivos en español para entradas inválidas.

### `tools/models.py` — Modelos de Datos

Modelos Pydantic con validadores `Field` para entrada/salida de cada herramienta de cálculo: `VATDiscountInput/Output`, `NetLiquidityInput/Output`, `InvestmentViabilityInput/Output`, `TaxLiabilityInput/Output`, `DepreciationInput/Output`.

## Relación con Otros Módulos

- **`backend/`** — El backend importa `crear_agente()` de `agent_config.py` durante el startup y lo invoca en cada petición `POST /api/v1/chat`
- **`knowledge_base/`** → `get_tax_knowledge` consulta los embeddings generados por el ETL desde estos documentos
- **`scripts/`** — `init_chromadb.py` y `etl_ingest.py` preparan la base vectorial que `get_tax_knowledge` consulta; `generate_mock_data.py` crea la base SQLite que `query_evergreen_finances` consulta

## Configuración

Las herramientas leen variables de entorno desde `.env`:

- `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL_NAME` — Configuración del proveedor LLM
- `EMBEDDING_MODEL_NAME` — Modelo de embeddings para `get_tax_knowledge`
- `SIMILARITY_THRESHOLD` — Umbral de similitud coseno (default: 0.35)
- `CHROMA_PERSIST_DIR` — Directorio de persistencia de ChromaDB
- `SQLITE_DB_PATH` — Ruta a la base de datos SQLite
