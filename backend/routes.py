"""
Rutas de la API de FIN-Advisor.

Define los endpoints ``POST /api/v1/chat`` y ``GET /api/v1/health``
para el backend FastAPI. Incluye gestión de sesiones en memoria
para conversaciones multi-turno.
"""

from __future__ import annotations

import logging
import sqlite3
from typing import Any

from fastapi import APIRouter, Request
from langchain_core.messages import AIMessage, ToolMessage

from backend.models import (
    ChatRequest,
    ChatResponse,
    HealthStatus,
    SourceReference,
)

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/api/v1")
"""Router principal de la API v1."""

# ---------------------------------------------------------------------------
# Almacén de sesiones en memoria
# ---------------------------------------------------------------------------
_historial_sesiones: dict[str, list[tuple[str, str]]] = {}
"""Historial de conversaciones por session_id.

Cada entrada es una lista de tuplas ``(rol, contenido)`` donde
``rol`` es ``"user"`` o ``"assistant"``.
"""


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def _extraer_herramientas_usadas(mensajes: list[Any]) -> list[str]:
    """Extrae los nombres de herramientas invocadas desde los mensajes del agente.

    Recorre la lista de mensajes del resultado de LangGraph y recopila
    los nombres de las herramientas que fueron llamadas durante el
    ciclo de razonamiento ReAct.

    Args:
        mensajes: Lista de mensajes retornados por ``agente.invoke()``.

    Returns:
        Lista de nombres de herramientas únicas utilizadas, en orden
        de primera aparición.
    """
    herramientas: list[str] = []
    vistas: set[str] = set()

    for msg in mensajes:
        # Los mensajes de herramienta (ToolMessage) contienen el nombre
        if isinstance(msg, ToolMessage) and msg.name:
            if msg.name not in vistas:
                herramientas.append(msg.name)
                vistas.add(msg.name)
        # Los AIMessage pueden tener tool_calls
        elif isinstance(msg, AIMessage) and hasattr(msg, "tool_calls"):
            for tool_call in (msg.tool_calls or []):
                nombre = tool_call.get("name", "")
                if nombre and nombre not in vistas:
                    herramientas.append(nombre)
                    vistas.add(nombre)

    return herramientas


def _extraer_fuentes(mensajes: list[Any]) -> list[SourceReference]:
    """Extrae referencias a fuentes desde los mensajes de herramientas.

    Busca en los mensajes de tipo ``ToolMessage`` con nombre
    ``get_tax_knowledge`` para extraer las fuentes documentales
    referenciadas en la respuesta.

    Args:
        mensajes: Lista de mensajes retornados por ``agente.invoke()``.

    Returns:
        Lista de ``SourceReference`` con las fuentes encontradas.
    """
    fuentes: list[SourceReference] = []
    documentos_vistos: set[str] = set()

    for msg in mensajes:
        if not isinstance(msg, ToolMessage):
            continue
        if msg.name != "get_tax_knowledge":
            continue

        # Intentar parsear el contenido como JSON
        try:
            import json
            contenido = msg.content
            if isinstance(contenido, str):
                datos = json.loads(contenido)
            else:
                datos = contenido

            # El resultado puede ser una lista de chunks o un dict con resultados
            resultados = []
            if isinstance(datos, list):
                resultados = datos
            elif isinstance(datos, dict):
                resultados = datos.get("resultados", datos.get("results", []))
                # Si es un solo resultado con source_document
                if "source_document" in datos:
                    resultados = [datos]

            for resultado in resultados:
                if not isinstance(resultado, dict):
                    continue
                doc = resultado.get("source_document", "")
                if doc and doc not in documentos_vistos:
                    documentos_vistos.add(doc)
                    tags_raw = resultado.get("topic_tags", [])
                    if isinstance(tags_raw, str):
                        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
                    else:
                        tags = tags_raw

                    fuentes.append(SourceReference(
                        article_number=resultado.get("article_number") or None,
                        source_document=doc,
                        topic_tags=tags,
                    ))
        except (json.JSONDecodeError, TypeError, AttributeError):
            logger.debug(
                "No se pudo parsear contenido de get_tax_knowledge: %s",
                msg.content[:200] if isinstance(msg.content, str) else str(msg.content)[:200],
            )

    return fuentes


def _obtener_respuesta_final(mensajes: list[Any]) -> str:
    """Extrae la respuesta final del agente desde los mensajes.

    Busca el último mensaje de tipo ``AIMessage`` que no sea una
    llamada a herramienta para obtener la respuesta textual final.

    Args:
        mensajes: Lista de mensajes retornados por ``agente.invoke()``.

    Returns:
        Texto de la respuesta final del agente.
    """
    for msg in reversed(mensajes):
        if isinstance(msg, AIMessage):
            contenido = msg.content
            # Gemini may return content as a list of dicts
            if isinstance(contenido, list):
                partes_texto = []
                for parte in contenido:
                    if isinstance(parte, dict) and parte.get("type") == "text":
                        partes_texto.append(parte["text"])
                    elif isinstance(parte, str):
                        partes_texto.append(parte)
                contenido = "\n".join(partes_texto)
            if contenido and isinstance(contenido, str) and contenido.strip():
                return contenido
    return "No se pudo generar una respuesta. Intenta de nuevo."


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, req: Request) -> ChatResponse:
    """Procesa una consulta del usuario mediante el agente ReAct.

    Valida la solicitud, construye el historial de mensajes si hay
    una sesión activa, invoca al agente y retorna la respuesta
    con fuentes y herramientas utilizadas.

    Args:
        request: Solicitud de chat validada por Pydantic.
        req: Objeto Request de FastAPI para acceder a ``app.state``.

    Returns:
        Respuesta del agente con texto, fuentes y herramientas.
    """
    # Verificar que el agente esté disponible
    agente = getattr(req.app.state, "agente", None)
    if agente is None:
        return ChatResponse(
            response="El servicio no está disponible en este momento. "
                     "El modelo de lenguaje no se pudo inicializar.",
            sources=[],
            tools_used=[],
        )

    config_invocacion = getattr(req.app.state, "config_invocacion", {})

    # Construir mensajes con historial de sesión
    mensajes: list[tuple[str, str]] = []

    if request.session_id and request.session_id in _historial_sesiones:
        mensajes.extend(_historial_sesiones[request.session_id])

    mensajes.append(("user", request.message))

    try:
        # Retry logic for intermittent Groq tool-calling format errors
        max_retries = 2
        last_error = None
        for attempt in range(max_retries):
            try:
                resultado = agente.invoke(
                    {"messages": mensajes},
                    config=config_invocacion,
                )
                break
            except Exception as e:
                error_msg = str(e)
                if "tool_use_failed" in error_msg or "Failed to call a function" in error_msg:
                    last_error = e
                    logger.warning(
                        "Reintentando invocación del agente (intento %d/%d) "
                        "por error de formato de herramienta.",
                        attempt + 1, max_retries,
                    )
                    continue
                raise
        else:
            raise last_error

        mensajes_resultado = resultado.get("messages", [])

        # Extraer componentes de la respuesta
        respuesta_texto = _obtener_respuesta_final(mensajes_resultado)
        herramientas = _extraer_herramientas_usadas(mensajes_resultado)
        fuentes = _extraer_fuentes(mensajes_resultado)

        # Actualizar historial de sesión
        if request.session_id:
            if request.session_id not in _historial_sesiones:
                _historial_sesiones[request.session_id] = []
            _historial_sesiones[request.session_id].append(
                ("user", request.message)
            )
            _historial_sesiones[request.session_id].append(
                ("assistant", respuesta_texto)
            )

        return ChatResponse(
            response=respuesta_texto,
            sources=fuentes,
            tools_used=herramientas,
        )

    except Exception:
        logger.exception("Error al procesar la consulta del usuario.")
        return ChatResponse(
            response="Error al procesar tu consulta. Intenta de nuevo.",
            sources=[],
            tools_used=[],
        )


@router.get("/health", response_model=HealthStatus)
async def health(req: Request) -> HealthStatus:
    """Verifica el estado de salud de todos los componentes del sistema.

    Comprueba la conectividad con ChromaDB, SQLite y el proveedor
    de LLM, retornando el estado de cada componente.

    Args:
        req: Objeto Request de FastAPI para acceder a ``app.state``.

    Returns:
        Estado de salud con el estado de cada componente.
    """
    estado_backend = "ok"
    estado_vector_store = "unavailable"
    estado_base_datos = "unavailable"
    estado_llm = "unavailable"

    # Verificar ChromaDB
    try:
        cliente_chroma = getattr(req.app.state, "chroma_client", None)
        if cliente_chroma is not None:
            # Intentar listar colecciones para verificar conectividad
            cliente_chroma.list_collections()
            estado_vector_store = "ok"
    except Exception:
        logger.warning("ChromaDB no disponible en health check.")
        estado_vector_store = "unavailable"

    # Verificar SQLite
    try:
        ruta_db = getattr(req.app.state, "sqlite_db_path", None)
        if ruta_db is not None:
            conn = sqlite3.connect(ruta_db)
            conn.execute("SELECT 1")
            conn.close()
            estado_base_datos = "ok"
    except Exception:
        logger.warning("SQLite no disponible en health check.")
        estado_base_datos = "unavailable"

    # Verificar LLM
    try:
        agente = getattr(req.app.state, "agente", None)
        modo_degradado = getattr(req.app.state, "modo_degradado", False)
        if agente is not None and not modo_degradado:
            estado_llm = "ok"
        elif modo_degradado:
            estado_llm = "degraded"
    except Exception:
        logger.warning("LLM no disponible en health check.")
        estado_llm = "unavailable"

    # Si algún componente no está ok, el backend está degradado
    estados = [estado_vector_store, estado_base_datos, estado_llm]
    if any(e == "unavailable" for e in estados):
        estado_backend = "degraded"

    return HealthStatus(
        backend=estado_backend,
        vector_store=estado_vector_store,
        financial_database=estado_base_datos,
        llm_connection=estado_llm,
    )
