/**
 * Punto de entrada principal de la aplicación React de FIN-Advisor.
 *
 * Renderiza el componente raíz App dentro del elemento #root del DOM.
 */
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
