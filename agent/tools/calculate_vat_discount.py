"""
Herramienta de cálculo de descuento de IVA.

Calcula el monto del descuento de IVA y el costo efectivo de una compra,
retornando una explicación en español. No invoca al LLM; es determinística.
"""

from typing import Union

from agent.tools.models import VATDiscountInput, VATDiscountOutput


def calculate_vat_discount(
    purchase_price: float,
    vat_rate: float = 0.19,
) -> dict[str, Union[float, str]]:
    """Calcula el descuento de IVA sobre una compra.

    Args:
        purchase_price: Precio de compra del bien en COP.
        vat_rate: Tasa de IVA aplicable (por defecto 0.19 = 19%).

    Returns:
        Diccionario con ``discount_amount``, ``effective_cost`` y
        ``explanation`` en español. Si la entrada es inválida, retorna
        un diccionario con la clave ``error`` y un mensaje descriptivo.
    """
    # Validación de entradas
    if purchase_price <= 0:
        return {
            "error": (
                "El precio de compra debe ser un valor positivo. "
                f"Se recibió: {purchase_price}"
            )
        }

    if vat_rate <= 0 or vat_rate > 1:
        return {
            "error": (
                "La tasa de IVA debe estar entre 0 (exclusivo) y 1 (inclusivo). "
                f"Se recibió: {vat_rate}"
            )
        }

    # Cálculos
    discount_amount = purchase_price * vat_rate
    effective_cost = purchase_price - discount_amount

    # Construir explicación
    explanation = (
        f"Para una compra de ${purchase_price:,.0f} COP con una tasa de IVA "
        f"del {vat_rate * 100:.1f}%, el descuento de IVA es "
        f"${discount_amount:,.0f} COP. El costo efectivo después del "
        f"descuento es ${effective_cost:,.0f} COP."
    )

    output = VATDiscountOutput(
        discount_amount=discount_amount,
        effective_cost=effective_cost,
        explanation=explanation,
    )

    return output.model_dump()
