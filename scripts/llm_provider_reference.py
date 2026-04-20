"""
LLM Provider Reference — FIN-Advisor
=====================================

This file contains reference code for integrating each supported LLM provider
with LangChain for the FIN-Advisor ReAct agent. Use this as a guide when
implementing the Strategy pattern in ``agent/llm_providers.py``.

Supported providers:
  1. Gemini (Google)       — RECOMMENDED for university project
  2. HuggingFace Inference API
  3. ChatGPT (OpenAI)
  4. Groq                  — Bonus option (fast, free tier)

Cost Analysis (as of 2025):
  - Gemini Flash:   Free tier 1,500 req/day | Paid: $0.35/1M input, $1.05/1M output
  - Gemini Pro:     Free tier 50 req/day    | Paid: $3.50/1M input, $10.50/1M output
  - HuggingFace:    Free tier (rate-limited) | Pay-as-you-go after
  - OpenAI GPT-4o-mini: $0.15/1M input, $0.60/1M output ($5-18 student credit)
  - Groq:           Free tier ~14,000 req/day | Very affordable after

Usage:
  Set LLM_PROVIDER env var to: gemini | huggingface | chatgpt | groq
  Set LLM_API_KEY to the respective API key.
  Set LLM_MODEL_NAME to override the default model for each provider.
"""

import os


# ---------------------------------------------------------------------------
# 1. Gemini (Google) — RECOMMENDED
# ---------------------------------------------------------------------------
# Free tier: 1,500 requests/day (Flash), 50 requests/day (Pro)
# Spanish: Excellent (trained on multilingual corpus, strong LATAM presence)
# Context window: 1 million tokens (massive)
# ReAct support: Native function calling
# Get API key free at: https://makersuite.google.com
#
# pip install langchain-google-genai

def create_gemini_llm(
    api_key: str | None = None,
    model_name: str = "gemini-1.5-flash",
    temperature: float = 0.3,
):
    """Create a Gemini LLM instance for LangChain.

    Args:
        api_key: Google API key. Falls back to GOOGLE_API_KEY or LLM_API_KEY env var.
        model_name: Gemini model identifier.
        temperature: Lower = more deterministic (good for financial advice).

    Returns:
        A ChatGoogleGenerativeAI instance.
    """
    from langchain_google_genai import ChatGoogleGenerativeAI

    key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("LLM_API_KEY")
    if not key:
        raise ValueError(
            "Gemini requires an API key. Set GOOGLE_API_KEY or LLM_API_KEY env var. "
            "Get a free key at https://makersuite.google.com"
        )

    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=key,
    )


# ---------------------------------------------------------------------------
# 2. HuggingFace Inference API
# ---------------------------------------------------------------------------
# Free tier: Rate-limited but available
# Models: meta-llama/Llama-3.1-70B-Instruct, CohereForAI/c4ai-command-r-plus
# Spanish: Llama 3.1 supports Spanish well
# Context window: 8K tokens (Llama 3.1)
# Get token at: https://huggingface.co/settings/tokens
#
# pip install langchain-huggingface

def create_huggingface_llm(
    api_token: str | None = None,
    model_name: str = "meta-llama/Llama-3.1-70B-Instruct",
    temperature: float = 0.3,
    max_new_tokens: int = 1024,
):
    """Create a HuggingFace Inference API LLM instance for LangChain.

    Args:
        api_token: HuggingFace API token. Falls back to HF_TOKEN or LLM_API_KEY env var.
        model_name: HuggingFace model repo ID.
        temperature: Sampling temperature.
        max_new_tokens: Maximum tokens to generate.

    Returns:
        A HuggingFaceEndpoint instance.
    """
    from langchain_huggingface import HuggingFaceEndpoint

    token = api_token or os.getenv("HF_TOKEN") or os.getenv("LLM_API_KEY")
    if not token:
        raise ValueError(
            "HuggingFace requires an API token. Set HF_TOKEN or LLM_API_KEY env var. "
            "Get a free token at https://huggingface.co/settings/tokens"
        )

    return HuggingFaceEndpoint(
        repo_id=model_name,
        huggingfacehub_api_token=token,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
    )


# ---------------------------------------------------------------------------
# 3. ChatGPT (OpenAI)
# ---------------------------------------------------------------------------
# Free tier: $5-18 credit for students (GitHub Student Pack)
# Models: gpt-4o-mini ($0.15/1M input, $0.60/1M output)
# Spanish: Best-in-class
# ReAct support: Industry standard
#
# pip install langchain-openai

def create_chatgpt_llm(
    api_key: str | None = None,
    model_name: str = "gpt-4o-mini",
    temperature: float = 0.3,
):
    """Create an OpenAI ChatGPT LLM instance for LangChain.

    Args:
        api_key: OpenAI API key. Falls back to OPENAI_API_KEY or LLM_API_KEY env var.
        model_name: OpenAI model identifier.
        temperature: Sampling temperature.

    Returns:
        A ChatOpenAI instance.
    """
    from langchain_openai import ChatOpenAI

    key = api_key or os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
    if not key:
        raise ValueError(
            "OpenAI requires an API key. Set OPENAI_API_KEY or LLM_API_KEY env var."
        )

    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        openai_api_key=key,
    )


# ---------------------------------------------------------------------------
# 4. Groq — Bonus option (extremely fast)
# ---------------------------------------------------------------------------
# Free tier: ~14,000 requests/day
# Models: llama-3.3-70b-versatile, mixtral-8x7b-32768
# Speed: ≤400ms responses (very fast)
# Spanish: Llama 3.3 supports Spanish well; Mixtral is multilingual by design
# Get API key at: https://groq.com
#
# pip install langchain-groq

def create_groq_llm(
    api_key: str | None = None,
    model_name: str = "llama-3.3-70b-versatile",
    temperature: float = 0.3,
):
    """Create a Groq LLM instance for LangChain.

    Args:
        api_key: Groq API key. Falls back to GROQ_API_KEY or LLM_API_KEY env var.
        model_name: Groq model identifier.
        temperature: Sampling temperature.

    Returns:
        A ChatGroq instance.
    """
    from langchain_groq import ChatGroq

    key = api_key or os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")
    if not key:
        raise ValueError(
            "Groq requires an API key. Set GROQ_API_KEY or LLM_API_KEY env var. "
            "Get a free key at https://groq.com"
        )

    return ChatGroq(
        model=model_name,
        temperature=temperature,
        groq_api_key=key,
    )
