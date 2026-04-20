#!/usr/bin/env python3
"""
Pipeline ETL para ingestión de documentos en ChromaDB — FIN-Advisor.

Lee archivos Markdown del directorio ``knowledge_base/``, los divide en
fragmentos (chunks) usando ``RecursiveCharacterTextSplitter``, genera
embeddings con el modelo configurado y los almacena en ChromaDB con
metadatos enriquecidos.

Variables de entorno:
    CHROMA_PERSIST_DIR: Directorio de persistencia de ChromaDB
        (por defecto ``./chroma_data``).
    EMBEDDING_MODEL_NAME: Modelo de embeddings de HuggingFace
        (por defecto ``intfloat/multilingual-e5-small``).

Uso:
    python scripts/etl_ingest.py
"""

from __future__ import annotations

import logging
import os
import re
import sys
from datetime import date
from pathlib import Path

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Configuración de logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
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

CHUNK_SIZE: int = 800
"""Tamaño de fragmento en caracteres."""

CHUNK_OVERLAP: int = 80
"""Solapamiento entre fragmentos (10% de CHUNK_SIZE)."""

SEPARADORES: list[str] = ["\n## ", "\n### ", "\n\n", "\n", " "]
"""Separadores para RecursiveCharacterTextSplitter."""

# Patrón regex para extraer números de artículo del contenido
_PATRON_ARTICULO = re.compile(
    r"(?:Art[íi]culo|Art\.)\s*(\d+(?:-\d+)?)",
    re.IGNORECASE,
)

# Mapeo de nombre de archivo a tipo de documento
_TIPO_DOCUMENTO: dict[str, str] = {
    "estatuto_tributario_libro1.md": "legal",
    "estatuto_tributario_libro3.md": "legal",
    "beneficios_compra_maquinaria.md": "guide",
    "exenciones_pequeno_productor.md": "guide",
    "programas_gobierno_agro.md": "guide",
    "calendario_tributario_2024.md": "calendar",
}

# Mapeo de nombre de archivo a etiquetas de tema
_TOPIC_TAGS: dict[str, list[str]] = {
    "estatuto_tributario_libro1.md": ["renta", "deducciones", "exenciones", "agricultura"],
    "estatuto_tributario_libro3.md": ["IVA", "bienes_de_capital", "exenciones", "maquinaria"],
    "beneficios_compra_maquinaria.md": ["maquinaria", "IVA", "crédito", "FINAGRO", "depreciación"],
    "exenciones_pequeno_productor.md": ["exenciones", "pequeño_productor", "renta", "IVA"],
    "programas_gobierno_agro.md": ["subsidios", "FINAGRO", "ICR", "crédito", "gobierno"],
    "calendario_tributario_2024.md": ["calendario", "renta", "IVA", "retención", "plazos"],
}


# ---------------------------------------------------------------------------
# Funciones auxiliares
# ---------------------------------------------------------------------------

def _obtener_directorio_persistencia() -> str:
    """Obtiene el directorio de persistencia de ChromaDB desde env."""
    return os.getenv("CHROMA_PERSIST_DIR", CHROMA_PERSIST_DIR_DEFAULT)


def _obtener_modelo_embedding() -> str:
    """Obtiene el nombre del modelo de embeddings desde env."""
    return os.getenv("EMBEDDING_MODEL_NAME", EMBEDDING_MODEL_DEFAULT)


def _obtener_directorio_knowledge_base() -> Path:
    """Retorna la ruta al directorio ``knowledge_base/``.

    Busca relativo al directorio del script (asume que el script está
    en ``scripts/`` y ``knowledge_base/`` es un directorio hermano).

    Returns:
        Ruta absoluta al directorio knowledge_base.
    """
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent / "knowledge_base"


def _extraer_articulos(texto: str) -> list[str]:
    """Extrae números de artículo del texto.

    Busca patrones como "Artículo 258-1", "Art. 23", "Artículo 57-1".

    Args:
        texto: Contenido del fragmento.

    Returns:
        Lista de números de artículo encontrados (sin duplicados).
    """
    encontrados = _PATRON_ARTICULO.findall(texto)
    # Eliminar duplicados preservando orden
    vistos: set[str] = set()
    resultado: list[str] = []
    for art in encontrados:
        if art not in vistos:
            vistos.add(art)
            resultado.append(art)
    return resultado


def _determinar_tipo_documento(nombre_archivo: str) -> str:
    """Determina el tipo de documento según el nombre del archivo.

    Args:
        nombre_archivo: Nombre del archivo Markdown.

    Returns:
        Tipo de documento: ``legal``, ``guide`` o ``calendar``.
    """
    return _TIPO_DOCUMENTO.get(nombre_archivo, "guide")


def _obtener_topic_tags(nombre_archivo: str) -> list[str]:
    """Obtiene las etiquetas de tema para un archivo.

    Args:
        nombre_archivo: Nombre del archivo Markdown.

    Returns:
        Lista de etiquetas de tema.
    """
    return _TOPIC_TAGS.get(nombre_archivo, ["general"])


# ---------------------------------------------------------------------------
# Funciones principales del pipeline
# ---------------------------------------------------------------------------

def cargar_modelo_embedding(nombre_modelo: str | None = None) -> SentenceTransformer:
    """Carga el modelo de embeddings configurado.

    Args:
        nombre_modelo: Nombre del modelo. Si es ``None``, se lee de
            la variable de entorno o se usa el valor por defecto.

    Returns:
        Modelo SentenceTransformer cargado.
    """
    modelo = nombre_modelo or _obtener_modelo_embedding()
    logger.info("Cargando modelo de embeddings: %s", modelo)
    return SentenceTransformer(modelo)


def obtener_coleccion(persist_dir: str | None = None) -> chromadb.Collection:
    """Obtiene la colección ChromaDB persistente.

    Args:
        persist_dir: Directorio de persistencia. Si es ``None``, se
            lee de la variable de entorno.

    Returns:
        Colección ChromaDB con métrica coseno.
    """
    directorio = persist_dir or _obtener_directorio_persistencia()
    cliente = chromadb.PersistentClient(path=directorio)
    return cliente.get_or_create_collection(
        name=NOMBRE_COLECCION,
        metadata={"hnsw:space": "cosine"},
    )


def leer_documentos_markdown(directorio_kb: Path | None = None) -> list[tuple[str, str]]:
    """Lee todos los archivos Markdown del directorio knowledge_base.

    Args:
        directorio_kb: Ruta al directorio. Si es ``None``, se calcula
            automáticamente.

    Returns:
        Lista de tuplas ``(nombre_archivo, contenido)``.
    """
    kb_dir = directorio_kb or _obtener_directorio_knowledge_base()

    if not kb_dir.exists():
        logger.error("Directorio knowledge_base no encontrado: %s", kb_dir)
        return []

    documentos: list[tuple[str, str]] = []
    for archivo in sorted(kb_dir.glob("*.md")):
        try:
            contenido = archivo.read_text(encoding="utf-8")
            documentos.append((archivo.name, contenido))
            logger.info("  Leído: %s (%d caracteres)", archivo.name, len(contenido))
        except Exception as e:
            logger.error("  Error al leer %s: %s", archivo.name, e)

    return documentos


def dividir_documento(contenido: str) -> list[str]:
    """Divide un documento Markdown en fragmentos.

    Usa ``RecursiveCharacterTextSplitter`` con los separadores y
    parámetros definidos en el diseño.

    Args:
        contenido: Texto completo del documento Markdown.

    Returns:
        Lista de fragmentos de texto.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARADORES,
        length_function=len,
    )
    return splitter.split_text(contenido)


def eliminar_chunks_existentes(
    coleccion: chromadb.Collection,
    nombre_documento: str,
) -> int:
    """Elimina fragmentos existentes de un documento para deduplicación.

    Busca y elimina todos los chunks cuyo metadato ``source_document``
    coincida con el nombre del documento proporcionado.

    Args:
        coleccion: Colección ChromaDB.
        nombre_documento: Nombre del archivo fuente.

    Returns:
        Número de fragmentos eliminados.
    """
    # Consultar IDs existentes para este documento
    resultados = coleccion.get(
        where={"source_document": nombre_documento},
    )

    ids_existentes = resultados.get("ids", [])
    if ids_existentes:
        coleccion.delete(ids=ids_existentes)
        logger.info(
            "  Dedup: eliminados %d chunks previos de '%s'",
            len(ids_existentes),
            nombre_documento,
        )
    return len(ids_existentes)


def ingerir_documento(
    nombre_archivo: str,
    contenido: str,
    coleccion: chromadb.Collection,
    modelo: SentenceTransformer,
) -> int:
    """Ingiere un documento Markdown en ChromaDB.

    Divide el documento en fragmentos, genera embeddings y los
    almacena con metadatos enriquecidos. Implementa deduplicación
    eliminando chunks previos del mismo documento.

    Args:
        nombre_archivo: Nombre del archivo Markdown.
        contenido: Texto completo del documento.
        coleccion: Colección ChromaDB destino.
        modelo: Modelo de embeddings cargado.

    Returns:
        Número de fragmentos creados.
    """
    logger.info("Procesando: %s", nombre_archivo)

    # Deduplicación: eliminar chunks previos
    eliminar_chunks_existentes(coleccion, nombre_archivo)

    # Dividir en fragmentos
    fragmentos = dividir_documento(contenido)
    total_fragmentos = len(fragmentos)
    logger.info("  Fragmentos generados: %d", total_fragmentos)

    if total_fragmentos == 0:
        logger.warning("  Sin fragmentos para '%s'. Omitiendo.", nombre_archivo)
        return 0

    # Generar embeddings
    embeddings = modelo.encode(fragmentos).tolist()

    # Preparar metadatos e IDs
    tipo_doc = _determinar_tipo_documento(nombre_archivo)
    tags = _obtener_topic_tags(nombre_archivo)
    fecha_ingesta = date.today().isoformat()

    ids: list[str] = []
    metadatos: list[dict[str, str | int]] = []
    for idx, fragmento in enumerate(fragmentos):
        articulos = _extraer_articulos(fragmento)
        articulo_str = ",".join(articulos) if articulos else ""

        chunk_id = f"{nombre_archivo}__chunk_{idx}"
        ids.append(chunk_id)

        metadatos.append({
            "source_document": nombre_archivo,
            "article_number": articulo_str,
            "topic_tags": ",".join(tags),
            "document_type": tipo_doc,
            "date_ingested": fecha_ingesta,
            "chunk_index": idx,
            "total_chunks_in_article": total_fragmentos,
        })

    # Almacenar en ChromaDB
    coleccion.add(
        ids=ids,
        embeddings=embeddings,
        documents=fragmentos,
        metadatas=metadatos,
    )

    logger.info("  ✅ %d fragmentos almacenados en ChromaDB.", total_fragmentos)
    return total_fragmentos


# ---------------------------------------------------------------------------
# Función principal del pipeline
# ---------------------------------------------------------------------------

def ejecutar_pipeline(
    directorio_kb: Path | None = None,
    persist_dir: str | None = None,
    nombre_modelo: str | None = None,
) -> dict[str, int]:
    """Ejecuta el pipeline ETL completo.

    Lee documentos Markdown, los divide en fragmentos, genera embeddings
    y los almacena en ChromaDB.

    Args:
        directorio_kb: Ruta al directorio knowledge_base.
        persist_dir: Directorio de persistencia de ChromaDB.
        nombre_modelo: Nombre del modelo de embeddings.

    Returns:
        Diccionario con estadísticas: ``documentos_procesados``,
        ``chunks_creados``, ``errores``.
    """
    estadisticas = {
        "documentos_procesados": 0,
        "chunks_creados": 0,
        "errores": 0,
    }

    # 1. Cargar modelo de embeddings
    try:
        modelo = cargar_modelo_embedding(nombre_modelo)
    except Exception as e:
        logger.error("❌ Error al cargar modelo de embeddings: %s", e)
        estadisticas["errores"] += 1
        return estadisticas

    # 2. Obtener colección ChromaDB
    try:
        coleccion = obtener_coleccion(persist_dir)
    except Exception as e:
        logger.error("❌ Error al conectar con ChromaDB: %s", e)
        estadisticas["errores"] += 1
        return estadisticas

    # 3. Leer documentos Markdown
    documentos = leer_documentos_markdown(directorio_kb)
    if not documentos:
        logger.warning("No se encontraron documentos Markdown para procesar.")
        return estadisticas

    logger.info("Documentos encontrados: %d", len(documentos))

    # 4. Procesar cada documento
    for nombre_archivo, contenido in documentos:
        try:
            chunks = ingerir_documento(nombre_archivo, contenido, coleccion, modelo)
            estadisticas["documentos_procesados"] += 1
            estadisticas["chunks_creados"] += chunks
        except Exception as e:
            logger.error("❌ Error al procesar '%s': %s", nombre_archivo, e)
            estadisticas["errores"] += 1

    return estadisticas


# ---------------------------------------------------------------------------
# Punto de entrada
# ---------------------------------------------------------------------------

def main() -> None:
    """Punto de entrada principal del script ETL."""
    logger.info("=== Pipeline ETL de FIN-Advisor ===")

    estadisticas = ejecutar_pipeline()

    logger.info("=== Resumen del Pipeline ETL ===")
    logger.info("  Documentos procesados: %d", estadisticas["documentos_procesados"])
    logger.info("  Fragmentos creados:    %d", estadisticas["chunks_creados"])
    logger.info("  Errores:               %d", estadisticas["errores"])

    if estadisticas["errores"] > 0:
        logger.warning("⚠️  Se encontraron errores durante la ingestión.")
        sys.exit(1)
    else:
        logger.info("✅ Pipeline ETL completado exitosamente.")


if __name__ == "__main__":
    main()
