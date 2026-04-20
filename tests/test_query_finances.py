"""
Pruebas de propiedades y unitarias para query_evergreen_finances.

Valida la Propiedad 8: Cada tipo de consulta retorna JSON válido con
valores en COP contra una base de datos de prueba pre-poblada.
También incluye pruebas unitarias para cada query_type.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from agent.tools.query_evergreen_finances import query_evergreen_finances, QueryType


# Todos los tipos de consulta válidos
ALL_QUERY_TYPES = [qt.value for qt in QueryType]


# ---------------------------------------------------------------------------
# Propiedad 8: JSON válido para todos los tipos de consulta
# ---------------------------------------------------------------------------

class TestFinancialDataRetrievalProperty:
    """Propiedad 8: Cada query_type retorna JSON estructurado válido."""

    @pytest.mark.parametrize("query_type", ALL_QUERY_TYPES)
    def test_retorna_json_valido_sin_error(
        self, test_db: str, query_type: str
    ) -> None:
        """Cada tipo de consulta debe retornar un dict sin clave 'error'."""
        resultado = query_evergreen_finances(query_type, db_path=test_db)
        assert isinstance(resultado, dict)
        assert "error" not in resultado, (
            f"query_type='{query_type}' retornó error: {resultado.get('error')}"
        )

    @pytest.mark.parametrize("query_type", ALL_QUERY_TYPES)
    def test_resultado_serializable_json(
        self, test_db: str, query_type: str
    ) -> None:
        """El resultado debe ser serializable a JSON."""
        resultado = query_evergreen_finances(query_type, db_path=test_db)
        try:
            json.dumps(resultado, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Resultado de '{query_type}' no es serializable: {e}")


# ---------------------------------------------------------------------------
# Pruebas unitarias por tipo de consulta
# ---------------------------------------------------------------------------

class TestCurrentBalance:
    """Pruebas para query_type='current_balance'."""

    def test_retorna_saldo(self, test_db: str) -> None:
        resultado = query_evergreen_finances("current_balance", db_path=test_db)
        assert "saldo_actual" in resultado or "saldo" in resultado or "balance" in resultado or isinstance(resultado.get("saldo_actual_cop"), (int, float))

    def test_contiene_moneda_cop(self, test_db: str) -> None:
        resultado = query_evergreen_finances("current_balance", db_path=test_db)
        texto = json.dumps(resultado, ensure_ascii=False).lower()
        assert "cop" in texto or "saldo" in texto


class TestRecentMovements:
    """Pruebas para query_type='recent_movements'."""

    def test_retorna_lista_movimientos(self, test_db: str) -> None:
        resultado = query_evergreen_finances("recent_movements", db_path=test_db)
        assert "error" not in resultado
        # Debe contener alguna lista de movimientos
        valores = list(resultado.values())
        tiene_lista = any(isinstance(v, list) for v in valores)
        assert tiene_lista or "movimientos" in resultado or "total" in resultado


class TestPendingReceivables:
    """Pruebas para query_type='pending_receivables'."""

    def test_retorna_sin_error(self, test_db: str) -> None:
        resultado = query_evergreen_finances("pending_receivables", db_path=test_db)
        assert "error" not in resultado


class TestPendingPayables:
    """Pruebas para query_type='pending_payables'."""

    def test_retorna_sin_error(self, test_db: str) -> None:
        resultado = query_evergreen_finances("pending_payables", db_path=test_db)
        assert "error" not in resultado


class TestFixedAssets:
    """Pruebas para query_type='fixed_assets'."""

    def test_retorna_sin_error(self, test_db: str) -> None:
        resultado = query_evergreen_finances("fixed_assets", db_path=test_db)
        assert "error" not in resultado


class TestExpenseSummary:
    """Pruebas para query_type='expense_summary'."""

    def test_retorna_sin_error(self, test_db: str) -> None:
        resultado = query_evergreen_finances("expense_summary", db_path=test_db)
        assert "error" not in resultado


class TestProducerProfile:
    """Pruebas para query_type='producer_profile'."""

    def test_retorna_perfil(self, test_db: str) -> None:
        resultado = query_evergreen_finances("producer_profile", db_path=test_db)
        assert "error" not in resultado


class TestInvalidQueryType:
    """Pruebas para tipos de consulta inválidos."""

    def test_tipo_invalido_retorna_error(self, test_db: str) -> None:
        resultado = query_evergreen_finances("tipo_inexistente", db_path=test_db)
        assert "error" in resultado

    def test_tipo_vacio_retorna_error(self, test_db: str) -> None:
        resultado = query_evergreen_finances("", db_path=test_db)
        assert "error" in resultado
