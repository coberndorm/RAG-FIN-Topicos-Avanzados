# FIN-Advisor: Knowledge Base Definition

## Overview
The knowledge base is the foundation of the RAG pipeline. It contains all the external (non-user-specific) information that the LLM needs to ground its responses. Every document in the knowledge base goes through an ETL pipeline: ingestion → chunking → embedding → storage in ChromaDB.

---

## Knowledge Base Elements

### KB-01: Estatuto Tributario Nacional (Colombian Tax Code)

| Attribute | Detail |
|---|---|
| Source | Public PDF from DIAN (Dirección de Impuestos y Aduanas Nacionales) official portal |
| Scope | Book I (Income Tax) and Book III (VAT) — only sections applicable to the agricultural sector |
| Format | PDF → converted to Markdown for processing |
| Update Frequency | Static for MVP (2024 version). In production, would require annual updates |
| Size Estimate | ~50-80 pages of relevant content after filtering |

**Key sections to include:**
- Art. 258-1: VAT discount on capital goods (machinery, equipment)
- Art. 23: Tax-exempt entities in the agricultural sector
- Art. 57-1: Income from agricultural activities
- Sections on withholding tax (retención en la fuente) for agricultural sales
- VAT exemptions on agricultural inputs (seeds, fertilizers)

**Conditions:**
- Only articles directly applicable to agricultural producers should be included
- Each article must retain its original numbering for traceability in responses
- Metadata must include: article number, book, title, and topic tags

---

### KB-02: Agricultural Sector Benefit Guides

| Attribute | Detail |
|---|---|
| Source | Mock documents created by the team, based on real MinAgricultura guidelines |
| Scope | Tax exemptions and government programs for small and medium agricultural producers |
| Format | Markdown files (3-4 documents) |
| Update Frequency | Static for MVP |
| Size Estimate | ~5-10 pages total |

**Documents to create:**
1. `beneficios_compra_maquinaria.md` — Benefits for purchasing agricultural machinery
2. `exenciones_pequeno_productor.md` — Exemptions for small producers (income thresholds)
3. `programas_gobierno_agro.md` — Government programs and subsidies for the agricultural sector
4. `calendario_tributario_2024.md` — Key tax dates and obligations for agricultural entities

**Conditions:**
- Content must be realistic and based on actual Colombian agricultural policy
- Each document must have clear section headers for effective chunking
- Documents should be written in Spanish (matching the user's query language)

---

### KB-03: Historical Exchange Rates (Optional — Phase 2)

| Attribute | Detail |
|---|---|
| Source | Synthetic data or public data from Banco de la República |
| Scope | USD/COP exchange rates for the last 12 months |
| Format | CSV or JSON |
| Update Frequency | Monthly (simulated) |
| Size Estimate | Minimal (~12 rows) |

**Conditions:**
- Only relevant for queries involving imported inputs (fertilizers, machinery parts)
- Low priority — include only if time permits
- Would be stored in the relational database, not the vector store

---

## Chunking Strategy

| Parameter | Value | Justification |
|---|---|---|
| Method | `RecursiveCharacterTextSplitter` | Respects document hierarchy (articles → paragraphs) |
| Chunk Size | 500-1000 characters | Large enough to preserve legal article context, small enough for precise retrieval |
| Overlap | 10% (~50-100 characters) | Prevents losing context at chunk boundaries, especially important for multi-paragraph articles |
| Separators | `["\n## ", "\n### ", "\n\n", "\n", " "]` | Prioritizes splitting at heading boundaries, then paragraphs, then sentences |

**Special considerations for legal text:**
- Articles should NOT be split mid-sentence
- If an article is shorter than the chunk size, it should be kept as a single chunk
- Numbered lists within articles (numerales) should stay together when possible

---

## Metadata Schema

Every chunk stored in ChromaDB must include the following metadata:

```json
{
  "source_document": "estatuto_tributario_2024.md",
  "article_number": "258-1",
  "topic_tags": ["IVA", "bienes_de_capital", "maquinaria"],
  "document_type": "legal",
  "date_ingested": "2024-XX-XX",
  "chunk_index": 3,
  "total_chunks_in_article": 5
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| source_document | string | Yes | Original file name |
| article_number | string | No | Applicable for legal documents only |
| topic_tags | list[string] | Yes | Searchable tags for filtering (e.g., #IVA, #Maquinaria, #Exenciones) |
| document_type | string | Yes | One of: `legal`, `guide`, `exchange_rate` |
| date_ingested | string | Yes | Date the document was processed into the vector store |
| chunk_index | int | Yes | Position of this chunk within the source document |
| total_chunks_in_article | int | No | Total chunks for the parent article (for legal docs) |

---

## Quality Criteria

The knowledge base must satisfy these conditions before the RAG pipeline is considered functional:

1. **Completeness:** All key articles from the Estatuto Tributario related to agricultural taxation are present
2. **Traceability:** Every response that cites a law must be traceable back to a specific chunk with its article number
3. **No Duplication:** The same article should not appear in multiple chunks unless overlap is intentional
4. **Relevance Filtering:** A test query like "IVA en tractores" must return chunks from Art. 258-1, not unrelated VAT articles
5. **Language Consistency:** All knowledge base content is in Spanish
6. **Metadata Integrity:** Every chunk has complete metadata — no null required fields
