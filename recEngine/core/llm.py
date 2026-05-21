"""
llm.py
------
Centralized LLM helper to configure OpenRouter for all agent tasks.
Allows switching models and providers easily.
"""

import os
from langchain_openai import ChatOpenAI

# OpenRouter Free Models:
# - "meta-llama/llama-3-8b-instruct:free"
# - "google/gemma-2-9b-it:free"
# - "qwen/qwen-2-7b-instruct:free"
# - "mistralai/mistral-7b-instruct:free"
DEFAULT_MODEL = "openrouter/free"

def get_llm(model_name: str = DEFAULT_MODEL, temperature: float = 0.2):
    """
    Get a LangChain ChatOpenAI instance configured for OpenRouter.
    """
    # Look for OPENROUTER_API_KEY, fallback to OPENAI_API_KEY, fallback to "free"
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    
    if not api_key:
        # Note: OpenRouter requires an API key even for free models, 
        # but you can generate one for free on openrouter.ai without a credit card.
        raise ValueError(
            "Missing OpenRouter API Key. Please set the OPENROUTER_API_KEY environment variable. "
            "You can create a free key on https://openrouter.ai/"
        )
        
    return ChatOpenAI(
        model=model_name,
        openai_api_key=api_key,
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=temperature,
        default_headers={
            "HTTP-Referer": "https://github.com/ayodejiades/heygent",
            "X-Title": "Heygent Recommendation Agent"
        }
    )
