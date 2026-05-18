"""
review_generator.py  —  Task A
-------------------------------
LLM agent that simulates a user's review for an unseen item.

Given:
  - A user persona (from persona_builder)
  - A product/business description

Produces:
  - A star rating (1–5)
  - A written review in the user's authentic voice
"""

import json
import re
import httpx
from core.persona_builder import _call_claude, persona_to_prompt_fragment

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

REVIEW_SYSTEM_PROMPT = """You are a review simulation engine.
Your task is to write a realistic review EXACTLY as a specific user would write it —
matching their vocabulary, sentence length, emotional tone, topics they care about,
and rating behaviour.

CRITICAL RULES:
1. The review must sound like a real human wrote it, NOT an AI.
2. Match the user's typical review length (verbosity level given).
3. If the user has Nigerian speech markers, naturally weave in Nigerian English
   expressions or Pidgin where appropriate — not forced, just natural.
4. The star rating must reflect the user's rating tendencies AND the item quality.
5. Return ONLY valid JSON. No markdown. No explanation.

Schema:
{
  "stars": <integer 1-5>,
  "review_text": "<the review>",
  "confidence": <float 0-1, how confident you are this matches the user's style>
}"""


def _build_review_prompt(persona_fragment: str, item: dict) -> str:
    """Construct the user-turn prompt for review generation."""
    item_str = json.dumps(item, indent=2)
    return f"""
{persona_fragment}

ITEM TO REVIEW:
{item_str}

Write this user's review of the item above. Consider:
- Would this user actually like this item based on their history?
- What specific aspects would they comment on?
- What would make them rate it higher or lower?

Respond with JSON only.
""".strip()


# ---------------------------------------------------------------------------
# Main agent function
# ---------------------------------------------------------------------------

def generate_review(persona: dict, item: dict) -> dict:
    """
    Simulate a user review for an unseen item.

    Args:
        persona: Output of persona_builder.build_persona()
        item: Dict describing the item, e.g.:
              {
                "name": "The Yellow Chilli",
                "categories": "Nigerian, Restaurants",
                "city": "Abuja",
                "price_range": "$$",
                "description": "Upscale Nigerian cuisine with a modern twist",
                "avg_rating": 4.1,
                "highlights": ["pepper soup", "amala", "good AC"]
              }

    Returns:
        {
          "stars": int,
          "review_text": str,
          "confidence": float,
          "persona_used": str  (summary)
        }
    """
    persona_fragment = persona_to_prompt_fragment(persona)
    prompt = _build_review_prompt(persona_fragment, item)

    raw = _call_claude(REVIEW_SYSTEM_PROMPT, prompt, max_tokens=600)
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Attempt to extract stars and text with regex as fallback
        stars_match = re.search(r'"stars"\s*:\s*(\d)', raw)
        result = {
            "stars": int(stars_match.group(1)) if stars_match else 3,
            "review_text": raw,
            "confidence": 0.4,
            "parse_error": True,
        }

    result["persona_used"] = persona.get("summary", "")
    return result


# ---------------------------------------------------------------------------
# Batch generation (for eval / dataset creation)
# ---------------------------------------------------------------------------

def batch_generate_reviews(persona: dict, items: list[dict]) -> list[dict]:
    """Generate reviews for multiple items for a single user."""
    results = []
    for item in items:
        result = generate_review(persona, item)
        result["item_name"] = item.get("name", "Unknown")
        results.append(result)
    return results
