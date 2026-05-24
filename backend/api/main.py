"""
main.py  —  FastAPI application
--------------------------------
Exposes Task A (review generation) and Task B (recommendation) as HTTP endpoints.
Containerised with Docker for submission.

Endpoints:
  POST /generate-review   —  Task A
  POST /recommend         —  Task B (one-shot)
  POST /recommend/refine  —  Task B (multi-turn refinement)
  GET  /health            —  liveness probe
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional

from core.persona_builder import build_persona
from core.review_generator import generate_review, batch_generate_reviews
from core.recommender import recommend_for_user, RecommendationSession
from core.agent import run_agent
from data.yelp_loader import (
    DEMO_USER_PROFILE,
    DEMO_SARAH_PROFILE,
    DEMO_GOODREADS_KATHRYN,
    DEMO_AMAZON_KENNY,
)
from api.dashboard import DASHBOARD_HTML

app = FastAPI(
    title="BCT Hack — LLM Agent API",
    description="User modeling and recommendation agents for DSN x BCT Hackathon 3.0",
    version="1.0.0",
)

# In-memory session store (use Redis for production)
_sessions: dict[str, RecommendationSession] = {}

# In-memory persona cache for real-time speedups
_persona_cache: dict[str, dict] = {}

def _get_persona(profile: dict) -> dict:
    """Helper to extract persona with in-memory caching to save latency/API calls."""
    if "persona" in profile and profile["persona"]:
        return profile["persona"]
    uid = profile.get("user_id", "temp_user")
    if uid in _persona_cache:
        return _persona_cache[uid]
    persona = build_persona(profile)
    _persona_cache[uid] = persona
    return persona


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ReviewInput(BaseModel):
    user_profile: dict = Field(
        ...,
        description="User profile dict (from yelp_loader.build_user_profile or compatible schema)",
        examples=[DEMO_USER_PROFILE],
    )
    item: dict = Field(
        ...,
        description="Item/business to review",
        examples=[{
            "name": "The Yellow Chilli",
            "categories": "Nigerian, Fine Dining",
            "city": "Lagos",
            "price_range": "$$",
            "highlights": ["pepper soup", "ambience", "good service"],
        }],
    )


class BatchReviewInput(BaseModel):
    user_profile: dict
    items: list[dict]


class RecommendInput(BaseModel):
    user_profile: dict = Field(..., description="User profile dict")
    candidates: list[dict] = Field(..., description="List of candidate items to rank")
    user_context: Optional[str] = Field(None, description="Free-text context e.g. 'looking for somewhere quiet'")
    cold_start: Optional[bool] = Field(False, description="Set True if user has sparse history")


class SessionRecommendInput(BaseModel):
    user_profile: dict
    candidates: list[dict]
    user_context: Optional[str] = None
    session_id: Optional[str] = None  # If None, starts a new session


class RefineInput(BaseModel):
    session_id: str
    feedback: str = Field(..., description="User's follow-up feedback on recommendations")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    """Serves the premium glassmorphic interactive web dashboard."""
    return DASHBOARD_HTML


@app.get("/demo-profiles")
def get_demo_profiles():
    """Returns a diverse set of demo profiles (including Goodreads/Amazon cross-domain)."""
    return {
        "tunde": DEMO_USER_PROFILE,
        "sarah": DEMO_SARAH_PROFILE,
        "kathryn": DEMO_GOODREADS_KATHRYN,
        "kenny": DEMO_AMAZON_KENNY,
    }


@app.post("/build-persona")
def build_persona_endpoint(body: dict):
    """
    Builds a taste persona with real-time in-memory caching
    to reduce Gemini LLM API latency to 0ms on subsequent requests.
    """
    try:
        uid = body.get("user_id", "temp_user")
        cached = False
        if uid in _persona_cache:
            persona = _persona_cache[uid]
            cached = True
        else:
            persona = build_persona(body)
            _persona_cache[uid] = persona
        return {"persona": persona, "cached": cached}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok", "model": "gemini-2.5-flash"}


@app.post("/generate-review")
def generate_review_endpoint(body: ReviewInput):
    """
    Task A: Generate a simulated review for a single item.
    Input: user_profile + item description
    Output: star rating + review text in the user's authentic voice
    """
    try:
        persona = _get_persona(body.user_profile)
        result = generate_review(persona, body.item)
        return {
            "user_id": body.user_profile.get("user_id"),
            "item": body.item.get("name"),
            **result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-reviews/batch")
def batch_review_endpoint(body: BatchReviewInput):
    """
    Task A (batch): Generate reviews for multiple items for one user.
    """
    try:
        persona = _get_persona(body.user_profile)
        results = batch_generate_reviews(persona, body.items)
        return {
            "user_id": body.user_profile.get("user_id"),
            "reviews": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend")
def recommend_endpoint(body: RecommendInput):
    """
    Task B (one-shot): Recommend and rank items for a user.
    Input: user_profile + candidate items
    Output: ranked recommendations with personalised reasoning
    """
    try:
        # Build Persona and embed it in user profile (utilizes cache)
        persona = _get_persona(body.user_profile)
        body.user_profile["persona"] = persona
        
        # Invoke the LangGraph ReAct agent
        result = run_agent(
            user_profile=body.user_profile,
            user_context=body.user_context or "",
            candidates_override=body.candidates,
        )
        return {
            "user_id": body.user_profile.get("user_id"),
            **result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend/session")
def session_recommend_endpoint(body: SessionRecommendInput):
    """
    Task B (multi-turn, turn 1): Start or continue a recommendation session.
    Returns a session_id for subsequent /recommend/refine calls.
    """
    import uuid
    try:
        session_id = body.session_id or str(uuid.uuid4())
        persona = _get_persona(body.user_profile)

        session = RecommendationSession(persona)
        _sessions[session_id] = session

        result = session.recommend(body.candidates, body.user_context or "")
        return {
            "session_id": session_id,
            "user_id": body.user_profile.get("user_id"),
            **result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend/refine")
def refine_endpoint(body: RefineInput):
    """
    Task B (multi-turn, turn 2+): Refine recommendations based on user feedback.
    """
    session = _sessions.get(body.session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{body.session_id}' not found.")
    try:
        result = session.refine(body.feedback)
        return {
            "session_id": body.session_id,
            **result,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
