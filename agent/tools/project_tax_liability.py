"""
Herramienta de proyección de obligación tributaria.

Calcula la renta gravable y el impuesto estimado del productor,
retornando una explicación en español. No invoca al LLM; es determinística.
"""

from typing import Union

from agent.tools.models import TaxLiabilityInput, TaxLiabilityOutput


def project_tax_liability(
    gross_income: float,
    deductions: float,
    tax_rate: float,
) -> dict[str, Union[float, str]]:
    """Proyecta la obligación tributaria del productor.

    Args:
        gross_income: Ingreso bruto en COP (debe ser >= 0).
        deductions: Deducciones aplicables en COP (debe ser >= 0).
        tax_rate: Tasa impositiva (entre 0 exclusivo y 1 inclusivo).

    Returns:
        Diccionario con ``taxable_income``, ``estimated_tax`` y
        ``explanation`` en español. Si la entrada es inválida, retorna
        un diccionario con la clave ``error`` y un mensaje descriptivo.
    """
    # Validación de entradas
    if gross_income < 0:
        return {
            "error": (
                "El ingreso bruto no puede ser negativo. "
                f"Se recibió: {gross_income}"
            )
        }

    if deductions < 0:
        return {
            "error": (
                "Las deducciones no pueden ser negativas. "
                f"Se recibió: {deductions}"
            )
        }

    if tax_rate <= 0 or tax_rate > 1:
        return {
            "error": (
                "La tasa impositiva debe estar entre 0 (exclusivo) y 1 "
                f"(inclusivo). Se recibió: {tax_rate}"
            )
        }

    # Cálculos
    taxable_income = max(0, gross_income - deductions)
    estimated_tax = taxable_income * tax_rate

    # Construir explicación
    explanation = (
        f"Con un ingreso bruto de ${gross_income:,.0f} COP y deducciones "
        f"de ${deductions:,.0f} COP, la renta gravable es "
        f"${taxable_income:,.0f} COP. Aplicando una tasa impositiva del "
        f"{tax_rate * 100:.1f}%, el impuesto estimado es "
        f"${estimated_tax:,.0f} COP."
    )

    output = TaxLiabilityOutput(
        taxable_income=taxable_income,
        estimated_tax=estimated_tax,
        explanation=explanation,
    )

    return output.model_dump()
