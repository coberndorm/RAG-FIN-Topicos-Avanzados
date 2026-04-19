# FIN-Advisor: Backlog de Fase 2

Funcionalidades diferidas del MVP para implementación futura.

---

## 1. Streaming de Respuestas (SSE)

Entrega progresiva de respuestas del agente al frontend mediante Server-Sent Events.

- Endpoint `POST /api/v1/chat` con parámetro `stream=true`
- Heartbeat periódico para mantener la conexión activa
- Evento final con metadatos (sources, tools_used)
- Evento de error en español si el agente falla durante el procesamiento
- Referencia: Requirement 2 en requirements.md

## 2. FIN Dashboard

Panel visual del módulo EverGreen FIN integrado en el frontend React.

- Vistas de facturas, movimientos, cuentas por pagar, activos fijos
- Componente separado del Chat UI
- Integración con los mismos datos de SQLite que usa el agente
- Referencia: Componente mencionado en 06-ARCHITECTURE.md (proyecto documentación original)

## 3. Soporte Multi-Usuario Concurrente

- Manejo de múltiples sesiones simultáneas
- Autenticación JWT y control de acceso basado en roles
- Persistencia de sesiones entre reinicios del servidor

## 4. Tasas de Cambio Históricas (KB-03)

- Datos USD/COP de los últimos 12 meses
- Relevante para consultas sobre insumos importados
- Almacenamiento en base de datos relacional (no vector store)
- Referencia: KB-03 en 04-KNOWLEDGE-BASE-DEFINITION.md
