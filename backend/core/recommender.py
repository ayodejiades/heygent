"""
recommender.py  —  Task B
--------------------------
Agentic recommendation engine that reasons before recommending.

Pipeline:
  1. Load user persona
  2. Retrieve candidate items (vector search or catalogue scan)
  3. Reason about fit: why would THIS user like THIS item?
  4. Rank and return top-N with explanations

Handles:
  - Normal case: user has rich history
  - Cold-start: new user with little/no history
  - Cross-domain: recommend across categories (e.g. book → restaurant)
  - Multi-turn: refine recommendations based on follow-up feedback
"""

import json
import os
import re
from core.persona_builder import _call_gemini, persona_to_prompt_fragment
from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

RECOMMENDER_SYSTEM_PROMPT = """You are an expert personalised recommendation agent.
Your job is to recommend items that a specific user will genuinely love —
not generic "top picks" but items tailored to their unique taste profile.

You REASON before you recommend:
1. What does this user demonstrably care about?
2. Which candidates match those values?
3. Why would THIS user specifically like each item?

CRITICAL RULES:
- Rank by predicted user satisfaction, not item quality alone.
- For Nigerian users, factor in local relevance and cultural fit.
- Provide honest, specific reasoning — not generic praise.
- Return ONLY valid JSON. No markdown. No explanation outside JSON.

Schema:
{
  "reasoning": "<your 3-5 sentence reasoning chain before recommending>",
  "recommendations": [
    {
      "rank": 1,
      "item_id": "<id from candidates>",
      "item_name": "<name>",
      "predicted_stars": <float 1-5>,
      "why_this_user": "<1-2 sentence personalised explanation>",
      "confidence": <float 0-1>
    }
  ]
}"""

COLD_START_SYSTEM_PROMPT = """You are a recommendation agent handling a cold-start scenario —
the user has little or no review history.

Use whatever signals you have:
- Demographics or stated preferences
- Item popularity and critical reception
- Cross-domain signals (e.g. someone who reads thrillers might like action films)
- Conservative defaults that minimise downside risk

Return ONLY valid JSON using the same schema as normal recommendations.
Be honest in your reasoning about the cold-start limitation."""


# ---------------------------------------------------------------------------
# Multi-turn conversation state
# ---------------------------------------------------------------------------

class RecommendationSession:
    """Maintains conversation history for multi-turn recommendation refinement."""

    def __init__(self, persona: dict):
        self.persona = persona
        self.persona_fragment = persona_to_prompt_fragment(persona)
        self.history: list[dict] = []  # {"role": ..., "content": ...}
        self.last_recommendations: list[dict] = []

    def _build_messages(self, new_user_message: str) -> list[dict]:
        messages = list(self.history)
        messages.append({"role": "user", "content": new_user_message})
        return messages

    def recommend(self, candidates: list[dict], user_context: str = "") -> dict:
        """First-turn recommendation."""
        candidates_str = json.dumps(candidates, indent=2)
        prompt = f"""
{self.persona_fragment}

USER CONTEXT: {user_context or 'No additional context provided.'}

CANDIDATE ITEMS:
{candidates_str}

Reason through these candidates and return your ranked recommendations as JSON.
""".strip()

        self.history.append({"role": "user", "content": prompt})

        raw = _gemini_multi_turn(RECOMMENDER_SYSTEM_PROMPT, self.history)
        raw = re.sub(r"```json|```", "", raw).strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {"reasoning": raw, "recommendations": [], "parse_error": True}

        self.last_recommendations = result.get("recommendations", [])
        self.history.append({"role": "model", "content": raw})
        return result

    def refine(self, user_feedback: str) -> dict:
        """Refine recommendations based on user follow-up (multi-turn)."""
        refinement_prompt = f"""
The user responded to your recommendations with this feedback:
"{user_feedback}"

Adjust your recommendations accordingly. Keep the same JSON schema.
Consider what this feedback reveals about the user's preferences.
""".strip()

        self.history.append({"role": "user", "content": refinement_prompt})
        raw = _gemini_multi_turn(RECOMMENDER_SYSTEM_PROMPT, self.history)
        raw = re.sub(r"```json|```", "", raw).strip()

        try:
            result = json.loads(raw)
        except json.JSONDecodeError:
            result = {"reasoning": raw, "recommendations": [], "parse_error": True}

        self.last_recommendations = result.get("recommendations", [])
        self.history.append({"role": "model", "content": raw})
        return result


def _gemini_multi_turn(system: str, messages: list[dict]) -> str:
    """Call Gemini with a full message history for multi-turn support."""
    import time

    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY", ""))

    # Convert messages to Gemini Content format
    # Gemini uses "user" and "model" roles (not "assistant")
    contents = []
    for msg in messages:
        role = "model" if msg["role"] in ("assistant", "model") else "user"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part(text=msg["content"])]
            )
        )

    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
        max_output_tokens=1024,
        temperature=0.1,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    last_err = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=config,
            )
            return response.text
        except Exception as e:
            last_err = e
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                time.sleep(2 ** attempt)
                continue
            raise
    raise last_err


# ---------------------------------------------------------------------------
# Simple one-shot recommend (no session needed)
# ---------------------------------------------------------------------------

def recommend_for_user(
    persona: dict,
    candidates: list[dict],
    user_context: str = "",
    cold_start: bool = False,
) -> dict:
    """
    One-shot recommendation call.

    Args:
        persona: From persona_builder.build_persona()
        candidates: List of item dicts, each with at least 'id' and 'name'
        user_context: Any extra context ("looking for somewhere quiet to read")
        cold_start: If True, use cold-start prompt with softer assumptions

    Returns:
        Dict with 'reasoning' and 'recommendations' list
    """
    system = COLD_START_SYSTEM_PROMPT if cold_start else RECOMMENDER_SYSTEM_PROMPT
    persona_fragment = persona_to_prompt_fragment(persona)

    prompt = f"""
{persona_fragment}

USER CONTEXT: {user_context or 'None provided.'}

CANDIDATE ITEMS:
{json.dumps(candidates, indent=2)}

{'NOTE: This is a cold-start scenario. The user has limited review history.' if cold_start else ''}

Return your ranked recommendations as JSON.
""".strip()

    raw = _call_gemini(system, prompt, max_tokens=1024)
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"reasoning": raw, "recommendations": [], "parse_error": True}
