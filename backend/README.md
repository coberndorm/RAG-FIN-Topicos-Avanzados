# backend/ — Servidor FastAPI

Este directorio contiene el servidor backend de FIN-Advisor, implementado con **FastAPI**. Expone la API REST que conecta la interfaz de chat React con el agente ReAct de LangChain.

## Contenido

```
backend/
├── __init__.py      # Exportaciones del paquete
├── app.py           # Fábrica de la aplicación FastAPI y evento de startup
├── routes.py        # Endpoints: POST /api/v1/chat, GET /api/v1/health
├── models.py        # Modelos Pydantic de request/response
└── middleware.py     # Configuración de CORS
```

## Componentes

### `app.py` — Aplicación FastAPI

Fábrica de la aplicación con evento de ciclo de vida (`lifespan`) que inicializa:

1. **Conexión a ChromaDB** — Base vectorial persistente local
2. **Conexión a SQLite** — Base de datos financiera `fin.db`
3. **Proveedor LLM** — Lee `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL_NAME` del entorno
4. **Agente ReAct** — Creado con las 7 herramientas registradas

Comportamiento de inicio:
- Si el LLM no es alcanzable → registra advertencia, inicia en modo degradado
- Si falta la clave de API requerida → falla con error descriptivo

### `routes.py` — Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/chat` | Recibe consulta del usuario, invoca el agente ReAct, retorna respuesta |
| `GET` | `/api/v1/health` | Estado del backend, vector_store, financial_database, llm_connection |

**Endpoint de chat:**
- Valida la petición con `ChatRequest` (Pydantic)
- Gestiona sesiones: si se proporciona `session_id`, mantiene historial de conversación en memoria
- Sin `session_id` → interacción de un solo turno
- Extrae herramientas usadas, fuentes referenciadas y respuesta final del agente

**Funciones auxiliares:**
- `_extraer_herramientas_usadas()` — Extrae nombres de herramientas invocadas durante el razonamiento
- `_extraer_fuentes()` — Extrae referencias a documentos citados
- `_obtener_respuesta_final()` — Obtiene la respuesta final del agente

### `models.py` — Modelos Pydantic

```python
ChatRequest       # message (str, 1-2000 chars), session_id (str, opcional)
ChatResponse      # response (str), sources (list[SourceReference]), tools_used (list[str])
SourceReference   # article_number (str?), source_document (str), topic_tags (list[str])
HealthStatus      # backend, vector_store, financial_database, llm_connection (str cada uno)
```

Todos los modelos incluyen type hints y docstrings en español estilo Google.

### `middleware.py` — CORS

Configura CORS para permitir peticiones desde el frontend React (`http://localhost:3000`).

## Contrato de la API

**Request:**
```json
POST /api/v1/chat
{
  "message": "¿Qué beneficios tributarios tengo como productor agrícola?",
  "session_id": "abc-123"
}
```

**Response (200):**
```json
{
  "response": "Según el Artículo 57-1 del Estatuto Tributario...",
  "sources": [
    {
      "article_number": "57-1",
      "source_document": "estatuto_tributario_libro1.md",
      "topic_tags": ["renta", "exención", "agrícola"]
    }
  ],
  "tools_used": ["get_tax_knowledge", "query_evergreen_finances"]
}
```

**Error (422):**
```json
{
  "detail": [{"loc": ["body", "message"], "msg": "field required", "type": "value_error.missing"}]
}
```

## Relación con Otros Módulos

- **`agent/`** — El backend importa `crear_agente()` y `crear_proveedor_llm()` para inicializar el agente durante el startup
- **`frontend/`** — El frontend envía peticiones HTTP a los endpoints definidos aquí
- **`scripts/`** — Los scripts de inicialización (`init_chromadb.py`, `generate_mock_data.py`) deben ejecutarse antes de iniciar el backend

## Cómo Ejecutar

```bash
# Desde la raíz del proyecto (RAG-FIN-Topicos-Avanzados/)
uvicorn backend.app:app --reload --port 8000
```

El servidor estará disponible en `http://localhost:8000`.

**Prerequisitos:**
1. Archivo `.env` configurado con las variables de entorno (ver `.env.example`)
2. Base de datos `fin.db` generada (`python scripts/generate_mock_data.py`)
3. ChromaDB inicializado y con datos (`python scripts/init_chromadb.py` + `python scripts/etl_ingest.py`)
