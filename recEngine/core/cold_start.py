"""
cold_start.py
-------------
Handles recommendation logic for users with < 5 reviews.
It intercepts the standard flow to apply demographic priors or fallback strategies.
"""

from dotenv import load_dotenv
load_dotenv()

from typing import List, Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

class ColdStartStrategy(BaseModel):
    clarifying_question: str = Field(
        description="A single, polite, natural question to ask the user to narrow down their tastes."
    )
    inferred_preferences: str = Field(
        description="What we can guess about this user based on their limited data or demographics."
    )
    search_query: str = Field(
        description="A broad, safe search query to fetch universally popular or highly rated items."
    )

def handle_cold_start(user_profile: dict, user_context: str) -> ColdStartStrategy:
    """
    Determine a cold start strategy for a new user.
    """
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.3)
    structured_llm = llm.with_structured_output(ColdStartStrategy)
    
    prompt = PromptTemplate.from_template("""
    You are an expert recommendation agent handling a "cold-start" user.
    This user has very little to no history in our system.
    
    User Info: Name: {name}, Reviews: {review_count}
    Current Context/Query: "{user_context}"
    
    Your task:
    1. Formulate ONE highly effective clarifying question that would help you recommend better items. (e.g. "Do you prefer spicy local food or continental dishes?")
    2. Infer any preferences based on their name, location (if known), or the context they provided.
    3. Formulate a 'search_query' for our vector database to fetch "safe", highly-rated, popular items as a fallback.
    """)
    
    chain = prompt | structured_llm
    
    return chain.invoke({
        "name": user_profile.get("name", "Unknown"),
        "review_count": user_profile.get("review_count", 0),
        "user_context": user_context or "None"
    })
