---
name: Contexto Carpeta Backend
description: Guía para la carpeta backend/ — Servidor FastAPI, endpoints, modelos Pydantic y middleware CORS.
inclusion: fileMatch
fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/backend/**'
---

# Carpeta `backend/` — Servidor FastAPI

## Propósito

Esta carpeta contiene el servidor FastAPI que expone la API REST del asistente FIN-Advisor. Recibe consultas del frontend React, invoca el agente ReAct y retorna respuestas estructuradas en JSON.

## Layout de Módulos

| Archivo | Responsabilidad |
|---|---|
| `app.py` | Factory de la aplicación FastAPI; inicializa conexiones a ChromaDB, SQLite y proveedor LLM al arrancar |
| `routes.py` | Endpoints: `POST /api/v1/chat` (consulta al agente) y `GET /api/v1/health` (estado del sistema) |
| `models.py` | Modelos Pydantic: `ChatRequest`, `ChatResponse`, `SourceReference`, `HealthStatus` |
| `middleware.py` | Configuración CORS permitiendo requests desde `http://localhost:3000` |

## Comunicación HTTP (MVP)

- El MVP usa **request/response HTTP estándar** (POST → JSON).
- **SSE streaming diferido a Fase 2** — no implementar streaming en esta fase.
- Endpoint único de chat: `POST /api/v1/chat` con body `{ "message": string, "session_id"?: string }`.
- Respuesta: `{ "response": string, "sources": [...], "tools_used": [...] }`.

## Gestión de Sesiones

- Si se proporciona `session_id` → mantener historial de conversación en memoria.
- Sin `session_id` → interacción de un solo turno.
- No se requiere persistencia entre reinicios para el MVP.

## Comportamiento al Arrancar

1. Inicializar conexión a ChromaDB (persistente local).
2. Inicializar conexión a SQLite (`fin.db`).
3. Inicializar proveedor LLM configurado.
4. Si LLM inalcanzable → log warning, arrancar en modo degradado.
5. Si API key requerida pero ausente → fallar con error claro.

## Relaciones con Otros Módulos

- **Agent (`agent/agent_config.py`)** — importado para crear y ejecutar el agente ReAct.
- **Frontend** — se comunica vía HTTP; CORS configurado para `localhost:3000`.
- **ChromaDB y SQLite** — conexiones inicializadas en `app.py`, usadas por el agente.

## Restricciones y Convenciones

- Validación de requests con **Pydantic** (HTTP 422 para payloads inválidos).
- `message`: min_length=1, max_length=2000.
- Health endpoint reporta estado de: backend, vector_store, financial_database, llm_connection.
- Errores del LLM durante request → HTTP 500 con mensaje en español.
- Docstrings en español, formato Google-style.
- Type hints obligatorios.
