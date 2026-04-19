# Caso de Aplicación RAG — Módulo de Finanzas (FIN)
# Asistente Inteligente de Optimización Tributaria y Flujo de Caja (FIN-Advisor)

**Proyecto:** EverGreen — Módulo de Finanzas (FIN)
**Equipo:** [Nombre del equipo]
**Curso:** Tópicos Avanzados de Software

---

## 1. Presentación de la Funcionalidad RAG

### 1.1 Descripción de la Funcionalidad

FIN-Advisor es un asistente basado en un Modelo de Lenguaje Extenso (LLM) que implementa el patrón RAG (Retrieval-Augmented Generation) para el módulo de Finanzas de EverGreen. El sistema analiza la situación contable actual del productor agrícola y la cruza con normativas legales tributarias colombianas para generar asesoría financiera personalizada.

Concretamente, el asistente:

- Recupera fragmentos relevantes de la legislación tributaria colombiana desde una base de datos vectorial (ChromaDB)
- Consulta los datos financieros del usuario en tiempo real desde la base de datos relacional de EverGreen (SQLite)
- Razona sobre ambas fuentes de datos mediante un agente ReAct (Reasoning and Acting) orquestado con LangChain
- Ejecuta cálculos financieros precisos mediante herramientas especializadas (sin depender del LLM para operaciones matemáticas)
- Genera recomendaciones personalizadas, fundamentadas y trazables

### 1.2 Justificación

El módulo de Finanzas de EverGreen gestiona frentes críticos como facturación, cuentas por cobrar/pagar y tributación. Sin embargo, actualmente funciona como un sistema pasivo de registro — los productores agrícolas enfrentan tres problemas recurrentes:

1. **Complejidad tributaria:** El Estatuto Tributario colombiano contiene exenciones y deducciones específicas para el sector agropecuario (por ejemplo, descuentos de IVA en bienes de capital según el Art. 258-1) que son difíciles de interpretar sin asesoría profesional.

2. **Ceguera de flujo de caja:** Los productores registran transacciones pero carecen de herramientas para entender el *porqué* del comportamiento de su caja o para proyectar liquidez futura.

3. **Timing de inversión:** Decidir cuándo comprar activos fijos (tractores, cosechadoras, sistemas de riego) requiere cruzar liquidez actual, cuentas por cobrar pendientes y beneficios tributarios aplicables — una tarea propensa a errores cuando se hace manualmente.

FIN-Advisor transforma el módulo de Finanzas de un repositorio pasivo de facturas a una **herramienta activa de soporte de decisiones**, reduciendo el riesgo de sanciones tributarias, aprovechando beneficios fiscales del agro y habilitando decisiones de inversión informadas por datos — todo sin requerir que el productor contrate un contador externo para consultas rutinarias.

---

## 2. Esquema Explicativo de la Funcionalidad RAG

### 2.1 Perspectiva de Negocio

El esquema de negocio opera a través de un viaje del usuario (Customer Journey) en cinco fases:

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  DESCUBRI-   │     │  FORMULACIÓN     │     │  PROCESAMIENTO          │
│  MIENTO      │────>│  DE CONSULTA     │────>│                         │
│              │     │                  │     │  ┌─────────────────┐    │
│ Productor    │     │ Escribe pregunta │     │  │ Agente ReAct    │    │
│ abre módulo  │     │ en lenguaje      │     │  │ razona sobre    │    │
│ FIN          │     │ natural          │     │  │ qué herramientas│    │
│              │     │                  │     │  │ invocar         │    │
└─────────────┘     └──────────────────┘     │  └────────┬────────┘    │
                                              │           │             │
                                              │  ┌────────▼────────┐    │
                                              │  │ Ejecución de    │    │
                                              │  │ Herramientas    │    │
                                              │  │ - Búsqueda KB   │    │
                                              │  │ - Consulta FIN  │    │
                                              │  │ - Cálculos      │    │
                                              │  └────────┬────────┘    │
                                              │           │             │
                                              └───────────┼─────────────┘
                                                          │
                                                          ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  SEGUIMIENTO │     │  ENTREGA DE      │     │  GENERACIÓN LLM         │
│              │<────│  RESPUESTA       │<────│                         │
│ Productor    │     │                  │     │  Sintetiza contexto     │
│ hace más     │     │ Recomendación    │     │  legal + financiero     │
│ preguntas    │     │ estructurada     │     │  en recomendación       │
│ o inicia     │     │ con referencias  │     │  personalizada          │
│ nuevo tema   │     │ y datos          │     │                         │
└─────────────┘     └──────────────────┘     └─────────────────────────┘
```

**Fase 1 — Descubrimiento:** El productor o administrador financiero ingresa al módulo FIN de EverGreen y accede a la interfaz de chat de FIN-Advisor, disponible como componente persistente en el dashboard financiero.

**Fase 2 — Formulación de Consulta:** El productor escribe una pregunta en lenguaje natural en español. No se requiere sintaxis especial ni entrada estructurada. Ejemplos:
- "¿Puedo descontar el IVA del tractor que quiero comprar?"
- "¿Cómo está mi flujo de caja este trimestre?"
- "Si compro una cosechadora este mes, ¿comprometo mi liquidez?"

**Fase 3 — Procesamiento (El "Cerebro"):** El agente ReAct analiza la consulta, determina qué herramientas necesita invocar (búsqueda en base de conocimiento, consulta de datos financieros, cálculos), las ejecuta en secuencia y recopila el contexto necesario. Esta fase es invisible para el usuario.

**Fase 4 — Entrega de Respuesta:** El LLM sintetiza todo el contexto recuperado en una recomendación coherente y personalizada que incluye: respuesta directa, referencias a artículos legales específicos, cifras financieras del usuario, curso de acción recomendado y disclaimers cuando corresponda.

**Fase 5 — Seguimiento:** El productor puede hacer preguntas de seguimiento, solicitar aclaraciones o iniciar un nuevo tema. El contexto conversacional se mantiene dentro de la sesión.

### 2.2 Ejemplo Concreto de Operación

**Consulta del usuario:** "¿Puedo descontar el IVA del tractor que quiero comprar?"

**Procesamiento interno:**
1. El agente identifica que necesita información legal (IVA en bienes de capital) y datos financieros del usuario
2. Llama a `get_tax_knowledge` → ChromaDB retorna el fragmento del Art. 258-1 del Estatuto Tributario
3. Llama a `query_evergreen_finances` → Obtiene saldo actual ($12.500.000), cuentas por cobrar ($8.000.000)
4. Llama a `calculate_vat_discount` → Calcula descuento de IVA: $3.420.000, costo efectivo: $14.580.000
5. Llama a `assess_investment_viability` → Determina: no viable hoy, viable en 15 días

**Respuesta generada:**
> "Según el Artículo 258-1 del Estatuto Tributario, los bienes de capital adquiridos para actividades agropecuarias permiten descontar el IVA pagado. Revisando tu flujo de caja actual, tienes un saldo disponible de $12.500.000 COP y cuentas por cobrar de $8.000.000 COP con vencimiento en 15 días. La compra de la cosechadora ($18.000.000 COP) sería viable en la semana 3 del mes, una vez se materialicen los cobros pendientes. Además, el descuento del IVA representaría un ahorro de $3.420.000 COP en tu declaración."

### 2.3 Alcance de Respuestas

| Lo que FIN-Advisor SÍ responde (In-Scope) | Lo que FIN-Advisor NO responde (Out-of-Scope) |
|---|---|
| Consultas sobre el Estatuto Tributario aplicable al agro | Consejos de inversión en bolsa o criptomonedas |
| Resúmenes de gastos e ingresos registrados en EverGreen | Temas de salud humana o veterinaria |
| Proyecciones de impuestos basadas en datos reales del usuario | Opiniones políticas o sociales |
| Explicación de conceptos contables básicos | Soporte técnico de hardware o maquinaria |
| Requisitos para acceder a beneficios del gobierno para el campo | Promesas de éxito financiero garantizado |
| Análisis de viabilidad de compra de activos fijos | Asesoría legal más allá de tributación (laboral, contratos) |

---

## 3. Elementos de Datos en la Funcionalidad RAG

### 3.1 Definición de la Base de Conocimiento

La base de conocimiento contiene toda la información externa (no específica del usuario) que el LLM necesita para fundamentar sus respuestas. Cada documento pasa por un pipeline ETL: ingestión → troceado (chunking) → generación de embeddings → almacenamiento en ChromaDB.

#### KB-01: Estatuto Tributario Nacional

| Atributo | Detalle |
|---|---|
| Fuente | PDF público del portal oficial de la DIAN |
| Alcance | Libro I (Impuesto de Renta) y Libro III (IVA) — solo secciones aplicables al sector agropecuario |
| Formato | PDF → convertido a Markdown para procesamiento |
| Frecuencia de actualización | Estático para MVP (versión 2024) |
| Tamaño estimado | ~50-80 páginas de contenido relevante después de filtrar |

**Secciones clave incluidas:**
- Art. 258-1: Descuento del IVA en bienes de capital (maquinaria, equipo)
- Art. 23: Entidades exentas de impuestos en el sector agropecuario
- Art. 57-1: Rentas provenientes de actividades agropecuarias
- Secciones sobre retención en la fuente para ventas agrícolas
- Exenciones de IVA en insumos agropecuarios (semillas, fertilizantes)

**Condiciones:**
- Solo se incluyen artículos directamente aplicables a productores agropecuarios
- Cada artículo debe conservar su numeración original para trazabilidad en las respuestas
- Los metadatos deben incluir: número de artículo, libro, título y etiquetas temáticas

#### KB-02: Guías de Beneficios del Sector Agropecuario

| Atributo | Detalle |
|---|---|
| Fuente | Documentos mock creados por el equipo, basados en lineamientos reales de MinAgricultura |
| Alcance | Exenciones tributarias y programas gubernamentales para pequeños y medianos productores |
| Formato | Archivos Markdown (3-4 documentos) |
| Tamaño estimado | ~5-10 páginas en total |

**Documentos a crear:**
1. `beneficios_compra_maquinaria.md` — Beneficios para la compra de maquinaria agrícola
2. `exenciones_pequeno_productor.md` — Exenciones para pequeños productores (umbrales de ingreso)
3. `programas_gobierno_agro.md` — Programas gubernamentales y subsidios para el sector
4. `calendario_tributario_2024.md` — Fechas clave de obligaciones tributarias para entidades agrícolas

**Condiciones:**
- El contenido debe ser realista y basado en política agrícola colombiana real
- Cada documento debe tener encabezados de sección claros para un troceado efectivo
- Los documentos deben estar escritos en español
- Deben incluir números, porcentajes y condiciones específicas (no declaraciones vagas)

#### KB-03: Tasas de Cambio Históricas (Opcional — Fase 2)

| Atributo | Detalle |
|---|---|
| Fuente | Datos sintéticos o datos públicos del Banco de la República |
| Alcance | Tasas USD/COP de los últimos 12 meses |
| Formato | CSV o JSON |
| Prioridad | Baja — incluir solo si el tiempo lo permite |

**Condición:** Solo relevante para consultas que involucren insumos importados. Se almacenaría en la base de datos relacional, no en el vector store.

#### Estrategia de Troceado (Chunking)

| Parámetro | Valor | Justificación |
|---|---|---|
| Método | `RecursiveCharacterTextSplitter` | Respeta la jerarquía del documento (artículos → párrafos) |
| Tamaño de trozo | 500-1000 tokens | Suficientemente grande para preservar el contexto de artículos legales, suficientemente pequeño para recuperación precisa |
| Solapamiento | 10% (~50-100 tokens) | Previene pérdida de contexto en los límites entre trozos |
| Separadores | `["\n## ", "\n### ", "\n\n", "\n", " "]` | Prioriza división en límites de encabezados, luego párrafos, luego oraciones |

**Consideraciones especiales para texto legal:**
- Los artículos NO deben cortarse a mitad de oración
- Si un artículo es más corto que el tamaño del trozo, se mantiene como un solo trozo
- Las listas numeradas dentro de artículos (numerales) deben permanecer juntas cuando sea posible

#### Esquema de Metadatos

Cada trozo almacenado en ChromaDB incluye los siguientes metadatos:

```json
{
  "source_document": "estatuto_tributario_2024.md",
  "article_number": "258-1",
  "book": "Libro III - IVA",
  "topic_tags": ["IVA", "bienes_de_capital", "maquinaria"],
  "document_type": "legal",
  "date_ingested": "2024-XX-XX",
  "chunk_index": 3,
  "total_chunks_in_article": 5
}
```

#### Criterios de Calidad de la Base de Conocimiento

1. **Completitud:** Todos los artículos clave del Estatuto Tributario relacionados con tributación agropecuaria están presentes
2. **Trazabilidad:** Cada respuesta que cite una ley debe ser rastreable hasta un trozo específico con su número de artículo
3. **Sin duplicación:** El mismo artículo no debe aparecer en múltiples trozos a menos que el solapamiento sea intencional
4. **Filtrado de relevancia:** Una consulta de prueba como "IVA en tractores" debe retornar trozos del Art. 258-1, no artículos de IVA no relacionados
5. **Consistencia de idioma:** Todo el contenido de la base de conocimiento está en español
6. **Integridad de metadatos:** Cada trozo tiene metadatos completos — sin campos requeridos nulos

---

### 3.2 Definición de Entradas

Las entradas son las fuentes de datos que alimentan el pipeline RAG en tiempo de consulta. Se dividen en dos categorías: la consulta del usuario (el disparador) y los datos transaccionales (el contexto).

#### Entrada 1: Consulta del Usuario (Lenguaje Natural)

| Atributo | Detalle |
|---|---|
| Fuente | Interfaz de chat en el módulo FIN de EverGreen |
| Formato | Cadena de texto libre en español |
| Longitud máxima | 500 caracteres (límite suave, aplicado por el frontend) |
| Idioma | Español (colombiano) |
| Requerido | Sí — es el disparador de cada interacción |

**Condiciones:**
- El sistema debe manejar lenguaje informal, errores tipográficos y expresiones coloquiales
- Las consultas fuera del alcance definido deben ser rechazadas con un mensaje útil
- Las consultas vacías o sin sentido deben solicitar al usuario que reformule

#### Entrada 2: Movimientos Contables

| Atributo | Detalle |
|---|---|
| Fuente | Base de datos relacional FIN de EverGreen (mock en SQLite) |
| Formato | Registros estructurados (filas en tabla) |
| Acceso | Solo lectura vía herramienta `query_evergreen_finances` |

| Campo | Tipo | Descripción |
|---|---|---|
| id | int | Identificador único del movimiento |
| date | date | Fecha de la transacción |
| type | enum | `INGRESO` o `EGRESO` |
| category | string | Categoría (ej. "Insumos", "Venta cosecha", "Servicios") |
| amount | decimal | Monto en COP |
| description | string | Descripción del movimiento |
| account_id | int | FK al plan de cuentas |

**Condiciones:** Los datos deben cubrir al menos los últimos 6 meses. Todos los montos en COP. El agente nunca debe modificar estos datos — acceso estrictamente de solo lectura.

#### Entrada 3: Facturación de Venta

| Atributo | Detalle |
|---|---|
| Fuente | Base de datos relacional FIN de EverGreen |
| Acceso | Solo lectura vía herramienta `query_evergreen_finances` |

| Campo | Tipo | Descripción |
|---|---|---|
| invoice_id | int | Identificador único de factura |
| date_issued | date | Fecha de emisión |
| date_due | date | Fecha de vencimiento |
| client_name | string | Nombre del comprador |
| total_amount | decimal | Monto total en COP |
| vat_amount | decimal | Componente de IVA |
| status | enum | `PAID`, `PENDING`, `OVERDUE` |

**Condiciones:** Las facturas pendientes y vencidas son críticas para proyecciones de flujo de caja. El sistema debe poder calcular el total de cuentas por cobrar a partir de facturas pendientes.

#### Entrada 4: Cuentas por Pagar

| Atributo | Detalle |
|---|---|
| Fuente | Base de datos relacional FIN de EverGreen |
| Acceso | Solo lectura vía herramienta `query_evergreen_finances` |

| Campo | Tipo | Descripción |
|---|---|---|
| payable_id | int | Identificador único |
| supplier_name | string | Nombre del proveedor (ej. "Semillas del Valle") |
| amount | decimal | Monto adeudado en COP |
| due_date | date | Fecha límite de pago |
| category | string | Tipo de gasto (ej. "Semillas", "Abono", "Combustible") |
| status | enum | `PENDING`, `PAID`, `OVERDUE` |

**Condiciones:** Las cuentas por pagar pendientes son esenciales para cálculos de liquidez. El sistema debe señalar cuentas vencidas en diagnósticos financieros.

#### Entrada 5: Inventario de Activos Fijos

| Atributo | Detalle |
|---|---|
| Fuente | Base de datos relacional FIN de EverGreen |
| Acceso | Solo lectura vía herramienta `query_evergreen_finances` |

| Campo | Tipo | Descripción |
|---|---|---|
| asset_id | int | Identificador único |
| name | string | Nombre del activo (ej. "Tractor John Deere 5075") |
| category | enum | `MAQUINARIA`, `TERRENO`, `VEHICULO`, `EQUIPO` |
| purchase_date | date | Fecha de adquisición |
| purchase_value | decimal | Costo original en COP |
| current_value | decimal | Valor depreciado en COP |
| depreciation_rate | decimal | Porcentaje de depreciación anual |

**Condiciones:** El valor actual debe calcularse con depreciación en línea recta. Los datos de activos son necesarios para el análisis de viabilidad de inversión (US-03).

---

### 3.3 Definición de Salidas

Las salidas son las respuestas generadas por el sistema. Cada tipo de salida corresponde a una o más historias de usuario.

#### Salida 1: Reporte de Diagnóstico Financiero

| Atributo | Detalle |
|---|---|
| Disparado por | US-02 (Diagnóstico de Flujo de Caja), US-06 (Optimización de Gastos) |
| Formato | Lenguaje natural estructurado en la interfaz de chat |

**Estructura:**
```
1. Resumen: Panorama en una oración de la situación financiera
2. Hallazgos Clave: Top 3 factores que explican el estado actual
   - Cada hallazgo incluye: categoría, monto y explicación
3. Comparación: Período actual vs. período anterior (si hay datos)
4. Recomendaciones: 2-3 sugerencias accionables
5. Disclaimer: "Este análisis se basa en datos registrados. Consulte un profesional para decisiones formales."
```

**Condiciones:** Debe incluir cifras monetarias reales del usuario. Debe explicar causas, no solo listar números. Máximo 400 palabras. Siempre incluir disclaimer.

#### Salida 2: Calendario Tributario Personalizado

| Atributo | Detalle |
|---|---|
| Disparado por | US-04 (Calendario Tributario Personalizado) |
| Formato | Lista cronológica en la interfaz de chat |

**Estructura:**
```
Próximas Obligaciones Tributarias (próximos 3 meses):

1. [FECHA] — [NOMBRE DE OBLIGACIÓN]
   Monto estimado: $X.XXX.XXX COP
   ⚠️ Advertencia: El saldo proyectado en esta fecha puede ser insuficiente

2. [FECHA] — [NOMBRE DE OBLIGACIÓN]
   Monto estimado: $X.XXX.XXX COP
   ✅ El saldo proyectado es suficiente
```

**Condiciones:** Fechas en orden cronológico. Cada entrada incluye nombre de obligación y monto estimado. Advertencias de liquidez basadas en saldo proyectado. Debe especificar que solo cubre obligaciones nacionales (DIAN).

#### Salida 3: Recomendación de Viabilidad de Inversión

| Atributo | Detalle |
|---|---|
| Disparado por | US-03 (Viabilidad de Compra de Activo Fijo) |
| Formato | Recomendación estructurada en la interfaz de chat |

**Estructura:**
```
1. Activo: [Nombre y costo estimado]
2. Beneficios Tributarios: [Deducciones/descuentos aplicables con referencias a artículos]
3. Costo Efectivo: [Costo después de beneficios tributarios]
4. Snapshot Financiero:
   - Saldo actual: $X
   - Cuentas por cobrar pendientes (próximos 30 días): $X
   - Cuentas por pagar pendientes (próximos 30 días): $X
   - Disponible para inversión: $X
5. Veredicto: [VIABLE / NO VIABLE AHORA / VIABLE EN X SEMANAS]
6. Razonamiento: [Explicación del cálculo]
7. Disclaimer
```

**Condiciones:** Debe mostrar el cálculo completo de forma transparente. Debe referenciar artículos tributarios específicos si aplican beneficios. Si no es viable ahora, debe sugerir la fecha viable más temprana. Siempre incluir supuestos usados en la proyección.

#### Salida 4: Explicación de Beneficio Tributario

| Atributo | Detalle |
|---|---|
| Disparado por | US-01 (Consulta de Beneficio Tributario) |
| Formato | Texto explicativo en la interfaz de chat |

**Estructura:**
```
1. Beneficio Aplicable: [Nombre y resumen]
2. Base Legal: [Número de artículo y cita breve]
3. Condiciones: [Requisitos que el productor debe cumplir]
4. Impacto Estimado: [Cuánto podría ahorrar, si es calculable]
5. Recomendación: [Próximos pasos para aprovechar el beneficio]
6. Disclaimer
```

**Condiciones:** Siempre citar el número de artículo específico. Explicar condiciones en lenguaje llano. Incluir disclaimer sobre validación profesional.

#### Salida 5: Explicación de Concepto Contable

| Atributo | Detalle |
|---|---|
| Disparado por | US-05 (Explicación de Concepto Contable) |
| Formato | Texto explicativo corto en la interfaz de chat |

**Condiciones:** Máximo 200 palabras. Sin jerga no explicada. Incluye ejemplo concreto (de datos del usuario si están disponibles, de lo contrario ejemplo agrícola genérico). No requiere disclaimer (educativo, no asesoría).

#### Reglas de Calidad de Salidas (Aplican a TODAS las salidas)

1. **Fundamentación:** Cada afirmación factual debe ser rastreable a la base de conocimiento o a los datos financieros del usuario. Sin cifras alucinadas.
2. **Transparencia:** Cuando el sistema no está seguro o carece de datos, debe decirlo explícitamente.
3. **Consistencia:** Las cifras monetarias deben usar COP con separadores de miles (ej. $12.500.000 COP).
4. **Tono:** Técnico pero accesible — escrito para un administrador de finca, no para un contador.
5. **Idioma:** Todas las respuestas en español.
6. **Disclaimers:** Cualquier salida que pueda interpretarse como asesoría financiera o legal debe incluir un disclaimer.

---

## 4. Propuesta de Arquitectura de la Solución

### 4.1 Visión General

FIN-Advisor sigue una **arquitectura por capas** con cuatro capas distintas, cada una con una responsabilidad única. Todos los componentes se ejecutan localmente — sin dependencias de nube.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     CAPA DE PRESENTACIÓN                                │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────────────┐   │
│   │                    React.js Frontend                            │   │
│   │   ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │   │
│   │   │  Chat UI     │  │  Dashboard   │  │  Renderizador      │   │   │
│   │   │  Component   │  │  FIN         │  │  de Respuestas     │   │   │
│   │   └──────────────┘  └──────────────┘  └────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────────────┘   │
│                              HTTP / REST                                 │
├──────────────────────────────────────────────────────────────────────────┤
│                     CAPA DE RAZONAMIENTO                                 │
│                                                                         │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │                    FastAPI Backend                                │  │
│   │   ┌──────────────────────────────────────────────────────────┐   │  │
│   │   │              Agente ReAct (LangChain)                    │   │  │
│   │   │                                                          │   │  │
│   │   │   ┌─────────────┐ ┌──────────────┐  Herramientas de     │   │  │
│   │   │   │ get_tax_    │ │ query_       │  Cálculo (x5):       │   │  │
│   │   │   │ knowledge   │ │ evergreen_   │  ┌────────────────┐  │   │  │
│   │   │   │ (ChromaDB)  │ │ finances     │  │ vat_discount   │  │   │  │
│   │   │   │             │ │ (SQLite)     │  │ net_liquidity  │  │   │  │
│   │   │   │             │ │              │  │ invest_viab.   │  │   │  │
│   │   │   │             │ │              │  │ tax_projection │  │   │  │
│   │   │   │             │ │              │  │ depreciation   │  │   │  │
│   │   │   └─────────────┘ └──────────────┘  └────────────────┘  │   │  │
│   │   └──────────────────────────────────────────────────────────┘   │  │
│   └──────────────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────────────────┤
│          CAPA DE CONOCIMIENTO              CAPA DE DATOS                 │
│                                                                         │
│   ┌──────────────────────┐  ┌───────────────────────────────────┐      │
│   │    ChromaDB           │  │    SQLite                         │      │
│   │    (Vector Store)     │  │    (Base de Datos FIN EverGreen)  │      │
│   │                       │  │                                   │      │
│   │  - Leyes tributarias  │  │  - Movimientos contables          │      │
│   │  - Guías de beneficios│  │  - Facturas de venta              │      │
│   │  - Docs sectoriales   │  │  - Cuentas por pagar              │      │
│   │                       │  │  - Activos fijos                  │      │
│   │  Embeddings vía       │  │  - Perfil del productor           │      │
│   │  sentence-transformers│  │                                   │      │
│   └──────────────────────┘  └───────────────────────────────────┘      │
├──────────────────────────────────────────────────────────────────────────┤
│                     CAPA DE INFERENCIA                                   │
│   ┌──────────────────────────────────────────────────────────────────┐  │
│   │  Ollama (LLM Local) — Llama 3 (8B) o Mistral (7B)               │  │
│   │  API: http://localhost:11434                                     │  │
│   └──────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Descripción de Capas

**Capa de Presentación (React.js):** Interfaz de chat donde el usuario ingresa consultas y recibe respuestas. Incluye el dashboard FIN existente y un renderizador de respuestas que formatea tablas, advertencias y calendarios. Comunicación con el backend vía REST API (`POST /api/v1/chat`).

**Capa de Razonamiento (FastAPI + LangChain):** El corazón del sistema. El servidor FastAPI recibe las peticiones HTTP y las pasa al agente ReAct de LangChain, que orquesta el ciclo de razonamiento: analiza la consulta, decide qué herramientas invocar, observa los resultados y sintetiza la respuesta final. Dispone de 7 herramientas: 2 de recuperación de datos y 5 de cálculo especializado.

**Capa de Conocimiento (ChromaDB):** Base de datos vectorial que almacena los embeddings de los documentos legales y guías sectoriales. Usa el modelo `all-MiniLM-L6-v2` para generar embeddings localmente. Organizada en colecciones: `tax_laws` y `sector_guides`.

**Capa de Datos (SQLite):** Base de datos relacional con datos mock que simulan el módulo FIN de EverGreen. Contiene 5 tablas: movimientos, facturas_venta, cuentas_por_pagar, activos_fijos y perfil_productor. Acceso estrictamente de solo lectura.

**Capa de Inferencia (Ollama):** Ejecuta el LLM localmente. Modelo primario: Llama 3 (8B). Modelo de respaldo: Mistral (7B) para máquinas con menos RAM. Expone una API REST en localhost:11434 que LangChain consume nativamente.

### 4.3 Diagrama de Flujo de Datos

```
                    ┌──────────┐
                    │ Usuario  │
                    │(Navegador)│
                    └────┬─────┘
                         │ 1. POST /api/v1/chat
                         │    { message: "¿Puedo descontar el IVA?" }
                         ▼
                    ┌──────────┐
                    │ FastAPI  │
                    │ Backend  │
                    └────┬─────┘
                         │ 2. Pasa consulta al Agente ReAct
                         ▼
                    ┌──────────┐
                    │  Agente  │
                    │  ReAct   │◄─────────────────────────────┐
                    └────┬─────┘                              │
                         │                                    │
              ┌──────────┼──────────┐                         │
              │          │          │                          │
              ▼          ▼          ▼                          │
        ┌──────────┐ ┌──────────┐ ┌──────────────────┐       │
        │ ChromaDB │ │ SQLite   │ │ Herramientas de  │       │
        │(búsqueda)│ │(consulta)│ │ Cálculo (x5)     │       │
        └────┬─────┘ └────┬─────┘ └────────┬─────────┘       │
             │            │                │                  │
             │ 3. Retorna │ 4. Retorna     │ 5. Retorna       │
             │ fragmentos │ datos fin.     │ cálculo           │
             └────────────┴────────────────┴──────────────────┘
                         │
                         │ 6. Agente sintetiza contexto
                         ▼
                    ┌──────────┐
                    │  Ollama  │
                    │  (LLM)   │
                    └────┬─────┘
                         │ 7. Respuesta generada
                         ▼
                    ┌──────────┐       ┌──────────┐
                    │ FastAPI  │──────>│ Usuario  │
                    │ Backend  │  8.   │(Navegador)│
                    └──────────┘ JSON  └──────────┘
```

### 4.4 Definición del Agente y Herramientas

El agente es de tipo **ReAct (Reasoning and Acting)**, implementado con `LangChain create_react_agent`. Opera en un ciclo iterativo `THOUGHT → ACTION → OBSERVATION → ... → FINAL ANSWER`, decidiendo dinámicamente el orden y número de invocaciones de herramientas según la consulta.

**Decisión de diseño clave:** Las capacidades de cálculo están divididas en 5 herramientas independientes de propósito único en lugar de una sola herramienta monolítica. Esto es intencional:
- El nombre de la herramienta le dice al agente qué hace (mejor razonamiento)
- Cada herramienta tiene un esquema de entrada estrecho y bien definido (menos ambigüedad)
- Mejor aislamiento de errores y facilidad de testing

#### Inventario de Herramientas

| # | Herramienta | Categoría | Entradas | Fuente de Datos | Historias de Usuario |
|---|---|---|---|---|---|
| 1 | `get_tax_knowledge` | Recuperación | consulta de búsqueda (string) | ChromaDB | US-01, US-03, US-04, US-06 |
| 2 | `query_evergreen_finances` | Recuperación | descriptor de consulta (estructurado) | SQLite | US-02, US-03, US-04, US-05, US-06 |
| 3 | `calculate_vat_discount` | Cálculo | purchase_price, vat_rate | Ninguna (cómputo puro) | US-01, US-03 |
| 4 | `calculate_net_liquidity` | Cálculo | balance, receivables, payables | Ninguna (cómputo puro) | US-02, US-03, US-04 |
| 5 | `assess_investment_viability` | Cálculo | balance, receivables, payables, purchase_cost, tax_benefit | Ninguna (cómputo puro) | US-03 |
| 6 | `project_tax_liability` | Cálculo | gross_income, deductions, tax_rate | Ninguna (cómputo puro) | US-04 |
| 7 | `calculate_depreciation` | Cálculo | purchase_value, useful_life_years, years_elapsed | Ninguna (cómputo puro) | US-05 |

**Restricciones compartidas de herramientas de cálculo:** No acceden a ninguna base de datos. Todos los cálculos son determinísticos (sin intervención del LLM). Retornan tanto el resultado numérico como una explicación legible en español.

#### Patrones de Interacción

| Patrón | Ejemplo de Consulta | Flujo de Herramientas |
|---|---|---|
| A: Consulta Legal Simple | "¿Qué dice la ley sobre exenciones de IVA para semillas?" | get_tax_knowledge → RESPUESTA |
| B: Consulta Financiera Simple | "¿Cuánto he gastado en insumos este trimestre?" | query_evergreen_finances → RESPUESTA |
| C: Análisis Combinado | "¿Puedo comprar un tractor sin quedarme sin liquidez?" | get_tax_knowledge → query_evergreen_finances → calculate_vat_discount → assess_investment_viability → RESPUESTA |
| D: Consulta Educativa | "¿Qué es la depreciación?" | RESPUESTA (del conocimiento del LLM) |
| E: Planificación Tributaria | "¿Cuánto voy a deber de renta este año?" | query_evergreen_finances → get_tax_knowledge → project_tax_liability → RESPUESTA |

### 4.5 Justificación de Decisiones Arquitectónicas

| Decisión | Elegido | Alternativas Consideradas | Justificación |
|---|---|---|---|
| Frontend | React.js | Next.js, Vue.js | Setup más simple para UI de chat. SSR (Next.js) innecesario para este caso |
| Backend | FastAPI | Flask, Django | Soporte async nativo, docs OpenAPI automáticas, estándar para APIs de IA/ML en Python |
| Framework de Agente | LangChain | LlamaIndex, Smolagents | Ecosistema más maduro para agentes ReAct con tool calling. Documentación extensa |
| Vector DB | ChromaDB | Pinecone, Weaviate, FAISS | Gratis, local, Python-nativo, modo persistente. Pinecone/Weaviate requieren nube. FAISS carece de filtrado por metadatos |
| LLM | Ollama (Llama 3 8B) | GPT-4 (API), Hugging Face | $0 costo, totalmente local, sin API keys. GPT-4 es superior pero cuesta dinero y requiere internet |
| BD Relacional | SQLite | PostgreSQL, MySQL | Cero configuración, basado en archivo, perfecto para datos mock |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | OpenAI embeddings, Cohere | Gratis, local, rápido. Calidad suficiente para los tipos de documento en alcance |

### 4.6 Stack Tecnológico Completo

| Capa | Tecnología | Versión | Licencia | Costo |
|---|---|---|---|---|
| Frontend | React.js | 18.x | MIT | Gratis |
| Backend | FastAPI | 0.100+ | MIT | Gratis |
| Framework de Agente | LangChain | 0.2+ | MIT | Gratis |
| Runtime LLM Local | Ollama | Latest | MIT | Gratis |
| Modelo LLM | Llama 3 (8B) | 8B-instruct | Llama 3 License | Gratis |
| Base de Datos Vectorial | ChromaDB | 0.4+ | Apache 2.0 | Gratis |
| Modelo de Embeddings | all-MiniLM-L6-v2 | - | Apache 2.0 | Gratis |
| Base de Datos Relacional | SQLite | 3.x | Public Domain | Gratis |
| Lenguaje | Python | 3.11+ | PSF | Gratis |

**Costo total de infraestructura: $0 USD**

### 4.7 Requisitos No Funcionales

| Requisito | Meta | Notas |
|---|---|---|
| Tiempo de respuesta | < 30s (consultas simples), < 45s (consultas multi-herramienta) | Depende del hardware. GPU reduce significativamente el tiempo de inferencia |
| Disponibilidad | Solo local — disponible cuando la máquina está encendida | Sin SLA requerido para proyecto universitario |
| Concurrencia | Usuario único | MVP no necesita manejar múltiples usuarios simultáneos |
| Privacidad de datos | Todos los datos permanecen locales | Ningún dato sale de la máquina. Sin llamadas a APIs externas |
| Seguridad | Básica — sin autenticación para MVP | En producción, se agregaría JWT auth y control de acceso por roles |

### 4.8 Topología de Despliegue

```
┌─────────────────────────────────────────────────┐
│              Máquina del Desarrollador            │
│                                                  │
│  ┌────────────┐  ┌────────────┐  ┌───────────┐  │
│  │ React Dev  │  │ FastAPI    │  │ Ollama    │  │
│  │ Server     │  │ Server     │  │ Server    │  │
│  │ :3000      │  │ :8000      │  │ :11434    │  │
│  └────────────┘  └────────────┘  └───────────┘  │
│                                                  │
│  ┌────────────┐  ┌────────────┐                  │
│  │ ChromaDB   │  │ SQLite     │                  │
│  │ (persist)  │  │ (file)     │                  │
│  │ :8001      │  │ fin.db     │                  │
│  └────────────┘  └────────────┘                  │
│                                                  │
└─────────────────────────────────────────────────┘
```

Todos los servicios corren en localhost. No se requiere Docker para el MVP.

---

## 5. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Estrategia de Mitigación |
|---|---|---|---|
| Alucinaciones del LLM en cálculos tributarios | Alta | Crítico | Usar herramientas de cálculo dedicadas para toda la matemática. System prompt prohíbe explícitamente inventar números |
| Baja calidad de recuperación (trozos incorrectos retornados) | Media | Alto | Estrategia de chunking cuidadosa, etiquetado de metadatos y consultas de prueba durante desarrollo |
| Rendimiento de Ollama demasiado lento en hardware del equipo | Media | Medio | Probar temprano en la máquina más débil. Usar Mistral 7B si Llama 3 es muy lento |
| Incompatibilidades de versión de LangChain | Media | Medio | Fijar todas las versiones de dependencias en requirements.txt. Usar entorno virtual |
| Scope creep (el equipo quiere agregar más features) | Alta | Medio | Adherencia estricta a las 6 historias de usuario definidas |

---

## 6. Restricciones del Proyecto

| Restricción | Detalle |
|---|---|
| Presupuesto | $0 USD — proyecto universitario, todas las herramientas deben ser gratuitas u open-source |
| Despliegue | Totalmente local — sin servicios de nube, sin API keys pagadas |
| Datos | Mezcla de documentos legales públicos y datos financieros sintéticos/mock |
| Timeline | Alcance de un semestre académico |
| Equipo | Estudiantes universitarios (primer proyecto mock) |
| Hardware | Mínimo 8GB RAM, recomendado 16GB. GPU opcional pero mejora velocidad |
