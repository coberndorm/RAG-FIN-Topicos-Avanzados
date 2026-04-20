"""
Pruebas de propiedades para get_tax_knowledge de FIN-Advisor.

Valida la Propiedad 7: La búsqueda retorna como máximo 5 chunks,
cada uno con metadatos requeridos, ordenados por similitud descendente,
y excluye chunks por debajo del umbral.
"""

from __future__ import annotations

import sys
from pathlib import Path

import chromadb
import numpy as np
import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from agent.tools.get_tax_knowledge import get_tax_knowledge


# ---------------------------------------------------------------------------
# Modelo mock que genera embeddings determinísticos
# ---------------------------------------------------------------------------

class _MockEmbeddingModel:
    """Modelo de embeddings simulado para pruebas."""

    def encode(self, textos: list[str]):
        rng = np.random.default_rng(hash(textos[0]) % 2**32 if textos else 42)
        return rng.random((len(textos), 384))


# ---------------------------------------------------------------------------
# Propiedad 7: Resultados acotados con metadatos
# ---------------------------------------------------------------------------

CAMPOS_REQUERIDOS_RESULTADO = {"contenido", "article_number", "source_document", "topic_tags", "similitud"}


class TestKnowledgeRetrievalBoundedResults:
    """Propiedad 7: Máximo 5 chunks, con metadatos, ordenados por similitud."""

    def test_maximo_5_resultados(self, test_chroma_collection: chromadb.Collection) -> None:
        modelo = _MockEmbeddingModel()
        resultado = get_tax_knowledge(
            "beneficios tributarios IVA maquinaria",
            coleccion=test_chroma_collection,
            modelo=modelo,
            umbral_similitud=0.0,  # umbral bajo para obtener resultados
        )
        assert len(resultado["resultados"]) <= 5

    def test_metadatos_requeridos_presentes(
        self, test_chroma_collection: chromadb.Collection
    ) -> None:
        modelo = _MockEmbeddingModel()
        resultado = get_tax_knowledge(
            "exenciones renta agrícola",
            coleccion=test_chroma_collection,
            modelo=modelo,
            umbral_similitud=0.0,
        )
        for i, chunk in enumerate(resultado["resultados"]):
            for campo in CAMPOS_REQUERIDOS_RESULTADO:
                assert campo in chunk, (
                    f"Chunk {i} no tiene el campo '{campo}'. "
                    f"Campos: {list(chunk.keys())}"
                )

    def test_ordenados_por_similitud_descendente(
        self, test_chroma_collection: chromadb.Collection
    ) -> None:
        modelo = _MockEmbeddingModel()
        resultado = get_tax_knowledge(
            "IVA bienes de capital",
            coleccion=test_chroma_collection,
            modelo=modelo,
            umbral_similitud=0.0,
        )
        similitudes = [r["similitud"] for r in resultado["resultados"]]
        for i in range(len(similitudes) - 1):
            assert similitudes[i] >= similitudes[i + 1], (
                f"Resultados no ordenados: posición {i} ({similitudes[i]}) "
                f"< posición {i+1} ({similitudes[i+1]})"
            )

    def test_umbral_alto_excluye_chunks(
        self, test_chroma_collection: chromadb.Collection
    ) -> None:
        modelo = _MockEmbeddingModel()
        resultado = get_tax_knowledge(
            "consulta genérica",
            coleccion=test_chroma_collection,
            modelo=modelo,
            umbral_similitud=0.99,  # umbral muy alto
        )
        assert resultado["total_encontrados"] == 0
        assert len(resultado["resultados"]) == 0
        assert resultado["mensaje"]  # debe tener mensaje descriptivo

    def test_consulta_vacia_retorna_vacio(
        self, test_chroma_collection: chromadb.Collection
    ) -> None:
        resultado = get_tax_knowledge(
            "",
            coleccion=test_chroma_collection,
        )
        assert resultado["total_encontrados"] == 0
        assert len(resultado["resultados"]) == 0

    @given(query=st.text(min_size=1, max_size=100).filter(lambda s: s.strip()))
    @settings(
        max_examples=15,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
    )
    def test_cualquier_consulta_retorna_estructura_valida(
        self, test_chroma_collection: chromadb.Collection, query: str
    ) -> None:
        modelo = _MockEmbeddingModel()
        resultado = get_tax_knowledge(
            query,
            coleccion=test_chroma_collection,
            modelo=modelo,
            umbral_similitud=0.0,
        )
        assert "resultados" in resultado
        assert "mensaje" in resultado
        assert "total_encontrados" in resultado
        assert isinstance(resultado["resultados"], list)
        assert len(resultado["resultados"]) <= 5
