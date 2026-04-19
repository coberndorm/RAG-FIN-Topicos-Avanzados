"""
ReAct Agent Reference — FIN-Advisor
====================================

This file contains reference code for setting up the LangChain ReAct agent
with tool calling for the FIN-Advisor project. Use this as a guide when
implementing ``agent/agent_config.py``.

The agent uses the ReAct (Reasoning + Acting) pattern:
  THOUGHT → ACTION → OBSERVATION → THOUGHT → ... → FINAL ANSWER

Max iterations: 5 (prevents infinite loops with 7 tools)
"""

from langchain.agents import create_react_agent, AgentExecutor
from langchain.tools import Tool
from langchain import hub


# ---------------------------------------------------------------------------
# Tool definitions (stubs — replace with actual implementations)
# ---------------------------------------------------------------------------

def query_sqlite(query: str) -> str:
    """Query the user's financial database.

    Args:
        query: Structured query descriptor (query_type + optional period_days).

    Returns:
        JSON string with financial data.
    """
    # Actual implementation in agent/tools/query_evergreen_finances.py
    pass


def retrieve_tax_laws(query: str) -> str:
    """Retrieve relevant tax law fragments from ChromaDB.

    Args:
        query: Natural language search query in Spanish.

    Returns:
        JSON string with top 5 chunks + metadata.
    """
    # Actual implementation in agent/tools/get_tax_knowledge.py
    pass


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------

tools = [
    Tool(
        name="query_financial_data",
        func=query_sqlite,
        description="Query user's financial data from EverGreen FIN database",
    ),
    Tool(
        name="retrieve_tax_laws",
        func=retrieve_tax_laws,
        description="Retrieve Colombian tax laws and agricultural benefit guides",
    ),
    # ... add calculate_vat_discount, calculate_net_liquidity, etc.
]


# ---------------------------------------------------------------------------
# Agent creation with ReAct prompt
# ---------------------------------------------------------------------------

# Option A: Use LangChain Hub's standard ReAct prompt
prompt = hub.pull("hwchase17/react")

# Option B: Use a custom prompt (recommended for FIN-Advisor)
# Load from agent/prompt.md at runtime
custom_prompt = """You're FIN-Advisor, an AI financial assistant for Colombian
agricultural producers. Answer in Spanish.

REACT BEHAVIOR EXAMPLES:

Question: ¿Cuánto impuesto debo pagar por mi cosecha de café?
Thought: I need to retrieve the user's coffee production data and find
         relevant tax laws.
Action: query_financial_data
Action Input: SELECT produccion_cafe FROM finanzas WHERE usuario_id = '123'
Observation: 15,000 kg
Thought: Now I need tax laws for coffee producers.
Action: retrieve_tax_laws
Action Input: impuestos productores café Colombia
Observation: [Chroma results about coffee tax laws]
Thought: Based on the data, for 15,000kg the user owes...
Final Answer: Según sus datos y el Decreto 1234, debe pagar...

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""


def create_fin_advisor_agent(llm, tools: list[Tool]) -> AgentExecutor:
    """Create the FIN-Advisor ReAct agent.

    Args:
        llm: A LangChain-compatible LLM instance (from any provider).
        tools: List of LangChain Tool instances.

    Returns:
        An AgentExecutor ready to invoke.
    """
    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=prompt,  # or custom_prompt
    )

    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,  # Important for robust error handling
    )


# ---------------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Import the provider you want to use
    from llm_provider_reference import create_gemini_llm

    llm = create_gemini_llm()
    agent_executor = create_fin_advisor_agent(llm, tools)

    response = agent_executor.invoke({
        "input": "¿Qué beneficios tributarios tengo como productor de hortalizas?"
    })
    print(response["output"])
