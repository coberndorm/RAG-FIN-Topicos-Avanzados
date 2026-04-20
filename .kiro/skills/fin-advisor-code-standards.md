---
name: FIN-Advisor Code Standards
description: Estándares de código, convenciones de testing, reglas de frontend y documentación para el proyecto FIN-Advisor RAG.
---

# FIN-Advisor — Estándares de Código

## Reglas de Código Python

### Type Hints
- **Obligatorio** en todos los parámetros de función y valores de retorno.
- Usar `Optional[T]` para parámetros opcionales, `list[T]` para listas (Python 3.10+).
- Importar tipos desde `typing` cuando sea necesario.

```python
def calcular_descuento_iva(precio_compra: float, tasa_iva: float = 0.19) -> VATDiscountOutput:
```

### Docstrings (Google-style, en Español)
- **Obligatorio** en todas las funciones y clases públicas.
- Formato Google-style con secciones: descripción, Args, Returns, Raises.
- Todo el contenido del docstring en **español**.

```python
def calcular_liquidez_neta(balance: float, cuentas_por_cobrar: float, cuentas_por_pagar: float) -> NetLiquidityOutput:
    """Calcula la liquidez neta actual y proyectada del productor.

    Args:
        balance: Saldo actual en COP.
        cuentas_por_cobrar: Total de cuentas por cobrar en COP.
        cuentas_por_pagar: Total de cuentas por pagar en COP.

    Returns:
        NetLiquidityOutput con liquidez actual, proyectada y explicación.

    Raises:
        ValueError: Si cuentas_por_cobrar o cuentas_por_pagar son negativos.
    """
```

### PEP 8
- Seguir convenciones PEP 8 para formato, nombres y estructura.
- Nombres de variables y funciones en `snake_case`.
- Nombres de clases en `PascalCase`.
- Constantes en `UPPER_SNAKE_CASE`.
- Líneas máximo 100 caracteres (preferible 88).

### Clases y Herencia
- Usar clases cuando representen entidades o patrones claros.
- Strategy pattern para proveedores LLM (`LLMProvider` base → `GeminiProvider`, `HuggingFaceProvider`, etc.).
- Herencia para modelos de datos compartidos.

### Modelos Pydantic
- Usar `BaseModel` para todos los modelos de entrada/salida de herramientas y API.
- Validación con `Field(...)` incluyendo constraints (`gt=0`, `ge=0`, `le=1`, `min_length`, `max_length`).
- Documentar campos con `description` en español.

```python
class VATDiscountInput(BaseModel):
    """Entrada para el cálculo de descuento IVA."""
    purchase_price: float = Field(..., gt=0, description="Precio de compra en COP")
    vat_rate: float = Field(default=0.19, gt=0, le=1, description="Tasa de IVA")
```

### SQL Parametrizado
- **Siempre** usar consultas parametrizadas con `?` placeholders.
- **Nunca** concatenar strings para construir SQL.
- Acceso **solo lectura** a la base de datos desde herramientas del agente.

```python
cursor.execute("SELECT * FROM movimientos WHERE date >= ? AND type = ?", (fecha_inicio, "INGRESO"))
```

## Requisitos de Testing

### Tests Unitarios (pytest)
- Un archivo de test por módulo funcional en `tests/`.
- Convención de nombres: `test_<modulo>.py` → `tests/test_calculation_tools.py`.
- Fixtures compartidos en `tests/conftest.py` (SQLite temporal, ChromaDB temporal, TestClient).
- Cubrir: cada herramienta de cálculo, cada tipo de consulta financiera, lógica de chunking ETL, endpoints API.

### Tests Basados en Propiedades (hypothesis)
- Usar `hypothesis` para verificar propiedades universales de las herramientas de cálculo.
- Mínimo 100 iteraciones por propiedad (`@settings(max_examples=100)`).
- Cada test incluye comentario: `# Feature: fin-advisor-rag, Property {N}: {título}`.
- Propiedades definidas:
  - **P1:** Invariante aritmético descuento IVA (`discount + effective_cost == purchase_price`)
  - **P2:** Invariante aritmético liquidez neta
  - **P3:** Invariante aritmético viabilidad de inversión
  - **P4:** Invariante aritmético proyección tributaria
  - **P5:** Invariante aritmético depreciación (`current_value >= 0`)
  - **P6:** Rechazo de entradas inválidas (mensaje en español, sin excepciones)
- Generadores inteligentes que restringen al espacio de entrada válido.

### Estructura de Tests

```
tests/
├── conftest.py                    # Fixtures compartidos
├── test_calculation_tools.py      # Unit + property tests (P1-P6)
├── test_query_finances.py         # Unit + property tests (P8)
├── test_etl_pipeline.py           # Unit + property tests (P9, P10)
├── test_get_tax_knowledge.py      # Unit + property tests (P7)
├── test_api_validation.py         # Unit + property tests (P13)
├── test_mock_data_generation.py   # Property tests (P11)
└── test_session_management.py     # Property tests (P14)
```

## Reglas de React / Frontend

- Componentes funcionales con JSX (`.jsx`).
- Estructura: `frontend/src/components/` para componentes reutilizables.
- `react-markdown` para renderizar respuestas del agente.
- Comunicación con backend vía `fetch` a `POST /api/v1/chat`.
- Manejo de errores: mensaje en español + botón de reintentar.
- Validación de entrada: límite suave 500 chars (contador), límite duro 2000 chars (backend).
- Botón de envío deshabilitado cuando input está vacío o solo whitespace.
- Saludo centrado: "Hola, soy FIN Advisor." / "¿En qué puedo ayudarte hoy?"

## Reglas de Documentación

- **Idioma:** Todo en español — READMEs, docstrings, comentarios, mensajes de error.
- **README por carpeta:** Cada directorio principal (`agent/`, `backend/`, `frontend/`, `scripts/`, `knowledge_base/`) tiene su propio `README.md`.
- **README raíz:** Incluye overview, instrucciones de setup, cómo ejecutar cada componente, sección de Knowledge Base Setup.
- **Comentarios de código:** En español, concisos y útiles.
- **Mensajes de error del agente:** Siempre en español con contexto descriptivo.

## Convenciones Docker

- `Dockerfile.frontend`: Build React production bundle, servir en puerto 3000.
- `Dockerfile.backend`: Instalar dependencias Python, ejecutar uvicorn en puerto 8000.
- `docker-compose.yml`: Definir servicios frontend y backend con port mappings y soporte de variables de entorno.
- Docker es **opcional** — el sistema funciona sin Docker vía `npm start` + `uvicorn`.
- Variables de entorno para selección de proveedor LLM y API keys pasadas al contenedor.
