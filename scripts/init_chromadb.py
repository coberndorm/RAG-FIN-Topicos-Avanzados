#!/usr/bin/env python3
"""
Inicialización de la colección ChromaDB para FIN-Advisor.

Script independiente que crea (o verifica) la colección persistente
de ChromaDB utilizada por el pipeline ETL y la herramienta
``get_tax_knowledge`` del agente ReAct.

Variables de entorno:
    CHROMA_PERSIST_DIR: Directorio de persistencia de ChromaDB.
        Por defecto: ``./chroma_data``

Uso:
    python scripts/init_chromadb.py
"""

from __future__ import annotations

import logging
import os
import sys

import chromadb

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
NOMBRE_COLECCION: str = "tax_knowledge"
"""Nombre de la colección ChromaDB para la base de conocimiento tributaria."""

CHROMA_PERSIST_DIR_DEFAULT: str = "./chroma_data"
"""Directorio de persistencia por defecto para ChromaDB."""


# ---------------------------------------------------------------------------
# Funciones principales
# ---------------------------------------------------------------------------

def obtener_directorio_persistencia() -> str:
    """Obtiene el directorio de persistencia de ChromaDB.

    Lee la variable de entorno ``CHROMA_PERSIST_DIR``. Si no está
    definida, utiliza el valor por defecto ``./chroma_data``.

    Returns:
        Ruta al directorio de persistencia.
    """
    return os.getenv("CHROMA_PERSIST_DIR", CHROMA_PERSIST_DIR_DEFAULT)


def inicializar_chromadb(persist_dir: str | None = None) -> chromadb.Collection:
    """Inicializa la colección persistente de ChromaDB.

    Crea el cliente persistente y la colección ``tax_knowledge`` con
    métrica de similitud coseno. Si la colección ya existe, la retorna
    sin modificarla.

    Args:
        persist_dir: Directorio de persistencia. Si es ``None``, se
            obtiene de la variable de entorno o el valor por defecto.

    Returns:
        La colección ChromaDB inicializada.
    """
    directorio = persist_dir or obtener_directorio_persistencia()
    logger.info("Directorio de persistencia: %s", directorio)

    # Crear cliente persistente
    cliente = chromadb.PersistentClient(path=directorio)
    logger.info("Cliente ChromaDB creado exitosamente.")

    # Crear o recuperar la colección con métrica coseno
    coleccion = cliente.get_or_create_collection(
        name=NOMBRE_COLECCION,
        metadata={"hnsw:space": "cosine"},
    )

    conteo = coleccion.count()
    logger.info(
        "Colección '%s' lista. Documentos existentes: %d",
        NOMBRE_COLECCION,
        conteo,
    )

    return coleccion


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    """Punto de entrada principal del script."""
    logger.info("=== Inicialización de ChromaDB para FIN-Advisor ===")

    try:
        coleccion = inicializar_chromadb()
        logger.info(
            "✅ Colección '%s' inicializada correctamente con métrica coseno.",
            NOMBRE_COLECCION,
        )
        logger.info("   Documentos en la colección: %d", coleccion.count())
    except Exception as e:
        logger.error("❌ Error al inicializar ChromaDB: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
