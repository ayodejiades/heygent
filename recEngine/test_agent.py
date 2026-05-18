"""
test_agent.py
-------------
Script to verify the agent logic.
"""

from dotenv import load_dotenv
load_dotenv()

from data.yelp_loader import DEMO_USER_PROFILE, DEMO_REVIEWS
from core.agent import run_agent

def test():
    print("Running recommendation agent with Tunde's profile...")
    
    # Normally we'd use ChromaDB, but for quick testing we can pass candidates directly
    # or rely on the fact that Chroma is empty and see how the agent handles it
    
    # We will pass the demo reviews as "candidates" just to test reasoning
    # In a real run, ChromaDB retrieves these
    candidates = [
        {
            "business_id": "biz_1",
            "name": "Mama Cass Restaurant",
            "categories": "Nigerian, African, Restaurants",
            "city": "Lagos",
            "stars": 4.5
        },
        {
            "business_id": "biz_2",
            "name": "Spice Garden",
            "categories": "African, Restaurants",
            "city": "Lagos",
            "stars": 2.5
        },
        {
            "business_id": "biz_3",
            "name": "The Suya Spot",
            "categories": "Street Food, Restaurants",
            "city": "Lagos",
            "stars": 4.0
        }
    ]
    
    # Inject a dummy persona so we don't have to call persona builder for the test
    profile = DEMO_USER_PROFILE.copy()
    profile["persona"] = {
        "rating_style": "balanced",
        "verbosity": "moderate",
        "emotional_tone": "expressive",
        "praise_triggers": ["good service", "authentic taste"],
        "complaint_triggers": ["cold food", "long wait"],
        "summary": "Tunde appreciates authentic Nigerian food and good service, but is sensitive to long wait times and cold food."
    }
    
    context = "I'm looking for a quick bite, somewhere with good suya."
    
    try:
        res = run_agent(profile, context, candidates_override=candidates)
        import json
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
