#!/usr/bin/env python3
"""
Generador de datos mock para la base de datos financiera de EverGreen FIN.

Crea una base de datos SQLite (``fin.db``) con datos sintéticos realistas
de un productor agrícola colombiano. Genera 5 tablas:

- ``perfil_productor`` — 1 registro de perfil del productor.
- ``movimientos`` — 30+ registros de ingresos y egresos en 6 meses.
- ``facturas_venta`` — 15+ facturas (60% PAID, 30% PENDING, 10% OVERDUE ±5%).
- ``cuentas_por_pagar`` — 10+ cuentas por pagar.
- ``activos_fijos`` — 5-8 activos fijos agrícolas.

Uso::

    python scripts/generate_mock_data.py

La ruta de salida se configura con la variable de entorno ``SQLITE_DB_PATH``
(por defecto ``./fin.db`` relativo al directorio ``RAG-FIN-Topicos-Avanzados/``).
"""

from __future__ import annotations

import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path


# ---------------------------------------------------------------------------
# Verificación de disponibilidad de sqlite3
# ---------------------------------------------------------------------------

def _verificar_sqlite3() -> None:
    """Verifica que el módulo ``sqlite3`` esté disponible.

    Si no está disponible, imprime instrucciones claras según el sistema
    operativo y termina el proceso.
    """
    try:
        import sqlite3  # noqa: F401
    except ImportError:
        print("ERROR: El módulo 'sqlite3' no está disponible en esta instalación de Python.")
        print()
        if sys.platform.startswith("linux"):
            print("En distribuciones basadas en Debian/Ubuntu:")
            print("  sudo apt-get install libsqlite3-dev")
            print("  # Luego recompila Python o instala python3-full")
        elif sys.platform == "darwin":
            print("En macOS con Homebrew:")
            print("  brew install sqlite3")
            print("  # Luego recompila Python con soporte SQLite")
        elif sys.platform == "win32":
            print("En Windows, reinstala Python desde https://www.python.org/")
            print("asegurándote de incluir el soporte para SQLite.")
        else:
            print("Instala las bibliotecas de desarrollo de SQLite para tu sistema")
            print("y recompila Python con soporte SQLite habilitado.")
        sys.exit(1)


_verificar_sqlite3()

import sqlite3  # noqa: E402


# ---------------------------------------------------------------------------
# Constantes de datos realistas colombianos
# ---------------------------------------------------------------------------

CATEGORIAS_INGRESO: list[tuple[str, float, float]] = [
    ("Venta cosecha", 3_000_000.0, 15_000_000.0),
    ("Venta ganado", 5_000_000.0, 25_000_000.0),
    ("Subsidio gobierno", 1_000_000.0, 5_000_000.0),
]

CATEGORIAS_EGRESO: list[tuple[str, float, float]] = [
    ("Semillas", 200_000.0, 1_500_000.0),
    ("Abono/Fertilizante", 500_000.0, 3_000_000.0),
    ("Combustible", 150_000.0, 800_000.0),
    ("Mano de obra", 1_000_000.0, 4_000_000.0),
    ("Servicios públicos", 100_000.0, 500_000.0),
    ("Mantenimiento maquinaria", 300_000.0, 2_000_000.0),
    ("Transporte", 200_000.0, 1_200_000.0),
]

CLIENTES: list[str] = [
    "Cooperativa Cafetera del Huila",
    "Distribuidora Agro Valle",
    "Exportadora Nacional S.A.",
    "Central de Abastos Bogotá",
    "Federación Nacional de Cacaoteros",
    "Almacenes Agropecuarios del Tolima",
    "Comercializadora Frutas del Eje",
    "Supermercados La Cosecha",
]

PROVEEDORES: list[str] = [
    "AgroInsumos Ltda.",
    "Transportes del Campo S.A.",
    "Semillas del Pacífico",
    "Ferretería Agrícola El Surco",
    "Combustibles Rurales S.A.S.",
    "Servicios Eléctricos Campesinos",
    "Taller Mecánico La Hacienda",
    "Distribuidora de Abonos Boyacá",
    "Riego y Tecnología Agro",
    "Cooperativa de Trabajo Rural",
]

ACTIVOS_FIJOS_CATALOGO: list[tuple[str, str, float, float]] = [
    ("Tractor John Deere 5075E", "MAQUINARIA", 120_000_000.0, 0.10),
    ("Camioneta Toyota Hilux 4x4", "VEHICULO", 95_000_000.0, 0.20),
    ("Terreno Lote Norte 5 ha", "TERRENO", 250_000_000.0, 0.0),
    ("Sistema de riego por goteo", "EQUIPO", 18_000_000.0, 0.15),
    ("Cosechadora de café", "MAQUINARIA", 45_000_000.0, 0.12),
    ("Motobomba diésel 3 pulgadas", "EQUIPO", 4_500_000.0, 0.15),
    ("Remolque agrícola 5 toneladas", "VEHICULO", 22_000_000.0, 0.10),
    ("Guadañadora industrial", "MAQUINARIA", 3_800_000.0, 0.15),
]


# ---------------------------------------------------------------------------
# Funciones de creación de tablas
# ---------------------------------------------------------------------------

def _crear_tablas(conn: sqlite3.Connection) -> None:
    """Crea las 5 tablas del esquema financiero de EverGreen.

    Args:
        conn: Conexión activa a la base de datos SQLite.
    """
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perfil_productor (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            farm_name TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            nit TEXT NOT NULL,
            tax_bracket TEXT NOT NULL,
            registered_since DATE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY,
            date DATE NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('INGRESO', 'EGRESO')),
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            account_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facturas_venta (
            invoice_id INTEGER PRIMARY KEY,
            date_issued DATE NOT NULL,
            date_due DATE NOT NULL,
            client_name TEXT NOT NULL,
            total_amount REAL NOT NULL,
            vat_amount REAL NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('PAID', 'PENDING', 'OVERDUE'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cuentas_por_pagar (
            payable_id INTEGER PRIMARY KEY,
            supplier_name TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date DATE NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('PENDING', 'PAID', 'OVERDUE'))
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activos_fijos (
            asset_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('MAQUINARIA', 'TERRENO', 'VEHICULO', 'EQUIPO')),
            purchase_date DATE NOT NULL,
            purchase_value REAL NOT NULL,
            current_value REAL NOT NULL,
            depreciation_rate REAL NOT NULL
        )
    """)

    conn.commit()


# ---------------------------------------------------------------------------
# Funciones de generación de datos
# ---------------------------------------------------------------------------

def _generar_perfil(conn: sqlite3.Connection) -> None:
    """Inserta 1 perfil de productor agrícola colombiano.

    Args:
        conn: Conexión activa a la base de datos SQLite.
    """
    conn.execute(
        "INSERT INTO perfil_productor VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            1,
            "Carlos Méndez Rodríguez",
            "Finca El Porvenir",
            "Café y Cacao",
            "900123456-7",
            "Régimen Simple",
            "2019-03-15",
        ),
    )
    conn.commit()


def _generar_movimientos(conn: sqlite3.Connection, cantidad: int = 36) -> None:
    """Genera movimientos financieros (ingresos y egresos) en los últimos 6 meses.

    Distribuye aproximadamente 40% ingresos y 60% egresos para simular
    un flujo de caja realista de una finca agrícola.

    Args:
        conn: Conexión activa a la base de datos SQLite.
        cantidad: Número total de movimientos a generar (mínimo 30).
    """
    hoy = date.today()
    inicio = hoy - timedelta(days=180)
    registros: list[tuple] = []

    num_ingresos = max(12, int(cantidad * 0.4))
    num_egresos = cantidad - num_ingresos

    for i in range(1, num_ingresos + 1):
        fecha = inicio + timedelta(days=random.randint(0, 180))
        cat, monto_min, monto_max = random.choice(CATEGORIAS_INGRESO)
        monto = round(random.uniform(monto_min, monto_max), -3)
        desc = f"{cat} — {fecha.strftime('%B %Y')}"
        registros.append((i, fecha.isoformat(), "INGRESO", cat, monto, desc, 1))

    for j in range(1, num_egresos + 1):
        idx = num_ingresos + j
        fecha = inicio + timedelta(days=random.randint(0, 180))
        cat, monto_min, monto_max = random.choice(CATEGORIAS_EGRESO)
        monto = round(random.uniform(monto_min, monto_max), -3)
        desc = f"{cat} — {fecha.strftime('%B %Y')}"
        registros.append((idx, fecha.isoformat(), "EGRESO", cat, monto, desc, 1))

    conn.executemany(
        "INSERT INTO movimientos VALUES (?, ?, ?, ?, ?, ?, ?)", registros
    )
    conn.commit()


def _generar_facturas(conn: sqlite3.Connection, cantidad: int = 18) -> None:
    """Genera facturas de venta con distribución 60/30/10% PAID/PENDING/OVERDUE.

    La distribución se calcula con redondeo para respetar el ±5% de tolerancia.

    Args:
        conn: Conexión activa a la base de datos SQLite.
        cantidad: Número total de facturas a generar (mínimo 15).
    """
    hoy = date.today()

    num_paid = max(1, round(cantidad * 0.60))
    num_overdue = max(1, round(cantidad * 0.10))
    num_pending = cantidad - num_paid - num_overdue

    estados: list[str] = (
        ["PAID"] * num_paid
        + ["PENDING"] * num_pending
        + ["OVERDUE"] * num_overdue
    )
    random.shuffle(estados)

    registros: list[tuple] = []
    for i, estado in enumerate(estados, start=1):
        dias_atras = random.randint(10, 150)
        fecha_emision = hoy - timedelta(days=dias_atras)
        plazo = random.choice([30, 45, 60])

        if estado == "PAID":
            fecha_vencimiento = fecha_emision + timedelta(days=plazo)
        elif estado == "PENDING":
            fecha_vencimiento = hoy + timedelta(days=random.randint(5, 45))
        else:  # OVERDUE
            fecha_vencimiento = hoy - timedelta(days=random.randint(5, 60))

        cliente = random.choice(CLIENTES)
        monto_total = round(random.uniform(1_500_000.0, 12_000_000.0), -3)
        monto_iva = round(monto_total * 0.19, 0)

        registros.append((
            i,
            fecha_emision.isoformat(),
            fecha_vencimiento.isoformat(),
            cliente,
            monto_total,
            monto_iva,
            estado,
        ))

    conn.executemany(
        "INSERT INTO facturas_venta VALUES (?, ?, ?, ?, ?, ?, ?)", registros
    )
    conn.commit()


def _generar_cuentas_por_pagar(conn: sqlite3.Connection, cantidad: int = 12) -> None:
    """Genera cuentas por pagar con proveedores agrícolas colombianos.

    Args:
        conn: Conexión activa a la base de datos SQLite.
        cantidad: Número total de cuentas por pagar (mínimo 10).
    """
    hoy = date.today()
    registros: list[tuple] = []

    for i in range(1, cantidad + 1):
        proveedor = random.choice(PROVEEDORES)
        cat, monto_min, monto_max = random.choice(CATEGORIAS_EGRESO)
        monto = round(random.uniform(monto_min, monto_max), -3)
        dias_vencimiento = random.randint(-30, 60)
        fecha_vencimiento = hoy + timedelta(days=dias_vencimiento)

        if dias_vencimiento < -5:
            estado = random.choice(["OVERDUE", "PAID"])
        elif dias_vencimiento < 0:
            estado = "OVERDUE"
        else:
            estado = random.choice(["PENDING", "PAID"])

        registros.append((
            i, proveedor, monto, fecha_vencimiento.isoformat(), cat, estado,
        ))

    conn.executemany(
        "INSERT INTO cuentas_por_pagar VALUES (?, ?, ?, ?, ?, ?)", registros
    )
    conn.commit()


def _generar_activos_fijos(conn: sqlite3.Connection, cantidad: int = 6) -> None:
    """Genera activos fijos agrícolas con depreciación calculada.

    Selecciona aleatoriamente del catálogo de activos y calcula el valor
    actual basado en la depreciación lineal.

    Args:
        conn: Conexión activa a la base de datos SQLite.
        cantidad: Número de activos a generar (entre 5 y 8).
    """
    cantidad = max(5, min(8, cantidad))
    seleccion = random.sample(
        ACTIVOS_FIJOS_CATALOGO, k=min(cantidad, len(ACTIVOS_FIJOS_CATALOGO))
    )
    registros: list[tuple] = []

    for i, (nombre, categoria, valor_compra, tasa_dep) in enumerate(seleccion, start=1):
        anios_atras = random.uniform(0.5, 5.0)
        fecha_compra = date.today() - timedelta(days=int(anios_atras * 365))
        dep_acumulada = valor_compra * tasa_dep * anios_atras
        valor_actual = max(0.0, round(valor_compra - dep_acumulada, 0))

        registros.append((
            i, nombre, categoria, fecha_compra.isoformat(),
            valor_compra, valor_actual, tasa_dep,
        ))

    conn.executemany(
        "INSERT INTO activos_fijos VALUES (?, ?, ?, ?, ?, ?, ?)", registros
    )
    conn.commit()


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def generar_base_de_datos(db_path: str | None = None) -> str:
    """Genera la base de datos SQLite completa con datos mock.

    Args:
        db_path: Ruta al archivo de base de datos. Si es ``None``, usa
            la variable de entorno ``SQLITE_DB_PATH`` o ``./fin.db``
            relativo al directorio del proyecto.

    Returns:
        Ruta absoluta al archivo de base de datos generado.
    """
    if db_path is None:
        db_path = os.environ.get("SQLITE_DB_PATH")

    if db_path is None:
        # Por defecto: ./fin.db relativo al directorio del proyecto
        proyecto_dir = Path(__file__).resolve().parent.parent
        db_path = str(proyecto_dir / "fin.db")

    # Eliminar base de datos existente para regenerar desde cero
    ruta = Path(db_path)
    if ruta.exists():
        ruta.unlink()

    conn = sqlite3.connect(db_path)
    try:
        _crear_tablas(conn)
        _generar_perfil(conn)
        _generar_movimientos(conn, cantidad=36)
        _generar_facturas(conn, cantidad=18)
        _generar_cuentas_por_pagar(conn, cantidad=12)
        _generar_activos_fijos(conn, cantidad=6)
    finally:
        conn.close()

    print(f"Base de datos generada exitosamente: {db_path}")

    # Resumen
    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()
        for tabla in [
            "perfil_productor", "movimientos", "facturas_venta",
            "cuentas_por_pagar", "activos_fijos",
        ]:
            cur.execute(f"SELECT COUNT(*) FROM {tabla}")  # noqa: S608
            conteo = cur.fetchone()[0]
            print(f"  {tabla}: {conteo} registros")

        # Distribución de facturas
        cur.execute("SELECT COUNT(*) FROM facturas_venta")
        total_facturas = cur.fetchone()[0]
        print("\n  Distribución de facturas:")
        cur.execute(
            "SELECT status, COUNT(*) FROM facturas_venta GROUP BY status"
        )
        for estado, conteo in cur.fetchall():
            porcentaje = (conteo / total_facturas) * 100 if total_facturas else 0
            print(f"    {estado}: {conteo} ({porcentaje:.1f}%)")
    finally:
        conn.close()

    return str(ruta.resolve())


if __name__ == "__main__":
    generar_base_de_datos()
