"""
Fixtures compartidos para la suite de pruebas de FIN-Advisor.

Provee fixtures de pytest reutilizables para:
- Base de datos SQLite temporal con datos mock pre-poblados.
- Colección ChromaDB temporal con embeddings de ejemplo.
- Instancia de TestClient de FastAPI.
"""

import sqlite3
from datetime import date, timedelta

import chromadb
import pytest


# ---------------------------------------------------------------------------
# Fixture 1: Base de datos SQLite temporal pre-poblada
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_db(tmp_path):
    """Crea una base de datos SQLite temporal con datos mock realistas.

    Genera las 5 tablas del esquema financiero de EverGreen
    (perfil_productor, movimientos, facturas_venta, cuentas_por_pagar,
    activos_fijos) y las pre-puebla con un conjunto pequeño de datos
    representativos de un productor agrícola colombiano.

    Args:
        tmp_path: Fixture de pytest que provee un directorio temporal.

    Yields:
        str: Ruta absoluta al archivo de base de datos SQLite temporal.
    """
    db_path = str(tmp_path / "test_fin.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --- Crear tablas ---
    cursor.execute("""
        CREATE TABLE perfil_productor (
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
        CREATE TABLE movimientos (
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
        CREATE TABLE facturas_venta (
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
        CREATE TABLE cuentas_por_pagar (
            payable_id INTEGER PRIMARY KEY,
            supplier_name TEXT NOT NULL,
            amount REAL NOT NULL,
            due_date DATE NOT NULL,
            category TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('PENDING', 'PAID', 'OVERDUE'))
        )
    """)

    cursor.execute("""
        CREATE TABLE activos_fijos (
            asset_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('MAQUINARIA', 'TERRENO', 'VEHICULO', 'EQUIPO')),
            purchase_date DATE NOT NULL,
            purchase_value REAL NOT NULL,
            current_value REAL NOT NULL,
            depreciation_rate REAL NOT NULL
        )
    """)

    # --- Insertar datos mock ---
    hoy = date.today()

    # 1 productor
    cursor.execute(
        "INSERT INTO perfil_productor VALUES (?, ?, ?, ?, ?, ?, ?)",
        (1, "Carlos Méndez", "Finca El Porvenir", "Café y Cacao",
         "900123456-7", "Régimen Simple", "2019-03-15"),
    )

    # ~5 movimientos (ingresos y egresos recientes)
    movimientos = [
        (1, (hoy - timedelta(days=10)).isoformat(), "INGRESO",
         "Venta cosecha", 8_500_000.0, "Venta de café pergamino", 1),
        (2, (hoy - timedelta(days=25)).isoformat(), "EGRESO",
         "Abono/Fertilizante", 1_200_000.0, "Compra de fertilizante NPK", 1),
        (3, (hoy - timedelta(days=40)).isoformat(), "INGRESO",
         "Subsidio gobierno", 3_000_000.0, "Incentivo agropecuario", 1),
        (4, (hoy - timedelta(days=55)).isoformat(), "EGRESO",
         "Mano de obra", 2_500_000.0, "Pago jornaleros recolección", 1),
        (5, (hoy - timedelta(days=5)).isoformat(), "EGRESO",
         "Combustible", 450_000.0, "Diésel para tractor", 1),
    ]
    cursor.executemany(
        "INSERT INTO movimientos VALUES (?, ?, ?, ?, ?, ?, ?)", movimientos
    )

    # ~3 facturas de venta
    facturas = [
        (1, (hoy - timedelta(days=30)).isoformat(),
         (hoy - timedelta(days=0)).isoformat(),
         "Cooperativa Cafetera del Huila", 5_000_000.0, 950_000.0, "PAID"),
        (2, (hoy - timedelta(days=15)).isoformat(),
         (hoy + timedelta(days=15)).isoformat(),
         "Distribuidora Agro Valle", 3_200_000.0, 608_000.0, "PENDING"),
        (3, (hoy - timedelta(days=60)).isoformat(),
         (hoy - timedelta(days=30)).isoformat(),
         "Exportadora Nacional S.A.", 7_800_000.0, 1_482_000.0, "OVERDUE"),
    ]
    cursor.executemany(
        "INSERT INTO facturas_venta VALUES (?, ?, ?, ?, ?, ?, ?)", facturas
    )

    # ~2 cuentas por pagar
    cuentas_por_pagar = [
        (1, "AgroInsumos Ltda.", 1_800_000.0,
         (hoy + timedelta(days=20)).isoformat(), "Abono/Fertilizante", "PENDING"),
        (2, "Transportes del Campo S.A.", 650_000.0,
         (hoy + timedelta(days=10)).isoformat(), "Transporte", "PENDING"),
    ]
    cursor.executemany(
        "INSERT INTO cuentas_por_pagar VALUES (?, ?, ?, ?, ?, ?)",
        cuentas_por_pagar,
    )

    # ~2 activos fijos
    activos = [
        (1, "Tractor John Deere 5075E", "MAQUINARIA",
         "2021-06-01", 120_000_000.0, 84_000_000.0, 0.10),
        (2, "Camioneta Toyota Hilux", "VEHICULO",
         "2022-01-15", 95_000_000.0, 76_000_000.0, 0.20),
    ]
    cursor.executemany(
        "INSERT INTO activos_fijos VALUES (?, ?, ?, ?, ?, ?, ?)", activos
    )

    conn.commit()
    conn.close()

    yield db_path

    # Limpieza: tmp_path se elimina automáticamente por pytest


# ---------------------------------------------------------------------------
# Fixture 2: Colección ChromaDB temporal con embeddings de ejemplo
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_chroma_collection():
    """Crea una colección ChromaDB en memoria con documentos de ejemplo.

    Agrega fragmentos representativos de la base de conocimiento tributaria
    con metadatos completos (article_number, source_document, topic_tags,
    document_type, date_ingested, chunk_index, total_chunks_in_article).

    Yields:
        chromadb.Collection: Colección ChromaDB temporal con datos de prueba.
    """
    client = chromadb.Client()  # Cliente en memoria (efímero)
    collection = client.get_or_create_collection(
        name="test_tax_knowledge",
        metadata={"hnsw:space": "cosine"},
    )

    # Documentos de ejemplo representativos de la base de conocimiento
    documentos = [
        "Artículo 258-1. Descuento del IVA en la adquisición de bienes de "
        "capital. Los responsables del impuesto sobre la renta podrán "
        "descontar del impuesto sobre la renta el IVA pagado en la "
        "adquisición de bienes de capital.",
        "Artículo 57-1. Rentas exentas de la actividad agrícola. Las rentas "
        "provenientes de inversiones en nuevos cultivos de tardío rendimiento "
        "estarán exentas del impuesto sobre la renta por un período de diez "
        "(10) años.",
        "Programa de incentivos para la compra de maquinaria agrícola. El "
        "gobierno nacional ofrece líneas de crédito con tasa subsidiada para "
        "la adquisición de maquinaria y equipo agrícola a través de FINAGRO.",
        "Calendario tributario 2024. Declaración de renta personas naturales: "
        "agosto a octubre 2024 según último dígito del NIT. Declaración de "
        "IVA bimestral: fechas límite cada dos meses.",
    ]

    metadatos = [
        {
            "article_number": "258-1",
            "source_document": "estatuto_tributario_libro3.md",
            "topic_tags": "IVA,bienes_de_capital,maquinaria",
            "document_type": "legal",
            "date_ingested": "2024-01-15",
            "chunk_index": 0,
            "total_chunks_in_article": 2,
        },
        {
            "article_number": "57-1",
            "source_document": "estatuto_tributario_libro1.md",
            "topic_tags": "renta,exenciones,agricultura",
            "document_type": "legal",
            "date_ingested": "2024-01-15",
            "chunk_index": 0,
            "total_chunks_in_article": 1,
        },
        {
            "article_number": "",
            "source_document": "beneficios_compra_maquinaria.md",
            "topic_tags": "maquinaria,crédito,FINAGRO",
            "document_type": "guide",
            "date_ingested": "2024-01-15",
            "chunk_index": 0,
            "total_chunks_in_article": 3,
        },
        {
            "article_number": "",
            "source_document": "calendario_tributario_2024.md",
            "topic_tags": "calendario,renta,IVA",
            "document_type": "calendar",
            "date_ingested": "2024-01-15",
            "chunk_index": 0,
            "total_chunks_in_article": 1,
        },
    ]

    ids = [f"test_doc_{i}" for i in range(len(documentos))]

    collection.add(
        documents=documentos,
        metadatas=metadatos,
        ids=ids,
    )

    yield collection

    # Limpieza: eliminar la colección para evitar conflictos entre pruebas
    client.delete_collection(name="test_tax_knowledge")


# ---------------------------------------------------------------------------
# Fixture 3: TestClient de FastAPI
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_client():
    """Crea una instancia de TestClient para la aplicación FastAPI.

    Intenta importar la aplicación desde ``backend.app``. Si el módulo
    aún no existe (desarrollo incremental), el fixture se salta
    automáticamente con ``pytest.skip``.

    Yields:
        httpx.AsyncClient | starlette.testclient.TestClient:
            Cliente de prueba configurado para la API de FIN-Advisor.
    """
    try:
        from backend.app import app  # noqa: WPS433
    except (ImportError, ModuleNotFoundError):
        pytest.skip(
            "El módulo backend.app aún no existe. "
            "Este fixture estará disponible cuando se implemente el backend."
        )
        return  # pragma: no cover

    from starlette.testclient import TestClient

    with TestClient(app) as client:
        yield client
