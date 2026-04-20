---
name: Contexto Carpeta Frontend
description: Guía para la carpeta frontend/ — Interfaz de chat React, componentes, conexión al backend y validación de entrada.
inclusion: fileMatch
fileMatchPattern: 'RAG-FIN-Topicos-Avanzados/frontend/**'
---

# Carpeta `frontend/` — Interfaz de Chat React

## Propósito

Esta carpeta contiene la aplicación React que proporciona la interfaz de chat conversacional para FIN-Advisor. Se ejecuta en `http://localhost:3000` y se comunica con el backend FastAPI.

## Estructura de Componentes

| Componente | Responsabilidad |
|---|---|
| `App.jsx` | Componente raíz; compone todos los componentes, conecta con `POST /api/v1/chat` vía fetch |
| `components/ChatUI.jsx` | Contenedor principal del chat: hilo de mensajes, input de texto (límite suave 500 chars), contador de caracteres, botón de envío |
| `components/SuggestionChips.jsx` | Chips de ejemplo clicables (3+); al hacer clic, pueblan el input y envían automáticamente |
| `components/ResponseRenderer.jsx` | Renderiza respuestas Markdown del agente con `react-markdown`; muestra sources y tools_used |
| `components/Logo.jsx` | Logo FIN-Advisor en esquina superior derecha; placeholder SVG/texto "FIN" si no existe archivo de logo |

## Comunicación con Backend

- **Método:** `fetch` a `POST /api/v1/chat` (HTTP estándar, no SSE).
- **Request:** `{ "message": string, "session_id"?: string }`.
- **Response:** `{ "response": string, "sources": [...], "tools_used": [...] }`.
- **SSE streaming diferido a Fase 2.**

## Manejo de Errores

- Error de red (backend inalcanzable) → mensaje en español: "No se pudo conectar con el servidor. Intenta de nuevo." + botón de reintentar.
- Error HTTP (4xx/5xx) → mensaje en español con contexto + botón de reintentar.
- Indicador de carga visible mientras se espera respuesta.

## Validación de Entrada

- Input vacío o solo whitespace → botón de envío **deshabilitado**.
- Más de 500 caracteres → contador en estado de advertencia (hint suave, envío permitido).
- Más de 2000 caracteres → rechazado por el backend con HTTP 422.

## Presentación Inicial

- Saludo centrado: "Hola, soy FIN Advisor." en una línea y "¿En qué puedo ayudarte hoy?" en la siguiente.
- Chips de sugerencia debajo del input con ejemplos relevantes.

## Restricciones y Convenciones

- Componentes funcionales con JSX (archivos `.jsx`).
- Dependencias: `react`, `react-dom`, `react-markdown`.
- Todo el texto visible al usuario en **español**.
- No usar frameworks CSS externos pesados; estilos en `App.css`.
