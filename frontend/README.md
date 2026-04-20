# frontend/ — Interfaz de Chat React

Este directorio contiene la interfaz de usuario de FIN-Advisor, una aplicación **React** que proporciona una experiencia de chat conversacional para productores agrícolas colombianos.

## Contenido

```
frontend/
├── package.json              # Dependencias y scripts npm
├── public/
│   └── index.html            # Plantilla HTML base
└── src/
    ├── index.jsx             # Punto de entrada de React
    ├── App.jsx               # Componente raíz — composición y lógica de comunicación
    ├── App.css               # Estilos globales de la aplicación
    └── components/
        ├── ChatUI.jsx        # Contenedor principal del chat
        ├── SuggestionChips.jsx  # Chips de sugerencia con consultas de ejemplo
        ├── ResponseRenderer.jsx # Renderizado de respuestas en Markdown
        └── Logo.jsx          # Logo de FIN-Advisor (o placeholder)
```

## Componentes

### `App.jsx` — Componente Raíz

Compone todos los componentes de la interfaz y gestiona:
- Comunicación con el backend via `POST /api/v1/chat` usando `fetch`
- Manejo de errores de red y HTTP con mensajes en español y botón de reintento
- Estado global del chat (mensajes, carga, errores)

### `ChatUI.jsx` — Contenedor del Chat

Componente principal de la interfaz conversacional:
- Hilo de mensajes (usuario y asistente)
- Campo de texto con contador de caracteres (límite suave de 500 caracteres)
- Botón de envío deshabilitado cuando la entrada está vacía o solo contiene espacios
- Indicador de carga mientras se espera la respuesta del backend
- Saludo centrado al inicio: "Hola, soy FIN Advisor." / "¿En qué puedo ayudarte hoy?"

### `SuggestionChips.jsx` — Chips de Sugerencia

Muestra 3+ consultas de ejemplo clicables al cargar la interfaz:
- "¿Qué beneficios tributarios tengo?"
- "¿Cómo está mi flujo de caja?"
- "¿Puedo comprar un tractor?"

Al hacer clic en un chip, se llena el campo de texto y se envía automáticamente.

### `ResponseRenderer.jsx` — Renderizado de Respuestas

Renderiza las respuestas del agente en formato Markdown usando `react-markdown`. Muestra también los metadatos de fuentes (`sources`) y herramientas utilizadas (`tools_used`).

### `Logo.jsx` — Logo

Muestra el logo de FIN-Advisor en la esquina superior derecha. Si no existe un archivo de logo, renderiza un placeholder SVG/texto "FIN".

## Dependencias

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `react` | ^18.2.0 | Librería de UI |
| `react-dom` | ^18.2.0 | Renderizado DOM |
| `react-markdown` | ^9.0.1 | Renderizado de Markdown en respuestas |
| `react-scripts` | 5.0.1 | Configuración de Create React App |

## Relación con Otros Módulos

- **`backend/`** — El frontend envía peticiones `POST /api/v1/chat` al backend FastAPI en `http://localhost:8000`
- El backend debe estar ejecutándose para que el chat funcione correctamente
- CORS está configurado en el backend para aceptar peticiones desde `http://localhost:3000`

## Cómo Ejecutar

```bash
# Desde la carpeta frontend/
npm install    # Solo la primera vez
npm start      # Inicia el servidor de desarrollo
```

La interfaz estará disponible en `http://localhost:3000`.

**Prerequisito:** El backend debe estar ejecutándose en `http://localhost:8000` para que las consultas funcionen.

## Scripts Disponibles

| Comando | Descripción |
|---------|-------------|
| `npm start` | Inicia el servidor de desarrollo en el puerto 3000 |
| `npm run build` | Genera el bundle de producción en `build/` |
| `npm test` | Ejecuta las pruebas con Jest |
