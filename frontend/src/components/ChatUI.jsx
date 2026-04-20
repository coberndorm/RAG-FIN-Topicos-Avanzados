/**
 * ChatUI — Contenedor principal del chat de FIN-Advisor.
 *
 * Incluye el hilo de mensajes (scrollable), área de entrada de texto
 * con contador de caracteres (límite suave de 500), botón de envío
 * (deshabilitado cuando la entrada está vacía/solo espacios),
 * e indicador de carga (spinner) mientras se espera respuesta.
 *
 * @param {Object} props
 * @param {Function} props.onSendMessage - Callback para enviar un mensaje
 * @param {Array} props.messages - Lista de mensajes del hilo
 * @param {boolean} props.isLoading - Indica si se está esperando respuesta
 */
import React, { useState, useRef, useEffect } from 'react';
import ResponseRenderer from './ResponseRenderer';

/** Límite suave de caracteres para mostrar advertencia */
const CHAR_SOFT_LIMIT = 500;

/**
 * Componente principal del chat.
 *
 * @param {Object} props
 * @param {Function} props.onSendMessage - Se invoca con el texto del mensaje
 * @param {Array<{role: string, content: string, sources?: Array, tools_used?: string[]}>} props.messages
 * @param {boolean} props.isLoading
 * @returns {JSX.Element}
 */
function ChatUI({ onSendMessage, messages, isLoading }) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  /** Scroll automático al último mensaje */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  /** Ajustar altura del textarea automáticamente */
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  /** Verificar si la entrada es solo espacios en blanco */
  const isInputEmpty = input.trim().length === 0;
  const charCount = input.length;
  const isOverLimit = charCount > CHAR_SOFT_LIMIT;

  /**
   * Enviar el mensaje actual.
   */
  const handleSubmit = () => {
    if (isInputEmpty || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  /**
   * Manejar tecla Enter para enviar (Shift+Enter para nueva línea).
   * @param {React.KeyboardEvent} e
   */
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="fin-chat-container">
      {/* Hilo de mensajes */}
      <div className="fin-messages" role="log" aria-label="Hilo de conversación">
        {messages.map((msg, idx) => (
          <div key={idx}>
            {msg.role === 'user' ? (
              <div className="fin-message fin-message-user">
                {msg.content}
              </div>
            ) : (
              <ResponseRenderer
                response={msg.content}
                sources={msg.sources || []}
                tools_used={msg.tools_used || []}
              />
            )}
          </div>
        ))}

        {/* Indicador de carga */}
        {isLoading && (
          <div className="fin-loading" role="status" aria-label="Procesando consulta">
            <div className="fin-spinner" />
            <span>Analizando tu consulta...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Área de entrada */}
      <div className="fin-input-area">
        <div className="fin-input-wrapper">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe tu consulta financiera..."
            rows={1}
            aria-label="Mensaje"
          />
          <div className={`fin-char-counter${isOverLimit ? ' warning' : ''}`}>
            {charCount} / {CHAR_SOFT_LIMIT}
          </div>
        </div>
        <button
          className="fin-send-btn"
          onClick={handleSubmit}
          disabled={isInputEmpty || isLoading}
          aria-label="Enviar mensaje"
          title="Enviar"
        >
          ➤
        </button>
      </div>
    </div>
  );
}

export default ChatUI;
