"""
Pruebas de validación de la API de FIN-Advisor.

Valida la Propiedad 13: Solicitudes inválidas a POST /api/v1/chat
retornan HTTP 422 con errores descriptivos.

También incluye pruebas unitarias para el endpoint de salud y
el ciclo de solicitud/respuesta de chat.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.models import ChatRequest, ChatResponse, HealthStatus


# ---------------------------------------------------------------------------
# Propiedad 13: Validación de solicitudes API
# ---------------------------------------------------------------------------

class TestAPIRequestValidation:
    """Propiedad 13: Payloads inválidos son rechazados por Pydantic."""

    def test_mensaje_faltante_rechazado(self) -> None:
        """Un payload sin campo 'message' debe ser rechazado."""
        with pytest.raises(ValidationError):
            ChatRequest()  # type: ignore[call-arg]

    def test_mensaje_vacio_rechazado(self) -> None:
        """Un mensaje vacío debe ser rechazado (min_length=1)."""
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    @given(msg=st.text(min_size=0, max_size=0))
    @settings(max_examples=5, deadline=None)
    def test_mensaje_vacio_property(self, msg: str) -> None:
        with pytest.raises(ValidationError):
            ChatRequest(message=msg)

    def test_mensaje_solo_espacios_aceptado(self) -> None:
        """Un mensaje de solo espacios pasa min_length pero es whitespace."""
        # Pydantic min_length=1 cuenta caracteres, " " tiene longitud 1
        req = ChatRequest(message=" ")
        assert req.message == " "

    def test_mensaje_excede_2000_rechazado(self) -> None:
        """Un mensaje de más de 2000 caracteres debe ser rechazado."""
        with pytest.raises(ValidationError):
            ChatRequest(message="a" * 2001)

    @given(msg=st.text(min_size=2001, max_size=3000))
    @settings(max_examples=10, deadline=None)
    def test_mensaje_largo_rechazado_property(self, msg: str) -> None:
        with pytest.raises(ValidationError):
            ChatRequest(message=msg)

    def test_mensaje_no_string_rechazado(self) -> None:
        """Un message que no es string debe ser rechazado."""
        with pytest.raises(ValidationError):
            ChatRequest(message=123)  # type: ignore[arg-type]

    @given(msg=st.text(min_size=1, max_size=2000))
    @settings(max_examples=20, deadline=None)
    def test_mensaje_valido_aceptado(self, msg: str) -> None:
        """Cualquier string de 1-2000 caracteres debe ser aceptado."""
        req = ChatRequest(message=msg)
        assert req.message == msg


# ---------------------------------------------------------------------------
# Pruebas unitarias para modelos de respuesta
# ---------------------------------------------------------------------------

class TestResponseModels:
    """Pruebas unitarias para los modelos de respuesta."""

    def test_chat_response_valido(self) -> None:
        resp = ChatResponse(
            response="Hola, soy FIN Advisor.",
            sources=[],
            tools_used=[],
        )
        assert resp.response == "Hola, soy FIN Advisor."

    def test_health_status_valido(self) -> None:
        status = HealthStatus(
            backend="ok",
            vector_store="ok",
            financial_database="ok",
            llm_connection="ok",
        )
        assert status.backend == "ok"

    def test_health_status_degradado(self) -> None:
        status = HealthStatus(
            backend="degraded",
            vector_store="unavailable",
            financial_database="ok",
            llm_connection="degraded",
        )
        assert status.vector_store == "unavailable"


# ---------------------------------------------------------------------------
# Pruebas con TestClient (si el backend es importable)
# ---------------------------------------------------------------------------

class TestHealthEndpoint:
    """Pruebas unitarias para GET /api/v1/health."""

    @pytest.mark.skipif(
        not __import__("os").getenv("LLM_API_KEY"),
        reason="LLM_API_KEY no configurada — el backend no puede arrancar",
    )
    def test_health_retorna_200(self, test_client) -> None:
        """El endpoint de salud debe retornar 200."""
        response = test_client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert "backend" in data
        assert "vector_store" in data
        assert "financial_database" in data
        assert "llm_connection" in data


@pytest.mark.skipif(
    not __import__("os").getenv("LLM_API_KEY"),
    reason="LLM_API_KEY no configurada — el backend no puede arrancar",
)
class TestChatEndpointValidation:
    """Pruebas de validación HTTP para POST /api/v1/chat."""

    def test_payload_vacio_retorna_422(self, test_client) -> None:
        response = test_client.post("/api/v1/chat", json={})
        assert response.status_code == 422

    def test_mensaje_faltante_retorna_422(self, test_client) -> None:
        response = test_client.post("/api/v1/chat", json={"session_id": "abc"})
        assert response.status_code == 422

    def test_mensaje_vacio_retorna_422(self, test_client) -> None:
        response = test_client.post("/api/v1/chat", json={"message": ""})
        assert response.status_code == 422

    def test_mensaje_excede_limite_retorna_422(self, test_client) -> None:
        response = test_client.post(
            "/api/v1/chat", json={"message": "x" * 2001}
        )
        assert response.status_code == 422
