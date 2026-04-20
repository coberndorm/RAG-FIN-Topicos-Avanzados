---
name: Contexto Carpeta Knowledge Base
description: Guía para la carpeta knowledge_base/ — Documentos Markdown fuente para el pipeline RAG, reglas de formato y relación con el ETL.
inclusion: fileMatch
fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/knowledge_base/**'
---

# Carpeta `knowledge_base/` — Documentos Fuente para RAG

## Propósito

Esta carpeta contiene los documentos Markdown que alimentan la base de conocimiento vectorizada del sistema FIN-Advisor. Estos documentos son procesados por el pipeline ETL (`scripts/etl_ingest.py`), divididos en chunks, convertidos a embeddings y almacenados en ChromaDB para búsqueda semántica.

## Documentos Esperados

| Documento | Tipo | Contenido |
|---|---|---|
| `estatuto_tributario_libro1.md` | Legal (externo) | Impuesto de renta, secciones agrícolas (Art. 23, Art. 57-1) |
| `estatuto_tributario_libro3.md` | Legal (externo) | IVA, bienes de capital agrícolas (Art. 258-1, exenciones) |
| `beneficios_compra_maquinaria.md` | Guía (mock) | Beneficios tributarios para compra de maquinaria agrícola |
| `exenciones_pequeno_productor.md` | Guía (mock) | Exenciones fiscales para pequeños productores agropecuarios |
| `programas_gobierno_agro.md` | Guía (mock) | Programas gubernamentales de apoyo al sector agropecuario |
| `calendario_tributario_2024.md` | Calendario | Fechas de vencimiento tributario por bracket NIT |

## Reglas de Formato para Chunking Efectivo

- Usar encabezados `##` y `###` para secciones principales y subsecciones.
- Preservar **números de artículo** del Estatuto Tributario en el texto.
- Escribir todo el contenido en **español**.
- Incluir porcentajes específicos, umbrales monetarios y condiciones reales.
- Evitar párrafos excesivamente largos (el chunker divide en ~800 caracteres).
- Los separadores del chunker son: `\n## `, `\n### `, `\n\n`, `\n`, ` ` (en ese orden de prioridad).

## Schema de Metadatos por Chunk

Cada chunk almacenado en ChromaDB lleva estos metadatos:

```json
{
  "source_document": "nombre_archivo.md",
  "article_number": "258-1",
  "topic_tags": ["IVA", "bienes_de_capital", "maquinaria"],
  "document_type": "legal | guide | calendar",
  "date_ingested": "2024-XX-XX",
  "chunk_index": 0,
  "total_chunks_in_article": 3
}
```

## Relación con el Pipeline ETL

- `scripts/etl_ingest.py` lee todos los archivos `.md` de esta carpeta.
- El chunking usa `RecursiveCharacterTextSplitter` (800 chars, 10% overlap).
- Los embeddings se generan con `intfloat/multilingual-e5-small` (configurable).
- La deduplicación se basa en `source_document` — re-ejecutar el ETL no crea duplicados.
- `agent/tools/get_tax_knowledge.py` consulta los chunks almacenados vía búsqueda por similitud coseno.

## Restricciones

- Los documentos marcados como "mock" son versiones simplificadas inspiradas en política real, no copias textuales.
- Los documentos legales externos deben ser descargados manualmente del portal DIAN o Secretaría del Senado antes de ejecutar el ETL.
- El umbral de similitud para retrieval es 0.35 (configurable vía `SIMILARITY_THRESHOLD`).
