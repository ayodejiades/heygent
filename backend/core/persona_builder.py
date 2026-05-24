"""
persona_builder.py
------------------
Extracts a structured behavioural persona from a user's review history.

The persona captures:
  - Rating tendencies (generous, harsh, balanced)
  - Writing style (verbose, terse, emotional, factual)
  - Topic focus (food, service, ambience, value)
  - Nigerian speech patterns (if detected or requested)
  - Sentiment triggers (what makes them rate high vs low)
"""

import json
import os
import re
from typing import Optional

from google import genai
from google.genai import types

MODEL = "gemini-2.5-flash"


def _get_client():
    """Lazy-init Gemini client."""
    return genai.Client(api_key=os.environ.get("GOOGLE_API_KEY", ""))


def _call_gemini(system: str, user: str, max_tokens: int = 1024) -> str:
    """Thin wrapper around the Google Gemini API with JSON mode."""
    import time

    client = _get_client()
    config = types.GenerateContentConfig(
        system_instruction=system,
        response_mime_type="application/json",
        max_output_tokens=max_tokens,
        temperature=0.1,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    last_err = None
    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=user,
                config=config,
            )
            return response.text
        except Exception as e:
            last_err = e
            err_str = str(e).upper()
            if "503" in err_str or "UNAVAILABLE" in err_str:
                sleep_time = 2 ** attempt + 3
                print(f"Warning: Gemini API 503 error, retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                continue
            elif "429" in err_str or "EXHAUSTED" in err_str or "LIMIT" in err_str:
                sleep_time = 35  # Sleep full 35 seconds to reset window
                print(f"Warning: Gemini API 429 Rate Limit hit. Sleeping for {sleep_time}s to reset window (attempt {attempt+1}/5)...")
                time.sleep(sleep_time)
                continue
            raise
    raise last_err


def _format_review_history(profile: dict) -> str:
    """Format review history into a compact prompt-friendly string."""
    lines = []
    for i, r in enumerate(profile["reviews"][:20], 1):  # cap at 20 for context
        lines.append(
            f"Review {i} | {r['stars']}★ | {r['business_name']} "
            f"({r.get('business_categories','')}) | {r.get('date','')}\n"
            f'"{r["text"][:400]}"'  # truncate very long reviews
        )
    return "\n\n".join(lines)


PERSONA_SYSTEM_PROMPT = """You are a behavioural analyst specialising in user modelling from online reviews.
Your job is to extract a precise, structured persona from a user's review history.

Return ONLY valid JSON — no markdown fences, no preamble. Schema:
{
  "rating_style": "generous|harsh|balanced|polarised",
  "avg_stars_tendency": <float>,
  "verbosity": "terse|moderate|verbose",
  "dominant_topics": [<up to 4 strings>],
  "emotional_tone": "expressive|neutral|analytical|humorous",
  "praise_triggers": [<up to 3 strings: what makes them rate high>],
  "complaint_triggers": [<up to 3 strings: what makes them rate low>],
  "nigerian_speech_markers": <true|false>,
  "vocabulary_signature": [<5 distinctive words/phrases this user uses>],
  "summary": "<2-sentence plain-English persona summary>"
}"""


def build_persona(profile: dict) -> dict:
    """
    Build a behavioural persona dict from a user profile.

    Args:
        profile: Output of yelp_loader.build_user_profile()

    Returns:
        Persona dict with keys defined in PERSONA_SYSTEM_PROMPT schema.
    """
    history_str = _format_review_history(profile)

    user_prompt = f"""
User: {profile['name']}
Total reviews: {profile['review_count']}
Average stars: {profile['average_stars']}
Rating distribution: {profile['rating_distribution']}
Avg review length (words): {profile['avg_review_length_words']}

--- REVIEW HISTORY ---
{history_str}

Extract this user's behavioural persona as JSON.
""".strip()

    raw = _call_gemini(PERSONA_SYSTEM_PROMPT, user_prompt, max_tokens=512)

    # Strip any accidental markdown fences
    raw = re.sub(r"```json|```", "", raw).strip()

    try:
        persona = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: return raw text wrapped in a dict
        persona = {"raw_persona": raw, "parse_error": True}

    persona["user_id"] = profile["user_id"]
    persona["name"] = profile["name"]
    return persona


def persona_to_prompt_fragment(persona: dict) -> str:
    """
    Convert a persona dict into a natural language fragment
    for injecting into review generation / recommendation prompts.
    """
    nigerian_note = (
        "This user naturally uses Nigerian English expressions, Pidgin phrases, "
        "and local cultural references in their writing. "
        if persona.get("nigerian_speech_markers")
        else ""
    )

    vocab = ", ".join(f'"{w}"' for w in persona.get("vocabulary_signature", []))

    return f"""
USER PERSONA:
- Writing style: {persona.get('verbosity', 'moderate')}, {persona.get('emotional_tone', 'neutral')} tone
- Rating tendency: {persona.get('rating_style', 'balanced')} (avg {persona.get('avg_stars_tendency', 3.5)}★)
- Cares most about: {', '.join(persona.get('dominant_topics', ['quality', 'service']))}
- Rates high when: {', '.join(persona.get('praise_triggers', ['good quality']))}
- Rates low when: {', '.join(persona.get('complaint_triggers', ['poor service']))}
- Characteristic vocabulary: {vocab}
{nigerian_note}- Summary: {persona.get('summary', '')}
""".strip()
