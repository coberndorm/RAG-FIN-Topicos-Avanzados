# scripts/ — Utilidades y Scripts Independientes

Este directorio contiene scripts ejecutables de forma independiente para preparar la infraestructura de datos de FIN-Advisor: generación de datos mock, inicialización de la base vectorial y pipeline ETL de ingesta.

## Contenido

```
scripts/
├── generate_mock_data.py       # Generación de datos financieros sintéticos (SQLite)
├── init_chromadb.py            # Inicialización de la colección ChromaDB
├── etl_ingest.py               # Pipeline ETL: Markdown → chunks → embeddings → ChromaDB
├── embedding_reference.py      # Código de referencia para el modelo de embeddings
├── llm_provider_reference.py   # Código de referencia para proveedores LLM con análisis de costos
└── react_agent_reference.py    # Código de referencia para configuración del agente ReAct
```

## Scripts Principales

### `generate_mock_data.py` — Generación de Datos Mock

Crea la base de datos SQLite `fin.db` con datos financieros sintéticos de un productor agrícola colombiano.

**Ejecución:**
```bash
python scripts/generate_mock_data.py
```

**Qué genera:**
- `perfil_productor` — 1 registro con datos del productor (NIT, tipo de actividad, régimen tributario)
- `movimientos` — 30+ registros de ingresos/egresos cubriendo 6 meses
- `facturas_venta` — 15+ facturas con distribución ~60% PAGADAS, ~30% PENDIENTES, ~10% VENCIDAS
- `cuentas_por_pagar` — 10+ registros de obligaciones con proveedores
- `activos_fijos` — 5-8 activos (maquinaria, terrenos, vehículos, equipos)

**Pre-verificación:** Comprueba que el módulo `sqlite3` esté disponible; si no, imprime instrucciones de instalación según el sistema operativo.

### `init_chromadb.py` — Inicialización de ChromaDB

Crea la colección persistente de ChromaDB con métrica de similitud coseno.

**Ejecución:**
```bash
python scripts/init_chromadb.py
```

**Funciones principales:**
- `obtener_directorio_persistencia()` — Lee `CHROMA_PERSIST_DIR` del entorno (default: `./chroma_data`)
- `inicializar_chromadb()` — Crea o conecta a la colección `tax_laws` con distancia coseno

### `etl_ingest.py` — Pipeline ETL

Procesa los documentos Markdown de `knowledge_base/` y los ingesta en ChromaDB.

**Ejecución:**
```bash
python scripts/etl_ingest.py
```

**Pasos del pipeline:**
1. Lee archivos Markdown desde `knowledge_base/`
2. Divide con `RecursiveCharacterTextSplitter` (800 chars, 10% overlap, separadores: `["\n## ", "\n### ", "\n\n", "\n", " "]`)
3. Preserva números de artículo como metadatos
4. Genera embeddings con `intfloat/multilingual-e5-small` (configurable via `EMBEDDING_MODEL_NAME`)
5. Almacena en ChromaDB con metadatos: `source_document`, `article_number`, `topic_tags`, `document_type`, `date_ingested`, `chunk_index`, `total_chunks_in_article`
6. Deduplicación por `source_document` (no crea duplicados al re-ejecutar)
7. Registra en log: documentos procesados, chunks creados, errores

## Scripts de Referencia

Estos scripts contienen código de referencia y ejemplos de implementación:

| Script | Propósito |
|--------|-----------|
| `embedding_reference.py` | Carga y uso del modelo de embeddings `intfloat/multilingual-e5-small` |
| `llm_provider_reference.py` | Funciones factoría para cada proveedor LLM con notas de costos |
| `react_agent_reference.py` | Configuración del agente ReAct con registro de herramientas |

## Orden de Ejecución

Los scripts deben ejecutarse en este orden antes de iniciar el backend:

```
1. python scripts/generate_mock_data.py   → Crea fin.db
2. python scripts/init_chromadb.py        → Inicializa ChromaDB
3. python scripts/etl_ingest.py           → Ingesta documentos en ChromaDB
```

## Relación con Otros Módulos

- **`knowledge_base/`** — `etl_ingest.py` lee los documentos Markdown de esta carpeta
- **`agent/tools/`** — `get_tax_knowledge` consulta los embeddings generados por `etl_ingest.py`; `query_evergreen_finances` consulta la base SQLite generada por `generate_mock_data.py`
- **`backend/`** — El backend requiere que estos scripts se hayan ejecutado antes de iniciar

## Variables de Entorno

| Variable | Default | Usada por |
|----------|---------|-----------|
| `EMBEDDING_MODEL_NAME` | `intfloat/multilingual-e5-small` | `etl_ingest.py` |
| `CHROMA_PERSIST_DIR` | `./chroma_data` | `init_chromadb.py`, `etl_ingest.py` |
| `SQLITE_DB_PATH` | `./fin.db` | `generate_mock_data.py` |
