"""
Herramienta de evaluación de viabilidad de inversión.

Determina si el productor puede realizar una compra de activo fijo
con base en su situación financiera actual y proyectada.
No invoca al LLM; es determinística.
"""

import math
from typing import Union

from agent.tools.models import InvestmentViabilityInput, InvestmentViabilityOutput


def assess_investment_viability(
    balance: float,
    receivables: float,
    payables: float,
    purchase_cost: float,
    tax_benefit: float = 0,
) -> dict[str, Union[float, bool, int, str]]:
    """Evalúa la viabilidad de una inversión en activo fijo.

    Args:
        balance: Saldo actual de la cuenta en COP.
        receivables: Cuentas por cobrar en COP (debe ser >= 0).
        payables: Cuentas por pagar en COP (debe ser >= 0).
        purchase_cost: Costo de compra del activo en COP (debe ser > 0).
        tax_benefit: Beneficio tributario aplicable en COP (debe ser >= 0).

    Returns:
        Diccionario con ``effective_cost``, ``available_funds_now``,
        ``available_funds_projected``, ``viable_now``, ``viable_in_days``
        y ``explanation`` en español. Si la entrada es inválida, retorna
        un diccionario con la clave ``error`` y un mensaje descriptivo.
    """
    # Validación de entradas
    if receivables < 0:
        return {
            "error": (
                "Las cuentas por cobrar no pueden ser negativas. "
                f"Se recibió: {receivables}"
            )
        }

    if payables < 0:
        return {
            "error": (
                "Las cuentas por pagar no pueden ser negativas. "
                f"Se recibió: {payables}"
            )
        }

    if purchase_cost <= 0:
        return {
            "error": (
                "El costo de compra debe ser un valor positivo. "
                f"Se recibió: {purchase_cost}"
            )
        }

    if tax_benefit < 0:
        return {
            "error": (
                "El beneficio tributario no puede ser negativo. "
                f"Se recibió: {tax_benefit}"
            )
        }

    # Cálculos
    effective_cost = purchase_cost - tax_benefit
    available_funds_now = balance - payables
    available_funds_projected = balance - payables + receivables
    viable_now = available_funds_now >= effective_cost

    # Calcular días estimados hasta viabilidad
    if viable_now:
        viable_in_days = 0
    else:
        funding_gap = effective_cost - available_funds_now
        # Flujo diario promedio de cuentas por cobrar (sobre 30 días)
        avg_daily_receivable_inflow = receivables / 30 if receivables > 0 else 0

        if avg_daily_receivable_inflow > 0:
            viable_in_days = math.ceil(funding_gap / avg_daily_receivable_inflow)
        else:
            # Sin ingresos proyectados, no se puede estimar
            viable_in_days = -1

    # Construir explicación
    viability_text = "SÍ es viable" if viable_now else "NO es viable"
    explanation = (
        f"Análisis de viabilidad para una compra de ${purchase_cost:,.0f} COP"
    )
    if tax_benefit > 0:
        explanation += f" con beneficio tributario de ${tax_benefit:,.0f} COP"
    explanation += (
        f": el costo efectivo es ${effective_cost:,.0f} COP. "
        f"Fondos disponibles actuales: ${available_funds_now:,.0f} COP. "
        f"Fondos proyectados: ${available_funds_projected:,.0f} COP. "
        f"La inversión {viability_text} en este momento."
    )

    if not viable_now and viable_in_days > 0:
        explanation += (
            f" Se estima que será viable en aproximadamente "
            f"{viable_in_days} días."
        )
    elif not viable_now and viable_in_days == -1:
        explanation += (
            " No se puede estimar una fecha de viabilidad sin "
            "cuentas por cobrar proyectadas."
        )

    output = InvestmentViabilityOutput(
        effective_cost=effective_cost,
        available_funds_now=available_funds_now,
        available_funds_projected=available_funds_projected,
        viable_now=viable_now,
        viable_in_days=viable_in_days,
        explanation=explanation,
    )

    return output.model_dump()
