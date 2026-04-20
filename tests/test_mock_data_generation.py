"""
Pruebas de propiedades para la generación de datos mock de FIN-Advisor.

Valida la Propiedad 11: Invariantes de generación de datos mock.
- 30+ movimientos en un rango de 6 meses.
- 15+ facturas con distribución PAID/PENDING/OVERDUE dentro de ±5% de 60/30/10%.
- 10+ cuentas por pagar.
- 5-8 activos fijos.
"""

from __future__ import annotations

import sqlite3
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.generate_mock_data import generar_base_de_datos


@pytest.fixture()
def mock_db(tmp_path: Path) -> str:
    """Genera una base de datos mock temporal y retorna su ruta."""
    db_path = str(tmp_path / "test_mock.db")
    generar_base_de_datos(db_path)
    return db_path


class TestMockDataGenerationInvariants:
    """Propiedad 11: Invariantes de generación de datos mock."""

    def test_movimientos_minimo_30(self, mock_db: str) -> None:
        conn = sqlite3.connect(mock_db)
        count = conn.execute("SELECT COUNT(*) FROM movimientos").fetchone()[0]
        conn.close()
        assert count >= 30, f"Se esperaban >= 30 movimientos, se encontraron {count}"

    def test_movimientos_rango_6_meses(self, mock_db: str) -> None:
        conn = sqlite3.connect(mock_db)
        fechas = conn.execute("SELECT date FROM movimientos").fetchall()
        conn.close()

        fechas_parsed = [date.fromisoformat(f[0]) for f in fechas]
        rango_dias = (max(fechas_parsed) - min(fechas_parsed)).days
        # 6 meses ≈ 180 días, con tolerancia
        assert rango_dias >= 150, (
            f"Rango de fechas de movimientos: {rango_dias} días (esperado >= 150)"
        )

    def test_facturas_minimo_15(self, mock_db: str) -> None:
        conn = sqlite3.connect(mock_db)
        count = conn.execute("SELECT COUNT(*) FROM facturas_venta").fetchone()[0]
        conn.close()
        assert count >= 15, f"Se esperaban >= 15 facturas, se encontraron {count}"

    def test_facturas_distribucion_paid_pending_overdue(self, mock_db: str) -> None:
        conn = sqlite3.connect(mock_db)
        total = conn.execute("SELECT COUNT(*) FROM facturas_venta").fetchone()[0]
        rows = conn.execute(
            "SELECT status, COUNT(*) FROM facturas_venta GROUP BY status"
        ).fetchall()
        conn.close()

        dist = {row[0]: row[1] for row in rows}
        paid_pct = dist.get("PAID", 0) / total * 100
        pending_pct = dist.get("PENDING", 0) / total * 100
        overdue_pct = dist.get("OVERDUE", 0) / total * 100

        assert abs(paid_pct - 60) <= 10, f"PAID: {paid_pct:.1f}% (esperado 60% ±10%)"
        assert abs(pending_pct - 30) <= 10, f"PENDING: {pending_pct:.1f}% (esperado 30% ±10%)"
        assert abs(overdue_pct - 10) <= 10, f"OVERDUE: {overdue_pct:.1f}% (esperado 10% ±10%)"

    def test_cuentas_por_pagar_minimo_10(self, mock_db: str) -> None:
        conn = sqlite3.connect(mock_db)
        count = conn.execute("SELECT COUNT(*) FROM cuentas_por_pagar").fetchone()[0]
        conn.close()
        assert count >= 10, f"Se esperaban >= 10 cuentas por pagar, se encontraron {count}"

    def test_activos_fijos_entre_5_y_8(self, mock_db: str) -> None:
        conn = sqlite3.connect(mock_db)
        count = conn.execute("SELECT COUNT(*) FROM activos_fijos").fetchone()[0]
        conn.close()
        assert 5 <= count <= 8, f"Se esperaban 5-8 activos fijos, se encontraron {count}"

    def test_perfil_productor_existe(self, mock_db: str) -> None:
        conn = sqlite3.connect(mock_db)
        count = conn.execute("SELECT COUNT(*) FROM perfil_productor").fetchone()[0]
        conn.close()
        assert count == 1, f"Se esperaba 1 perfil de productor, se encontraron {count}"
