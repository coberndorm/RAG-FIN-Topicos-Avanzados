/**
 * ResponseRenderer — Renderizador de respuestas del agente.
 *
 * Renderiza respuestas en formato Markdown usando react-markdown.
 * Muestra metadatos de fuentes (article_number, source_document)
 * y herramientas utilizadas (tools_used).
 *
 * @param {Object} props
 * @param {string} props.response - Texto de respuesta del agente (Markdown)
 * @param {Array} props.sources - Lista de fuentes referenciadas
 * @param {Array} props.tools_used - Lista de herramientas invocadas
 */
import React from 'react';
import ReactMarkdown from 'react-markdown';

/**
 * Renderiza la respuesta del agente con formato Markdown y metadatos.
 *
 * @param {Object} props
 * @param {string} props.response - Respuesta en Markdown
 * @param {Array<{article_number?: string, source_document: string, topic_tags?: string[]}>} props.sources
 * @param {string[]} props.tools_used
 * @returns {JSX.Element}
 */
function ResponseRenderer({ response, sources, tools_used }) {
  const hasSources = sources && sources.length > 0;
  const hasTools = tools_used && tools_used.length > 0;

  return (
    <div className="fin-response">
      <div className="fin-message fin-message-bot">
        <ReactMarkdown>{response}</ReactMarkdown>

        {(hasSources || hasTools) && (
          <div className="fin-response-sources">
            {hasSources && (
              <details>
                <summary>📄 Fuentes consultadas ({sources.length})</summary>
                {sources.map((src, idx) => (
                  <div key={idx} className="fin-source-item">
                    {src.article_number && (
                      <span><strong>Art. {src.article_number}</strong> — </span>
                    )}
                    <span>{src.source_document}</span>
                  </div>
                ))}
              </details>
            )}

            {hasTools && (
              <div className="fin-tools-used">
                <span style={{ fontSize: '0.78rem', marginRight: 4 }}>🔧</span>
                {tools_used.map((tool) => (
                  <span key={tool} className="fin-tool-tag">{tool}</span>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ResponseRenderer;
