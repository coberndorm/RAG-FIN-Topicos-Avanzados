/**
 * Logo — Componente del logo de FIN-Advisor.
 *
 * Muestra el logo en la esquina superior derecha.
 * Si no existe un archivo de logo, renderiza un placeholder SVG/texto "FIN".
 */
import React from 'react';

/**
 * Renderiza el logo de FIN-Advisor.
 * Usa un placeholder circular con el texto "FIN" como diseño limpio por defecto.
 *
 * @returns {JSX.Element} Componente del logo
 */
function Logo() {
  return (
    <div className="fin-logo" aria-label="FIN-Advisor logo">
      <div className="fin-logo-placeholder">
        <svg
          width="48"
          height="48"
          viewBox="0 0 48 48"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          role="img"
          aria-label="FIN-Advisor"
        >
          <circle cx="24" cy="24" r="24" fill="#2e7d32" />
          <text
            x="24"
            y="26"
            textAnchor="middle"
            dominantBaseline="middle"
            fill="white"
            fontSize="14"
            fontWeight="700"
            fontFamily="Segoe UI, Roboto, sans-serif"
            letterSpacing="1"
          >
            FIN
          </text>
        </svg>
      </div>
    </div>
  );
}

export default Logo;
