"""
Pruebas de propiedades para el pipeline ETL de FIN-Advisor.

Valida la Propiedad 9: El chunking del ETL preserva metadatos y
respeta restricciones de tamaño.

- Los fragmentos tienen entre 500 y 1000 caracteres (con tolerancia
  para documentos cortos o límites del splitter).
- Cada fragmento lleva los campos de metadatos requeridos:
  ``source_document``, ``document_type``, ``date_ingested``,
  ``chunk_index``.
- Los números de artículo presentes en el texto fuente se preservan
  en el campo ``article_number`` de los metadatos.
"""

from __future__ import annotations

import sys
from pathlib import Path

import chromadb
import pytest
from hypothesis import given, settings, assume, HealthCheck
from hypothesis import strategies as st

# Agregar raíz del proyecto al path para importar módulos
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.etl_ingest import (
    dividir_documento,
    ingerir_documento,
    _extraer_articulos,
    CHUNK_SIZE,
)


# ---------------------------------------------------------------------------
# Estrategias de Hypothesis
# ---------------------------------------------------------------------------

def _seccion_markdown(titulo: str, cuerpo: str) -> str:
    """Construye una sección Markdown con encabezado ##."""
    return f"\n## {titulo}\n\n{cuerpo}\n"


# Estrategia: texto de párrafo realista (sin caracteres nulos)
_parrafo = st.text(
    alphabet=st.characters(
        whitelist_categories=("L", "N", "P", "Z"),
        blacklist_characters="\x00",
    ),
    min_size=50,
    max_size=400,
)

# Estrategia: número de artículo estilo Estatuto Tributario
_numero_articulo = st.from_regex(r"\d{1,3}(-\d{1,2})?", fullmatch=True)

# Estrategia: párrafo que contiene una referencia a artículo
_parrafo_con_articulo = st.builds(
    lambda art, texto: f"Artículo {art}. {texto}",
    _numero_articulo,
    _parrafo,
)

# Estrategia: documento Markdown con varias secciones y artículos
_documento_markdown = st.builds(
    lambda secciones: "\n".join(secciones),
    st.lists(
        st.one_of(
            st.builds(_seccion_markdown, st.text(min_size=5, max_size=30), _parrafo),
            st.builds(
                _seccion_markdown,
                st.text(min_size=5, max_size=30),
                _parrafo_con_articulo,
            ),
        ),
        min_size=2,
        max_size=8,
    ),
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def chroma_collection_temporal():
    """Colección ChromaDB en memoria para pruebas de ingestión."""
    client = chromadb.Client()
    col = client.get_or_create_collection(
        name="test_etl_chunking",
        metadata={"hnsw:space": "cosine"},
    )
    yield col
    client.delete_collection(name="test_etl_chunking")


# ---------------------------------------------------------------------------
# Propiedad 9: Chunking preserva metadatos y respeta tamaño
# ---------------------------------------------------------------------------

class TestChunkSizeConstraints:
    """Verifica que los fragmentos respetan las restricciones de tamaño."""

    @given(documento=_documento_markdown)
    @settings(
        max_examples=30,
        deadline=None,
        suppress_health_check=[HealthCheck.too_slow],
    )
    def test_chunks_dentro_de_rango_aceptable(self, documento: str) -> None:
        """Los fragmentos generados deben tener entre 1 y ~1000 caracteres.

        El diseño establece un rango de 500-1000 caracteres. Sin embargo,
        el último fragmento de un documento o secciones cortas pueden
        producir chunks menores a 500 caracteres. Verificamos que ningún
        chunk exceda el tamaño máximo configurado más el overlap.
        """
        assume(len(documento.strip()) > 0)

        fragmentos = dividir_documento(documento)

        for i, fragmento in enumerate(fragmentos):
            largo = len(fragmento)
            assert largo > 0, (
                f"Fragmento {i} está vacío"
            )
            # El tamaño máximo no debe exceder chunk_size + margen de overlap
            assert largo <= CHUNK_SIZE + 200, (
                f"Fragmento {i} excede el límite: {largo} caracteres "
                f"(máximo esperado ~{CHUNK_SIZE + 200})"
            )

    def test_chunks_documento_real_dentro_de_rango(self) -> None:
        """Verifica tamaño de chunks con un documento real de la KB."""
        kb_dir = _PROJECT_ROOT / "knowledge_base"
        archivo = kb_dir / "beneficios_compra_maquinaria.md"
        if not archivo.exists():
            pytest.skip("Archivo de knowledge base no disponible")

        contenido = archivo.read_text(encoding="utf-8")
        fragmentos = dividir_documento(contenido)

        assert len(fragmentos) > 0, "El documento debe generar al menos un fragmento"

        for i, fragmento in enumerate(fragmentos):
            largo = len(fragmento)
            # Para documentos reales, la mayoría de chunks deben estar
            # en el rango 500-1000 (excepto el último que puede ser menor)
            assert largo <= CHUNK_SIZE + 200, (
                f"Fragmento {i} excede el límite: {largo} caracteres"
            )


class TestMetadataFields:
    """Verifica que cada chunk lleva los campos de metadatos requeridos."""

    CAMPOS_REQUERIDOS = {
        "source_document",
        "document_type",
        "date_ingested",
        "chunk_index",
        "article_number",
        "topic_tags",
        "total_chunks_in_article",
    }

    def test_metadatos_completos_documento_real(
        self, chroma_collection_temporal: chromadb.Collection
    ) -> None:
        """Ingerir un documento real debe producir chunks con todos los metadatos."""
        kb_dir = _PROJECT_ROOT / "knowledge_base"
        archivo = kb_dir / "beneficios_compra_maquinaria.md"
        if not archivo.exists():
            pytest.skip("Archivo de knowledge base no disponible")

        contenido = archivo.read_text(encoding="utf-8")

        # Usar un modelo mock para evitar descargar el modelo real
        modelo = _MockEmbeddingModel()

        num_chunks = ingerir_documento(
            nombre_archivo="beneficios_compra_maquinaria.md",
            contenido=contenido,
            coleccion=chroma_collection_temporal,
            modelo=modelo,
        )

        assert num_chunks > 0, "Debe generar al menos un fragmento"

        # Recuperar todos los chunks almacenados
        resultados = chroma_collection_temporal.get(
            where={"source_document": "beneficios_compra_maquinaria.md"},
            include=["metadatas", "documents"],
        )

        assert len(resultados["ids"]) == num_chunks

        for i, metadata in enumerate(resultados["metadatas"]):
            for campo in self.CAMPOS_REQUERIDOS:
                assert campo in metadata, (
                    f"Chunk {i} no tiene el campo requerido '{campo}'. "
                    f"Campos presentes: {list(metadata.keys())}"
                )

            # Validar tipos de valores
            assert isinstance(metadata["source_document"], str)
            assert metadata["source_document"] == "beneficios_compra_maquinaria.md"
            assert metadata["document_type"] in ("legal", "guide", "calendar")
            assert isinstance(metadata["date_ingested"], str)
            assert len(metadata["date_ingested"]) == 10  # formato YYYY-MM-DD
            assert isinstance(metadata["chunk_index"], int)
            assert metadata["chunk_index"] == i
            assert isinstance(metadata["total_chunks_in_article"], int)
            assert metadata["total_chunks_in_article"] == num_chunks


class TestArticleNumberPreservation:
    """Verifica que los números de artículo se preservan en los metadatos."""

    @given(numero=_numero_articulo)
    @settings(max_examples=30, deadline=None)
    def test_extraccion_articulos_preserva_numeros(self, numero: str) -> None:
        """La función de extracción debe encontrar artículos en el texto."""
        texto = f"Según el Artículo {numero} del Estatuto Tributario, los productores..."
        articulos = _extraer_articulos(texto)
        assert numero in articulos, (
            f"Artículo '{numero}' no fue extraído del texto. "
            f"Artículos encontrados: {articulos}"
        )

    def test_articulos_preservados_en_chunks_reales(
        self, chroma_collection_temporal: chromadb.Collection
    ) -> None:
        """Los artículos del documento fuente deben aparecer en los metadatos de los chunks."""
        kb_dir = _PROJECT_ROOT / "knowledge_base"
        archivo = kb_dir / "beneficios_compra_maquinaria.md"
        if not archivo.exists():
            pytest.skip("Archivo de knowledge base no disponible")

        contenido = archivo.read_text(encoding="utf-8")

        # Artículos que sabemos están en el documento
        articulos_esperados = {"258-1", "137", "424"}

        modelo = _MockEmbeddingModel()

        ingerir_documento(
            nombre_archivo="beneficios_compra_maquinaria.md",
            contenido=contenido,
            coleccion=chroma_collection_temporal,
            modelo=modelo,
        )

        resultados = chroma_collection_temporal.get(
            where={"source_document": "beneficios_compra_maquinaria.md"},
            include=["metadatas"],
        )

        # Recopilar todos los artículos encontrados en los metadatos
        articulos_en_metadata: set[str] = set()
        for metadata in resultados["metadatas"]:
            art_str = metadata.get("article_number", "")
            if art_str:
                for art in art_str.split(","):
                    articulos_en_metadata.add(art.strip())

        for esperado in articulos_esperados:
            assert esperado in articulos_en_metadata, (
                f"Artículo '{esperado}' del documento fuente no se encontró "
                f"en los metadatos de ningún chunk. "
                f"Artículos encontrados: {articulos_en_metadata}"
            )

    @given(
        art1=_numero_articulo,
        art2=_numero_articulo,
        texto=_parrafo,
    )
    @settings(max_examples=20, deadline=None)
    def test_multiples_articulos_extraidos(
        self, art1: str, art2: str, texto: str
    ) -> None:
        """Múltiples artículos en un mismo texto deben extraerse todos."""
        assume(art1 != art2)
        contenido = f"Art. {art1} establece que {texto}. Artículo {art2} complementa."
        articulos = _extraer_articulos(contenido)
        assert art1 in articulos, f"Artículo '{art1}' no extraído"
        assert art2 in articulos, f"Artículo '{art2}' no extraído"


# ---------------------------------------------------------------------------
# Modelo mock para evitar descargar el modelo de embeddings real
# ---------------------------------------------------------------------------

class _MockEmbeddingModel:
    """Modelo de embeddings simulado para pruebas.

    Genera vectores aleatorios de dimensión 384 (misma dimensión que
    ``intfloat/multilingual-e5-small``) sin necesidad de descargar
    el modelo real.
    """

    def encode(self, textos: list[str]):
        """Genera embeddings simulados.

        Args:
            textos: Lista de textos a codificar.

        Returns:
            ndarray de forma (n, 384) compatible con ``.tolist()``.
        """
        import numpy as np

        return np.random.default_rng(42).random((len(textos), 384))



# ---------------------------------------------------------------------------
# Propiedad 10: Idempotencia de ingestión ETL
# ---------------------------------------------------------------------------

class TestETLIdempotence:
    """Propiedad 10: Re-ejecutar el ETL no crea chunks duplicados."""

    def test_doble_ingestion_sin_duplicados(
        self, chroma_collection_temporal: chromadb.Collection
    ) -> None:
        """Ingerir el mismo documento dos veces no debe duplicar chunks."""
        kb_dir = _PROJECT_ROOT / "knowledge_base"
        archivo = kb_dir / "beneficios_compra_maquinaria.md"
        if not archivo.exists():
            pytest.skip("Archivo de knowledge base no disponible")

        contenido = archivo.read_text(encoding="utf-8")
        modelo = _MockEmbeddingModel()

        # Primera ingestión
        chunks_primera = ingerir_documento(
            nombre_archivo="beneficios_compra_maquinaria.md",
            contenido=contenido,
            coleccion=chroma_collection_temporal,
            modelo=modelo,
        )

        resultados_primera = chroma_collection_temporal.get(
            where={"source_document": "beneficios_compra_maquinaria.md"},
        )
        count_primera = len(resultados_primera["ids"])

        # Segunda ingestión (misma doc)
        chunks_segunda = ingerir_documento(
            nombre_archivo="beneficios_compra_maquinaria.md",
            contenido=contenido,
            coleccion=chroma_collection_temporal,
            modelo=modelo,
        )

        resultados_segunda = chroma_collection_temporal.get(
            where={"source_document": "beneficios_compra_maquinaria.md"},
        )
        count_segunda = len(resultados_segunda["ids"])

        assert count_segunda == count_primera, (
            f"Después de la segunda ingestión hay {count_segunda} chunks, "
            f"pero después de la primera había {count_primera}. "
            "Se crearon duplicados."
        )
        assert chunks_segunda == chunks_primera
