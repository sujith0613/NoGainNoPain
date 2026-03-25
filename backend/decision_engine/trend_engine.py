"""
Trend Engine: Identify rising and declining cuisines/dishes by growth metrics.
"""
import pandas as pd
from data_pipeline.ingestion import load_raw_data
from data_pipeline.cleaning import clean_data
from data_pipeline.feature_engineering import engineer_features


def get_trend_analysis(city: str = "", cuisine_type: str = "") -> dict:
    """Return rising and declining cuisine/dish trends."""
    filters = {}
    if city:
        filters["city"] = city

    df = load_raw_data(filters)
    if df.empty:
        return {"rising": [], "declining": []}

    df = clean_data(df)
    df = engineer_features(df)

    if cuisine_type:
        filtered = df[df["cuisine_type"].str.lower() == cuisine_type.lower()]
    else:
        filtered = df

    # Cuisine-level trends
    cuisine_trends = (
        filtered.groupby("cuisine_type")
        .agg(
            avg_review_growth=("review_growth_rate", "mean"),
            avg_demand_growth=("demand_growth_rate", "mean"),
            avg_demand=("demand_score", "mean"),
            avg_rating=("rating", "mean"),
            record_count=("restaurant_id", "count"),
        )
        .reset_index()
    )
    cuisine_trends["trend_score"] = (
        0.5 * cuisine_trends["avg_review_growth"] +
        0.5 * cuisine_trends["avg_demand_growth"]
    ).round(4)

    rising = cuisine_trends[cuisine_trends["trend_score"] > 0.05].sort_values(
        "trend_score", ascending=False
    )
    declining = cuisine_trends[cuisine_trends["trend_score"] < 0].sort_values("trend_score")

    # Dish-level trends
    dish_trends = (
        filtered.groupby(["cuisine_type", "dish_name"])
        .agg(
            avg_demand_growth=("demand_growth_rate", "mean"),
            avg_demand=("demand_score", "mean"),
            new_dish_flag=("new_dish_flag", "sum"),
        )
        .reset_index()
        .sort_values("avg_demand_growth", ascending=False)
    )

    return {
        "city": city or "All",
        "rising_cuisines": [
            {
                "cuisine_type": r["cuisine_type"],
                "trend_score": round(float(r["trend_score"]), 4),
                "review_growth": round(float(r["avg_review_growth"]), 4),
                "demand_growth": round(float(r["avg_demand_growth"]), 4),
                "avg_rating": round(float(r["avg_rating"]), 2),
            }
            for _, r in rising.head(6).iterrows()
        ],
        "declining_cuisines": [
            {
                "cuisine_type": r["cuisine_type"],
                "trend_score": round(float(r["trend_score"]), 4),
                "review_growth": round(float(r["avg_review_growth"]), 4),
                "demand_growth": round(float(r["avg_demand_growth"]), 4),
            }
            for _, r in declining.head(5).iterrows()
        ],
        "trending_dishes": [
            {
                "cuisine_type": row["cuisine_type"],
                "dish_name": row["dish_name"],
                "demand_growth": round(float(row["avg_demand_growth"]), 4),
                "demand_score": round(float(row["avg_demand"]), 4),
                "is_new": bool(row["new_dish_flag"] > 0),
            }
            for _, row in dish_trends[dish_trends["avg_demand_growth"] > 0.1].head(10).iterrows()
        ],
        "ai_summary": (
            f"Top rising cuisine: {rising.iloc[0]['cuisine_type']} "
            f"(trend score: {rising.iloc[0]['trend_score']:.3f}). "
            f"{len(declining)} cuisines are on decline in {city or 'this market'}."
            if not rising.empty else "Trend data being computed."
        ),
    }
