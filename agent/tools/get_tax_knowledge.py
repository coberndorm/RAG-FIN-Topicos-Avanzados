"""
Herramienta de recuperación de conocimiento tributario — FIN-Advisor.

Realiza búsqueda por similitud coseno en la colección ChromaDB para
encontrar fragmentos relevantes de la base de conocimiento tributaria
colombiana. Retorna los 5 fragmentos más similares con sus metadatos.

Variables de entorno:
    CHROMA_PERSIST_DIR: Directorio de persistencia de ChromaDB
        (por defecto ``./chroma_data``).
    EMBEDDING_MODEL_NAME: Modelo de embeddings de HuggingFace
        (por defecto ``intfloat/multilingual-e5-small``).
    SIMILARITY_THRESHOLD: Umbral mínimo de similitud coseno
        (por defecto ``0.35``).
"""

from __future__ import annotations

import logging
import os
from typing import Any

import chromadb
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constantes y valores por defecto
# ---------------------------------------------------------------------------
NOMBRE_COLECCION: str = "tax_knowledge"
"""Nombre de la colección ChromaDB."""

CHROMA_PERSIST_DIR_DEFAULT: str = "./chroma_data"
"""Directorio de persistencia por defecto."""

EMBEDDING_MODEL_DEFAULT: str = "intfloat/multilingual-e5-small"
"""Modelo de embeddings por defecto."""

SIMILARITY_THRESHOLD_DEFAULT: float = 0.35
"""Umbral de similitud coseno por defecto."""

TOP_K: int = 5
"""Número máximo de fragmentos a retornar."""

# ---------------------------------------------------------------------------
# Variables de módulo (carga diferida)
# ---------------------------------------------------------------------------
_modelo_embedding: SentenceTransformer | None = None
_coleccion: chromadb.Collection | None = None


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def _obtener_directorio_persistencia() -> str:
    """Obtiene el directorio de persistencia de ChromaDB desde env."""
    return os.getenv("CHROMA_PERSIST_DIR", CHROMA_PERSIST_DIR_DEFAULT)


def _obtener_nombre_modelo() -> str:
    """Obtiene el nombre del modelo de embeddings desde env."""
    return os.getenv("EMBEDDING_MODEL_NAME", EMBEDDING_MODEL_DEFAULT)


def _obtener_umbral_similitud() -> float:
    """Obtiene el umbral de similitud coseno desde env.

    Returns:
        Umbral de similitud como float.
    """
    valor = os.getenv("SIMILARITY_THRESHOLD")
    if valor is not None:
        try:
            return float(valor)
        except ValueError:
            logger.warning(
                "Valor inválido para SIMILARITY_THRESHOLD: '%s'. "
                "Usando valor por defecto: %f",
                valor,
                SIMILARITY_THRESHOLD_DEFAULT,
            )
    return SIMILARITY_THRESHOLD_DEFAULT


def _cargar_modelo() -> SentenceTransformer:
    """Carga el modelo de embeddings (singleton).

    Returns:
        Modelo SentenceTransformer cargado.
    """
    global _modelo_embedding  # noqa: PLW0603
    if _modelo_embedding is None:
        nombre = _obtener_nombre_modelo()
        logger.info("Cargando modelo de embeddings: %s", nombre)
        _modelo_embedding = SentenceTransformer(nombre)
    return _modelo_embedding


def _obtener_coleccion(
    persist_dir: str | None = None,
) -> chromadb.Collection:
    """Obtiene la colección ChromaDB (singleton).

    Args:
        persist_dir: Directorio de persistencia. Si es ``None``, se
            lee de la variable de entorno.

    Returns:
        Colección ChromaDB con métrica coseno.
    """
    global _coleccion  # noqa: PLW0603
    if _coleccion is None:
        directorio = persist_dir or _obtener_directorio_persistencia()
        cliente = chromadb.PersistentClient(path=directorio)
        _coleccion = cliente.get_or_create_collection(
            name=NOMBRE_COLECCION,
            metadata={"hnsw:space": "cosine"},
        )
    return _coleccion


def resetear_estado() -> None:
    """Resetea el estado global del módulo.

    Útil para pruebas unitarias que necesitan inyectar colecciones
    o modelos de prueba.
    """
    global _modelo_embedding, _coleccion  # noqa: PLW0603
    _modelo_embedding = None
    _coleccion = None


# ---------------------------------------------------------------------------
# Función principal de búsqueda
# ---------------------------------------------------------------------------

def get_tax_knowledge(
    query: str,
    coleccion: chromadb.Collection | None = None,
    modelo: SentenceTransformer | None = None,
    umbral_similitud: float | None = None,
    n_resultados: int = TOP_K,
) -> dict[str, Any]:
    """Busca fragmentos relevantes en la base de conocimiento tributaria.

    Convierte la consulta en un embedding y realiza búsqueda por
    similitud coseno en ChromaDB. Retorna los fragmentos más similares
    que superen el umbral configurado, junto con sus metadatos.

    Args:
        query: Consulta de búsqueda en texto libre.
        coleccion: Colección ChromaDB a consultar. Si es ``None``,
            se usa la colección persistente configurada.
        modelo: Modelo de embeddings. Si es ``None``, se carga el
            modelo configurado.
        umbral_similitud: Umbral mínimo de similitud coseno. Si es
            ``None``, se lee de la variable de entorno.
        n_resultados: Número máximo de resultados a retornar.

    Returns:
        Diccionario con las claves:
            - ``resultados``: Lista de diccionarios con ``contenido``,
              ``article_number``, ``source_document``, ``topic_tags``
              y ``similitud``.
            - ``mensaje``: Mensaje descriptivo del resultado.
            - ``total_encontrados``: Número de fragmentos retornados.
    """
    if not query or not query.strip():
        return {
            "resultados": [],
            "mensaje": "La consulta está vacía. Proporcione una pregunta sobre normativa tributaria.",
            "total_encontrados": 0,
        }

    # Obtener recursos
    col = coleccion or _obtener_coleccion()
    mdl = modelo or _cargar_modelo()
    threshold = umbral_similitud if umbral_similitud is not None else _obtener_umbral_similitud()

    # Generar embedding de la consulta
    query_embedding = mdl.encode([query]).tolist()

    # Buscar en ChromaDB
    resultados_raw = col.query(
        query_embeddings=query_embedding,
        n_results=n_resultados,
        include=["documents", "metadatas", "distances"],
    )

    # Procesar resultados
    documentos = resultados_raw.get("documents", [[]])[0]
    metadatos = resultados_raw.get("metadatas", [[]])[0]
    distancias = resultados_raw.get("distances", [[]])[0]

    resultados_filtrados: list[dict[str, Any]] = []

    for doc, meta, distancia in zip(documentos, metadatos, distancias):
        # ChromaDB con métrica coseno retorna distancia = 1 - similitud
        similitud = 1.0 - distancia

        if similitud < threshold:
            continue

        # Convertir topic_tags de string a lista
        tags_raw = meta.get("topic_tags", "")
        tags_lista = [t.strip() for t in tags_raw.split(",") if t.strip()] if tags_raw else []

        resultados_filtrados.append({
            "contenido": doc,
            "article_number": meta.get("article_number", ""),
            "source_document": meta.get("source_document", ""),
            "topic_tags": tags_lista,
            "similitud": round(similitud, 4),
        })

    # Construir respuesta
    if not resultados_filtrados:
        return {
            "resultados": [],
            "mensaje": (
                "No encontré información específica sobre este tema en la "
                "base de conocimiento tributaria. Intente reformular su "
                "consulta con términos más específicos sobre normativa "
                "tributaria colombiana para el sector agropecuario."
            ),
            "total_encontrados": 0,
        }

    return {
        "resultados": resultados_filtrados,
        "mensaje": (
            f"Se encontraron {len(resultados_filtrados)} fragmento(s) "
            f"relevante(s) en la base de conocimiento tributaria."
        ),
        "total_encontrados": len(resultados_filtrados),
    }
