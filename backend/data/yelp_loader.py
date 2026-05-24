"""
Yelp dataset loader and preprocessor.
Yelp dataset: https://www.yelp.com/dataset
Expected files: yelp_academic_dataset_review.json
                yelp_academic_dataset_business.json
                yelp_academic_dataset_user.json
Each file is newline-delimited JSON (one object per line).
"""

import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Review:
    review_id: str
    user_id: str
    business_id: str
    stars: float
    text: str
    date: str
    useful: int = 0
    funny: int = 0
    cool: int = 0


@dataclass
class Business:
    business_id: str
    name: str
    categories: Optional[str]
    city: str
    state: str
    stars: float
    review_count: int
    attributes: dict = field(default_factory=dict)


@dataclass
class UserProfile:
    user_id: str
    name: str
    review_count: int
    average_stars: float
    reviews: list[Review] = field(default_factory=list)


def stream_json_lines(filepath: str):
    """Stream a newline-delimited JSON file line by line (memory efficient)."""
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def load_reviews_for_users(
    reviews_path: str,
    user_ids: set[str],
    max_reviews_per_user: int = 50,
) -> dict[str, list[Review]]:
    """
    Load reviews filtered to a specific set of user IDs.
    Caps per-user reviews to avoid bloated persona prompts.
    """
    user_reviews: dict[str, list[Review]] = defaultdict(list)

    for obj in stream_json_lines(reviews_path):
        uid = obj.get("user_id", "")
        if uid not in user_ids:
            continue
        if len(user_reviews[uid]) >= max_reviews_per_user:
            continue
        user_reviews[uid].append(
            Review(
                review_id=obj["review_id"],
                user_id=uid,
                business_id=obj["business_id"],
                stars=float(obj["stars"]),
                text=obj["text"],
                date=obj["date"],
                useful=obj.get("useful", 0),
                funny=obj.get("funny", 0),
                cool=obj.get("cool", 0),
            )
        )

    return dict(user_reviews)


def load_businesses(
    businesses_path: str,
    business_ids: Optional[set[str]] = None,
) -> dict[str, Business]:
    """Load businesses, optionally filtered to a set of IDs."""
    businesses = {}
    for obj in stream_json_lines(businesses_path):
        bid = obj["business_id"]
        if business_ids and bid not in business_ids:
            continue
        businesses[bid] = Business(
            business_id=bid,
            name=obj.get("name", ""),
            categories=obj.get("categories"),
            city=obj.get("city", ""),
            state=obj.get("state", ""),
            stars=float(obj.get("stars", 0)),
            review_count=int(obj.get("review_count", 0)),
            attributes=obj.get("attributes") or {},
        )
    return businesses


def load_user_meta(users_path: str, user_ids: set[str]) -> dict[str, dict]:
    """Load user metadata for a set of user IDs."""
    users = {}
    for obj in stream_json_lines(users_path):
        uid = obj.get("user_id", "")
        if uid in user_ids:
            users[uid] = obj
    return users


def build_user_profile(
    user_id: str,
    user_meta: dict,
    reviews: list[Review],
    businesses: dict[str, Business],
) -> dict:
    """
    Construct a rich user profile dict ready for persona building.
    Includes aggregated stats and enriched review history.
    """
    enriched_reviews = []
    for r in reviews:
        biz = businesses.get(r.business_id)
        enriched_reviews.append({
            "stars": r.stars,
            "text": r.text,
            "date": r.date,
            "business_name": biz.name if biz else "Unknown",
            "business_categories": biz.categories if biz else "",
            "business_city": biz.city if biz else "",
        })

    # Compute rating distribution
    rating_dist = defaultdict(int)
    for r in reviews:
        rating_dist[int(r.stars)] += 1

    avg_stars = (
        sum(r.stars for r in reviews) / len(reviews) if reviews else 0.0
    )
    avg_len = (
        sum(len(r.text.split()) for r in reviews) / len(reviews) if reviews else 0
    )

    return {
        "user_id": user_id,
        "name": user_meta.get("name", "User"),
        "review_count": user_meta.get("review_count", len(reviews)),
        "average_stars": round(avg_stars, 2),
        "avg_review_length_words": round(avg_len),
        "rating_distribution": dict(rating_dist),
        "reviews": enriched_reviews,
    }


# ---------------------------------------------------------------------------
# Quick demo loader for development (uses small synthetic data if no dataset)
# ---------------------------------------------------------------------------

DEMO_REVIEWS = [
    {
        "stars": 5,
        "text": "This place is absolutely amazing! The jollof rice reminds me of home. "
                "Service was warm, portions were generous. Will definitely come back!",
        "date": "2023-08-14",
        "business_name": "Mama Cass Restaurant",
        "business_categories": "Nigerian, African, Restaurants",
        "business_city": "Lagos",
    },
    {
        "stars": 2,
        "text": "Honestly expected better. Waited almost an hour for food and it arrived cold. "
                "The pepper soup had potential but they over-salted it. Not worth the price.",
        "date": "2023-06-22",
        "business_name": "Spice Garden",
        "business_categories": "African, Restaurants",
        "business_city": "Lagos",
    },
    {
        "stars": 4,
        "text": "Solid spot. The suya was on point and the service dey try. "
                "A bit noisy on weekends but the vibe makes up for it.",
        "date": "2024-01-10",
        "business_name": "The Suya Spot",
        "business_categories": "Street Food, Restaurants",
        "business_city": "Lagos",
    },
]

DEMO_USER_PROFILE = {
    "user_id": "demo_user_001",
    "name": "Tunde",
    "review_count": 3,
    "average_stars": 3.67,
    "avg_review_length_words": 42,
    "rating_distribution": {2: 1, 4: 1, 5: 1},
    "reviews": DEMO_REVIEWS,
}

DEMO_SARAH_REVIEWS = [
    {
        "stars": 4,
        "text": "Really enjoyed my time here! The spicy noodles were very delicious and packed a serious punch. Ambience was lovely and romantic. Service is high quality, but prices are fine dining standard.",
        "business_name": "Auntie Ann's Thai",
        "business_categories": "Thai, Restaurants",
        "business_city": "Philadelphia"
    },
    {
        "stars": 5,
        "text": "Unbelievable culinary experience. The wood-fired pizza was outstanding. Crust is thin, crispy and perfectly blistered. The service was top notch. A bit loud but the food makes up for it.",
        "business_name": "Pizzeria Stella",
        "business_categories": "Italian, Restaurants",
        "business_city": "Philadelphia"
    }
]

DEMO_SARAH_PROFILE = {
    "user_id": "demo_sarah_002",
    "name": "Sarah (Yelp Spicy Dining Lover)",
    "review_count": 2,
    "average_stars": 4.5,
    "avg_review_length_words": 35,
    "rating_distribution": {4: 1, 5: 1},
    "reviews": DEMO_SARAH_REVIEWS
}

DEMO_GOODREADS_KATHRYN = {
    "user_id": "demo_kathryn_goodreads",
    "name": "Kathryn (Goodreads Mystery Reader)",
    "review_count": 2,
    "average_stars": 4.5,
    "avg_review_length_words": 85,
    "rating_distribution": {4: 1, 5: 1},
    "reviews": [
        {
            "stars": 5,
            "text": "A masterclass in historical suspense. The intricate depiction of a 14th-century monastery combined with theological debates makes this the perfect intellectual mystery. The prose is verbose, academic, and extremely rich. I care most about historical accuracy and slow-burn depth.",
            "business_name": "The Name of the Rose (Umberto Eco)",
            "business_categories": "Goodreads, Books, Historical Fiction",
            "business_city": "Amazon Kindle"
        },
        {
            "stars": 4,
            "text": "Fascinating puzzle-solving narrative. Although some plot details are a bit sensationalist, the code-breaking and fast-paced symbology debates were incredibly engaging. Kept me up all night. A bit terse in character depth, but brilliant structure.",
            "business_name": "The Da Vinci Code (Dan Brown)",
            "business_categories": "Goodreads, Books, Mystery, Thriller",
            "business_city": "Amazon Kindle"
        }
    ]
}

DEMO_AMAZON_KENNY = {
    "user_id": "demo_kenny_amazon",
    "name": "Kenny (Amazon Tech Reviewer)",
    "review_count": 2,
    "average_stars": 4.5,
    "avg_review_length_words": 55,
    "rating_distribution": {4: 1, 5: 1},
    "reviews": [
        {
            "stars": 5,
            "text": "Build quality is absolutely stellar! The matte black finish looks incredibly premium, and the aluminum frame feels robust. Setup took under 3 minutes, and latency is non-existent. Highly recommended for power users seeking sleek design.",
            "business_name": "Logitech MX Master 3S Mouse",
            "business_categories": "Amazon, Electronics, Office Supplies",
            "business_city": "Amazon Prime"
        },
        {
            "stars": 4,
            "text": "Excellent noise cancellation and soundstage. The high frequencies are crisp, though the bass is slightly boomy out of the box. Casing is robust but a bit bulky to carry. Good value but lacks absolute perfection.",
            "business_name": "Sony WH-1000XM5 Headphones",
            "business_categories": "Amazon, Electronics, Audio, Travel",
            "business_city": "Amazon Prime"
        }
    ]
}
