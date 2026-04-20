"""
Configuración del agente ReAct de FIN-Advisor.

Crea y configura el agente LangChain/LangGraph ReAct con las 7 herramientas
del sistema, el prompt del sistema cargado desde ``prompt.md`` y
el proveedor de LLM configurado mediante variables de entorno.

El agente usa un máximo de 5 iteraciones de razonamiento (controlado
mediante ``recursion_limit`` en la configuración de invocación) y
manejo robusto de errores de parsing.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph

from agent.llm_providers import ProveedorLLM, crear_proveedor_llm
from agent.tools import TODAS_LAS_HERRAMIENTAS

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
MAX_ITERACIONES: int = 5
"""Número máximo de iteraciones del ciclo ReAct."""

RECURSION_LIMIT: int = MAX_ITERACIONES * 2 + 1
"""Límite de recursión para el grafo (2 nodos por iteración + 1)."""

_RUTA_PROMPT: Path = Path(__file__).resolve().parent / "prompt.md"
"""Ruta al archivo de prompt del sistema."""


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def _cargar_prompt_sistema() -> str:
    """Carga el prompt del sistema desde el archivo ``prompt.md``.

    Returns:
        Contenido del prompt del sistema como cadena de texto.

    Raises:
        FileNotFoundError: Si el archivo ``prompt.md`` no existe.
    """
    if not _RUTA_PROMPT.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de prompt del sistema en: "
            f"{_RUTA_PROMPT}. Asegúrese de que el archivo "
            f"'agent/prompt.md' existe."
        )

    contenido = _RUTA_PROMPT.read_text(encoding="utf-8")
    logger.info("Prompt del sistema cargado desde: %s", _RUTA_PROMPT)
    return contenido


# ---------------------------------------------------------------------------
# Función principal de creación del agente
# ---------------------------------------------------------------------------

def crear_agente(
    proveedor: ProveedorLLM | None = None,
) -> CompiledStateGraph:
    """Crea y configura el agente ReAct de FIN-Advisor.

    Inicializa el agente con las 7 herramientas, el prompt del sistema
    cargado desde ``prompt.md`` y el proveedor de LLM configurado.
    Usa ``langgraph.prebuilt.create_react_agent`` que retorna un
    ``CompiledStateGraph``.

    Para invocar el agente::

        agente = crear_agente()
        resultado = agente.invoke(
            {"messages": [("user", "¿Qué beneficios tributarios tengo?")]},
            config=obtener_config_invocacion(),
        )

    Args:
        proveedor: Instancia de ``ProveedorLLM`` a usar. Si es ``None``,
            se crea uno automáticamente leyendo las variables de entorno.

    Returns:
        ``CompiledStateGraph`` configurado y listo para invocar.

    Raises:
        FileNotFoundError: Si no se encuentra el archivo ``prompt.md``.
        ValueError: Si la configuración del proveedor LLM es inválida.
    """
    # Obtener proveedor de LLM
    if proveedor is None:
        proveedor = crear_proveedor_llm()

    llm = proveedor.obtener_llm()
    logger.info(
        "Agente configurado con proveedor LLM: %s",
        proveedor.obtener_nombre_modelo(),
    )

    # Cargar prompt del sistema
    prompt_sistema = _cargar_prompt_sistema()

    # Crear agente ReAct con langgraph
    herramientas = TODAS_LAS_HERRAMIENTAS
    agente = create_react_agent(
        model=llm,
        tools=herramientas,
        prompt=prompt_sistema,
    )

    logger.info(
        "Agente ReAct creado con %d herramientas y máximo %d iteraciones.",
        len(herramientas),
        MAX_ITERACIONES,
    )

    return agente


def obtener_config_invocacion() -> dict[str, Any]:
    """Retorna la configuración de invocación para el agente.

    Incluye el ``recursion_limit`` que controla el número máximo
    de iteraciones del ciclo ReAct.

    Returns:
        Diccionario de configuración compatible con ``RunnableConfig``.
    """
    return {
        "recursion_limit": RECURSION_LIMIT,
    }
