"""
Abstracción de proveedores LLM — FIN-Advisor.

Implementa el patrón Strategy para soportar múltiples proveedores de LLM
(HuggingFace, Gemini, ChatGPT, Groq) intercambiables mediante variables
de entorno. Todos los proveedores usan temperature=0.3 para generar
respuestas determinísticas en asesoría financiera.

Variables de entorno:
    LLM_PROVIDER: Proveedor a usar (``huggingface``, ``gemini``,
        ``chatgpt``, ``groq``). Por defecto ``huggingface``.
    LLM_API_KEY: Clave de API del proveedor seleccionado.
    LLM_MODEL_NAME: Nombre del modelo (opcional, cada proveedor
        tiene un valor por defecto).
"""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from langchain_core.language_models import BaseLanguageModel

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
TEMPERATURA_DEFAULT: float = 0.3
"""Temperatura por defecto para todos los proveedores."""

MODELOS_DEFAULT: dict[str, str] = {
    "gemini": "gemini-1.5-flash",
    "chatgpt": "gpt-4o-mini",
    "groq": "llama-3.3-70b-versatile",
}
"""Modelos por defecto para cada proveedor."""


# ---------------------------------------------------------------------------
# Interfaz base (Strategy)
# ---------------------------------------------------------------------------

class ProveedorLLM(ABC):
    """Interfaz base para proveedores de LLM.

    Define el contrato que deben cumplir todos los proveedores
    de modelos de lenguaje soportados por FIN-Advisor.
    """

    @abstractmethod
    def obtener_llm(self) -> BaseLanguageModel:
        """Crea y retorna la instancia del LLM configurado.

        Returns:
            Instancia de LangChain compatible con ``BaseLanguageModel``.
        """

    @abstractmethod
    def obtener_nombre_modelo(self) -> str:
        """Retorna el nombre del modelo configurado.

        Returns:
            Identificador del modelo.
        """


# ---------------------------------------------------------------------------
# Proveedores concretos
# ---------------------------------------------------------------------------

class HuggingFaceProvider(ProveedorLLM):
    """Proveedor de LLM usando HuggingFace Inference API.

    Utiliza ``langchain_huggingface.HuggingFaceEndpoint`` para conectarse
    a modelos alojados en HuggingFace Hub.

    Attributes:
        nombre_modelo: Identificador del repositorio del modelo.
        api_key: Token de API de HuggingFace.
    """

    def __init__(
        self,
        api_key: str,
        nombre_modelo: str | None = None,
    ) -> None:
        """Inicializa el proveedor de HuggingFace.

        Args:
            api_key: Token de API de HuggingFace.
            nombre_modelo: Repo ID del modelo. Si es ``None``,
                usa el modelo por defecto.
        """
        self.api_key = api_key
        self.nombre_modelo = nombre_modelo or MODELOS_DEFAULT["gemini-1.5-flash"]

    def obtener_llm(self) -> BaseLanguageModel:
        """Crea una instancia de HuggingFaceEndpoint.

        Returns:
            Instancia de ``HuggingFaceEndpoint`` configurada.
        """
        from langchain_huggingface import HuggingFaceEndpoint

        logger.info(
            "Inicializando proveedor HuggingFace con modelo: %s",
            self.nombre_modelo,
        )
        return HuggingFaceEndpoint(
            repo_id=self.nombre_modelo,
            huggingfacehub_api_token=self.api_key,
            temperature=TEMPERATURA_DEFAULT,
            max_new_tokens=1024,
        )

    def obtener_nombre_modelo(self) -> str:
        """Retorna el nombre del modelo configurado.

        Returns:
            Repo ID del modelo de HuggingFace.
        """
        return self.nombre_modelo


class GeminiProvider(ProveedorLLM):
    """Proveedor de LLM usando Google Gemini API.

    Utiliza ``langchain_google_genai.ChatGoogleGenerativeAI`` para
    conectarse a los modelos Gemini de Google.

    Attributes:
        nombre_modelo: Identificador del modelo Gemini.
        api_key: Clave de API de Google.
    """

    def __init__(
        self,
        api_key: str,
        nombre_modelo: str | None = None,
    ) -> None:
        """Inicializa el proveedor de Gemini.

        Args:
            api_key: Clave de API de Google.
            nombre_modelo: Modelo Gemini a usar. Si es ``None``,
                usa el modelo por defecto.
        """
        self.api_key = api_key
        self.nombre_modelo = nombre_modelo or MODELOS_DEFAULT["gemini"]

    def obtener_llm(self) -> BaseLanguageModel:
        """Crea una instancia de ChatGoogleGenerativeAI.

        Returns:
            Instancia de ``ChatGoogleGenerativeAI`` configurada.
        """
        from langchain_google_genai import ChatGoogleGenerativeAI

        logger.info(
            "Inicializando proveedor Gemini con modelo: %s",
            self.nombre_modelo,
        )
        return ChatGoogleGenerativeAI(
            model=self.nombre_modelo,
            temperature=TEMPERATURA_DEFAULT,
            google_api_key=self.api_key,
        )

    def obtener_nombre_modelo(self) -> str:
        """Retorna el nombre del modelo configurado.

        Returns:
            Identificador del modelo Gemini.
        """
        return self.nombre_modelo


class ChatGPTProvider(ProveedorLLM):
    """Proveedor de LLM usando OpenAI ChatGPT API.

    Utiliza ``langchain_openai.ChatOpenAI`` para conectarse a los
    modelos de OpenAI.

    Attributes:
        nombre_modelo: Identificador del modelo de OpenAI.
        api_key: Clave de API de OpenAI.
    """

    def __init__(
        self,
        api_key: str,
        nombre_modelo: str | None = None,
    ) -> None:
        """Inicializa el proveedor de ChatGPT.

        Args:
            api_key: Clave de API de OpenAI.
            nombre_modelo: Modelo de OpenAI a usar. Si es ``None``,
                usa el modelo por defecto.
        """
        self.api_key = api_key
        self.nombre_modelo = nombre_modelo or MODELOS_DEFAULT["chatgpt"]

    def obtener_llm(self) -> BaseLanguageModel:
        """Crea una instancia de ChatOpenAI.

        Returns:
            Instancia de ``ChatOpenAI`` configurada.
        """
        from langchain_openai import ChatOpenAI

        logger.info(
            "Inicializando proveedor ChatGPT con modelo: %s",
            self.nombre_modelo,
        )
        return ChatOpenAI(
            model=self.nombre_modelo,
            temperature=TEMPERATURA_DEFAULT,
            openai_api_key=self.api_key,
        )

    def obtener_nombre_modelo(self) -> str:
        """Retorna el nombre del modelo configurado.

        Returns:
            Identificador del modelo de OpenAI.
        """
        return self.nombre_modelo


class GroqProvider(ProveedorLLM):
    """Proveedor de LLM usando Groq API.

    Utiliza ``langchain_groq.ChatGroq`` para conectarse a los modelos
    de Groq, conocidos por su velocidad de inferencia (≤400ms).

    Attributes:
        nombre_modelo: Identificador del modelo de Groq.
        api_key: Clave de API de Groq.
    """

    def __init__(
        self,
        api_key: str,
        nombre_modelo: str | None = None,
    ) -> None:
        """Inicializa el proveedor de Groq.

        Args:
            api_key: Clave de API de Groq.
            nombre_modelo: Modelo de Groq a usar. Si es ``None``,
                usa el modelo por defecto.
        """
        self.api_key = api_key
        self.nombre_modelo = nombre_modelo or MODELOS_DEFAULT["groq"]

    def obtener_llm(self) -> BaseLanguageModel:
        """Crea una instancia de ChatGroq.

        Returns:
            Instancia de ``ChatGroq`` configurada.
        """
        from langchain_groq import ChatGroq

        logger.info(
            "Inicializando proveedor Groq con modelo: %s",
            self.nombre_modelo,
        )
        return ChatGroq(
            model=self.nombre_modelo,
            temperature=TEMPERATURA_DEFAULT,
            groq_api_key=self.api_key,
        )

    def obtener_nombre_modelo(self) -> str:
        """Retorna el nombre del modelo configurado.

        Returns:
            Identificador del modelo de Groq.
        """
        return self.nombre_modelo


# ---------------------------------------------------------------------------
# Mapeo de proveedores
# ---------------------------------------------------------------------------

_PROVEEDORES: dict[str, type[ProveedorLLM]] = {
    "huggingface": HuggingFaceProvider,
    "gemini": GeminiProvider,
    "chatgpt": ChatGPTProvider,
    "groq": GroqProvider,
}
"""Mapeo de nombres de proveedor a sus clases concretas."""


# ---------------------------------------------------------------------------
# Función fábrica
# ---------------------------------------------------------------------------

def crear_proveedor_llm(
    proveedor: str | None = None,
    api_key: str | None = None,
    nombre_modelo: str | None = None,
) -> ProveedorLLM:
    """Crea un proveedor de LLM según la configuración.

    Lee las variables de entorno ``LLM_PROVIDER``, ``LLM_API_KEY`` y
    ``LLM_MODEL_NAME`` si no se proporcionan como argumentos. Si
    ``LLM_PROVIDER`` no está definido, usa HuggingFace por defecto.

    Args:
        proveedor: Nombre del proveedor (``huggingface``, ``gemini``,
            ``chatgpt``, ``groq``). Si es ``None``, lee de env.
        api_key: Clave de API. Si es ``None``, lee de env.
        nombre_modelo: Nombre del modelo. Si es ``None``, lee de env
            o usa el valor por defecto del proveedor.

    Returns:
        Instancia del proveedor de LLM configurado.

    Raises:
        ValueError: Si el proveedor no es válido o falta la clave de API.
    """
    nombre_proveedor = (
        proveedor
        or os.getenv("LLM_PROVIDER", "huggingface")
    ).lower().strip()

    clave_api = api_key or os.getenv("LLM_API_KEY")
    modelo = nombre_modelo or os.getenv("LLM_MODEL_NAME")

    # Validar proveedor
    if nombre_proveedor not in _PROVEEDORES:
        proveedores_validos = ", ".join(sorted(_PROVEEDORES.keys()))
        raise ValueError(
            f"Proveedor de LLM no válido: '{nombre_proveedor}'. "
            f"Los proveedores soportados son: {proveedores_validos}"
        )

    # Validar clave de API
    if not clave_api:
        raise ValueError(
            f"Se requiere una clave de API para el proveedor '{nombre_proveedor}'. "
            f"Configure la variable de entorno LLM_API_KEY con su clave de "
            f"API de {nombre_proveedor}."
        )

    # Crear instancia del proveedor
    clase_proveedor = _PROVEEDORES[nombre_proveedor]
    kwargs: dict[str, Any] = {"api_key": clave_api}
    if modelo:
        kwargs["nombre_modelo"] = modelo

    logger.info(
        "Creando proveedor LLM: %s (modelo: %s)",
        nombre_proveedor,
        modelo or MODELOS_DEFAULT.get(nombre_proveedor, "default"),
    )

    return clase_proveedor(**kwargs)
