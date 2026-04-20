"""
Herramienta de cálculo de liquidez neta.

Calcula la liquidez neta actual y proyectada del productor,
retornando una explicación en español. No invoca al LLM; es determinística.
"""

from typing import Union

from agent.tools.models import NetLiquidityInput, NetLiquidityOutput


def calculate_net_liquidity(
    balance: float,
    receivables: float,
    payables: float,
) -> dict[str, Union[float, str]]:
    """Calcula la liquidez neta actual y proyectada.

    Args:
        balance: Saldo actual de la cuenta en COP.
        receivables: Cuentas por cobrar en COP (debe ser >= 0).
        payables: Cuentas por pagar en COP (debe ser >= 0).

    Returns:
        Diccionario con ``net_liquidity_now``, ``net_liquidity_projected``
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

    # Cálculos
    net_liquidity_now = balance - payables
    net_liquidity_projected = balance - payables + receivables

    # Construir explicación
    explanation = (
        f"Con un saldo de ${balance:,.0f} COP, cuentas por pagar de "
        f"${payables:,.0f} COP y cuentas por cobrar de "
        f"${receivables:,.0f} COP: la liquidez neta actual es "
        f"${net_liquidity_now:,.0f} COP y la liquidez neta proyectada "
        f"(incluyendo cobros pendientes) es ${net_liquidity_projected:,.0f} COP."
    )

    output = NetLiquidityOutput(
        net_liquidity_now=net_liquidity_now,
        net_liquidity_projected=net_liquidity_projected,
        explanation=explanation,
    )

    return output.model_dump()
