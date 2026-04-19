# FIN-Advisor: Data Requirements & Mock Data Plan

---

## Data Categories

The project requires two distinct categories of data:

1. **Knowledge Base Documents** — Public legal and regulatory texts, converted to embeddings and stored in ChromaDB
2. **Transactional Mock Data** — Synthetic financial records simulating EverGreen's FIN module, stored in SQLite

---

## Category 1: Knowledge Base Documents

### Document Inventory

| ID | Document | Source | Format | Processing |
|---|---|---|---|---|
| DOC-01 | Estatuto Tributario — Book I (Income Tax, agricultural sections) | DIAN public portal | PDF → Markdown | Chunk + embed + store in ChromaDB |
| DOC-02 | Estatuto Tributario — Book III (VAT, agricultural sections) | DIAN public portal | PDF → Markdown | Chunk + embed + store in ChromaDB |
| DOC-03 | Agricultural Machinery Purchase Benefits Guide | Team-created (mock) | Markdown | Chunk + embed + store in ChromaDB |
| DOC-04 | Small Producer Exemptions Guide | Team-created (mock) | Markdown | Chunk + embed + store in ChromaDB |
| DOC-05 | Government Agricultural Programs Guide | Team-created (mock) | Markdown | Chunk + embed + store in ChromaDB |
| DOC-06 | 2024 Tax Calendar for Agricultural Entities | Team-created (mock) | Markdown | Chunk + embed + store in ChromaDB |

### Document Preparation Workflow

```
1. Download PDF from official source (DOC-01, DOC-02)
   OR write Markdown directly (DOC-03 through DOC-06)
        │
        ▼
2. Convert PDF to Markdown (if applicable)
   Tool: PyMuPDF, pdfplumber, or manual extraction
        │
        ▼
3. Clean and structure the Markdown
   - Ensure article numbers are preserved as headers
   - Remove page numbers, footers, watermarks
   - Verify Spanish characters are intact
        │
        ▼
4. Run the ETL ingestion script
   - RecursiveCharacterTextSplitter (500-1000 tokens, 10% overlap)
   - Generate embeddings via sentence-transformers
   - Store in ChromaDB with metadata
        │
        ▼
5. Validate
   - Run test queries to verify retrieval quality
   - Check that metadata is complete for all chunks
```

### Mock Document Guidelines (DOC-03 to DOC-06)

Each team-created document should:
- Be 2-4 pages in Markdown
- Use clear section headers (## and ###) for effective chunking
- Include realistic but simplified content based on actual Colombian agricultural policy
- Be written in Spanish
- Include specific numbers, percentages, and conditions (not vague statements)

**Example structure for DOC-03 (Machinery Benefits):**
```markdown
# Beneficios Tributarios para la Compra de Maquinaria Agrícola

## 1. Descuento del IVA en Bienes de Capital
Según el Artículo 258-1 del Estatuto Tributario...
### Condiciones
- El bien debe ser utilizado directamente en la actividad agropecuaria
- El productor debe estar inscrito en el RUT con actividad agrícola
### Porcentaje de Descuento
...

## 2. Depreciación Acelerada
...
```

---

## Category 2: Transactional Mock Data (SQLite)

### Table Definitions and Sample Data

#### Table: `perfil_productor`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Producer ID |
| name | TEXT | Producer name |
| farm_name | TEXT | Farm name |
| activity_type | TEXT | Main agricultural activity |
| nit | TEXT | Tax ID (simulated) |
| tax_bracket | TEXT | Tax category |
| registered_since | DATE | Registration date |

**Sample row:**
```
(1, "Carlos Mendoza", "Finca El Roble", "Hortalizas", "900123456-1", "Régimen Simple", "2020-03-15")
```

---

#### Table: `movimientos`

| Column | Type | Description |
|---|---|---|
| id | INTEGER PK | Movement ID |
| date | DATE | Transaction date |
| type | TEXT | INGRESO or EGRESO |
| category | TEXT | Expense/income category |
| amount | REAL | Amount in COP |
| description | TEXT | Description |
| account_id | INTEGER | Account reference |

**Sample data (minimum 30 rows covering 6 months):**

Categories to include:
- INGRESO: "Venta cosecha", "Venta ganado", "Subsidio gobierno"
- EGRESO: "Semillas", "Abono/Fertilizante", "Combustible", "Mano de obra", "Servicios públicos", "Mantenimiento maquinaria", "Transporte"

**Data generation approach:** Python script using `random` and `datetime` to generate realistic patterns (higher income during harvest months, regular monthly expenses).

---

#### Table: `facturas_venta`

| Column | Type | Description |
|---|---|---|
| invoice_id | INTEGER PK | Invoice ID |
| date_issued | DATE | Issue date |
| date_due | DATE | Due date |
| client_name | TEXT | Buyer name |
| total_amount | REAL | Total in COP |
| vat_amount | REAL | VAT component |
| status | TEXT | PAID, PENDING, or OVERDUE |

**Sample data (minimum 15 rows):**
- Mix of PAID (60%), PENDING (30%), and OVERDUE (10%)
- Clients: "Cooperativa del Valle", "Mercado Central", "Distribuidora Agrícola del Sur", "Plaza de Mercado Municipal"

---

#### Table: `cuentas_por_pagar`

| Column | Type | Description |
|---|---|---|
| payable_id | INTEGER PK | Payable ID |
| supplier_name | TEXT | Supplier name |
| amount | REAL | Amount owed in COP |
| due_date | DATE | Payment deadline |
| category | TEXT | Expense type |
| status | TEXT | PENDING, PAID, or OVERDUE |

**Sample data (minimum 10 rows):**
- Suppliers: "Semillas del Valle", "AgroInsumos S.A.", "Combustibles del Campo", "Ferretería Rural"

---

#### Table: `activos_fijos`

| Column | Type | Description |
|---|---|---|
| asset_id | INTEGER PK | Asset ID |
| name | TEXT | Asset name |
| category | TEXT | MAQUINARIA, TERRENO, VEHICULO, EQUIPO |
| purchase_date | DATE | Acquisition date |
| purchase_value | REAL | Original cost in COP |
| current_value | REAL | Depreciated value |
| depreciation_rate | REAL | Annual depreciation % |

**Sample data (5-8 rows):**
- "Tractor John Deere 5075" — MAQUINARIA — $45.000.000
- "Terreno Lote 3 — Vereda El Carmen" — TERRENO — $120.000.000
- "Camioneta Toyota Hilux" — VEHICULO — $85.000.000
- "Sistema de Riego por Goteo" — EQUIPO — $15.000.000
- "Fumigadora de Espalda Motorizada" — EQUIPO — $2.500.000

---

## Data Volume Summary

| Data Source | Estimated Volume | Storage |
|---|---|---|
| Knowledge base documents | ~60-90 pages of text → ~200-400 chunks | ChromaDB |
| Movimientos | ~30-50 rows | SQLite |
| Facturas de venta | ~15-20 rows | SQLite |
| Cuentas por pagar | ~10-15 rows | SQLite |
| Activos fijos | ~5-8 rows | SQLite |
| Perfil productor | 1 row | SQLite |

This is intentionally small — enough to demonstrate the RAG pipeline without requiring significant data generation effort.

---

## Data Generation Responsibility

| Task | Owner | Estimated Effort |
|---|---|---|
| Download and extract Estatuto Tributario sections | 1 team member | 2-3 hours |
| Write mock benefit guides (DOC-03 to DOC-06) | 1-2 team members | 3-4 hours |
| Write Python script to generate SQLite mock data | 1 team member | 2-3 hours |
| Write ETL ingestion script (PDF/MD → ChromaDB) | 1 team member | 3-4 hours |
| Validate retrieval quality with test queries | Whole team | 1-2 hours |
