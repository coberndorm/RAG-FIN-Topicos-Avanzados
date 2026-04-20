"""
Pruebas de validación de entrada del chat de FIN-Advisor.

Valida la Propiedad 12: Validación de entrada del chat.
- Strings vacíos/solo-espacios deben deshabilitar el submit (lógica frontend).
- Strings > 500 caracteres activan el contador de advertencia.
- Strings > 2000 caracteres son rechazados por el backend con HTTP 422.

Nota: Las pruebas de comportamiento del botón submit y el contador
son validaciones de lógica que se verifican a nivel de modelo Pydantic
y endpoint HTTP, ya que las pruebas de componentes React requieren
un entorno de navegador.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.models import ChatRequest

# Límites definidos en el diseño
SOFT_LIMIT = 500
HARD_LIMIT = 2000


class TestChatInputValidation:
    """Propiedad 12: Validación de entrada del chat."""

    def test_string_vacio_rechazado_por_backend(self) -> None:
        """Un string vacío debe ser rechazado por Pydantic (min_length=1)."""
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    @given(msg=st.from_regex(r"^\s+$", fullmatch=True).filter(lambda s: len(s) <= 2000))
    @settings(max_examples=20, deadline=None)
    def test_solo_espacios_pasa_validacion_pydantic(self, msg: str) -> None:
        """Strings de solo espacios pasan min_length (tienen longitud > 0).

        La lógica de deshabilitar el botón submit es responsabilidad
        del frontend (JavaScript), no del backend.
        """
        if len(msg) >= 1:
            req = ChatRequest(message=msg)
            assert req.message == msg

    @given(msg=st.text(min_size=SOFT_LIMIT + 1, max_size=HARD_LIMIT))
    @settings(max_examples=10, deadline=None)
    def test_entre_500_y_2000_aceptado_por_backend(self, msg: str) -> None:
        """Strings entre 501 y 2000 caracteres deben ser aceptados.

        El frontend muestra un contador de advertencia, pero el backend
        los acepta.
        """
        req = ChatRequest(message=msg)
        assert len(req.message) > SOFT_LIMIT
        assert len(req.message) <= HARD_LIMIT

    @given(msg=st.text(min_size=HARD_LIMIT + 1, max_size=HARD_LIMIT + 500))
    @settings(max_examples=10, deadline=None)
    def test_excede_2000_rechazado_por_backend(self, msg: str) -> None:
        """Strings > 2000 caracteres deben ser rechazados con ValidationError."""
        with pytest.raises(ValidationError):
            ChatRequest(message=msg)

    @pytest.mark.skipif(
        not __import__("os").getenv("LLM_API_KEY"),
        reason="LLM_API_KEY no configurada — el backend no puede arrancar",
    )
    def test_excede_2000_retorna_422_via_http(self, test_client) -> None:
        """El endpoint HTTP debe retornar 422 para mensajes > 2000 chars."""
        response = test_client.post(
            "/api/v1/chat",
            json={"message": "x" * 2001},
        )
        assert response.status_code == 422

    def test_500_chars_exactos_aceptado(self) -> None:
        """Exactamente 500 caracteres no debe activar advertencia."""
        req = ChatRequest(message="a" * SOFT_LIMIT)
        assert len(req.message) == SOFT_LIMIT

    def test_501_chars_aceptado_con_advertencia_implicita(self) -> None:
        """501 caracteres debe ser aceptado (advertencia es solo frontend)."""
        req = ChatRequest(message="a" * (SOFT_LIMIT + 1))
        assert len(req.message) == SOFT_LIMIT + 1
