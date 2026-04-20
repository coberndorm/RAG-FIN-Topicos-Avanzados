"""
Herramientas del agente ReAct de FIN-Advisor.

Incluye herramientas de recuperación (knowledge base, datos financieros)
y herramientas de cálculo (IVA, liquidez, viabilidad, impuestos, depreciación).

Exporta las 7 herramientas como definiciones compatibles con LangChain
usando ``@tool`` decorator para integración directa con el agente ReAct.
"""

from __future__ import annotations

import json
from typing import Any

from langchain_core.tools import tool

from agent.tools.get_tax_knowledge import get_tax_knowledge as _get_tax_knowledge
from agent.tools.query_evergreen_finances import (
    query_evergreen_finances as _query_evergreen_finances,
)
from agent.tools.calculate_vat_discount import (
    calculate_vat_discount as _calculate_vat_discount,
)
from agent.tools.calculate_net_liquidity import (
    calculate_net_liquidity as _calculate_net_liquidity,
)
from agent.tools.assess_investment_viability import (
    assess_investment_viability as _assess_investment_viability,
)
from agent.tools.project_tax_liability import (
    project_tax_liability as _project_tax_liability,
)
from agent.tools.calculate_depreciation import (
    calculate_depreciation as _calculate_depreciation,
)


# ---------------------------------------------------------------------------
# Herramientas LangChain (decoradas con @tool)
# ---------------------------------------------------------------------------

@tool
def get_tax_knowledge(query: str) -> str:
    """Busca fragmentos relevantes en la base de conocimiento tributaria colombiana.

    Realiza búsqueda por similitud coseno en ChromaDB para encontrar
    artículos del Estatuto Tributario, guías de beneficios y programas
    gubernamentales relevantes a la consulta del usuario.

    Args:
        query: Consulta de búsqueda en texto libre sobre normativa
            tributaria colombiana para el sector agropecuario.

    Returns:
        Resultados de la búsqueda en formato JSON con los fragmentos
        más relevantes y sus metadatos (artículo, fuente, etiquetas).
    """
    resultado = _get_tax_knowledge(query=query)
    return json.dumps(resultado, ensure_ascii=False, indent=2)


@tool
def query_evergreen_finances(
    query_type: str,
    period_days: int | None = None,
) -> str:
    """Consulta los datos financieros del productor en la base de datos EverGreen FIN.

    Ejecuta consultas SQL de solo lectura para obtener información
    financiera del productor agrícola: saldos, movimientos, facturas,
    cuentas por pagar, activos fijos y perfil del productor.

    Args:
        query_type: Tipo de consulta. Valores válidos: current_balance,
            recent_movements, pending_receivables, pending_payables,
            fixed_assets, expense_summary, producer_profile.
        period_days: Número de días hacia atrás para filtrar datos.
            Si no se especifica, usa el trimestre actual.

    Returns:
        Resultados de la consulta en formato JSON con valores en COP.
    """
    resultado = _query_evergreen_finances(
        query_type=query_type,
        period_days=period_days,
    )
    return json.dumps(resultado, ensure_ascii=False, indent=2)


@tool
def calculate_vat_discount(
    purchase_price: float,
    vat_rate: float = 0.19,
) -> str:
    """Calcula el descuento de IVA sobre una compra de bien de capital.

    Determina el monto del descuento de IVA y el costo efectivo
    después del descuento para compras de maquinaria, equipo u
    otros bienes de capital según el Artículo 258-1.

    Args:
        purchase_price: Precio de compra del bien en COP (debe ser positivo).
        vat_rate: Tasa de IVA aplicable (por defecto 0.19 = 19%).

    Returns:
        Resultado del cálculo en formato JSON con descuento, costo
        efectivo y explicación en español.
    """
    resultado = _calculate_vat_discount(
        purchase_price=purchase_price,
        vat_rate=vat_rate,
    )
    return json.dumps(resultado, ensure_ascii=False, indent=2)


@tool
def calculate_net_liquidity(
    balance: float,
    receivables: float,
    payables: float,
) -> str:
    """Calcula la liquidez neta actual y proyectada del productor.

    Determina la liquidez neta actual (saldo menos cuentas por pagar)
    y la liquidez neta proyectada (incluyendo cuentas por cobrar)
    para evaluar la salud financiera del productor.

    Args:
        balance: Saldo actual de la cuenta en COP.
        receivables: Cuentas por cobrar en COP (debe ser >= 0).
        payables: Cuentas por pagar en COP (debe ser >= 0).

    Returns:
        Resultado del cálculo en formato JSON con liquidez actual,
        proyectada y explicación en español.
    """
    resultado = _calculate_net_liquidity(
        balance=balance,
        receivables=receivables,
        payables=payables,
    )
    return json.dumps(resultado, ensure_ascii=False, indent=2)


@tool
def assess_investment_viability(
    balance: float,
    receivables: float,
    payables: float,
    purchase_cost: float,
    tax_benefit: float = 0,
) -> str:
    """Evalúa si una inversión en activo fijo es viable financieramente.

    Analiza la situación financiera del productor para determinar si
    puede realizar una compra de maquinaria, equipo u otro activo fijo,
    considerando beneficios tributarios aplicables.

    Args:
        balance: Saldo actual de la cuenta en COP.
        receivables: Cuentas por cobrar en COP (debe ser >= 0).
        payables: Cuentas por pagar en COP (debe ser >= 0).
        purchase_cost: Costo de compra del activo en COP (debe ser > 0).
        tax_benefit: Beneficio tributario aplicable en COP (por defecto 0).

    Returns:
        Resultado del análisis en formato JSON con viabilidad, costos
        efectivos, fondos disponibles y explicación en español.
    """
    resultado = _assess_investment_viability(
        balance=balance,
        receivables=receivables,
        payables=payables,
        purchase_cost=purchase_cost,
        tax_benefit=tax_benefit,
    )
    return json.dumps(resultado, ensure_ascii=False, indent=2)


@tool
def project_tax_liability(
    gross_income: float,
    deductions: float,
    tax_rate: float,
) -> str:
    """Proyecta la obligación tributaria del productor agrícola.

    Calcula la renta gravable y el impuesto estimado con base en
    los ingresos brutos, deducciones aplicables y la tasa impositiva.

    Args:
        gross_income: Ingreso bruto en COP (debe ser >= 0).
        deductions: Deducciones aplicables en COP (debe ser >= 0).
        tax_rate: Tasa impositiva (entre 0 exclusivo y 1 inclusivo).

    Returns:
        Resultado de la proyección en formato JSON con renta gravable,
        impuesto estimado y explicación en español.
    """
    resultado = _project_tax_liability(
        gross_income=gross_income,
        deductions=deductions,
        tax_rate=tax_rate,
    )
    return json.dumps(resultado, ensure_ascii=False, indent=2)


@tool
def calculate_depreciation(
    purchase_value: float,
    useful_life_years: int,
    years_elapsed: float,
) -> str:
    """Calcula la depreciación de un activo fijo por línea recta.

    Determina la depreciación anual, acumulada y el valor actual
    de un activo fijo del productor (maquinaria, vehículos, equipo).

    Args:
        purchase_value: Valor de compra del activo en COP (debe ser > 0).
        useful_life_years: Vida útil del activo en años (debe ser > 0).
        years_elapsed: Años transcurridos desde la compra (debe ser >= 0).

    Returns:
        Resultado del cálculo en formato JSON con depreciación anual,
        acumulada, valor actual y explicación en español.
    """
    resultado = _calculate_depreciation(
        purchase_value=purchase_value,
        useful_life_years=useful_life_years,
        years_elapsed=years_elapsed,
    )
    return json.dumps(resultado, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Lista de todas las herramientas para registro en el agente
# ---------------------------------------------------------------------------

TODAS_LAS_HERRAMIENTAS = [
    get_tax_knowledge,
    query_evergreen_finances,
    calculate_vat_discount,
    calculate_net_liquidity,
    assess_investment_viability,
    project_tax_liability,
    calculate_depreciation,
]
"""Lista de las 7 herramientas LangChain del agente FIN-Advisor."""
