---
name: Contexto Carpeta Scripts
description: Guía para la carpeta scripts/ — Utilidades independientes para ETL, generación de datos mock, inicialización de ChromaDB y código de referencia.
inclusion: fileMatch
fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/scripts/**'
---

# Carpeta `scripts/` — Utilidades Independientes

## Propósito

Esta carpeta contiene scripts ejecutables de forma independiente para preparar el entorno de datos del sistema FIN-Advisor: pipeline ETL, generación de datos mock, inicialización de ChromaDB y código de referencia para embeddings, proveedores LLM y agente ReAct.

## Scripts y Roles

| Script | Rol |
|---|---|
| `etl_ingest.py` | Pipeline ETL: lee Markdown de `knowledge_base/`, divide con `RecursiveCharacterTextSplitter` (800 chars, 10% overlap), genera embeddings con modelo configurable, almacena en ChromaDB con metadatos. Dedup por `source_document` |
| `generate_mock_data.py` | Genera `fin.db` con datos sintéticos: 1 perfil, 30+ movimientos (6 meses), 15+ facturas (60/30/10% PAID/PENDING/OVERDUE), 10+ cuentas por pagar, 5-8 activos fijos |
| `init_chromadb.py` | Inicializa colección ChromaDB persistente con métrica de similitud coseno |
| `embedding_reference.py` | Código de referencia para cargar y usar modelos de embeddings soportados |
| `llm_provider_reference.py` | Factory de proveedores LLM con análisis de costos |
| `react_agent_reference.py` | Setup del agente ReAct con registro de herramientas |

## Configuración del ETL

- **Chunking:** `RecursiveCharacterTextSplitter` con separadores `["\n## ", "\n### ", "\n\n", "\n", " "]`.
- **Tamaño de chunk:** 800 chars (rango aceptable: 500-1000), overlap 10%.
- **Modelo de embeddings:** Configurable vía `EMBEDDING_MODEL_NAME` (default: `intfloat/multilingual-e5-small`).
- **Metadatos por chunk:** `source_document`, `article_number`, `topic_tags`, `document_type`, `date_ingested`, `chunk_index`, `total_chunks_in_article`.
- **Idempotencia:** Dedup por `source_document` — no crea duplicados al re-ejecutar.

## Schema SQLite para Datos Mock

5 tablas: `perfil_productor`, `movimientos`, `facturas_venta`, `cuentas_por_pagar`, `activos_fijos`.
- Tipos de movimiento: `INGRESO` / `EGRESO`.
- Estados de factura: `PAID` / `PENDING` / `OVERDUE`.
- Categorías de activos: `MAQUINARIA` / `TERRENO` / `VEHICULO` / `EQUIPO`.
- Datos realistas del contexto agropecuario colombiano.

## Relaciones con Otros Módulos

- **`knowledge_base/`** — fuente de documentos Markdown para `etl_ingest.py`.
- **`agent/tools/get_tax_knowledge.py`** — consume los embeddings almacenados por el ETL en ChromaDB.
- **`agent/tools/query_evergreen_finances.py`** — consulta la base SQLite generada por `generate_mock_data.py`.
- **`agent/`** — los scripts de referencia documentan patrones usados en `agent_config.py` y `llm_providers.py`.

## Restricciones

- Cada script debe ser ejecutable de forma independiente desde la línea de comandos.
- `generate_mock_data.py` verifica disponibilidad de `sqlite3` al inicio.
- El ETL registra: documentos procesados, chunks creados, errores encontrados.
- SQL siempre parametrizado con `?` placeholders.
