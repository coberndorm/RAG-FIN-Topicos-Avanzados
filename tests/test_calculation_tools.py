"""
Pruebas de propiedades para las herramientas de cálculo de FIN-Advisor.

Valida las Propiedades 1-6 del documento de diseño:
- P1: Invariante aritmético de descuento IVA
- P2: Invariante aritmético de liquidez neta
- P3: Invariante aritmético de viabilidad de inversión
- P4: Invariante aritmético de obligación tributaria
- P5: Invariante aritmético de depreciación
- P6: Rechazo de entradas inválidas con mensaje en español
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from agent.tools.calculate_vat_discount import calculate_vat_discount
from agent.tools.calculate_net_liquidity import calculate_net_liquidity
from agent.tools.assess_investment_viability import assess_investment_viability
from agent.tools.project_tax_liability import project_tax_liability
from agent.tools.calculate_depreciation import calculate_depreciation

# ---------------------------------------------------------------------------
# Estrategias comunes
# ---------------------------------------------------------------------------
_precio_positivo = st.floats(min_value=0.01, max_value=1e12, allow_nan=False, allow_infinity=False)
_tasa_valida = st.floats(min_value=0.001, max_value=1.0, allow_nan=False, allow_infinity=False)
_monto_no_negativo = st.floats(min_value=0.0, max_value=1e12, allow_nan=False, allow_infinity=False, allow_subnormal=False)
_balance = st.floats(min_value=-1e12, max_value=1e12, allow_nan=False, allow_infinity=False)
_entero_positivo = st.integers(min_value=1, max_value=100)
_anios_transcurridos = st.floats(min_value=0.0, max_value=200.0, allow_nan=False, allow_infinity=False)


# ---------------------------------------------------------------------------
# Propiedad 1: Invariante aritmético de descuento IVA
# ---------------------------------------------------------------------------

class TestVATDiscountArithmeticInvariant:
    """Propiedad 1: discount_amount + effective_cost == purchase_price."""

    @given(price=_precio_positivo, rate=_tasa_valida)
    @settings(max_examples=100, deadline=None)
    def test_suma_descuento_mas_costo_igual_precio(
        self, price: float, rate: float
    ) -> None:
        resultado = calculate_vat_discount(price, rate)
        assert "error" not in resultado
        assert math.isclose(
            resultado["discount_amount"] + resultado["effective_cost"],
            price,
            rel_tol=1e-9,
        )

    @given(price=_precio_positivo, rate=_tasa_valida)
    @settings(max_examples=100, deadline=None)
    def test_descuento_igual_precio_por_tasa(
        self, price: float, rate: float
    ) -> None:
        resultado = calculate_vat_discount(price, rate)
        assert "error" not in resultado
        assert math.isclose(
            resultado["discount_amount"],
            price * rate,
            rel_tol=1e-9,
        )


# ---------------------------------------------------------------------------
# Propiedad 2: Invariante aritmético de liquidez neta
# ---------------------------------------------------------------------------

class TestNetLiquidityArithmeticInvariant:
    """Propiedad 2: net_liquidity_now == balance - payables."""

    @given(balance=_balance, receivables=_monto_no_negativo, payables=_monto_no_negativo)
    @settings(max_examples=100, deadline=None)
    def test_liquidez_actual(
        self, balance: float, receivables: float, payables: float
    ) -> None:
        resultado = calculate_net_liquidity(balance, receivables, payables)
        assert "error" not in resultado
        assert math.isclose(
            resultado["net_liquidity_now"],
            balance - payables,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )

    @given(balance=_balance, receivables=_monto_no_negativo, payables=_monto_no_negativo)
    @settings(max_examples=100, deadline=None)
    def test_liquidez_proyectada(
        self, balance: float, receivables: float, payables: float
    ) -> None:
        resultado = calculate_net_liquidity(balance, receivables, payables)
        assert "error" not in resultado
        assert math.isclose(
            resultado["net_liquidity_projected"],
            balance - payables + receivables,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )


# ---------------------------------------------------------------------------
# Propiedad 3: Invariante aritmético de viabilidad de inversión
# ---------------------------------------------------------------------------

class TestInvestmentViabilityArithmeticInvariant:
    """Propiedad 3: effective_cost == purchase_cost - tax_benefit, etc."""

    @given(
        balance=_balance,
        receivables=_monto_no_negativo,
        payables=_monto_no_negativo,
        purchase_cost=_precio_positivo,
        tax_benefit=_monto_no_negativo,
    )
    @settings(max_examples=100, deadline=None)
    def test_costo_efectivo_y_fondos(
        self,
        balance: float,
        receivables: float,
        payables: float,
        purchase_cost: float,
        tax_benefit: float,
    ) -> None:
        resultado = assess_investment_viability(
            balance, receivables, payables, purchase_cost, tax_benefit
        )
        assert "error" not in resultado

        assert math.isclose(
            resultado["effective_cost"],
            purchase_cost - tax_benefit,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )
        assert math.isclose(
            resultado["available_funds_now"],
            balance - payables,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )
        assert resultado["viable_now"] == (
            (balance - payables) >= (purchase_cost - tax_benefit)
        )


# ---------------------------------------------------------------------------
# Propiedad 4: Invariante aritmético de obligación tributaria
# ---------------------------------------------------------------------------

class TestTaxLiabilityArithmeticInvariant:
    """Propiedad 4: taxable_income == max(0, gross - deductions)."""

    @given(
        gross=_monto_no_negativo,
        deductions=_monto_no_negativo,
        rate=_tasa_valida,
    )
    @settings(max_examples=100, deadline=None)
    def test_renta_gravable_e_impuesto(
        self, gross: float, deductions: float, rate: float
    ) -> None:
        resultado = project_tax_liability(gross, deductions, rate)
        assert "error" not in resultado

        expected_taxable = max(0, gross - deductions)
        assert math.isclose(
            resultado["taxable_income"],
            expected_taxable,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )
        assert math.isclose(
            resultado["estimated_tax"],
            expected_taxable * rate,
            rel_tol=1e-9,
            abs_tol=1e-9,
        )


# ---------------------------------------------------------------------------
# Propiedad 5: Invariante aritmético de depreciación
# ---------------------------------------------------------------------------

class TestDepreciationArithmeticInvariant:
    """Propiedad 5: annual_depreciation == purchase_value / useful_life_years."""

    @given(
        purchase_value=_precio_positivo,
        useful_life=_entero_positivo,
        years_elapsed=_anios_transcurridos,
    )
    @settings(max_examples=100, deadline=None)
    def test_depreciacion_anual_y_acumulada(
        self,
        purchase_value: float,
        useful_life: int,
        years_elapsed: float,
    ) -> None:
        resultado = calculate_depreciation(purchase_value, useful_life, years_elapsed)
        assert "error" not in resultado

        expected_annual = purchase_value / useful_life
        expected_accumulated = min(expected_annual * years_elapsed, purchase_value)

        assert math.isclose(
            resultado["annual_depreciation"],
            expected_annual,
            rel_tol=1e-9,
        )
        assert math.isclose(
            resultado["accumulated_depreciation"],
            expected_accumulated,
            rel_tol=1e-9,
        )
        assert resultado["current_value"] >= 0


# ---------------------------------------------------------------------------
# Propiedad 6: Rechazo de entradas inválidas
# ---------------------------------------------------------------------------

class TestInvalidInputRejection:
    """Propiedad 6: entradas inválidas retornan error en español."""

    @given(price=st.floats(max_value=0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, deadline=None)
    def test_vat_precio_no_positivo(self, price: float) -> None:
        resultado = calculate_vat_discount(price)
        assert "error" in resultado
        assert isinstance(resultado["error"], str)

    @given(rate=st.one_of(
        st.floats(max_value=0, allow_nan=False, allow_infinity=False),
        st.floats(min_value=1.001, max_value=100, allow_nan=False, allow_infinity=False),
    ))
    @settings(max_examples=30, deadline=None)
    def test_vat_tasa_invalida(self, rate: float) -> None:
        resultado = calculate_vat_discount(1000.0, rate)
        assert "error" in resultado

    @given(payables=st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, deadline=None)
    def test_liquidez_payables_negativos(self, payables: float) -> None:
        resultado = calculate_net_liquidity(1000.0, 500.0, payables)
        assert "error" in resultado

    @given(receivables=st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, deadline=None)
    def test_liquidez_receivables_negativos(self, receivables: float) -> None:
        resultado = calculate_net_liquidity(1000.0, receivables, 500.0)
        assert "error" in resultado

    @given(cost=st.floats(max_value=0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, deadline=None)
    def test_viabilidad_costo_no_positivo(self, cost: float) -> None:
        resultado = assess_investment_viability(1000.0, 500.0, 200.0, cost)
        assert "error" in resultado

    @given(benefit=st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, deadline=None)
    def test_viabilidad_beneficio_negativo(self, benefit: float) -> None:
        resultado = assess_investment_viability(1000.0, 500.0, 200.0, 1000.0, benefit)
        assert "error" in resultado

    @given(gross=st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, deadline=None)
    def test_tax_ingreso_negativo(self, gross: float) -> None:
        resultado = project_tax_liability(gross, 0.0, 0.3)
        assert "error" in resultado

    @given(rate=st.one_of(
        st.floats(max_value=0, allow_nan=False, allow_infinity=False),
        st.floats(min_value=1.001, max_value=100, allow_nan=False, allow_infinity=False),
    ))
    @settings(max_examples=30, deadline=None)
    def test_tax_tasa_invalida(self, rate: float) -> None:
        resultado = project_tax_liability(1000.0, 0.0, rate)
        assert "error" in resultado

    def test_depreciacion_vida_util_cero(self) -> None:
        resultado = calculate_depreciation(1000.0, 0, 1.0)
        assert "error" in resultado

    @given(value=st.floats(max_value=0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, deadline=None)
    def test_depreciacion_valor_no_positivo(self, value: float) -> None:
        resultado = calculate_depreciation(value, 10, 1.0)
        assert "error" in resultado

    @given(years=st.floats(max_value=-0.01, allow_nan=False, allow_infinity=False))
    @settings(max_examples=30, deadline=None)
    def test_depreciacion_anios_negativos(self, years: float) -> None:
        resultado = calculate_depreciation(1000.0, 10, years)
        assert "error" in resultado
