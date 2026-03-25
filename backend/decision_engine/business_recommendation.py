"""
Business Recommendation Engine
Input: area + budget
Output: suggested cuisine, business type, opportunity score summary
"""
import pandas as pd
from data_pipeline.ingestion import load_raw_data
from data_pipeline.cleaning import clean_data
from data_pipeline.normalization import normalize_data
from data_pipeline.feature_engineering import engineer_features
from data_pipeline.scoring import compute_scores


def get_business_recommendation(area: str, budget: float, city: str = "") -> dict:
    """
    Recommend top cuisine types to start in the given area within budget.

    Returns:
        dict with top_recommendations (list), area_summary, ai_summary
    """
    filters: dict = {}
    if city:
        filters["city"] = city

    df = load_raw_data(filters)
    if df.empty:
        return {"error": "No data available", "top_recommendations": []}

    df = clean_data(df)
    df = normalize_data(df)
    df = engineer_features(df)
    df = compute_scores(df)

    # Filter by area
    area_df = df[df["area"].str.lower() == area.lower()]
    if area_df.empty:
        area_df = df  # fallback to all

    # Compute budget feasibility: avg dish_price vs budget estimate
    # (Assume budget correlates with avg_price * 1500 as rough seat-count proxy)
    cuisine_stats = (
        area_df.groupby("cuisine_type")
        .agg(
            avg_opportunity=("opportunity_score", "mean"),
            avg_demand=("demand_score", "mean"),
            avg_sentiment=("sentiment_score", "mean"),
            avg_price=("dish_price", "mean"),
            avg_risk=("risk_score", "mean"),
            supply_count=("supply_count", "mean"),
            review_growth=("review_growth_rate", "mean"),
        )
        .reset_index()
    )

    # Budget filter: rough estimate — low budget (<500k) suits QSR/Street Food, higher for Fine Dining
    budget_thresholds = {
        "QSR": 300_000, "Street Food": 200_000, "Cafe": 400_000,
        "Cloud Kitchen": 250_000, "Biryani": 350_000, "Fast Food": 300_000,
        "Fine Dining": 800_000, "Dhaba": 200_000, "Bakery": 250_000,
    }

    def cuisine_to_type(cuisine: str) -> str:
        mapping = {
            "Street Food": "Street Food", "Fast Food": "QSR",
            "Desserts": "Cafe", "Biryani": "Dhaba", "Mughlai": "Dhaba",
            "Bengali": "Dhaba", "Gujarati": "Dhaba", "Rajasthani": "Dhaba",
            "Chinese": "QSR", "Italian": "Fine Dining", "Continental": "Fine Dining",
            "Mexican": "Cafe", "Seafood": "Fine Dining",
        }
        return mapping.get(cuisine, "Cafe")

    cuisine_stats["suggested_business_type"] = cuisine_stats["cuisine_type"].apply(cuisine_to_type)
    cuisine_stats["est_min_budget"] = cuisine_stats["suggested_business_type"].apply(
        lambda bt: budget_thresholds.get(bt, 300_000)
    )
    cuisine_stats = cuisine_stats[cuisine_stats["est_min_budget"] <= budget]

    if cuisine_stats.empty:
        cuisine_stats_all = (
            area_df.groupby("cuisine_type")
            .agg(avg_opportunity=("opportunity_score", "mean"), avg_risk=("risk_score", "mean"))
            .reset_index()
        )
        cuisine_stats = cuisine_stats_all

    cuisine_stats = cuisine_stats.sort_values("avg_opportunity", ascending=False).head(5)

    recommendations = []
    for _, row in cuisine_stats.iterrows():
        recommendations.append({
            "cuisine_type": row.get("cuisine_type", ""),
            "suggested_business_type": row.get("suggested_business_type", "Cafe"),
            "opportunity_score": round(float(row.get("avg_opportunity", 0)), 4),
            "demand_score": round(float(row.get("avg_demand", 0)), 4),
            "risk_score": round(float(row.get("avg_risk", 0)), 4),
            "avg_competitor_price": round(float(row.get("avg_price", 0)), 2),
            "review_growth_rate": round(float(row.get("review_growth", 0)), 4),
        })

    top = recommendations[0] if recommendations else {}
    ai_summary = (
        f"Based on market analysis for {area}, we recommend starting a "
        f"**{top.get('suggested_business_type', 'Cafe')}** focusing on "
        f"**{top.get('cuisine_type', 'the top cuisine')}**. "
        f"Opportunity score: {top.get('opportunity_score', 0):.4f} with "
        f"risk score: {top.get('risk_score', 0):.4f}."
    ) if top else "No recommendation available for the given area and budget."

    return {
        "area": area,
        "budget": budget,
        "top_recommendations": recommendations,
        "ai_summary": ai_summary,
    }
