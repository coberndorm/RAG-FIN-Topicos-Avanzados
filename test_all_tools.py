"""Test each agent tool individually via Groq to verify they all work."""
from dotenv import load_dotenv
load_dotenv()

from agent.agent_config import crear_agente, obtener_config_invocacion

agente = crear_agente()
config = obtener_config_invocacion()

# Test prompts designed to trigger each specific tool
test_cases = [
    ("query_evergreen_finances", "¿Cuál es mi saldo actual en la cuenta?"),
    ("get_tax_knowledge", "¿Qué dice el artículo 258-1 sobre descuento de IVA en bienes de capital?"),
    ("calculate_vat_discount", "Si compro un tractor por $18.000.000 COP, ¿cuánto me descuentan de IVA?"),
    ("calculate_net_liquidity", "Tengo un saldo de $10.000.000, cuentas por cobrar de $5.000.000 y cuentas por pagar de $2.000.000. ¿Cuál es mi liquidez neta?"),
    ("assess_investment_viability", "Con saldo de $12.000.000, cobros pendientes de $8.000.000, deudas de $2.000.000, ¿puedo comprar una máquina de $15.000.000?"),
    ("project_tax_liability", "Si mis ingresos brutos son $50.000.000, deducciones de $12.000.000 y tasa del 25%, ¿cuánto debo de impuestos?"),
    ("calculate_depreciation", "Compré un tractor por $45.000.000 con vida útil de 10 años y han pasado 3 años. ¿Cuál es su valor actual?"),
]

print("=" * 70)
print("TESTING ALL 7 TOOLS WITH GROQ (llama-3.3-70b-versatile)")
print("=" * 70)

results = {}
for tool_name, pregunta in test_cases:
    print(f"\n{'─' * 70}")
    print(f"Tool: {tool_name}")
    print(f"Pregunta: {pregunta}")
    print(f"{'─' * 70}")
    try:
        resultado = agente.invoke(
            {"messages": [("user", pregunta)]},
            config=config,
        )
        respuesta = resultado["messages"][-1].content
        print(f"✅ OK — Respuesta (primeros 200 chars):")
        print(f"   {respuesta[:200]}...")
        results[tool_name] = "PASS"
    except Exception as e:
        print(f"❌ FAIL — {type(e).__name__}: {e}")
        results[tool_name] = f"FAIL: {e}"

print(f"\n{'=' * 70}")
print("SUMMARY")
print(f"{'=' * 70}")
for tool_name, status in results.items():
    icon = "✅" if status == "PASS" else "❌"
    print(f"  {icon} {tool_name}: {status}")
