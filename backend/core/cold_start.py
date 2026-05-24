"""
cold_start.py
-------------
Handles recommendation logic for users with < 5 reviews.
It intercepts the standard flow to apply demographic priors or fallback strategies.
"""

from dotenv import load_dotenv
load_dotenv()

import json
import re
from typing import Any
from pydantic import BaseModel, Field
from core.llm import get_llm

class ColdStartStrategy(BaseModel):
    clarifying_question: str = Field(
        description="A single, polite, natural question to ask the user to narrow down their tastes."
    )
    inferred_preferences: Any = Field(
        description="What we can guess about this user based on their limited data or demographics."
    )
    search_query: str = Field(
        description="A broad, safe search query to fetch universally popular or highly rated items."
    )

def handle_cold_start(user_profile: dict, user_context: str) -> ColdStartStrategy:
    """
    Determine a cold start strategy for a new user.
    """
    llm = get_llm(temperature=0.3)
    
    prompt = """You are an expert recommendation agent handling a "cold-start" user.
This user has very little to no history in our system.

User Info: Name: {name}, Reviews: {review_count}
Current Context/Query: "{user_context}"

Your task:
1. Formulate ONE highly effective clarifying question that would help you recommend better items. (e.g. "Do you prefer spicy local food or continental dishes?")
2. Infer any preferences based on their name, location (if known), or the context they provided.
3. Formulate a 'search_query' for our vector database to fetch "safe", highly-rated, popular items as a fallback.

Return ONLY a valid JSON object matching this schema:
{{
  "clarifying_question": "a clarifying question",
  "inferred_preferences": "what you inferred",
  "search_query": "broad search query"
}}"""
    
    formatted_prompt = prompt.format(
        name=user_profile.get("name", "Unknown"),
        review_count=user_profile.get("review_count", 0),
        user_context=user_context or "None"
    )
    
    response = llm.invoke(formatted_prompt)
    raw_content = response.content.strip()
    
    cleaned = re.sub(r"^```json\s*|\s*```$", "", raw_content, flags=re.MULTILINE | re.IGNORECASE).strip()
    
    try:
        data = json.loads(cleaned)
        return ColdStartStrategy(
            clarifying_question=data.get("clarifying_question", "What kind of restaurants do you like?"),
            inferred_preferences=data.get("inferred_preferences", "None"),
            search_query=data.get("search_query", user_context or "popular restaurants")
        )
    except Exception as e:
        print(f"Warning: Error parsing JSON in cold start: {e}. Raw content: {raw_content}")
        return ColdStartStrategy(
            clarifying_question="What kind of restaurants do you like?",
            inferred_preferences="None",
            search_query=user_context or "popular restaurants"
        )
