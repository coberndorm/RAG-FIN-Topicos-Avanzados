"""
Pruebas de rendimiento (benchmarks) para FIN-Advisor.

Mide y registra los tiempos de respuesta del agente ReAct para consultas
simples (una herramienta) y complejas (múltiples herramientas). Los
objetivos de tiempo son benchmarks suaves — las pruebas siempre pasan,
pero emiten advertencias si se exceden los umbrales.

Estas pruebas requieren una conexión activa a un proveedor LLM. Se omiten
automáticamente si la variable de entorno ``LLM_API_KEY`` no está configurada.

Validates: Requirements 26.1, 26.2, 26.3, 26.4
"""

from __future__ import annotations

import logging
import os
import time

import pytest

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Condición de omisión global: sin LLM_API_KEY no se ejecutan las pruebas
# ---------------------------------------------------------------------------

SIN_LLM_API_KEY = not os.environ.get("LLM_API_KEY")
RAZON_OMISION = (
    "Se requiere la variable de entorno LLM_API_KEY para ejecutar "
    "las pruebas de rendimiento con el agente."
)

pytestmark = pytest.mark.skipif(SIN_LLM_API_KEY, reason=RAZON_OMISION)

# ---------------------------------------------------------------------------
# Umbrales de rendimiento (segundos) — benchmarks suaves
# ---------------------------------------------------------------------------

UMBRAL_CONSULTA_SIMPLE: float = 30.0
"""Tiempo objetivo para consultas simples con una sola herramienta."""

UMBRAL_CONSULTA_COMPLEJA: float = 45.0
"""Tiempo objetivo para consultas complejas con múltiples herramientas."""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def agente_y_config():
    """Crea el agente ReAct y su configuración de invocación una sola vez por módulo.

    Returns:
        tuple: ``(agente, config)`` listos para invocar.
    """
    from agent.agent_config import crear_agente, obtener_config_invocacion

    agente = crear_agente()
    config = obtener_config_invocacion()
    return agente, config


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def _invocar_con_medicion(agente_y_config, consulta: str) -> tuple[dict, float]:
    """Invoca el agente midiendo el tiempo de respuesta.

    Args:
        agente_y_config: Tupla ``(agente, config)`` del fixture.
        consulta: Texto de la consulta del usuario.

    Returns:
        Tupla ``(resultado, tiempo_segundos)`` con el resultado del agente
        y el tiempo transcurrido en segundos.
    """
    agente, config = agente_y_config
    inicio = time.time()
    resultado = agente.invoke(
        {"messages": [("user", consulta)]},
        config=config,
    )
    tiempo = time.time() - inicio
    return resultado, tiempo


def _obtener_respuesta_final(resultado: dict) -> str:
    """Obtiene el texto de la respuesta final del agente.

    Args:
        resultado: Resultado de ``agente.invoke()``.

    Returns:
        Texto de la última respuesta del agente.
    """
    from langchain_core.messages import AIMessage

    for msg in reversed(resultado.get("messages", [])):
        if isinstance(msg, AIMessage) and msg.content and isinstance(msg.content, str):
            return msg.content
    return ""


# ---------------------------------------------------------------------------
# Pruebas de rendimiento
# ---------------------------------------------------------------------------

class TestRendimientoConsultaSimple:
    """Benchmark para consultas simples que usan una sola herramienta.

    Validates: Requirements 26.1, 26.4
    """

    def test_consulta_simple_responde_y_mide_tiempo(self, agente_y_config):
        """Mide el tiempo de respuesta para una consulta de saldo actual.

        La consulta ``¿Cuál es mi saldo actual?`` debería invocar una sola
        herramienta (``query_evergreen_finances``). El objetivo es ≤30s,
        pero la prueba siempre pasa — solo emite una advertencia si se
        excede el umbral.
        """
        consulta = "¿Cuál es mi saldo actual?"
        resultado, tiempo = _invocar_con_medicion(agente_y_config, consulta)
        respuesta = _obtener_respuesta_final(resultado)

        # Verificar que el agente retornó una respuesta no vacía (sin timeout)
        assert respuesta.strip(), (
            "El agente debe retornar una respuesta no vacía. "
            "Posible timeout o desconexión."
        )

        # Registrar el tiempo de respuesta
        logger.info(
            "Consulta simple — tiempo: %.2fs (objetivo: ≤%.0fs)",
            tiempo,
            UMBRAL_CONSULTA_SIMPLE,
        )

        # Emitir advertencia si se excede el umbral (benchmark suave)
        if tiempo > UMBRAL_CONSULTA_SIMPLE:
            logger.warning(
                "⚠️ Consulta simple excedió el objetivo de rendimiento: "
                "%.2fs > %.0fs. Consulta: '%s'",
                tiempo,
                UMBRAL_CONSULTA_SIMPLE,
                consulta,
            )


class TestRendimientoConsultaCompleja:
    """Benchmark para consultas complejas que usan múltiples herramientas.

    Validates: Requirements 26.2, 26.4
    """

    def test_consulta_compleja_responde_y_mide_tiempo(self, agente_y_config):
        """Mide el tiempo de respuesta para una consulta multi-herramienta.

        La consulta sobre viabilidad de compra de un tractor debería invocar
        múltiples herramientas (``query_evergreen_finances``,
        ``calculate_vat_discount``, ``assess_investment_viability``,
        ``get_tax_knowledge``). El objetivo es ≤45s, pero la prueba siempre
        pasa — solo emite una advertencia si se excede el umbral.
        """
        consulta = (
            "Quiero comprar un tractor de $80M, ¿es viable? "
            "¿Qué beneficios tributarios aplican?"
        )
        resultado, tiempo = _invocar_con_medicion(agente_y_config, consulta)
        respuesta = _obtener_respuesta_final(resultado)

        # Verificar que el agente retornó una respuesta no vacía (sin timeout)
        assert respuesta.strip(), (
            "El agente debe retornar una respuesta no vacía. "
            "Posible timeout o desconexión."
        )

        # Registrar el tiempo de respuesta
        logger.info(
            "Consulta compleja — tiempo: %.2fs (objetivo: ≤%.0fs)",
            tiempo,
            UMBRAL_CONSULTA_COMPLEJA,
        )

        # Emitir advertencia si se excede el umbral (benchmark suave)
        if tiempo > UMBRAL_CONSULTA_COMPLEJA:
            logger.warning(
                "⚠️ Consulta compleja excedió el objetivo de rendimiento: "
                "%.2fs > %.0fs. Consulta: '%s'",
                tiempo,
                UMBRAL_CONSULTA_COMPLEJA,
                consulta,
            )
