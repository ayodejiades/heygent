"""
intent_classifier.py
--------------------
Classifies the user's intent to guide the agent's retrieval strategy.
Uses LangChain and ChatAnthropic.
"""

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate

class IntentClassification(BaseModel):
    intent: str = Field(
        description="Must be one of: 'exploratory', 'goal_directed', 'gift_shopping', 'cold_start'"
    )
    search_query: str = Field(
        description="The optimized semantic search query to use for retrieving candidates based on this intent."
    )
    reasoning: str = Field(
        description="Brief reasoning for why this intent was chosen."
    )

def classify_intent(user_profile: dict, user_context: str) -> IntentClassification:
    """
    Classify the intent of the recommendation request.
    """
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0)
    structured_llm = llm.with_structured_output(IntentClassification)
    
    prompt = PromptTemplate.from_template("""
    You are an intent classification agent for a recommendation system.
    
    User Profile Summary:
    {profile_summary}
    
    User Context/Query:
    "{user_context}"
    
    Determine the user's intent from the following categories:
    - 'goal_directed': User has a specific need (e.g., "looking for a quiet cafe to study")
    - 'exploratory': User is just browsing or wants general recommendations (e.g., "what's good around here?")
    - 'gift_shopping': User is looking for something for someone else
    - 'cold_start': User has almost no history AND provided very little context.
    
    Also, generate an optimized 'search_query' that we can use in a vector database (e.g. ChromaDB) 
    to retrieve items. The query should combine their explicit context with their implicit tastes.
    
    Respond in JSON matching the requested schema.
    """)
    
    # Create a minimal summary so we don't blow up the prompt
    profile_summary = f"Name: {user_profile.get('name')}, " \
                      f"Review count: {user_profile.get('review_count')}. " \
                      f"Rating avg: {user_profile.get('average_stars')}."
                      
    if "persona" in user_profile:
        profile_summary += f"\nTaste Summary: {user_profile['persona'].get('summary', '')}"
        
    chain = prompt | structured_llm
    
    return chain.invoke({
        "profile_summary": profile_summary,
        "user_context": user_context or "No specific context provided. Just recommend something."
    })
