"""
Embedding Model Reference — FIN-Advisor
========================================

This file contains reference code for loading and using the supported
embedding models in the FIN-Advisor project. Use this as a guide when
integrating embeddings into the ETL pipeline or the get_tax_knowledge tool.

Supported models (all free, unlimited, ChromaDB-compatible):
  1. intfloat/multilingual-e5-small   — Primary (~134MB, best for Spanish legal text)
  2. sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 — Alternative (~120MB)
  3. intfloat/multilingual-e5-base    — Premium (~440MB, higher quality)

Usage:
  Set the EMBEDDING_MODEL_NAME environment variable to switch models.
  Default: intfloat/multilingual-e5-small
"""

import os
from sentence_transformers import SentenceTransformer


# --- Configuration ---
DEFAULT_MODEL = "intfloat/multilingual-e5-small"

SUPPORTED_MODELS = {
    "intfloat/multilingual-e5-small": {
        "size_mb": 134,
        "description": "Primary choice. Optimized for Spanish, great for legal/financial docs.",
    },
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": {
        "size_mb": 120,
        "description": "Most popular multilingual model. Good sentence-level similarity.",
    },
    "intfloat/multilingual-e5-base": {
        "size_mb": 440,
        "description": "Premium option. Better quality, larger footprint.",
    },
}


def load_embedding_model(model_name: str | None = None) -> SentenceTransformer:
    """Load the configured embedding model.

    Args:
        model_name: HuggingFace model identifier. Falls back to
            the ``EMBEDDING_MODEL_NAME`` env var, then to the default.

    Returns:
        A loaded SentenceTransformer model ready for encoding.

    Raises:
        ValueError: If the requested model is not in the supported list.
    """
    name = model_name or os.getenv("EMBEDDING_MODEL_NAME", DEFAULT_MODEL)
    if name not in SUPPORTED_MODELS:
        raise ValueError(
            f"Unsupported embedding model: {name}. "
            f"Supported: {list(SUPPORTED_MODELS.keys())}"
        )
    return SentenceTransformer(name)


# --- Example usage ---
if __name__ == "__main__":
    model = load_embedding_model()
    print(f"Loaded model: {os.getenv('EMBEDDING_MODEL_NAME', DEFAULT_MODEL)}")

    # Sample Colombian tax documents
    documents = [
        "Artículo 258-1. Descuento del IVA en la adquisición de bienes de capital para actividades agropecuarias.",
        "Decreto 1234 de 2023. Se establecen beneficios fiscales para productores de café.",
        "Los pequeños productores agrícolas con ingresos inferiores a 3.500 UVT están exentos del impuesto de renta.",
    ]

    embeddings = model.encode(documents)
    print(f"Generated {len(embeddings)} embeddings, dimension: {embeddings.shape[1]}")
