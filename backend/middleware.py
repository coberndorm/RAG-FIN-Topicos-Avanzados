"""
Configuración de middleware para el backend de FIN-Advisor.

Define la configuración de CORS para permitir solicitudes desde
el frontend React en desarrollo (``http://localhost:3000``).
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# Orígenes permitidos
# ---------------------------------------------------------------------------

ORIGENES_PERMITIDOS: list[str] = [
    "http://localhost:3000",
]
"""Lista de orígenes permitidos para solicitudes CORS."""


# ---------------------------------------------------------------------------
# Función de configuración
# ---------------------------------------------------------------------------

def configurar_cors(app: FastAPI) -> None:
    """Aplica el middleware CORS a la aplicación FastAPI.

    Permite solicitudes desde el frontend React en desarrollo,
    habilitando todos los métodos HTTP y encabezados para facilitar
    el desarrollo local.

    Args:
        app: Instancia de la aplicación FastAPI.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ORIGENES_PERMITIDOS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
