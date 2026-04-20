"""
Pruebas de integración (smoke tests) para las historias de usuario de FIN-Advisor.

Cada prueba invoca el agente ReAct con una consulta representativa y valida
la estructura de la respuesta y el uso de herramientas esperadas.

Estas pruebas requieren una conexión activa a un proveedor LLM. Se omiten
automáticamente si la variable de entorno ``LLM_API_KEY`` no está configurada.
"""

from __future__ import annotations

import os

import pytest
from langchain_core.messages import ToolMessage

# ---------------------------------------------------------------------------
# Condición de omisión global: sin LLM_API_KEY no se ejecutan las pruebas
# ---------------------------------------------------------------------------

SIN_LLM_API_KEY = not os.environ.get("LLM_API_KEY")
RAZON_OMISION = (
    "Se requiere la variable de entorno LLM_API_KEY para ejecutar "
    "las pruebas de integración con el agente."
)

pytestmark = pytest.mark.skipif(SIN_LLM_API_KEY, reason=RAZON_OMISION)


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


def _invocar_agente(agente_y_config, consulta: str) -> dict:
    """Invoca el agente con una consulta y retorna el resultado.

    Args:
        agente_y_config: Tupla ``(agente, config)`` del fixture.
        consulta: Texto de la consulta del usuario.

    Returns:
        Diccionario con las claves ``messages`` del resultado del agente.
    """
    agente, config = agente_y_config
    return agente.invoke(
        {"messages": [("user", consulta)]},
        config=config,
    )


def _extraer_herramientas(resultado: dict) -> list[str]:
    """Extrae los nombres de herramientas usadas desde los mensajes del resultado.

    Args:
        resultado: Resultado de ``agente.invoke()``.

    Returns:
        Lista de nombres de herramientas invocadas.
    """
    return [
        msg.name
        for msg in resultado.get("messages", [])
        if isinstance(msg, ToolMessage)
    ]


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
# US-01: Consulta sobre beneficios tributarios
# ---------------------------------------------------------------------------

class TestUS01BeneficiosTributarios:
    """Pruebas para la historia de usuario US-01: Consulta de beneficios tributarios."""

    def test_invoca_get_tax_knowledge(self, agente_y_config):
        """Verifica que el agente invoca get_tax_knowledge al preguntar sobre beneficios."""
        resultado = _invocar_agente(
            agente_y_config,
            "¿Qué beneficios tributarios tengo como productor agrícola?",
        )
        herramientas = _extraer_herramientas(resultado)
        assert "get_tax_knowledge" in herramientas, (
            "El agente debe invocar get_tax_knowledge para consultas tributarias."
        )

    def test_respuesta_contiene_articulo(self, agente_y_config):
        """Verifica que la respuesta incluye al menos un número de artículo."""
        resultado = _invocar_agente(
            agente_y_config,
            "¿Qué beneficios tributarios tengo como productor agrícola?",
        )
        respuesta = _obtener_respuesta_final(resultado)
        # Buscar patrones como "Artículo 258-1", "Art. 57-1", "artículo 23"
        import re
        patron_articulo = re.compile(r"[Aa]rt[íi]culo\s+\d+", re.IGNORECASE)
        assert patron_articulo.search(respuesta), (
            f"La respuesta debe contener al menos un número de artículo. "
            f"Respuesta: {respuesta[:300]}"
        )

    def test_respuesta_incluye_descargo(self, agente_y_config):
        """Verifica que la respuesta incluye un descargo de responsabilidad."""
        resultado = _invocar_agente(
            agente_y_config,
            "¿Qué beneficios tributarios tengo como productor agrícola?",
        )
        respuesta = _obtener_respuesta_final(resultado).lower()
        palabras_descargo = ["nota", "orientativa", "asesor", "contador", "profesional"]
        assert any(p in respuesta for p in palabras_descargo), (
            "La respuesta debe incluir un descargo de responsabilidad financiera."
        )


# ---------------------------------------------------------------------------
# US-02: Diagnóstico de flujo de caja
# ---------------------------------------------------------------------------

class TestUS02FlujoDeCaja:
    """Pruebas para la historia de usuario US-02: Diagnóstico de flujo de caja."""

    def test_invoca_query_evergreen_finances(self, agente_y_config):
        """Verifica que el agente consulta datos financieros para flujo de caja."""
        resultado = _invocar_agente(
            agente_y_config,
            "¿Cómo está mi flujo de caja actualmente?",
        )
        herramientas = _extraer_herramientas(resultado)
        assert "query_evergreen_finances" in herramientas, (
            "El agente debe invocar query_evergreen_finances para consultas de flujo de caja."
        )

    def test_respuesta_contiene_cifras_cop(self, agente_y_config):
        """Verifica que la respuesta contiene cifras monetarias en COP."""
        resultado = _invocar_agente(
            agente_y_config,
            "¿Cómo está mi flujo de caja actualmente?",
        )
        respuesta = _obtener_respuesta_final(resultado)
        import re
        # Buscar patrones monetarios: $1.500.000, 1,500,000 COP, etc.
        patron_cop = re.compile(
            r"(\$[\d.,]+|\d{1,3}([.,]\d{3})+)\s*(COP)?",
        )
        assert patron_cop.search(respuesta), (
            f"La respuesta debe contener cifras monetarias en COP. "
            f"Respuesta: {respuesta[:300]}"
        )


# ---------------------------------------------------------------------------
# US-03: Viabilidad de compra de activo fijo
# ---------------------------------------------------------------------------

class TestUS03CompraActivoFijo:
    """Pruebas para la historia de usuario US-03: Compra de activo fijo (tractor)."""

    def test_invoca_herramientas_de_calculo(self, agente_y_config):
        """Verifica que el agente usa calculate_vat_discount y assess_investment_viability."""
        resultado = _invocar_agente(
            agente_y_config,
            "Quiero comprar un tractor de $80.000.000 COP. ¿Es viable financieramente?",
        )
        herramientas = _extraer_herramientas(resultado)
        assert "calculate_vat_discount" in herramientas, (
            "El agente debe invocar calculate_vat_discount para compras de activos."
        )
        assert "assess_investment_viability" in herramientas, (
            "El agente debe invocar assess_investment_viability para evaluar viabilidad."
        )


# ---------------------------------------------------------------------------
# US-04: Calendario tributario
# ---------------------------------------------------------------------------

class TestUS04CalendarioTributario:
    """Pruebas para la historia de usuario US-04: Consulta de calendario tributario."""

    def test_invoca_get_tax_knowledge(self, agente_y_config):
        """Verifica que el agente busca en la base de conocimiento tributaria."""
        resultado = _invocar_agente(
            agente_y_config,
            "¿Cuáles son las próximas fechas límite para declarar impuestos?",
        )
        herramientas = _extraer_herramientas(resultado)
        assert "get_tax_knowledge" in herramientas, (
            "El agente debe invocar get_tax_knowledge para consultas del calendario tributario."
        )

    def test_respuesta_contiene_fechas(self, agente_y_config):
        """Verifica que la respuesta contiene fechas cronológicas."""
        resultado = _invocar_agente(
            agente_y_config,
            "¿Cuáles son las próximas fechas límite para declarar impuestos?",
        )
        respuesta = _obtener_respuesta_final(resultado)
        import re
        # Buscar patrones de fecha: "agosto 2024", "15 de marzo", "2024-08-15", etc.
        patron_fecha = re.compile(
            r"(\d{1,2}\s+de\s+\w+|"
            r"(enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
            r"septiembre|octubre|noviembre|diciembre)\s*\d{0,4}|"
            r"\d{4}[-/]\d{2}[-/]\d{2})",
            re.IGNORECASE,
        )
        assert patron_fecha.search(respuesta), (
            f"La respuesta debe contener fechas. Respuesta: {respuesta[:300]}"
        )


# ---------------------------------------------------------------------------
# US-05: Explicación de concepto contable
# ---------------------------------------------------------------------------

class TestUS05ExplicacionConcepto:
    """Pruebas para la historia de usuario US-05: Explicación de conceptos financieros."""

    def test_respuesta_concisa(self, agente_y_config):
        """Verifica que la explicación de un concepto simple es menor a 200 palabras."""
        resultado = _invocar_agente(
            agente_y_config,
            "¿Qué es la depreciación?",
        )
        respuesta = _obtener_respuesta_final(resultado)
        num_palabras = len(respuesta.split())
        assert num_palabras <= 200, (
            f"La explicación de un concepto simple debe ser menor a 200 palabras. "
            f"Se obtuvieron {num_palabras} palabras."
        )


# ---------------------------------------------------------------------------
# US-06: Optimización de gastos
# ---------------------------------------------------------------------------

class TestUS06OptimizacionGastos:
    """Pruebas para la historia de usuario US-06: Análisis y optimización de gastos."""

    def test_invoca_query_con_expense_summary(self, agente_y_config):
        """Verifica que el agente consulta el resumen de egresos."""
        resultado = _invocar_agente(
            agente_y_config,
            "Analiza mis gastos recientes y sugiere dónde puedo ahorrar.",
        )
        herramientas = _extraer_herramientas(resultado)
        assert "query_evergreen_finances" in herramientas, (
            "El agente debe invocar query_evergreen_finances para análisis de gastos."
        )
        # Verificar que se usó con expense_summary revisando los mensajes
        from langchain_core.messages import AIMessage
        mensajes = resultado.get("messages", [])
        tool_calls_args = []
        for msg in mensajes:
            if isinstance(msg, AIMessage) and hasattr(msg, "tool_calls"):
                for tc in (msg.tool_calls or []):
                    if tc.get("name") == "query_evergreen_finances":
                        tool_calls_args.append(tc.get("args", {}))

        tiene_expense_summary = any(
            args.get("query_type") == "expense_summary"
            for args in tool_calls_args
        )
        assert tiene_expense_summary, (
            "El agente debe invocar query_evergreen_finances con query_type='expense_summary'."
        )


# ---------------------------------------------------------------------------
# Pruebas de rechazo fuera de alcance (Task 17.2)
# ---------------------------------------------------------------------------

class TestFueraDeAlcance:
    """Pruebas de rechazo para consultas fuera del alcance del agente.

    Verifica que el agente declina amablemente en español cuando recibe
    consultas sobre temas no relacionados con finanzas agrícolas colombianas.
    """

    @pytest.mark.parametrize(
        "consulta,tema",
        [
            (
                "¿Debería invertir en acciones de Tesla o Amazon?",
                "bolsa de valores",
            ),
            (
                "Tengo dolor de cabeza frecuente, ¿qué medicamento me recomiendas?",
                "salud",
            ),
            (
                "¿Qué opinas de las próximas elecciones presidenciales en Colombia?",
                "política",
            ),
        ],
        ids=["acciones_bolsa", "salud_medicina", "politica_electoral"],
    )
    def test_declina_consulta_fuera_de_alcance(
        self, agente_y_config, consulta: str, tema: str
    ):
        """Verifica que el agente declina consultas sobre {tema} de forma cortés en español.

        Args:
            agente_y_config: Fixture con el agente y su configuración.
            consulta: Texto de la consulta fuera de alcance.
            tema: Descripción del tema para mensajes de error.
        """
        resultado = _invocar_agente(agente_y_config, consulta)
        respuesta = _obtener_respuesta_final(resultado).lower()

        # Verificar que la respuesta está en español (contiene palabras comunes)
        palabras_espanol = ["no", "puedo", "ayudar", "tema", "alcance", "especializ"]
        contiene_espanol = any(p in respuesta for p in palabras_espanol)
        assert contiene_espanol, (
            f"La respuesta a una consulta sobre '{tema}' debe estar en español. "
            f"Respuesta: {respuesta[:300]}"
        )

        # Verificar que el agente menciona los temas en los que SÍ puede ayudar
        temas_validos = [
            "tributar", "financier", "agr", "impuesto", "contab",
            "fiscal", "iva", "renta", "evergreen",
        ]
        menciona_alcance = any(t in respuesta for t in temas_validos)
        assert menciona_alcance, (
            f"Al declinar una consulta sobre '{tema}', el agente debe listar "
            f"los temas en los que sí puede ayudar. Respuesta: {respuesta[:300]}"
        )
