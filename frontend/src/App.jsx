/**
 * App — Componente raíz de la aplicación FIN-Advisor.
 *
 * Compone todos los componentes (Logo, ChatUI, SuggestionChips,
 * ResponseRenderer) y gestiona el estado de la aplicación.
 * Se conecta al backend via POST /api/v1/chat.
 * Maneja errores de red/HTTP con mensajes en español y botón de reintento.
 */
import React, { useState, useCallback } from 'react';
import Logo from './components/Logo';
import ChatUI from './components/ChatUI';
import SuggestionChips from './components/SuggestionChips';
import './App.css';

/** URL del endpoint del backend */
const API_URL = 'http://localhost:8000/api/v1/chat';

/**
 * App — Punto de entrada principal de FIN-Advisor.
 *
 * Gestiona el estado de mensajes, carga y errores.
 * Conecta los componentes de chat con el backend.
 *
 * @returns {JSX.Element}
 */
function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  /** Guardar el último mensaje para reintento */
  const [lastMessage, setLastMessage] = useState(null);

  /**
   * Enviar un mensaje al backend y procesar la respuesta.
   * @param {string} text - Texto del mensaje del usuario
   */
  const handleSendMessage = useCallback(async (text) => {
    setError(null);
    setLastMessage(text);

    // Agregar mensaje del usuario al hilo
    const userMsg = { role: 'user', content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });

      if (!res.ok) {
        throw new Error(`Error del servidor (${res.status})`);
      }

      const data = await res.json();

      // Agregar respuesta del agente al hilo
      const botMsg = {
        role: 'assistant',
        content: data.response || 'Sin respuesta del agente.',
        sources: data.sources || [],
        tools_used: data.tools_used || [],
      };
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      const errorText = err.message.includes('Failed to fetch')
        ? 'No se pudo conectar con el servidor. Verifica que el backend esté activo.'
        : `Error al procesar tu consulta: ${err.message}`;
      setError(errorText);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Reintentar el último mensaje fallido.
   */
  const handleRetry = useCallback(() => {
    if (lastMessage) {
      // Remover el último mensaje del usuario que falló
      setMessages((prev) => prev.slice(0, -1));
      handleSendMessage(lastMessage);
    }
  }, [lastMessage, handleSendMessage]);

  /**
   * Manejar selección de chip de sugerencia (auto-submit).
   * @param {string} text - Texto de la sugerencia
   */
  const handleChipSelect = useCallback((text) => {
    handleSendMessage(text);
  }, [handleSendMessage]);

  const hasMessages = messages.length > 0;

  return (
    <div className="fin-advisor-app">
      <Logo />

      {/* Saludo centrado — solo cuando no hay mensajes */}
      {!hasMessages && !isLoading && (
        <div className="fin-greeting">
          <p className="fin-greeting-line1">Hola, soy FIN Advisor.</p>
          <p className="fin-greeting-line2">¿En qué puedo ayudarte hoy?</p>
        </div>
      )}

      {/* Chips de sugerencia — solo cuando no hay mensajes */}
      <SuggestionChips
        onSelect={handleChipSelect}
        visible={!hasMessages && !isLoading}
      />

      {/* Chat UI — siempre visible cuando hay mensajes o carga */}
      {(hasMessages || isLoading) && (
        <ChatUI
          onSendMessage={handleSendMessage}
          messages={messages}
          isLoading={isLoading}
        />
      )}

      {/* Error con botón de reintento */}
      {error && (
        <div className="fin-error" role="alert">
          <p className="fin-error-text">{error}</p>
          <button className="fin-retry-btn" onClick={handleRetry} type="button">
            Reintentar
          </button>
        </div>
      )}

      {/* Input area cuando no hay mensajes (estado inicial) */}
      {!hasMessages && !isLoading && (
        <InitialInput onSend={handleSendMessage} />
      )}
    </div>
  );
}

/**
 * InitialInput — Área de entrada para el estado inicial (sin mensajes).
 *
 * Muestra un campo de texto con contador de caracteres y botón de envío
 * en la parte inferior de la pantalla de bienvenida.
 *
 * @param {Object} props
 * @param {Function} props.onSend - Callback para enviar el mensaje
 * @returns {JSX.Element}
 */
function InitialInput({ onSend }) {
  const [input, setInput] = React.useState('');
  const isInputEmpty = input.trim().length === 0;
  const charCount = input.length;
  const isOverLimit = charCount > 500;

  const handleSubmit = () => {
    if (isInputEmpty) return;
    onSend(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="fin-input-area">
      <div className="fin-input-wrapper">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe tu consulta financiera..."
          rows={1}
          aria-label="Mensaje"
        />
        <div className={`fin-char-counter${isOverLimit ? ' warning' : ''}`}>
          {charCount} / 500
        </div>
      </div>
      <button
        className="fin-send-btn"
        onClick={handleSubmit}
        disabled={isInputEmpty}
        aria-label="Enviar mensaje"
        title="Enviar"
      >
        ➤
      </button>
    </div>
  );
}

export default App;
