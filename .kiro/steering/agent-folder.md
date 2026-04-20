---
name: Contexto Carpeta Agent
description: Guía para la carpeta agent/ — Agente ReAct LangChain, prompt del sistema, herramientas y abstracción de proveedores LLM.
inclusion: fileMatch
fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/agent/**'
---

# Carpeta `agent/` — Agente ReAct LangChain

## Propósito

Esta carpeta contiene el agente de razonamiento ReAct implementado con LangChain, el prompt del sistema en Markdown, las 7 herramientas del agente y la abstracción de proveedores LLM mediante Strategy pattern.

## Layout de Módulos

| Archivo | Responsabilidad |
|---|---|
| `agent_config.py` | Creación del agente ReAct vía `create_react_agent`, registro de herramientas, carga del prompt |
| `llm_providers.py` | Strategy pattern: interfaz base + proveedores concretos (HuggingFace, Gemini, ChatGPT, Groq) |
| `prompt.md` | Prompt del sistema en español (Markdown, cargado en runtime) |
| `tools/__init__.py` | Exporta las 7 herramientas como definiciones LangChain-compatible |
| `tools/get_tax_knowledge.py` | Búsqueda semántica en ChromaDB (retrieval) |
| `tools/query_evergreen_finances.py` | Consultas SQL parametrizadas a SQLite (retrieval) |
| `tools/calculate_vat_discount.py` | Cálculo de descuento IVA |
| `tools/calculate_net_liquidity.py` | Cálculo de liquidez neta |
| `tools/assess_investment_viability.py` | Evaluación de viabilidad de inversión |
| `tools/project_tax_liability.py` | Proyección de obligación tributaria |
| `tools/calculate_depreciation.py` | Cálculo de depreciación de activos fijos |

## Relaciones con Otros Módulos

- **Backend (`backend/routes.py`)** importa y ejecuta el agente configurado en `agent_config.py`.
- **ChromaDB** es accedido por `get_tax_knowledge.py` para búsqueda semántica (solo lectura).
- **SQLite (`fin.db`)** es accedido por `query_evergreen_finances.py` con SQL parametrizado (solo lectura).
- **LLM Provider** es instanciado por `llm_providers.py` leyendo variables de entorno (`LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL_NAME`).

## Restricciones y Convenciones

- Máximo **5 iteraciones** de razonamiento por consulta (`max_iterations=5`).
- `handle_parsing_errors=True` para manejo robusto de errores.
- Todas las herramientas de cálculo son **determinísticas** (no invocan el LLM).
- Herramientas de retrieval tienen acceso **solo lectura** a sus fuentes de datos.
- Modelos de entrada/salida definidos con **Pydantic** y validación con `Field`.
- Mensajes de error siempre en **español** con contexto descriptivo.
- Docstrings en español, formato Google-style.
- Type hints obligatorios en todos los parámetros y retornos.
