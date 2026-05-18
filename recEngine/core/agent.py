"""
agent.py
--------
The LangGraph ReAct agent for Task B.
Coordinates Intent Classification, Retrieval, Reasoning, and Response generation.
"""

from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from core.intent_classifier import classify_intent, IntentClassification
from core.cold_start import handle_cold_start, ColdStartStrategy
from data.indexer import BusinessIndexer

# State for the Graph
class AgentState(TypedDict):
    user_profile: dict
    user_context: str
    is_cold_start: bool
    intent_data: Optional[IntentClassification]
    cold_start_data: Optional[ColdStartStrategy]
    search_query: str
    retrieved_candidates: List[Dict[str, Any]]
    scored_candidates: List[Dict[str, Any]]
    reasoning_trace: str
    final_recommendations: List[Dict[str, Any]]

# --- Nodes ---

def analyze_intent_node(state: AgentState) -> AgentState:
    """Determine if this is a cold start or normal flow, and extract intent + search query."""
    profile = state["user_profile"]
    context = state["user_context"]
    
    # We define cold start as < 5 reviews
    if profile.get("review_count", 0) < 5 or state.get("is_cold_start", False):
        state["is_cold_start"] = True
        cold_data = handle_cold_start(profile, context)
        state["cold_start_data"] = cold_data
        state["search_query"] = cold_data.search_query
    else:
        state["is_cold_start"] = False
        intent_data = classify_intent(profile, context)
        state["intent_data"] = intent_data
        state["search_query"] = intent_data.search_query
        
    return state

def retrieve_node(state: AgentState) -> AgentState:
    """Retrieve candidates from ChromaDB using the search query."""
    indexer = BusinessIndexer()
    candidates = indexer.retrieve(state["search_query"], n_results=10)
    
    # If Chroma is empty (e.g. hackathon demo without indexing), fallback to empty list
    state["retrieved_candidates"] = candidates
    return state

class ScoredCandidate(BaseModel):
    item_id: str
    predicted_stars: float
    why_this_user: str
    confidence: float

class ReasoningResult(BaseModel):
    reasoning_trace: str
    scored_items: List[ScoredCandidate]

def reason_and_score_node(state: AgentState) -> AgentState:
    """Reason about the candidates against the user's persona and score them."""
    if not state["retrieved_candidates"]:
        state["reasoning_trace"] = "No candidates retrieved from database."
        state["scored_candidates"] = []
        return state
        
    llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.1)
    structured_llm = llm.with_structured_output(ReasoningResult)
    
    persona = state["user_profile"].get("persona", {})
    
    prompt = PromptTemplate.from_template("""
    You are the reasoning core of a recommendation agent.
    
    User Profile:
    Name: {name}
    Taste Persona: {persona}
    Current Context: "{context}"
    
    Candidates:
    {candidates}
    
    Step 1: Reason step-by-step (Chain of Thought) about why this user would like or dislike these candidates.
    Step 2: Score each candidate (predicted_stars 1-5, confidence 0-1) and write a 1-2 sentence justification tailored to this user ('why_this_user').
    
    Return the result in JSON matching the schema.
    """)
    
    import json
    # Minify candidates to fit in context easily
    minified_candidates = []
    for c in state["retrieved_candidates"]:
        minified_candidates.append({
            "id": c.get("business_id"),
            "name": c.get("name"),
            "categories": c.get("categories"),
            "stars": c.get("stars")
        })
        
    result = structured_llm.invoke({
        "name": state["user_profile"].get("name"),
        "persona": json.dumps(persona),
        "context": state["user_context"],
        "candidates": json.dumps(minified_candidates)
    })
    
    state["reasoning_trace"] = result.reasoning_trace
    
    # Merge scores back with full candidate data
    scored_full = []
    for score in result.scored_items:
        full_biz = next((c for c in state["retrieved_candidates"] if c.get("business_id") == score.item_id), None)
        if full_biz:
            scored_full.append({
                "item_id": score.item_id,
                "item_name": full_biz.get("name"),
                "predicted_stars": score.predicted_stars,
                "why_this_user": score.why_this_user,
                "confidence": score.confidence,
                "raw_data": full_biz
            })
            
    # Rank by predicted stars (descending)
    scored_full.sort(key=lambda x: x["predicted_stars"], reverse=True)
    state["scored_candidates"] = scored_full
    
    return state

def format_response_node(state: AgentState) -> AgentState:
    """Format the final output to match the hackathon API spec."""
    final = []
    for i, c in enumerate(state["scored_candidates"]):
        final.append({
            "rank": i + 1,
            "item_id": c["item_id"],
            "item_name": c["item_name"],
            "predicted_stars": c["predicted_stars"],
            "why_this_user": c["why_this_user"],
            "confidence": c["confidence"]
        })
        
    state["final_recommendations"] = final
    return state

# --- Build the Graph ---
workflow = StateGraph(AgentState)

workflow.add_node("analyze_intent", analyze_intent_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("reason_and_score", reason_and_score_node)
workflow.add_node("format_response", format_response_node)

workflow.set_entry_point("analyze_intent")
workflow.add_edge("analyze_intent", "retrieve")
workflow.add_edge("retrieve", "reason_and_score")
workflow.add_edge("reason_and_score", "format_response")
workflow.add_edge("format_response", END)

recommendation_app = workflow.compile()

def run_agent(user_profile: dict, user_context: str = "", candidates_override: List[dict] = None) -> dict:
    """Helper to run the graph and extract the response."""
    initial_state = {
        "user_profile": user_profile,
        "user_context": user_context,
        "is_cold_start": False,
        "intent_data": None,
        "cold_start_data": None,
        "search_query": "",
        "retrieved_candidates": candidates_override or [], # If passed directly, skips Chroma
        "scored_candidates": [],
        "reasoning_trace": "",
        "final_recommendations": []
    }
    
    # If candidates are passed manually, we can skip retrieval for testing
    if candidates_override:
        # Override the graph temporarily if needed, but for now we'll let retrieve run,
        # so let's actually just run it standard.
        pass

    final_state = recommendation_app.invoke(initial_state)
    
    response = {
        "reasoning": final_state["reasoning_trace"],
        "recommendations": final_state["final_recommendations"]
    }
    
    if final_state.get("cold_start_data"):
        response["clarifying_question"] = final_state["cold_start_data"].clarifying_question
        
    return response
