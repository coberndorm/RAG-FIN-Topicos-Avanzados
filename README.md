# FIN-Advisor RAG — Asistente Financiero para Productores Agrícolas Colombianos

Sistema de asesoría financiera basado en **RAG** (Retrieval-Augmented Generation) para productores agrícolas colombianos, integrado al módulo EverGreen Finance (FIN). Combina una base de conocimiento vectorizada de legislación tributaria colombiana (ChromaDB), datos financieros del productor en tiempo real (SQLite) y herramientas de cálculo determinísticas, todo orquestado por un agente ReAct de LangChain respaldado por un LLM configurable.

## Arquitectura General

```
┌─────────────────────┐     POST /api/v1/chat     ┌──────────────────────┐
│   React Frontend    │ ──────────────────────────▶│   FastAPI Backend    │
│   (puerto 3000)     │◀────────── JSON ───────────│   (puerto 8000)      │
└─────────────────────┘                            └──────────┬───────────┘
                                                              │
                                                   ┌──────────▼───────────┐
                                                   │  Agente ReAct        │
                                                   │  (LangChain, 7 tools)│
                                                   └──┬──────┬────────┬───┘
                                                      │      │        │
                                            ┌─────────▼┐  ┌──▼─────┐ ┌▼──────────────┐
                                            │ ChromaDB  │  │ SQLite │ │ Herramientas  │
                                            │ (tax_laws)│  │(fin.db)│ │ de Cálculo (5)│
                                            └───────────┘  └────────┘ └───────────────┘
```

**Componentes principales:**

- **Frontend React** — Interfaz de chat con chips de sugerencia, renderizado Markdown y contador de caracteres
- **Backend FastAPI** — API REST con endpoints `/api/v1/chat` y `/api/v1/health`
- **Agente ReAct (LangChain)** — 7 herramientas: 2 de recuperación + 5 de cálculo, máximo 5 iteraciones
- **ChromaDB** — Base vectorial con embeddings de legislación tributaria colombiana
- **SQLite** — Base de datos financiera con datos mock del módulo EverGreen FIN

## Requisitos Previos

| Requisito | Versión mínima | Notas |
|-----------|---------------|-------|
| Python | 3.11+ | SQLite viene incluido en la librería estándar |
| Node.js | 18+ | Para el frontend React |
| pip | Última versión | Gestor de paquetes de Python |
| npm | Incluido con Node.js | Gestor de paquetes de JavaScript |

## Instalación

### 1. Dependencias de Python

```bash
cd RAG-FIN-Topicos-Avanzados
pip install -r requirements.txt
```

Esto instala: FastAPI, uvicorn, LangChain, ChromaDB, sentence-transformers, hypothesis, pytest, entre otros.

### 2. Dependencias del Frontend

```bash
cd RAG-FIN-Topicos-Avanzados/frontend
npm install
```

### 3. Variables de Entorno

Copiar el archivo de ejemplo y completar los valores:

```bash
cp .env.example .env
```

Editar `.env` con tu clave de API del proveedor LLM elegido. Consulta la sección [Variables de Entorno](#variables-de-entorno) para más detalles.

## Cómo Ejecutar

### Paso 1 — Generar datos mock (SQLite)

Crea la base de datos `fin.db` con datos financieros sintéticos de un productor agrícola colombiano:

```bash
python scripts/generate_mock_data.py
```

Genera: 1 perfil de productor, 30+ movimientos (6 meses), 15+ facturas, 10+ cuentas por pagar, 5-8 activos fijos.

### Paso 2 — Inicializar ChromaDB

Crea la colección persistente de ChromaDB con métrica de similitud coseno:

```bash
python scripts/init_chromadb.py
```

### Paso 3 — Ejecutar el pipeline ETL

Ingesta los documentos Markdown de la base de conocimiento en ChromaDB:

```bash
python scripts/etl_ingest.py
```

Procesa los 6 documentos de `knowledge_base/`, los divide en fragmentos de ~800 caracteres, genera embeddings con `intfloat/multilingual-e5-small` y los almacena con metadatos.

### Paso 4 — Iniciar el backend

```bash
uvicorn backend.app:app --reload --port 8000
```

El servidor estará disponible en `http://localhost:8000`. Endpoint de salud: `GET /api/v1/health`.

### Paso 5 — Iniciar el frontend

```bash
cd frontend && npm start
```

La interfaz de chat estará disponible en `http://localhost:3000`.

## Variables de Entorno

Referencia completa en [`.env.example`](.env.example):

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `LLM_PROVIDER` | `huggingface` | Proveedor LLM: `gemini` (recomendado), `huggingface`, `chatgpt`, `groq` |
| `LLM_API_KEY` | — | Clave de API del proveedor seleccionado (requerida) |
| `LLM_MODEL_NAME` | Según proveedor | Identificador del modelo (ej: `gemini-2.5-flash`, `gpt-4o-mini`, `llama-3.3-70b-versatile`) |
| `EMBEDDING_MODEL_NAME` | `intfloat/multilingual-e5-small` | Modelo de embeddings para ETL y recuperación |
| `SIMILARITY_THRESHOLD` | `0.35` | Umbral mínimo de similitud coseno para resultados |
| `CHROMA_PERSIST_DIR` | `./chroma_data` | Directorio de persistencia de ChromaDB |
| `SQLITE_DB_PATH` | `./fin.db` | Ruta al archivo de base de datos SQLite |

### Proveedores LLM soportados

| Proveedor | Modelo por defecto | Clave gratuita |
|-----------|--------------------|----------------|
| Gemini (recomendado) | `gemini-2.5-flash` | [ai.google.dev](https://ai.google.dev) |
| HuggingFace | `meta-llama/Llama-3.1-70B-Instruct` | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) |
| ChatGPT | `gpt-4o-mini` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Groq | `llama-3.3-70b-versatile` | [console.groq.com](https://console.groq.com) |

## Base de Conocimiento

Documentos Markdown en `knowledge_base/` que alimentan el sistema RAG:

| Documento | Tipo | Contenido |
|-----------|------|-----------|
| `estatuto_tributario_libro1.md` | Legal | Impuesto de renta — secciones agrícolas (Art. 23, Art. 57-1) |
| `estatuto_tributario_libro3.md` | Legal | IVA — Art. 258-1, exenciones sobre insumos agrícolas |
| `beneficios_compra_maquinaria.md` | Guía | Beneficios tributarios para compra de maquinaria agrícola |
| `exenciones_pequeno_productor.md` | Guía | Exenciones fiscales para pequeños productores |
| `programas_gobierno_agro.md` | Guía | Programas gubernamentales de apoyo al sector agropecuario |
| `calendario_tributario_2024.md` | Calendario | Fechas clave de obligaciones tributarias 2024 |

Estos documentos deben estar en su lugar antes de ejecutar el pipeline ETL (`scripts/etl_ingest.py`).

## Pruebas

Ejecutar todas las pruebas:

```bash
pytest tests/ -v
```

El proyecto incluye pruebas unitarias y pruebas basadas en propiedades (Hypothesis) para las herramientas de cálculo, el pipeline ETL, la validación de API y la generación de datos mock.

## Estructura del Proyecto

```
RAG-FIN-Topicos-Avanzados/
├── agent/                    # Agente ReAct de LangChain
├── backend/                  # Servidor FastAPI
├── frontend/                 # Interfaz de chat React
├── scripts/                  # Utilidades: ETL, datos mock, ChromaDB
├── knowledge_base/           # Documentos Markdown para RAG
├── tests/                    # Pruebas pytest + hypothesis
├── chroma_data/              # Datos persistentes de ChromaDB
├── project_documentation/    # Documentación del proyecto
├── .env.example              # Plantilla de variables de entorno
├── requirements.txt          # Dependencias de Python
└── README.md                 # Este archivo
```

## READMEs por Carpeta

Cada carpeta principal contiene su propio README con documentación detallada:

- [`agent/README.md`](agent/README.md) — Módulo del agente: proveedores LLM, agente ReAct, herramientas, prompt del sistema
- [`backend/README.md`](backend/README.md) — Backend: aplicación FastAPI, rutas, modelos, middleware
- [`frontend/README.md`](frontend/README.md) — Frontend: interfaz de chat React y componentes
- [`scripts/README.md`](scripts/README.md) — Scripts: ETL, generación de datos mock, inicialización de ChromaDB
- [`knowledge_base/README.md`](knowledge_base/README.md) — Base de conocimiento: documentos Markdown para RAG
