"""
main.py
-------
FastAPI application for Task B (recEngine).
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
import uuid

from core.persona_builder import build_persona
from core.agent import run_agent

app = FastAPI(
    title="BCT Hack - Recommendation Engine (Task B)",
    description="Agentic recommendation engine built with LangGraph.",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class RecommendInput(BaseModel):
    user_profile: dict = Field(..., description="User profile dict")
    candidates: Optional[List[dict]] = Field(None, description="Optional candidates if skipping vector DB")
    user_context: Optional[str] = Field(None, description="Free-text context e.g. 'looking for somewhere quiet'")

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "service": "recEngine-TaskB"}

@app.post("/recommend")
def recommend_endpoint(body: RecommendInput):
    """
    Task B: Recommend and rank items for a user using LangGraph.
    """
    try:
        # 1. Build Persona (if not already built)
        if "persona" not in body.user_profile:
            persona = build_persona(body.user_profile)
            body.user_profile["persona"] = persona
            
        # 2. Run the LangGraph Agent
        result = run_agent(
            user_profile=body.user_profile,
            user_context=body.user_context or "",
            candidates_override=body.candidates
        )
        
        return {
            "user_id": body.user_profile.get("user_id"),
            **result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
