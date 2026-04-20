# knowledge_base/ — Base de Conocimiento para RAG

Este directorio contiene los documentos Markdown que alimentan el sistema de Retrieval-Augmented Generation (RAG) de FIN-Advisor. Estos documentos son procesados por el pipeline ETL, convertidos en embeddings y almacenados en ChromaDB para recuperación semántica.

## Contenido

```
knowledge_base/
├── estatuto_tributario_libro1.md    # Impuesto de renta — secciones agrícolas
├── estatuto_tributario_libro3.md    # IVA — exenciones sobre insumos agrícolas
├── beneficios_compra_maquinaria.md  # Beneficios tributarios para maquinaria
├── exenciones_pequeno_productor.md  # Exenciones para pequeños productores
├── programas_gobierno_agro.md       # Programas gubernamentales agropecuarios
└── calendario_tributario_2024.md    # Calendario de obligaciones tributarias 2024
```

## Documentos

### Legislación Tributaria (Fuente: DIAN / Estatuto Tributario)

| Documento | Contenido | Artículos clave |
|-----------|-----------|-----------------|
| `estatuto_tributario_libro1.md` | Libro I — Impuesto sobre la renta, secciones relevantes para el sector agrícola | Art. 23, Art. 57-1 |
| `estatuto_tributario_libro3.md` | Libro III — IVA, exenciones sobre insumos y maquinaria agrícola | Art. 258-1 |

### Guías del Sector Agrícola (Creadas por el equipo)

| Documento | Contenido |
|-----------|-----------|
| `beneficios_compra_maquinaria.md` | Beneficios tributarios aplicables a la compra de maquinaria agrícola: descuentos de IVA, depreciación acelerada, condiciones y requisitos |
| `exenciones_pequeno_productor.md` | Exenciones fiscales disponibles para pequeños productores agrícolas: umbrales de ingresos, tipos de exención, requisitos de elegibilidad |
| `programas_gobierno_agro.md` | Programas gubernamentales de apoyo al sector agropecuario: líneas de crédito, subsidios, incentivos fiscales |

### Calendario Tributario

| Documento | Contenido |
|-----------|-----------|
| `calendario_tributario_2024.md` | Fechas clave de obligaciones tributarias para el año 2024: declaración de renta, IVA, retención en la fuente |

## Formato de los Documentos

Todos los documentos siguen estas convenciones para facilitar el chunking efectivo por el pipeline ETL:

- **Idioma:** Español
- **Encabezados:** Uso de `##` y `###` para secciones y subsecciones
- **Números de artículo:** Incluidos explícitamente para que el ETL los preserve como metadatos
- **Datos específicos:** Porcentajes reales, umbrales monetarios y condiciones concretas
- **Tipo de documento:** Cada archivo se clasifica como `legal`, `guide` o `calendar` en los metadatos del ETL

## Cómo se Procesan

1. El script `scripts/etl_ingest.py` lee todos los archivos `.md` de esta carpeta
2. Cada documento se divide en fragmentos de ~800 caracteres con 10% de solapamiento
3. Se generan embeddings con el modelo `intfloat/multilingual-e5-small`
4. Los fragmentos se almacenan en ChromaDB con metadatos:
   - `source_document` — Nombre del archivo fuente
   - `article_number` — Número(s) de artículo extraídos
   - `topic_tags` — Etiquetas temáticas
   - `document_type` — Tipo: `legal`, `guide` o `calendar`
   - `date_ingested` — Fecha de ingesta
   - `chunk_index` — Índice del fragmento
   - `total_chunks_in_article` — Total de fragmentos del artículo

## Relación con Otros Módulos

- **`scripts/etl_ingest.py`** — Procesa estos documentos y los ingesta en ChromaDB
- **`agent/tools/get_tax_knowledge.py`** — Consulta los embeddings generados a partir de estos documentos para responder preguntas tributarias
- **`chroma_data/`** — Directorio donde ChromaDB almacena los embeddings persistentes

## Agregar Nuevos Documentos

Para agregar un nuevo documento a la base de conocimiento:

1. Crear un archivo `.md` en esta carpeta siguiendo el formato descrito arriba
2. Usar encabezados `##` y `###` para facilitar el chunking
3. Incluir números de artículo cuando aplique
4. Ejecutar el pipeline ETL para ingestar el nuevo documento:
   ```bash
   python scripts/etl_ingest.py
   ```
   El pipeline detecta documentos nuevos y los procesa sin duplicar los existentes.
