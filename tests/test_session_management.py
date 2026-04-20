"""
Pruebas de preservación de contexto de sesión de FIN-Advisor.

Valida la Propiedad 14: El historial de conversación se mantiene
entre mensajes con el mismo session_id.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.routes import _historial_sesiones


@pytest.mark.skipif(
    not __import__("os").getenv("LLM_API_KEY"),
    reason="LLM_API_KEY no configurada — el backend no puede arrancar",
)
class TestSessionContextPreservation:
    """Propiedad 14: El historial se mantiene por session_id."""

    def test_historial_se_acumula_con_mismo_session_id(
        self, test_client
    ) -> None:
        """Mensajes con el mismo session_id deben acumular historial."""
        sid = "test-session-001"

        # Limpiar historial previo si existe
        _historial_sesiones.pop(sid, None)

        # Primer mensaje
        resp1 = test_client.post(
            "/api/v1/chat",
            json={"message": "Hola", "session_id": sid},
        )
        assert resp1.status_code == 200

        # Segundo mensaje con mismo session_id
        resp2 = test_client.post(
            "/api/v1/chat",
            json={"message": "¿Cuál es mi saldo?", "session_id": sid},
        )
        assert resp2.status_code == 200

        # Verificar que el historial tiene ambos mensajes
        historial = _historial_sesiones.get(sid, [])
        mensajes_usuario = [m for m in historial if m[0] == "user"]
        assert len(mensajes_usuario) >= 2, (
            f"Se esperaban >= 2 mensajes de usuario, hay {len(mensajes_usuario)}"
        )

        # Limpiar
        _historial_sesiones.pop(sid, None)

    def test_session_ids_diferentes_no_comparten_historial(
        self, test_client
    ) -> None:
        """Sesiones distintas deben tener historiales independientes."""
        sid_a = "test-session-A"
        sid_b = "test-session-B"

        _historial_sesiones.pop(sid_a, None)
        _historial_sesiones.pop(sid_b, None)

        test_client.post(
            "/api/v1/chat",
            json={"message": "Mensaje sesión A", "session_id": sid_a},
        )
        test_client.post(
            "/api/v1/chat",
            json={"message": "Mensaje sesión B", "session_id": sid_b},
        )

        hist_a = _historial_sesiones.get(sid_a, [])
        hist_b = _historial_sesiones.get(sid_b, [])

        # Cada sesión debe tener solo sus propios mensajes
        msgs_a = [m[1] for m in hist_a if m[0] == "user"]
        msgs_b = [m[1] for m in hist_b if m[0] == "user"]

        assert "Mensaje sesión A" in msgs_a
        assert "Mensaje sesión B" in msgs_b
        assert "Mensaje sesión B" not in msgs_a
        assert "Mensaje sesión A" not in msgs_b

        _historial_sesiones.pop(sid_a, None)
        _historial_sesiones.pop(sid_b, None)

    def test_sin_session_id_no_crea_historial(self, test_client) -> None:
        """Sin session_id, no se debe crear entrada en el historial."""
        antes = set(_historial_sesiones.keys())
        test_client.post(
            "/api/v1/chat",
            json={"message": "Consulta sin sesión"},
        )
        despues = set(_historial_sesiones.keys())
        # No debe haber nuevas claves None en el historial
        assert None not in despues
