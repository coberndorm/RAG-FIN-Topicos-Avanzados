"""
Aplicación FastAPI de FIN-Advisor.

Fábrica de la aplicación con ciclo de vida (lifespan) que inicializa
las conexiones a ChromaDB, SQLite y el proveedor de LLM al arrancar.
Registra las rutas de la API y aplica el middleware CORS.

Comportamiento de arranque:
    1. Inicializa conexión a ChromaDB (persistente local).
    2. Inicializa conexión a SQLite (``fin.db``).
    3. Inicializa el proveedor de LLM configurado por variables de entorno.
    4. Si el LLM no es alcanzable → registra advertencia, arranca en modo degradado.
    5. Si falta la clave de API → falla al arrancar con error claro.
"""

from __future__ import annotations

import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import chromadb
from fastapi import FastAPI

from backend.middleware import configurar_cors
from backend.routes import router

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Directorio base del proyecto
# ---------------------------------------------------------------------------
_DIRECTORIO_PROYECTO = Path(__file__).resolve().parent.parent
"""Ruta al directorio raíz del proyecto (RAG-FIN-Topicos-Avanzados/)."""


# ---------------------------------------------------------------------------
# Lifespan (ciclo de vida de la aplicación)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Gestiona el ciclo de vida de la aplicación FastAPI.

    Al iniciar:
        - Conecta a ChromaDB (persistente local).
        - Conecta a SQLite (``fin.db``).
        - Inicializa el proveedor de LLM y crea el agente ReAct.
        - Si el LLM no es alcanzable, arranca en modo degradado.
        - Si falta la clave de API, falla con error claro.

    Al cerrar:
        - Libera recursos (logging de cierre).

    Args:
        app: Instancia de la aplicación FastAPI.

    Yields:
        None: Control al servidor durante la ejecución.

    Raises:
        ValueError: Si falta la clave de API del proveedor de LLM.
    """
    logger.info("Iniciando FIN-Advisor backend...")

    # --- 1. Inicializar ChromaDB ---
    chroma_persist_dir = os.getenv(
        "CHROMA_PERSIST_DIR",
        str(_DIRECTORIO_PROYECTO / "chroma_data"),
    )
    try:
        cliente_chroma = chromadb.PersistentClient(path=chroma_persist_dir)
        app.state.chroma_client = cliente_chroma
        logger.info(
            "ChromaDB inicializado en: %s", chroma_persist_dir
        )
    except Exception:
        logger.warning(
            "No se pudo conectar a ChromaDB en: %s. "
            "La base de conocimiento no estará disponible.",
            chroma_persist_dir,
        )
        app.state.chroma_client = None

    # --- 2. Inicializar SQLite ---
    sqlite_db_path = os.getenv(
        "SQLITE_DB_PATH",
        str(_DIRECTORIO_PROYECTO / "fin.db"),
    )
    try:
        # Verificar que el archivo existe y es accesible
        conn = sqlite3.connect(sqlite_db_path)
        conn.execute("SELECT 1")
        conn.close()
        app.state.sqlite_db_path = sqlite_db_path
        logger.info("SQLite conectado en: %s", sqlite_db_path)
    except Exception:
        logger.warning(
            "No se pudo conectar a SQLite en: %s. "
            "Los datos financieros no estarán disponibles.",
            sqlite_db_path,
        )
        app.state.sqlite_db_path = None

    # --- 3. Inicializar proveedor de LLM y agente ---
    app.state.modo_degradado = False
    app.state.agente = None
    app.state.config_invocacion = {}

    proveedor_nombre = os.getenv("LLM_PROVIDER", "huggingface")
    api_key = os.getenv("LLM_API_KEY", "")

    # Validar clave de API antes de intentar crear el proveedor
    if not api_key or not api_key.strip():
        raise ValueError(
            f"Se requiere la variable de entorno LLM_API_KEY para el "
            f"proveedor '{proveedor_nombre}'. Configure LLM_API_KEY con "
            f"su clave de API antes de iniciar el servidor."
        )

    try:
        from agent.agent_config import crear_agente, obtener_config_invocacion

        agente = crear_agente()
        app.state.agente = agente
        app.state.config_invocacion = obtener_config_invocacion()
        logger.info(
            "Agente ReAct inicializado con proveedor: %s",
            proveedor_nombre,
        )
    except ValueError:
        # Error de configuración (proveedor inválido, API key inválida)
        raise
    except Exception:
        logger.warning(
            "No se pudo inicializar el proveedor de LLM '%s'. "
            "El servidor arrancará en modo degradado. "
            "Las consultas al chat no estarán disponibles.",
            proveedor_nombre,
            exc_info=True,
        )
        app.state.modo_degradado = True

    logger.info("FIN-Advisor backend listo.")

    yield

    # --- Cierre ---
    logger.info("Cerrando FIN-Advisor backend...")


# ---------------------------------------------------------------------------
# Creación de la aplicación
# ---------------------------------------------------------------------------

app = FastAPI(
    title="FIN-Advisor API",
    description="API del asistente financiero RAG para productores agrícolas colombianos.",
    version="1.0.0",
    lifespan=lifespan,
)
"""Instancia principal de la aplicación FastAPI."""

# Aplicar middleware CORS
configurar_cors(app)

# Registrar rutas
app.include_router(router)
