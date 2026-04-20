"""
Modelos Pydantic de entrada y salida para las herramientas de cálculo.

Define los esquemas de validación para las cinco herramientas de cálculo
determinístico del agente FIN-Advisor.
"""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Descuento de IVA
# ---------------------------------------------------------------------------

class VATDiscountInput(BaseModel):
    """Entrada para el cálculo de descuento de IVA.

    Attributes:
        purchase_price: Precio de compra del bien (debe ser positivo).
        vat_rate: Tasa de IVA aplicable (entre 0 exclusivo y 1 inclusivo).
    """

    purchase_price: float = Field(
        ...,
        gt=0,
        description="Precio de compra del bien en COP",
    )
    vat_rate: float = Field(
        default=0.19,
        gt=0,
        le=1,
        description="Tasa de IVA (por defecto 0.19 = 19%)",
    )


class VATDiscountOutput(BaseModel):
    """Salida del cálculo de descuento de IVA.

    Attributes:
        discount_amount: Monto del descuento de IVA en COP.
        effective_cost: Costo efectivo después del descuento en COP.
        explanation: Explicación del cálculo en español.
    """

    discount_amount: float
    effective_cost: float
    explanation: str


# ---------------------------------------------------------------------------
# Liquidez neta
# ---------------------------------------------------------------------------

class NetLiquidityInput(BaseModel):
    """Entrada para el cálculo de liquidez neta.

    Attributes:
        balance: Saldo actual de la cuenta.
        receivables: Cuentas por cobrar (no negativo).
        payables: Cuentas por pagar (no negativo).
    """

    balance: float = Field(
        ...,
        description="Saldo actual en COP",
    )
    receivables: float = Field(
        ...,
        ge=0,
        description="Cuentas por cobrar en COP",
    )
    payables: float = Field(
        ...,
        ge=0,
        description="Cuentas por pagar en COP",
    )


class NetLiquidityOutput(BaseModel):
    """Salida del cálculo de liquidez neta.

    Attributes:
        net_liquidity_now: Liquidez neta actual (balance - cuentas por pagar).
        net_liquidity_projected: Liquidez neta proyectada
            (balance - cuentas por pagar + cuentas por cobrar).
        explanation: Explicación del cálculo en español.
    """

    net_liquidity_now: float
    net_liquidity_projected: float
    explanation: str


# ---------------------------------------------------------------------------
# Viabilidad de inversión
# ---------------------------------------------------------------------------

class InvestmentViabilityInput(BaseModel):
    """Entrada para la evaluación de viabilidad de inversión.

    Attributes:
        balance: Saldo actual de la cuenta.
        receivables: Cuentas por cobrar (no negativo).
        payables: Cuentas por pagar (no negativo).
        purchase_cost: Costo de compra del activo (debe ser positivo).
        tax_benefit: Beneficio tributario aplicable (no negativo).
    """

    balance: float = Field(
        ...,
        description="Saldo actual en COP",
    )
    receivables: float = Field(
        ...,
        ge=0,
        description="Cuentas por cobrar en COP",
    )
    payables: float = Field(
        ...,
        ge=0,
        description="Cuentas por pagar en COP",
    )
    purchase_cost: float = Field(
        ...,
        gt=0,
        description="Costo de compra del activo en COP",
    )
    tax_benefit: float = Field(
        default=0,
        ge=0,
        description="Beneficio tributario aplicable en COP",
    )


class InvestmentViabilityOutput(BaseModel):
    """Salida de la evaluación de viabilidad de inversión.

    Attributes:
        effective_cost: Costo efectivo después del beneficio tributario.
        available_funds_now: Fondos disponibles actualmente.
        available_funds_projected: Fondos disponibles proyectados.
        viable_now: Indica si la inversión es viable actualmente.
        viable_in_days: Días estimados hasta que la inversión sea viable.
        explanation: Explicación del análisis en español.
    """

    effective_cost: float
    available_funds_now: float
    available_funds_projected: float
    viable_now: bool
    viable_in_days: int
    explanation: str


# ---------------------------------------------------------------------------
# Proyección de impuestos
# ---------------------------------------------------------------------------

class TaxLiabilityInput(BaseModel):
    """Entrada para la proyección de obligación tributaria.

    Attributes:
        gross_income: Ingreso bruto (no negativo).
        deductions: Deducciones aplicables (no negativo).
        tax_rate: Tasa impositiva (entre 0 exclusivo y 1 inclusivo).
    """

    gross_income: float = Field(
        ...,
        ge=0,
        description="Ingreso bruto en COP",
    )
    deductions: float = Field(
        ...,
        ge=0,
        description="Deducciones aplicables en COP",
    )
    tax_rate: float = Field(
        ...,
        gt=0,
        le=1,
        description="Tasa impositiva (ej. 0.35 = 35%)",
    )


class TaxLiabilityOutput(BaseModel):
    """Salida de la proyección de obligación tributaria.

    Attributes:
        taxable_income: Renta gravable calculada.
        estimated_tax: Impuesto estimado.
        explanation: Explicación del cálculo en español.
    """

    taxable_income: float
    estimated_tax: float
    explanation: str


# ---------------------------------------------------------------------------
# Depreciación
# ---------------------------------------------------------------------------

class DepreciationInput(BaseModel):
    """Entrada para el cálculo de depreciación.

    Attributes:
        purchase_value: Valor de compra del activo (debe ser positivo).
        useful_life_years: Vida útil en años (debe ser positivo).
        years_elapsed: Años transcurridos desde la compra (no negativo).
    """

    purchase_value: float = Field(
        ...,
        gt=0,
        description="Valor de compra del activo en COP",
    )
    useful_life_years: int = Field(
        ...,
        gt=0,
        description="Vida útil del activo en años",
    )
    years_elapsed: float = Field(
        ...,
        ge=0,
        description="Años transcurridos desde la compra",
    )


class DepreciationOutput(BaseModel):
    """Salida del cálculo de depreciación.

    Attributes:
        annual_depreciation: Depreciación anual.
        accumulated_depreciation: Depreciación acumulada.
        current_value: Valor actual del activo (nunca negativo).
        explanation: Explicación del cálculo en español.
    """

    annual_depreciation: float
    accumulated_depreciation: float
    current_value: float
    explanation: str
