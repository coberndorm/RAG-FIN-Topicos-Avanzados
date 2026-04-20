"""
Herramienta de cálculo de depreciación de activos fijos.

Calcula la depreciación anual, acumulada y el valor actual de un activo,
retornando una explicación en español. No invoca al LLM; es determinística.
"""

from typing import Union

from agent.tools.models import DepreciationInput, DepreciationOutput


def calculate_depreciation(
    purchase_value: float,
    useful_life_years: int,
    years_elapsed: float,
) -> dict[str, Union[float, str]]:
    """Calcula la depreciación de un activo fijo (método de línea recta).

    Args:
        purchase_value: Valor de compra del activo en COP (debe ser > 0).
        useful_life_years: Vida útil del activo en años (debe ser > 0).
        years_elapsed: Años transcurridos desde la compra (debe ser >= 0).

    Returns:
        Diccionario con ``annual_depreciation``,
        ``accumulated_depreciation``, ``current_value`` y ``explanation``
        en español. Si la entrada es inválida, retorna un diccionario
        con la clave ``error`` y un mensaje descriptivo.
    """
    # Validación de entradas
    if purchase_value <= 0:
        return {
            "error": (
                "El valor de compra debe ser un valor positivo. "
                f"Se recibió: {purchase_value}"
            )
        }

    if useful_life_years <= 0:
        return {
            "error": (
                "La vida útil debe ser un número entero positivo de años. "
                f"Se recibió: {useful_life_years}"
            )
        }

    if years_elapsed < 0:
        return {
            "error": (
                "Los años transcurridos no pueden ser negativos. "
                f"Se recibió: {years_elapsed}"
            )
        }

    # Cálculos
    annual_depreciation = purchase_value / useful_life_years
    accumulated_depreciation = min(
        annual_depreciation * years_elapsed, purchase_value
    )
    current_value = max(0, purchase_value - accumulated_depreciation)

    # Construir explicación
    explanation = (
        f"Para un activo con valor de compra de ${purchase_value:,.0f} COP "
        f"y vida útil de {useful_life_years} años, la depreciación anual "
        f"(línea recta) es ${annual_depreciation:,.0f} COP. Después de "
        f"{years_elapsed:.1f} años, la depreciación acumulada es "
        f"${accumulated_depreciation:,.0f} COP y el valor actual del "
        f"activo es ${current_value:,.0f} COP."
    )

    output = DepreciationOutput(
        annual_depreciation=annual_depreciation,
        accumulated_depreciation=accumulated_depreciation,
        current_value=current_value,
        explanation=explanation,
    )

    return output.model_dump()
