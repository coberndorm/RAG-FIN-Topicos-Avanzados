"""
Herramienta de consulta de datos financieros de EverGreen FIN.

Ejecuta consultas SQL parametrizadas de solo lectura contra la base de datos
SQLite del módulo financiero y retorna resultados estructurados en JSON
con valores monetarios en COP.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import date, timedelta
from enum import Enum
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Tipos de consulta soportados
# ---------------------------------------------------------------------------

class QueryType(str, Enum):
    """Tipos de consulta disponibles para datos financieros de EverGreen.

    Attributes:
        CURRENT_BALANCE: Saldo actual (ingresos - egresos) en el período.
        RECENT_MOVEMENTS: Movimientos recientes (ingresos y egresos).
        PENDING_RECEIVABLES: Facturas de venta pendientes de cobro.
        PENDING_PAYABLES: Cuentas por pagar pendientes.
        FIXED_ASSETS: Inventario de activos fijos.
        EXPENSE_SUMMARY: Resumen de egresos por categoría.
        PRODUCER_PROFILE: Perfil del productor agrícola.
    """

    CURRENT_BALANCE = "current_balance"
    RECENT_MOVEMENTS = "recent_movements"
    PENDING_RECEIVABLES = "pending_receivables"
    PENDING_PAYABLES = "pending_payables"
    FIXED_ASSETS = "fixed_assets"
    EXPENSE_SUMMARY = "expense_summary"
    PRODUCER_PROFILE = "producer_profile"


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

def _obtener_ruta_db() -> str:
    """Obtiene la ruta a la base de datos SQLite.

    Lee la variable de entorno ``SQLITE_DB_PATH``. Si no está definida,
    usa ``./fin.db`` relativo al directorio del proyecto.

    Returns:
        Ruta al archivo de base de datos SQLite.
    """
    ruta = os.environ.get("SQLITE_DB_PATH")
    if ruta:
        return ruta
    # Por defecto: ./fin.db relativo al directorio del proyecto
    proyecto_dir = Path(__file__).resolve().parent.parent.parent
    return str(proyecto_dir / "fin.db")


def _calcular_inicio_trimestre_actual() -> str:
    """Calcula la fecha de inicio del trimestre actual.

    Returns:
        Fecha de inicio del trimestre en formato ISO (YYYY-MM-DD).
    """
    hoy = date.today()
    mes_inicio = ((hoy.month - 1) // 3) * 3 + 1
    return date(hoy.year, mes_inicio, 1).isoformat()


def _calcular_fecha_inicio(period_days: int | None) -> str:
    """Calcula la fecha de inicio del período de consulta.

    Args:
        period_days: Número de días hacia atrás. Si es ``None``,
            se usa el inicio del trimestre actual.

    Returns:
        Fecha de inicio en formato ISO (YYYY-MM-DD).
    """
    if period_days is not None:
        return (date.today() - timedelta(days=period_days)).isoformat()
    return _calcular_inicio_trimestre_actual()


def _conectar_db(db_path: str | None = None) -> sqlite3.Connection:
    """Crea una conexión de solo lectura a la base de datos SQLite.

    Args:
        db_path: Ruta al archivo de base de datos. Si es ``None``,
            se usa la ruta por defecto.

    Returns:
        Conexión SQLite configurada para retornar filas como diccionarios.

    Raises:
        sqlite3.Error: Si no se puede conectar a la base de datos.
    """
    ruta = db_path or _obtener_ruta_db()
    if not Path(ruta).exists():
        raise sqlite3.OperationalError(
            f"No se encontró la base de datos en: {ruta}. "
            "Ejecute primero 'python scripts/generate_mock_data.py' para generarla."
        )
    conn = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------------------------------
# Funciones de consulta individuales
# ---------------------------------------------------------------------------

def _consultar_saldo_actual(
    conn: sqlite3.Connection, fecha_inicio: str,
) -> dict[str, Any]:
    """Calcula el saldo actual: sum(INGRESO) - sum(EGRESO).

    Args:
        conn: Conexión activa a la base de datos.
        fecha_inicio: Fecha de inicio del período (ISO).

    Returns:
        Diccionario con el saldo actual en COP.
    """
    cursor = conn.execute(
        """
        SELECT
            COALESCE(SUM(CASE WHEN type = 'INGRESO' THEN amount ELSE 0 END), 0) AS ingresos,
            COALESCE(SUM(CASE WHEN type = 'EGRESO' THEN amount ELSE 0 END), 0) AS egresos
        FROM movimientos
        WHERE date >= ?
        """,
        (fecha_inicio,),
    )
    fila = cursor.fetchone()
    ingresos = fila["ingresos"]
    egresos = fila["egresos"]
    saldo = ingresos - egresos

    return {
        "tipo_consulta": "current_balance",
        "periodo_desde": fecha_inicio,
        "periodo_hasta": date.today().isoformat(),
        "moneda": "COP",
        "total_ingresos": ingresos,
        "total_egresos": egresos,
        "saldo_actual": saldo,
    }


def _consultar_movimientos_recientes(
    conn: sqlite3.Connection, fecha_inicio: str,
) -> dict[str, Any]:
    """Obtiene los movimientos recientes del período.

    Args:
        conn: Conexión activa a la base de datos.
        fecha_inicio: Fecha de inicio del período (ISO).

    Returns:
        Diccionario con la lista de movimientos en COP.
    """
    cursor = conn.execute(
        """
        SELECT id, date, type, category, amount, description
        FROM movimientos
        WHERE date >= ?
        ORDER BY date DESC
        """,
        (fecha_inicio,),
    )
    movimientos = [
        {
            "id": fila["id"],
            "fecha": fila["date"],
            "tipo": fila["type"],
            "categoria": fila["category"],
            "monto_cop": fila["amount"],
            "descripcion": fila["description"],
        }
        for fila in cursor.fetchall()
    ]

    return {
        "tipo_consulta": "recent_movements",
        "periodo_desde": fecha_inicio,
        "periodo_hasta": date.today().isoformat(),
        "moneda": "COP",
        "total_movimientos": len(movimientos),
        "movimientos": movimientos,
    }


def _consultar_cuentas_por_cobrar(
    conn: sqlite3.Connection,
) -> dict[str, Any]:
    """Obtiene las facturas de venta pendientes y vencidas.

    Args:
        conn: Conexión activa a la base de datos.

    Returns:
        Diccionario con facturas pendientes de cobro en COP.
    """
    cursor = conn.execute(
        """
        SELECT invoice_id, date_issued, date_due, client_name,
               total_amount, vat_amount, status
        FROM facturas_venta
        WHERE status IN ('PENDING', 'OVERDUE')
        ORDER BY date_due ASC
        """
    )
    facturas = [
        {
            "factura_id": fila["invoice_id"],
            "fecha_emision": fila["date_issued"],
            "fecha_vencimiento": fila["date_due"],
            "cliente": fila["client_name"],
            "monto_total_cop": fila["total_amount"],
            "monto_iva_cop": fila["vat_amount"],
            "estado": fila["status"],
        }
        for fila in cursor.fetchall()
    ]
    total = sum(f["monto_total_cop"] for f in facturas)

    return {
        "tipo_consulta": "pending_receivables",
        "moneda": "COP",
        "total_pendiente_cop": total,
        "cantidad_facturas": len(facturas),
        "facturas": facturas,
    }


def _consultar_cuentas_por_pagar(
    conn: sqlite3.Connection,
) -> dict[str, Any]:
    """Obtiene las cuentas por pagar pendientes y vencidas.

    Args:
        conn: Conexión activa a la base de datos.

    Returns:
        Diccionario con cuentas por pagar en COP.
    """
    cursor = conn.execute(
        """
        SELECT payable_id, supplier_name, amount, due_date, category, status
        FROM cuentas_por_pagar
        WHERE status IN ('PENDING', 'OVERDUE')
        ORDER BY due_date ASC
        """
    )
    cuentas = [
        {
            "cuenta_id": fila["payable_id"],
            "proveedor": fila["supplier_name"],
            "monto_cop": fila["amount"],
            "fecha_vencimiento": fila["due_date"],
            "categoria": fila["category"],
            "estado": fila["status"],
        }
        for fila in cursor.fetchall()
    ]
    total = sum(c["monto_cop"] for c in cuentas)

    return {
        "tipo_consulta": "pending_payables",
        "moneda": "COP",
        "total_pendiente_cop": total,
        "cantidad_cuentas": len(cuentas),
        "cuentas": cuentas,
    }


def _consultar_activos_fijos(
    conn: sqlite3.Connection,
) -> dict[str, Any]:
    """Obtiene el inventario de activos fijos.

    Args:
        conn: Conexión activa a la base de datos.

    Returns:
        Diccionario con activos fijos y sus valores en COP.
    """
    cursor = conn.execute(
        """
        SELECT asset_id, name, category, purchase_date,
               purchase_value, current_value, depreciation_rate
        FROM activos_fijos
        ORDER BY purchase_value DESC
        """
    )
    activos = [
        {
            "activo_id": fila["asset_id"],
            "nombre": fila["name"],
            "categoria": fila["category"],
            "fecha_compra": fila["purchase_date"],
            "valor_compra_cop": fila["purchase_value"],
            "valor_actual_cop": fila["current_value"],
            "tasa_depreciacion": fila["depreciation_rate"],
        }
        for fila in cursor.fetchall()
    ]
    valor_total = sum(a["valor_actual_cop"] for a in activos)

    return {
        "tipo_consulta": "fixed_assets",
        "moneda": "COP",
        "valor_total_actual_cop": valor_total,
        "cantidad_activos": len(activos),
        "activos": activos,
    }


def _consultar_resumen_egresos(
    conn: sqlite3.Connection, fecha_inicio: str,
) -> dict[str, Any]:
    """Genera un resumen de egresos agrupados por categoría.

    Args:
        conn: Conexión activa a la base de datos.
        fecha_inicio: Fecha de inicio del período (ISO).

    Returns:
        Diccionario con resumen de egresos por categoría en COP.
    """
    cursor = conn.execute(
        """
        SELECT category, SUM(amount) AS total, COUNT(*) AS cantidad
        FROM movimientos
        WHERE type = 'EGRESO' AND date >= ?
        GROUP BY category
        ORDER BY total DESC
        """,
        (fecha_inicio,),
    )
    categorias = [
        {
            "categoria": fila["category"],
            "total_cop": fila["total"],
            "cantidad_movimientos": fila["cantidad"],
        }
        for fila in cursor.fetchall()
    ]
    total_egresos = sum(c["total_cop"] for c in categorias)

    return {
        "tipo_consulta": "expense_summary",
        "periodo_desde": fecha_inicio,
        "periodo_hasta": date.today().isoformat(),
        "moneda": "COP",
        "total_egresos_cop": total_egresos,
        "categorias": categorias,
    }


def _consultar_perfil_productor(
    conn: sqlite3.Connection,
) -> dict[str, Any]:
    """Obtiene el perfil del productor agrícola.

    Args:
        conn: Conexión activa a la base de datos.

    Returns:
        Diccionario con los datos del perfil del productor.
    """
    cursor = conn.execute(
        """
        SELECT id, name, farm_name, activity_type, nit,
               tax_bracket, registered_since
        FROM perfil_productor
        LIMIT 1
        """
    )
    fila = cursor.fetchone()
    if fila is None:
        return {
            "tipo_consulta": "producer_profile",
            "error": "No se encontró perfil de productor en la base de datos.",
        }

    return {
        "tipo_consulta": "producer_profile",
        "productor": {
            "id": fila["id"],
            "nombre": fila["name"],
            "nombre_finca": fila["farm_name"],
            "tipo_actividad": fila["activity_type"],
            "nit": fila["nit"],
            "regimen_tributario": fila["tax_bracket"],
            "registrado_desde": fila["registered_since"],
        },
    }


# ---------------------------------------------------------------------------
# Función principal de la herramienta
# ---------------------------------------------------------------------------

def query_evergreen_finances(
    query_type: str,
    period_days: int | None = None,
    db_path: str | None = None,
) -> dict[str, Any]:
    """Consulta datos financieros del módulo EverGreen FIN.

    Ejecuta consultas SQL parametrizadas de solo lectura contra la base
    de datos SQLite y retorna resultados estructurados con valores en COP.

    Args:
        query_type: Tipo de consulta. Valores válidos:
            ``current_balance``, ``recent_movements``,
            ``pending_receivables``, ``pending_payables``,
            ``fixed_assets``, ``expense_summary``, ``producer_profile``.
        period_days: Número de días hacia atrás para filtrar datos.
            Si es ``None``, se usa el trimestre actual como período.
        db_path: Ruta al archivo de base de datos SQLite. Si es ``None``,
            se usa la variable de entorno ``SQLITE_DB_PATH`` o ``./fin.db``.

    Returns:
        Diccionario con los resultados de la consulta en formato JSON
        con valores monetarios en COP. Si ocurre un error, retorna
        un diccionario con la clave ``error`` y un mensaje descriptivo
        en español.
    """
    # Validar tipo de consulta
    try:
        tipo = QueryType(query_type)
    except ValueError:
        tipos_validos = ", ".join(t.value for t in QueryType)
        return {
            "error": (
                f"Tipo de consulta no válido: '{query_type}'. "
                f"Los tipos válidos son: {tipos_validos}"
            )
        }

    # Conectar a la base de datos
    try:
        conn = _conectar_db(db_path)
    except sqlite3.Error as e:
        return {
            "error": f"Error al conectar con la base de datos financiera: {e}"
        }

    try:
        fecha_inicio = _calcular_fecha_inicio(period_days)

        if tipo == QueryType.CURRENT_BALANCE:
            return _consultar_saldo_actual(conn, fecha_inicio)
        elif tipo == QueryType.RECENT_MOVEMENTS:
            return _consultar_movimientos_recientes(conn, fecha_inicio)
        elif tipo == QueryType.PENDING_RECEIVABLES:
            return _consultar_cuentas_por_cobrar(conn)
        elif tipo == QueryType.PENDING_PAYABLES:
            return _consultar_cuentas_por_pagar(conn)
        elif tipo == QueryType.FIXED_ASSETS:
            return _consultar_activos_fijos(conn)
        elif tipo == QueryType.EXPENSE_SUMMARY:
            return _consultar_resumen_egresos(conn, fecha_inicio)
        elif tipo == QueryType.PRODUCER_PROFILE:
            return _consultar_perfil_productor(conn)
        else:
            return {"error": f"Tipo de consulta no implementado: {query_type}"}
    except sqlite3.Error as e:
        return {
            "error": f"Error al ejecutar la consulta financiera: {e}"
        }
    finally:
        conn.close()
