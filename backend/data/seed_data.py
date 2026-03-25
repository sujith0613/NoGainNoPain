"""
Synthetic Data Generator for Food Market Intelligence System.
Generates 1000+ realistic restaurant & dish records for Indian cities.
"""

import random
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker

fake = Faker("en_IN")
random.seed(42)

# ── Constants ──────────────────────────────────────────────────────────────────
CITIES = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Pune", "Kolkata"]

AREAS = {
    "Mumbai": ["Bandra", "Juhu", "Andheri", "Dadar", "Worli", "Colaba", "Kurla", "Malad"],
    "Delhi": ["Connaught Place", "Lajpat Nagar", "Hauz Khas", "Karol Bagh", "Saket", "Dwarka"],
    "Bangalore": ["Koramangala", "Indiranagar", "Whitefield", "MG Road", "Jayanagar", "HSR Layout"],
    "Hyderabad": ["Banjara Hills", "Jubilee Hills", "Hitech City", "Secunderabad", "Madhapur"],
    "Chennai": ["Anna Nagar", "T Nagar", "Adyar", "Nungambakkam", "Velachery", "Mylapore"],
    "Pune": ["Koregaon Park", "Viman Nagar", "Baner", "Kothrud", "Hadapsar", "Camp"],
    "Kolkata": ["Park Street", "Salt Lake", "Ballygunge", "New Town", "Behala", "Howrah"],
}

AREA_COORDS = {
    "Bandra": (19.0596, 72.8295), "Juhu": (19.1075, 72.8263),
    "Andheri": (19.1136, 72.8697), "Dadar": (19.0178, 72.8478),
    "Worli": (19.0176, 72.8156), "Colaba": (18.9067, 72.8147),
    "Kurla": (19.0726, 72.8845), "Malad": (19.1872, 72.8483),
    "Connaught Place": (28.6315, 77.2167), "Lajpat Nagar": (28.5700, 77.2437),
    "Hauz Khas": (28.5494, 77.2001), "Karol Bagh": (28.6517, 77.1909),
    "Saket": (28.5244, 77.2066), "Dwarka": (28.5921, 77.0460),
    "Koramangala": (12.9352, 77.6245), "Indiranagar": (12.9784, 77.6408),
    "Whitefield": (12.9698, 77.7499), "MG Road": (12.9757, 77.6011),
    "Jayanagar": (12.9302, 77.5834), "HSR Layout": (12.9121, 77.6446),
    "Banjara Hills": (17.4156, 78.4347), "Jubilee Hills": (17.4329, 78.4071),
    "Hitech City": (17.4435, 78.3772), "Secunderabad": (17.4399, 78.4983),
    "Madhapur": (17.4486, 78.3908),
    "Anna Nagar": (13.0850, 80.2101), "T Nagar": (13.0418, 80.2341),
    "Adyar": (13.0012, 80.2565), "Nungambakkam": (13.0569, 80.2425),
    "Velachery": (12.9815, 80.2180), "Mylapore": (13.0336, 80.2700),
    "Koregaon Park": (18.5362, 73.8938), "Viman Nagar": (18.5679, 73.9143),
    "Baner": (18.5590, 73.7868), "Kothrud": (18.5074, 73.8077),
    "Hadapsar": (18.5018, 73.9260), "Camp": (18.5205, 73.8760),
    "Park Street": (22.5514, 88.3612), "Salt Lake": (22.5805, 88.4197),
    "Ballygunge": (22.5266, 88.3670), "New Town": (22.5868, 88.4803),
    "Behala": (22.4991, 88.3140), "Howrah": (22.5958, 88.2636),
}

CUISINES = [
    "North Indian", "South Indian", "Chinese", "Italian", "Continental",
    "Mexican", "Fast Food", "Biryani", "Seafood", "Mughlai",
    "Street Food", "Desserts", "Bengali", "Gujarati", "Rajasthani",
]

DISHES = {
    "North Indian": [
        ("Butter Chicken", "Main Course", 280, False),
        ("Dal Makhani", "Main Course", 220, True),
        ("Paneer Tikka", "Starter", 260, True),
        ("Naan", "Bread", 40, True),
        ("Chole Bhature", "Main Course", 180, True),
        ("Rajma Chawal", "Main Course", 160, True),
        ("Palak Paneer", "Main Course", 240, True),
        ("Lamb Rogan Josh", "Main Course", 360, False),
    ],
    "South Indian": [
        ("Masala Dosa", "Breakfast", 120, True),
        ("Idli Sambar", "Breakfast", 80, True),
        ("Vada", "Snack", 60, True),
        ("Chettinad Chicken", "Main Course", 320, False),
        ("Rasam", "Soup", 60, True),
        ("Filter Coffee", "Beverage", 50, True),
        ("Pongal", "Breakfast", 90, True),
        ("Uttapam", "Breakfast", 110, True),
    ],
    "Chinese": [
        ("Schezwan Fried Rice", "Main Course", 200, True),
        ("Chilli Chicken", "Starter", 280, False),
        ("Hakka Noodles", "Main Course", 190, True),
        ("Manchurian", "Starter", 220, False),
        ("Spring Rolls", "Starter", 140, True),
        ("Hot and Sour Soup", "Soup", 110, True),
        ("Kung Pao Chicken", "Main Course", 300, False),
    ],
    "Italian": [
        ("Margherita Pizza", "Main Course", 350, True),
        ("Pasta Arrabiata", "Main Course", 320, True),
        ("Risotto", "Main Course", 380, True),
        ("Tiramisu", "Dessert", 200, True),
        ("Caesar Salad", "Salad", 280, True),
        ("Lasagna", "Main Course", 390, False),
        ("Bruschetta", "Starter", 180, True),
    ],
    "Fast Food": [
        ("Veg Burger", "Burger", 150, True),
        ("Chicken Burger", "Burger", 220, False),
        ("French Fries", "Side", 100, True),
        ("Chicken Nuggets", "Snack", 180, False),
        ("Milkshake", "Beverage", 160, True),
        ("Onion Rings", "Side", 120, True),
        ("Grilled Sandwich", "Snack", 140, True),
    ],
    "Biryani": [
        ("Hyderabadi Chicken Biryani", "Main Course", 320, False),
        ("Mutton Biryani", "Main Course", 420, False),
        ("Veg Biryani", "Main Course", 240, True),
        ("Egg Biryani", "Main Course", 280, False),
        ("Prawn Biryani", "Main Course", 380, False),
        ("Raita", "Side", 60, True),
        ("Mirchi ka Salan", "Side", 80, True),
    ],
    "Seafood": [
        ("Goan Fish Curry", "Main Course", 360, False),
        ("Prawn Masala", "Main Course", 420, False),
        ("Fish Tikka", "Starter", 300, False),
        ("Crab Curry", "Main Course", 480, False),
        ("Calamari", "Starter", 340, False),
        ("Lobster Thermidor", "Main Course", 800, False),
    ],
    "Street Food": [
        ("Pani Puri", "Snack", 50, True),
        ("Pav Bhaji", "Snack", 100, True),
        ("Bhel Puri", "Snack", 60, True),
        ("Vada Pav", "Snack", 40, True),
        ("Samosa", "Snack", 30, True),
        ("Chai", "Beverage", 20, True),
        ("Aloo Tikki", "Snack", 60, True),
    ],
    "Desserts": [
        ("Gulab Jamun", "Dessert", 80, True),
        ("Ras Malai", "Dessert", 120, True),
        ("Kulfi", "Dessert", 80, True),
        ("Jalebi", "Dessert", 60, True),
        ("Chocolate Lava Cake", "Dessert", 220, True),
        ("Ice Cream", "Dessert", 100, True),
    ],
    "Mughlai": [
        ("Seekh Kebab", "Starter", 320, False),
        ("Chicken Korma", "Main Course", 380, False),
        ("Biryani Dum", "Main Course", 350, False),
        ("Shahi Paneer", "Main Course", 280, True),
        ("Nihari", "Main Course", 400, False),
    ],
    "Mexican": [
        ("Nachos", "Starter", 200, True),
        ("Burrito", "Main Course", 320, False),
        ("Tacos", "Main Course", 280, False),
        ("Quesadilla", "Snack", 240, True),
        ("Guacamole", "Side", 160, True),
    ],
    "Continental": [
        ("Grilled Chicken", "Main Course", 380, False),
        ("Pasta Carbonara", "Main Course", 360, False),
        ("Club Sandwich", "Snack", 280, True),
        ("French Onion Soup", "Soup", 200, True),
        ("Steak", "Main Course", 650, False),
    ],
    "Bengali": [
        ("Hilsa Fish Curry", "Main Course", 450, False),
        ("Shorshe Ilish", "Main Course", 480, False),
        ("Mishti Doi", "Dessert", 80, True),
        ("Kosha Mangsho", "Main Course", 380, False),
        ("Luchi Alur Dom", "Breakfast", 120, True),
    ],
    "Gujarati": [
        ("Dhokla", "Snack", 80, True),
        ("Thepla", "Bread", 60, True),
        ("Gujarati Thali", "Main Course", 280, True),
        ("Khandvi", "Snack", 100, True),
        ("Handvo", "Snack", 90, True),
    ],
    "Rajasthani": [
        ("Dal Baati Churma", "Main Course", 220, True),
        ("Laal Maas", "Main Course", 380, False),
        ("Ker Sangri", "Main Course", 200, True),
        ("Ghevar", "Dessert", 120, True),
        ("Bajre ki Roti", "Bread", 40, True),
    ],
}

REVIEW_TEMPLATES = {
    "positive": [
        "Absolutely loved the {dish}! The taste was amazing and service was excellent.",
        "Best {dish} I've ever had. Great ambiance and quick service.",
        "The {dish} was perfectly spiced. Highly recommend this place!",
        "Amazing food quality! The {dish} was fresh and delicious.",
        "Wonderful experience! {dish} was cooked to perfection.",
        "Great value for money. The {dish} portion was generous and tasty.",
        "Excellent service and the {dish} was outstanding.",
        "Can't get enough of their {dish}. Always consistent quality!",
    ],
    "neutral": [
        "The {dish} was decent, nothing extraordinary. Service was okay.",
        "Average experience. {dish} was fine but a bit pricey.",
        "Not bad, not great. {dish} could have been better.",
        "Mediocre experience. {dish} was okay-ish.",
        "The {dish} was acceptable. Would try again if nearby.",
    ],
    "negative": [
        "Disappointed with the {dish}. Cold food and slow service.",
        "Overpriced for the quality. {dish} lacked flavor.",
        "Had to wait too long. {dish} was not worth the price.",
        "The {dish} was average at best. Service needs improvement.",
        "Not impressed. {dish} tasted bland and stale.",
        "Poor experience overall. {dish} was not fresh.",
    ],
}

BUSINESS_TYPES = ["QSR", "Fine Dining", "Cafe", "Cloud Kitchen", "Food Truck", "Dhaba", "Bakery"]


def _random_coords(area: str):
    base = AREA_COORDS.get(area, (19.0760, 72.8777))
    return (
        round(base[0] + random.uniform(-0.015, 0.015), 6),
        round(base[1] + random.uniform(-0.015, 0.015), 6),
    )


def _random_timestamp():
    now = datetime(2026, 3, 25)
    days_back = random.randint(0, 365)
    hour = random.randint(8, 23)
    minute = random.choice([0, 15, 30, 45])
    dt = now - timedelta(days=days_back, hours=0)
    dt = dt.replace(hour=hour, minute=minute)
    return dt


def _generate_review(dish_name: str, sentiment: str) -> str:
    template = random.choice(REVIEW_TEMPLATES[sentiment])
    return template.format(dish=dish_name)


from typing import List

def generate_records(n: int = 1200) -> List[dict]:
    """Generate n synthetic restaurant-dish records with all core + derived fields."""
    records = []
    restaurant_id = 1

    restaurants_pool = []
    for city in CITIES:
        for area in AREAS[city]:
            for cuisine in random.sample(CUISINES, random.randint(1, 4)):
                restaurant_name = f"{fake.last_name()} {random.choice(['Kitchen', 'Bistro', 'Dhaba', 'Cafe', 'Restaurant', 'House', 'Palace'])}"
                lat, lng = _random_coords(area)
                base_rating = round(random.uniform(2.5, 5.0), 1)
                review_count = random.randint(10, 2500)
                business_type = random.choice(BUSINESS_TYPES)
                restaurants_pool.append({
                    "restaurant_id": str(restaurant_id),
                    "restaurant_name": restaurant_name,
                    "area": area,
                    "city": city,
                    "latitude": lat,
                    "longitude": lng,
                    "cuisine_type": cuisine,
                    "business_type": business_type,
                    "base_rating": base_rating,
                    "review_count": review_count,
                })
                restaurant_id += 1

    # Generate records until we hit n
    attempts = 0
    while len(records) < n and attempts < n * 5:
        attempts += 1
        rest = random.choice(restaurants_pool)
        cuisine = rest["cuisine_type"]
        if cuisine not in DISHES:
            cuisine = random.choice(list(DISHES.keys()))
        dish_name, dish_category, base_price, is_veg = random.choice(DISHES[cuisine])

        # Price variation ±30%
        price_multiplier = random.uniform(0.7, 1.4)
        dish_price = round(base_price * price_multiplier)

        # Timestamp
        ts = _random_timestamp()
        hour = ts.hour
        dow = ts.strftime("%A")
        weekend_flag = dow in ("Saturday", "Sunday")

        # Rating jitter
        rating = round(max(1.0, min(5.0, rest["base_rating"] + random.uniform(-0.8, 0.8))), 1)
        normalized_rating = round((rating - 1) / 4, 4)

        # Sentiment seeded from rating
        if rating >= 4.0:
            sentiment_key = "positive"
            sentiment_score = round(random.uniform(0.3, 1.0), 4)
            taste_score = round(random.uniform(0.5, 1.0), 4)
            service_score = round(random.uniform(0.4, 1.0), 4)
            price_sentiment = round(random.uniform(0.0, 0.8), 4)
        elif rating >= 3.0:
            sentiment_key = "neutral"
            sentiment_score = round(random.uniform(-0.2, 0.3), 4)
            taste_score = round(random.uniform(0.2, 0.6), 4)
            service_score = round(random.uniform(0.1, 0.5), 4)
            price_sentiment = round(random.uniform(-0.3, 0.3), 4)
        else:
            sentiment_key = "negative"
            sentiment_score = round(random.uniform(-1.0, -0.1), 4)
            taste_score = round(random.uniform(0.0, 0.3), 4)
            service_score = round(random.uniform(0.0, 0.3), 4)
            price_sentiment = round(random.uniform(-1.0, -0.1), 4)

        review_text = _generate_review(dish_name, sentiment_key)

        # Demand signals
        dish_mentions = random.randint(1, 150)
        dish_frequency = round(dish_mentions / max(rest["review_count"], 1), 4)
        demand_score = round(
            0.4 * normalized_rating + 0.3 * (dish_mentions / 150) + 0.3 * max(sentiment_score, 0), 4
        )
        supply_count = random.randint(1, 30)

        # Pricing features
        avg_price_area = round(base_price * random.uniform(0.85, 1.15))
        price_range = (round(base_price * 0.75), round(base_price * 1.25))
        price_deviation = round((dish_price - avg_price_area) / max(avg_price_area, 1), 4)
        price_elasticity_score = round(random.uniform(-1.0, 1.0), 4)

        # Trend features
        review_growth_rate = round(random.uniform(-0.3, 0.8), 4)
        demand_growth_rate = round(random.uniform(-0.2, 0.6), 4)
        price_change = round(random.uniform(-0.15, 0.25), 4)
        new_dish_flag = random.random() < 0.1

        # Time features
        peak_hour_score = round(
            1.0 if 12 <= hour <= 14 else
            0.9 if 19 <= hour <= 22 else
            0.5 if 8 <= hour <= 10 else 0.3, 2
        )
        daily_demand = round(demand_score * peak_hour_score * random.uniform(0.8, 1.2), 4)

        # Combo features
        co_ordered_items = _pick_co_ordered(cuisine, dish_name)
        combo_score = round(random.uniform(0.1, 1.0), 4)
        association_strength = round(random.uniform(0.0, 0.9), 4)

        # Location intelligence
        area_demand_score = round(random.uniform(0.3, 1.0), 4)
        area_competition_score = round(random.uniform(0.1, 1.0), 4)
        area_popularity_rank = random.randint(1, 10)

        # Scoring
        opportunity_score = round(
            (demand_score * max(sentiment_score, 0.01) * max(demand_growth_rate, 0.01))
            / max(supply_count, 1), 6
        )
        risk_score = round(
            0.4 * area_competition_score +
            0.3 * max(-sentiment_score, 0) +
            0.3 * abs(price_elasticity_score), 4
        )
        profitability_score = round(
            dish_price * demand_score * max(sentiment_score, 0), 4
        )

        record = {
            # Core
            "restaurant_id": rest["restaurant_id"],
            "restaurant_name": rest["restaurant_name"],
            "area": rest["area"],
            "city": rest["city"],
            "latitude": rest["latitude"],
            "longitude": rest["longitude"],
            "cuisine_type": cuisine,
            "business_type": rest["business_type"],
            # Dish
            "dish_name": dish_name,
            "dish_category": dish_category,
            "dish_price": dish_price,
            "is_veg": is_veg,
            # Ratings
            "rating": rating,
            "normalized_rating": normalized_rating,
            "review_count": rest["review_count"],
            "review_text": review_text,
            # Time
            "timestamp": ts.isoformat(),
            "day_of_week": dow,
            "hour_of_day": hour,
            # NLP
            "sentiment_score": sentiment_score,
            "taste_score": taste_score,
            "price_sentiment": price_sentiment,
            "service_score": service_score,
            # Demand & Supply
            "dish_mentions": dish_mentions,
            "dish_frequency": dish_frequency,
            "demand_score": demand_score,
            "supply_count": supply_count,
            # Pricing
            "avg_price_area": avg_price_area,
            "price_range": price_range,
            "price_deviation": price_deviation,
            "price_elasticity_score": price_elasticity_score,
            # Trend
            "review_growth_rate": review_growth_rate,
            "demand_growth_rate": demand_growth_rate,
            "price_change": price_change,
            "new_dish_flag": new_dish_flag,
            # Time intelligence
            "peak_hour_score": peak_hour_score,
            "daily_demand": daily_demand,
            "weekend_flag": weekend_flag,
            # Combo
            "co_ordered_items": co_ordered_items,
            "combo_score": combo_score,
            "association_strength": association_strength,
            # Location
            "area_demand_score": area_demand_score,
            "area_competition_score": area_competition_score,
            "area_popularity_rank": area_popularity_rank,
            # Scores
            "opportunity_score": opportunity_score,
            "risk_score": risk_score,
            "profitability_score": profitability_score,
        }
        records.append(record)

    return records


def _pick_co_ordered(cuisine: str, dish_name: str) -> list[str]:
    same_cuisine_dishes = [d[0] for d in DISHES.get(cuisine, []) if d[0] != dish_name]
    count = random.randint(0, min(3, len(same_cuisine_dishes)))
    return random.sample(same_cuisine_dishes, count)


def seed_database():
    """Seed MongoDB with generated records."""
    from pymongo import MongoClient
    from config import MONGODB_URL, DATABASE_NAME, COLLECTION_NAME

    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    col = db[COLLECTION_NAME]

    existing = col.count_documents({})
    if existing >= 1000:
        print(f"[seed] Collection already has {existing} records. Skipping.")
        return

    records = generate_records(1200)
    col.delete_many({})
    result = col.insert_many(records)
    print(f"[seed] Inserted {len(result.inserted_ids)} records into '{DATABASE_NAME}.{COLLECTION_NAME}'")
    client.close()


if __name__ == "__main__":
    seed_database()
