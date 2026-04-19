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

La base de conocimiento contiene toda la información externa (no específica del usuario) que el LLM necesita para fundamentar sus respuestas. Cada documento pasa por un pipeline ETL: ingestión, chunking, generación de embeddings, almacenamiento en Base de Datos Vectorial.

#### KB-01: Estatuto Tributario Nacional

| Atributo | Detalle |
|---|---|
| Fuente | PDF público del portal oficial de la DIAN |
| Alcance | Libro I (Impuesto de Renta) y Libro III (IVA) — solo secciones aplicables al sector agropecuario |
| Formato | PDF → convertido a Markdown para procesamiento |
| Frecuencia de actualización | Estático para MVP (versión 2024) |
| Tamaño estimado | ~50-80 páginas de contenido relevante después de filtrar |

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

**Documentos a crear como información legal de la empresa:**
1. `beneficios_compra_maquinaria.md` — Beneficios para la compra de maquinaria agrícola
2. `exenciones_pequeno_productor.md` — Exenciones para pequeños productores
3. `programas_gobierno_agro.md` — Programas gubernamentales y subsidios para el sector

**Condiciones:**
- El contenido debe ser realista y basado en política agrícola colombiana real
- Cada documento debe tener encabezados de sección claros para un troceado efectivo
- Los documentos deben estar escritos en español
- Deben incluir números, porcentajes y condiciones específicas (no declaraciones vagas)

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

---

### 3.2 Definición de Entradas

Las entradas de la funcionalidad FIN-Advisor son los datos dinámicos y operativos que se inyectan en el prompt en el momento de cada consulta. Se clasifican en dos categorías: la consulta explícita del usuario y los datos transaccionales extraídos del módulo FIN de Evergreen.

#### E1 — Consulta del Usuario (Prompt de entrada)

Pregunta o solicitud formulada en lenguaje natural por el productor o administrador financiero a través de la interfaz del sistema. Ejemplo: "¿Cómo puedo reducir el impacto del IVA en mi próxima compra de tractor?". Es el disparador de todo el flujo RAG.

**Condiciones:** debe estar redactada en español, referirse a situaciones financieras o tributarias del contexto agropecuario, y ser lo suficientemente específica para permitir una recuperación semántica efectiva en la base de datos vectorial. Una consulta ambigua o muy genérica reduce la calidad de los fragmentos recuperados y, en consecuencia, la calidad de la respuesta generada.

#### E2 — Movimientos Contables del Período

Registros de la entidad Movimientos asociados a las CuentasContables del productor, entregados en formato JSON estructurado desde la API del módulo FIN. Deben corresponder al período fiscal vigente o al rango de fechas relevante para la consulta, e incluir fecha, valor, tipo de movimiento y cuenta asociada.

**Condición:** el volumen de registros debe acotarse al período pertinente para no exceder la ventana de contexto del modelo de lenguaje; si el historial es extenso, se aplica chunking para dividirlo en fragmentos procesables.

#### E3 — Facturas de Venta y Comprobantes de Egreso

Documentos de las entidades FacturaDeVenta y ComprobanteDeEgreso que reflejan las transacciones comerciales recientes del productor, entregados en formato JSON. Deben contener concepto, valor, fecha e identificación del responsable. Son fundamentales para que el LLM calcule la carga tributaria real del período y detecte posibles exenciones o riesgos aplicables.

**Condiciones:** las facturas en estado PENDIENTE y VENCIDA deben priorizarse al construir el contexto del prompt, ya que son determinantes para el análisis de liquidez; el sistema debe ser capaz de calcular el total de cuentas por cobrar sumando los montos pendientes; y al igual que E2, el volumen de documentos debe acotarse al período relevante para no exceder la ventana de contexto del modelo.

#### E4 — Estado de Cuentas Contables

Saldos actuales de las cuentas clasificadas como Activos, Pasivos, Patrimonio, Ingresos, Costos y Gastos, extraídos del módulo FIN en el momento de la consulta.

**Condición:** deben estar actualizados al cierre del último período contable registrado en el sistema para garantizar que el razonamiento del LLM refleje la situación financiera real y no datos desactualizados.

#### Nota sobre separación en el prompt

Las entradas E2, E3 y E4 se inyectan en el prompt aumentado delimitadas mediante marcadores estructurales (`'''...'''` o `{...}`) para que el modelo de lenguaje distinga claramente qué es una instrucción del sistema y qué son datos del usuario, evitando confusiones en el razonamiento.

---

### 3.3 Definición de Salidas

Las salidas de FIN-Advisor son generadas por el LLM a partir del prompt aumentado —que combina la consulta del usuario, los datos transaccionales del módulo FIN y los fragmentos relevantes recuperados de la base de conocimiento— y se clasifican según su naturaleza y destinatario.

#### S1 — Diagnóstico de Flujo de Caja

Texto explicativo en lenguaje natural que presenta el panorama financiero actual del productor, identificando los principales factores que explican su situación, comparando con el período anterior cuando haya datos disponibles, e incluyendo 2 o 3 recomendaciones accionables. Formato: texto estructurado presentado en la interfaz de usuario.

**Condiciones:** debe incluir cifras monetarias reales del productor (no genéricas), explicar causas y no solo listar números, tener una extensión máxima de 400 palabras, y siempre incluir un disclaimer indicando que el análisis se basa en los datos registrados y que se recomienda validación con un profesional contable.

#### S2 — Recomendación de Viabilidad de Inversión

Evaluación estructurada que determina si el productor puede adquirir un activo fijo en el momento de la consulta, considerando su liquidez actual, cuentas por cobrar y por pagar pendientes, y los beneficios tributarios aplicables. Incluye el costo efectivo después de deducciones, el saldo disponible estimado para inversión y un veredicto explícito (VIABLE / NO VIABLE AHORA / VIABLE EN X SEMANAS). Formato: texto estructurado presentado en la interfaz de usuario.

**Condiciones:** debe referenciar los artículos tributarios específicos que fundamentan los beneficios calculados, mostrar el razonamiento del cálculo de forma transparente, y si la inversión no es viable en el momento, sugerir la fecha viable más temprana con base en las proyecciones de flujo de caja.

#### S3 — Explicación de Beneficio Tributario

Respuesta explicativa que detalla un beneficio fiscal aplicable al productor, incluyendo su base legal (número de artículo del Estatuto Tributario o resolución DIAN), las condiciones que el productor debe cumplir para acceder a él, el impacto estimado en términos monetarios cuando sea calculable, y los próximos pasos sugeridos. Formato: texto en la interfaz de usuario.

**Condición:** siempre debe citar el número de artículo específico y explicar las condiciones en lenguaje llano, accesible para un administrador de finca sin formación contable.

#### S4 — Alerta Tributaria hacia el Módulo de Mensajería (JSON)

Cuando el LLM identifica en los datos del productor una situación de riesgo financiero o tributario urgente —como el vencimiento próximo de una obligación o un desequilibrio crítico de liquidez— genera una alerta en formato JSON estructurado para ser consumida directamente por el módulo de Mensajería de Evergreen, el cual la envía al productor vía WhatsApp, SMS o correo electrónico.

**Ejemplo de estructura:**
```json
{
  "tipo": "alerta_tributaria",
  "urgencia": "alta",
  "mensaje": "Vence declaración de IVA en 5 días. Revise su módulo de Finanzas.",
  "canal": "whatsapp"
}
```

**Condición:** esta salida solo se genera cuando la situación detectada supera un umbral de urgencia definido en el prompt del sistema; no se disparan notificaciones por situaciones de bajo riesgo para evitar saturar al productor con alertas irrelevantes.

#### Reglas de Calidad aplicables a TODAS las salidas

1. **Fundamentación:** Toda afirmación factual debe ser trazable a la base de conocimiento o a los datos financieros del usuario; no se admiten cifras generadas sin respaldo.
2. **Transparencia:** Cuando el sistema carece de datos suficientes para responder, debe declararlo explícitamente en lugar de inferir.
3. **Consistencia:** Las cifras monetarias usan siempre COP con separadores de miles (ej. $12.500.000 COP).
4. **Tono:** Técnico pero accesible, orientado a un administrador de finca, no a un contador especializado.
5. **Disclaimers:** Toda salida que pueda interpretarse como asesoría financiera o legal debe incluir un disclaimer de validación profesional.

---

## 4. Propuesta de Arquitectura de la Solución

### 4.1 Nivel 1 — Contexto del Sistema FIN-Advisor

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

### 4.2 Nivel 2 — Contenedores FIN-Advisor

**Capa de Presentación (React.js):** Interfaz de chat donde el usuario ingresa consultas y recibe respuestas. Incluye el dashboard FIN existente y un renderizador de respuestas que formatea tablas, advertencias y calendarios. Comunicación con el backend vía REST API (`POST /api/v1/chat`).

**Capa de Razonamiento (FastAPI + LangChain):** El corazón del sistema. El servidor FastAPI recibe las peticiones HTTP y las pasa al agente ReAct de LangChain, que orquesta el ciclo de razonamiento: analiza la consulta, decide qué herramientas invocar, observa los resultados y sintetiza la respuesta final. Dispone de 7 herramientas: 2 de recuperación de datos y 5 de cálculo especializado.

**Capa de Conocimiento (ChromaDB):** Base de datos vectorial que almacena los embeddings de los documentos legales y guías sectoriales. Usa el modelo `all-MiniLM-L6-v2` para generar embeddings localmente. Organizada en colecciones: `tax_laws` y `sector_guides`.

**Capa de Datos (SQLite):** Base de datos relacional con datos mock que simulan el módulo FIN de EverGreen. Contiene 5 tablas: movimientos, facturas_venta, cuentas_por_pagar, activos_fijos y perfil_productor. Acceso estrictamente de solo lectura.

**Capa de Inferencia (Ollama):** Ejecuta el LLM localmente. Modelo primario: Llama 3 (8B). Modelo de respaldo: Mistral (7B) para máquinas con menos RAM. Expone una API REST en localhost:11434 que LangChain consume nativamente.

### 4.3 Nivel 3 — Componentes FastAPI Backend

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

### 4.4 Nivel 4 — Flujo Dinámico

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

## 5. Conclusiones del Caso de Aplicación

**Frente funcional:** La funcionalidad FIN-Advisor demuestra que el patrón RAG aporta mayor valor en dominios donde coexisten datos privados y cambiantes del usuario —como las transacciones contables del módulo FIN— con conocimiento público especializado y relativamente estable, como la normativa tributaria colombiana. Ninguna de las dos fuentes por sí sola es suficiente para generar asesoría financiera de valor real: sin los datos del productor la respuesta es genérica; sin la normativa, carece de fundamento legal.

**Frente de datos:** La distinción entre base de conocimiento, entradas y salidas no es un ejercicio académico sino una decisión de diseño con consecuencias técnicas directas. Clasificar mal un elemento —por ejemplo, tratar la estructura de centros de costos como una entrada dinámica cuando es una configuración estable— aumenta innecesariamente la carga de tokens en cada consulta y puede comprometer el rendimiento del sistema o superar la ventana de contexto del modelo.

**Frente de arquitectura:** La integración del FIN-Advisor con el módulo de Mensajería de Evergreen mediante salidas en formato JSON estructurado evidencia que en sistemas RAG de uso empresarial las salidas no son únicamente respuestas textuales para humanos, sino que pueden convertirse en eventos que disparan acciones en otros componentes del sistema. Esto exige que el formato de las salidas se diseñe desde la etapa de análisis y no como una decisión de implementación posterior.

**Frente técnico:** RAG resulta más adecuado que el fine-tuning para este caso porque la normativa tributaria colombiana cambia con frecuencia; actualizar la base de conocimiento con nuevos documentos es significativamente más eficiente que reentrenar el modelo. Esta flexibilidad es una ventaja estructural del patrón RAG en contextos regulatorios donde la información evoluciona continuamente.

**Consideraciones personales:** Este ejercicio permitió comprender que diseñar una funcionalidad RAG bien fundamentada requiere entender el negocio con la misma profundidad que la tecnología. La claridad en los elementos de datos —qué entra, en qué formato, con qué condiciones, y qué produce el sistema para quién— es lo que determina si el LLM puede razonar correctamente o si, independientemente de la calidad del modelo, generará respuestas poco útiles o incluso riesgosas en un contexto legal como el tributario.
