"""
test_agent.py
-------------
Comprehensive smoke test for HeyGent agents (Task A & Task B).
Verifies Persona Builder, Review Generator, LSA Indexing, and the LangGraph ReAct Agent.
"""

import os
import sys
import json
import warnings

# Ignore deprecation warnings
warnings.filterwarnings('ignore')

# Add heygent to system path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from data.yelp_loader import DEMO_USER_PROFILE, DEMO_REVIEWS
from core.persona_builder import build_persona
from core.review_generator import generate_review
from data.indexer import BusinessIndexer
from core.agent import run_agent

def run_tests():
    print("=" * 70)
    print("🚀 STARTING HEYGENT AGENTS SMOKE TESTS")
    print("=" * 70)

    # -------------------------------------------------------------------------
    # STEP 1: Task A - Persona Building
    # -------------------------------------------------------------------------
    print("\n[STEP 1] Running Task A: Persona Builder...")
    persona = build_persona(DEMO_USER_PROFILE)
    print("✅ Persona Builder succeeded!")
    print(json.dumps(persona, indent=2))

    # -------------------------------------------------------------------------
    # STEP 2: Task A - Review Generation
    # -------------------------------------------------------------------------
    print("\n[STEP 2] Running Task A: Review Generator...")
    test_item = {
        "name": "The Yellow Chilli",
        "categories": "Nigerian, Fine Dining, Restaurants",
        "city": "Lagos",
        "price_range": "$$",
        "highlights": ["pepper soup", "ambience", "good service"],
    }
    simulated = generate_review(persona, test_item)
    print("✅ Review Generator succeeded!")
    print(json.dumps(simulated, indent=2))

    # -------------------------------------------------------------------------
    # STEP 3: Task B - ChromaDB Indexing and Semantic Retrieval
    # -------------------------------------------------------------------------
    print("\n[STEP 3] Running Task B: ChromaDB Custom LSA Indexer...")
    indexer = BusinessIndexer()
    
    # Let's index some mock businesses
    businesses = [
        {
            "business_id": "biz_1",
            "name": "Mama Cass Restaurant",
            "categories": "Nigerian, African, Restaurants",
            "city": "Lagos",
            "stars": 4.5,
            "attributes": {"WiFi": "Yes", "AC": "Yes", "PowerBackup": "Yes"}
        },
        {
            "business_id": "biz_2",
            "name": "Spice Garden",
            "categories": "African, Restaurants",
            "city": "Lagos",
            "stars": 2.5,
            "attributes": {"AC": "Yes"}
        },
        {
            "business_id": "biz_3",
            "name": "The Suya Spot",
            "categories": "Street Food, Restaurants",
            "city": "Lagos",
            "stars": 4.0,
            "attributes": {"OutdoorSeating": "Yes"}
        },
        {
            "business_id": "biz_4",
            "name": "Slow-paced Italian Cafe",
            "categories": "Cafe, Italian, Restaurants",
            "city": "Lagos",
            "stars": 4.2,
            "attributes": {"Quiet": "Yes", "WiFi": "Yes"}
        }
    ]
    
    print("Indexing mock businesses...")
    indexer.index_businesses(businesses)
    print("Retrieving recommendations for 'looking for spicy suya'...")
    retrieved = indexer.retrieve("spicy suya local food", n_results=2)
    print("✅ Indexing & Retrieval succeeded!")
    print(f"Retrieved {len(retrieved)} candidates:")
    for c in retrieved:
        print(f" - {c['name']} (Stars: {c['stars']}, Categories: {c['categories']})")

    # -------------------------------------------------------------------------
    # STEP 4: Task B - LangGraph ReAct Agent
    # -------------------------------------------------------------------------
    print("\n[STEP 4] Running Task B: LangGraph ReAct Recommendation Agent...")
    
    # We will embed the persona in the user profile
    profile = DEMO_USER_PROFILE.copy()
    profile["persona"] = persona
    
    context = "I am looking for a quick, spicy local bite like suya. Power backup and good customer service is key."
    
    # We let the agent retrieve candidates semantically from ChromaDB automatically!
    print("Invoking the recommendation agent state graph...")
    recommendations = run_agent(profile, context)
    
    print("✅ LangGraph Recommendation Agent succeeded!")
    print(json.dumps(recommendations, indent=2))
    
    print("\n" + "=" * 70)
    print("🎉 ALL HEYGENT AGENT TESTS SUCESSFULLY PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
