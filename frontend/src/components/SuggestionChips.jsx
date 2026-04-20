/**
 * SuggestionChips — Chips de sugerencia para consultas de ejemplo.
 *
 * Muestra 3+ consultas de ejemplo clicables relevantes a finanzas agrícolas.
 * Al hacer clic, se envía la consulta automáticamente mediante el prop onSelect.
 * Solo se muestra cuando no hay mensajes en el hilo de conversación.
 *
 * @param {Object} props
 * @param {Function} props.onSelect - Callback que recibe el texto de la sugerencia seleccionada
 * @param {boolean} props.visible - Si es true, muestra los chips
 */
import React from 'react';

/** Consultas de ejemplo predefinidas */
const SUGGESTIONS = [
  '¿Qué beneficios tributarios tengo?',
  '¿Cómo está mi flujo de caja?',
  '¿Puedo comprar un tractor?',
  '¿Cuándo son mis fechas tributarias?',
];

/**
 * Renderiza los chips de sugerencia.
 *
 * @param {Object} props
 * @param {Function} props.onSelect - Se invoca con el texto del chip al hacer clic
 * @param {boolean} props.visible - Controla la visibilidad de los chips
 * @returns {JSX.Element|null}
 */
function SuggestionChips({ onSelect, visible }) {
  if (!visible) return null;

  return (
    <div className="fin-suggestion-chips" role="group" aria-label="Sugerencias de consulta">
      {SUGGESTIONS.map((text) => (
        <button
          key={text}
          className="fin-chip"
          type="button"
          onClick={() => onSelect(text)}
          aria-label={`Preguntar: ${text}`}
        >
          {text}
        </button>
      ))}
    </div>
  );
}

export default SuggestionChips;
