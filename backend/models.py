"""
Modelos Pydantic para la API del backend de FIN-Advisor.

Define los esquemas de solicitud, respuesta y estado de salud
utilizados por los endpoints de FastAPI.
"""

from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Modelo de solicitud para el endpoint de chat.

    Attributes:
        message: Mensaje del usuario. Debe tener entre 1 y 2000 caracteres.
        session_id: Identificador opcional de sesión para conversaciones
            multi-turno.
    """

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Mensaje del usuario en español",
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Identificador de sesión para contexto multi-turno",
    )


class SourceReference(BaseModel):
    """Referencia a un documento fuente utilizado en la respuesta.

    Attributes:
        article_number: Número de artículo del Estatuto Tributario u otra
            fuente legal referenciada.
        source_document: Nombre del documento fuente.
        topic_tags: Etiquetas temáticas asociadas al fragmento.
    """

    article_number: Optional[str] = Field(
        default=None,
        description="Número de artículo referenciado",
    )
    source_document: str = Field(
        ...,
        description="Nombre del documento fuente",
    )
    topic_tags: list[str] = Field(
        default=[],
        description="Etiquetas temáticas del fragmento",
    )


class ChatResponse(BaseModel):
    """Modelo de respuesta del endpoint de chat.

    Attributes:
        response: Respuesta completa del agente en español.
        sources: Lista de referencias a documentos fuente utilizados.
        tools_used: Lista de nombres de herramientas invocadas durante
            el razonamiento.
    """

    response: str = Field(
        ...,
        description="Respuesta del agente en español",
    )
    sources: list[SourceReference] = Field(
        default=[],
        description="Documentos fuente referenciados",
    )
    tools_used: list[str] = Field(
        default=[],
        description="Herramientas utilizadas durante el razonamiento",
    )


class HealthStatus(BaseModel):
    """Estado de salud del sistema.

    Cada componente puede tener uno de los siguientes estados:
    ``"ok"``, ``"degraded"`` o ``"unavailable"``.

    Attributes:
        backend: Estado del servidor backend.
        vector_store: Estado de la conexión a ChromaDB.
        financial_database: Estado de la conexión a SQLite.
        llm_connection: Estado de la conexión al proveedor de LLM.
    """

    backend: str = Field(
        ...,
        description="Estado del backend: 'ok' | 'degraded' | 'unavailable'",
    )
    vector_store: str = Field(
        ...,
        description="Estado de ChromaDB: 'ok' | 'degraded' | 'unavailable'",
    )
    financial_database: str = Field(
        ...,
        description="Estado de SQLite: 'ok' | 'degraded' | 'unavailable'",
    )
    llm_connection: str = Field(
        ...,
        description="Estado del LLM: 'ok' | 'degraded' | 'unavailable'",
    )
