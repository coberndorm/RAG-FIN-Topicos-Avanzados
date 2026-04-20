"""Quick test: invoke the FIN-Advisor agent using Groq as LLM provider."""
import os
from dotenv import load_dotenv

load_dotenv()

from agent.agent_config import crear_agente, obtener_config_invocacion

agente = crear_agente()
config = obtener_config_invocacion()

# Single test invocation
pregunta = "¿Cuál es mi saldo actual?"
print(f"Pregunta: {pregunta}\n")

resultado = agente.invoke(
    {"messages": [("user", pregunta)]},
    config=config,
)

respuesta = resultado["messages"][-1].content
print(f"Respuesta del agente:\n{respuesta}")
