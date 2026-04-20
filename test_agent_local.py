from dotenv import load_dotenv
load_dotenv()

from agent.agent_config import crear_agente, obtener_config_invocacion

agente = crear_agente()
config = obtener_config_invocacion()
messages = []

while True:
    user_input = input("\nTú: ")
    if user_input.lower() in ("exit", "quit", "salir"):
        break
    messages.append(("user", user_input))
    resultado = agente.invoke({"messages": messages}, config=config)
    messages = resultado["messages"]
    print(f"\nAgente: {messages[-1].content}")
