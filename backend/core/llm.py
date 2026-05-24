"""
llm.py
------
Centralized LLM helper utilizing the Google GenAI SDK (Gemini) under a lightweight
LangChain emulation layer. Enables running existing LangGraph agents with no external
LangChain LLM package requirements, keeping costs free and latency low.
"""

import os
from google import genai
from google.genai import types

class GeminiResponse:
    """Emulates LangChain's AIMessage structure."""
    def __init__(self, content: str):
        self.content = content

class GeminiLangChainWrapper:
    """Emulates LangChain's ChatModel invoke behavior using the official google-genai SDK."""
    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.2):
        self.model_name = model_name
        self.temperature = temperature

    def invoke(self, prompt: str) -> GeminiResponse:
        import time
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        client = genai.Client(api_key=api_key)

        # Detect if prompt requests structured JSON output to optimize generation reliability
        is_json = "json" in prompt.lower() or "schema" in prompt.lower()

        config = types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=1500,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )
        
        if is_json:
            config.response_mime_type = "application/json"

        last_err = None
        for attempt in range(5):
            try:
                response = client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config,
                )
                return GeminiResponse(response.text or "")
            except Exception as e:
                last_err = e
                err_str = str(e).upper()
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    sleep_time = 2 ** attempt + 3
                    print(f"Warning: Gemini API 503 error: {e}. Retrying in {sleep_time}s (attempt {attempt+1}/5)...")
                    time.sleep(sleep_time)
                    continue
                elif "429" in err_str or "EXHAUSTED" in err_str or "LIMIT" in err_str:
                    sleep_time = 35
                    print(f"Warning: Gemini API 429 Rate Limit hit. Sleeping for {sleep_time}s to reset window (attempt {attempt+1}/5)...")
                    time.sleep(sleep_time)
                    continue
                raise
        raise last_err

def get_llm(model_name: str = "gemini-2.5-flash", temperature: float = 0.2) -> GeminiLangChainWrapper:
    """
    Get an emulated LangChain ChatModel targeting Gemini 2.5 Flash.
    """
    return GeminiLangChainWrapper(model_name=model_name, temperature=temperature)
