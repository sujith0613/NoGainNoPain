"""
Menu Generator: Recommend top dishes using demand_score + normalized_rating.
"""
import pandas as pd
from data_pipeline.ingestion import load_raw_data
from data_pipeline.cleaning import clean_data
from data_pipeline.normalization import normalize_data
from data_pipeline.feature_engineering import engineer_features
from data_pipeline.scoring import compute_scores


def get_menu_recommendations(area: str, cuisine_type: str, top_n: int = 10) -> dict:
    """Return top recommended dishes for a cuisine in an area."""
    df = load_raw_data()
    if df.empty:
        return {"dishes": []}

    df = clean_data(df)
    df = normalize_data(df)
    df = engineer_features(df)
    df = compute_scores(df)

    subset = df[(df["area"].str.lower() == area.lower()) &
                (df["cuisine_type"].str.lower() == cuisine_type.lower())]
    if subset.empty:
        subset = df[df["cuisine_type"].str.lower() == cuisine_type.lower()]

    if subset.empty:
        return {"area": area, "cuisine_type": cuisine_type, "dishes": []}

    # Menu score = 0.5 * demand_score + 0.3 * normalized_rating + 0.2 * sentiment_score_normalized
    subset = subset.copy()
    subset["menu_score"] = (
        0.5 * subset["demand_score"].clip(0, 1) +
        0.3 * subset["normalized_rating"].clip(0, 1) +
        0.2 * subset["sentiment_score"].clip(0, 1)
    )

    dish_summary = (
        subset.groupby(["dish_name", "dish_category", "is_veg"])
        .agg(
            menu_score=("menu_score", "mean"),
            demand_score=("demand_score", "mean"),
            avg_rating=("rating", "mean"),
            avg_price=("dish_price", "mean"),
            sentiment_score=("sentiment_score", "mean"),
            dish_mentions=("dish_mentions", "sum"),
            profitability=("profitability_score", "mean"),
        )
        .reset_index()
        .sort_values("menu_score", ascending=False)
        .head(top_n)
    )

    dishes = []
    for _, row in dish_summary.iterrows():
        dishes.append({
            "dish_name": row["dish_name"],
            "dish_category": row["dish_category"],
            "is_veg": bool(row["is_veg"]),
            "menu_score": round(float(row["menu_score"]), 4),
            "demand_score": round(float(row["demand_score"]), 4),
            "avg_rating": round(float(row["avg_rating"]), 2),
            "avg_price": round(float(row["avg_price"]), 2),
            "sentiment_score": round(float(row["sentiment_score"]), 4),
            "dish_mentions": int(row["dish_mentions"]),
            "profitability_score": round(float(row["profitability"]), 4),
        })

    return {
        "area": area,
        "cuisine_type": cuisine_type,
        "dishes": dishes,
        "ai_summary": (
            f"Top {len(dishes)} dishes recommended for {cuisine_type} in {area}. "
            f"Lead with '{dishes[0]['dish_name']}' (score: {dishes[0]['menu_score']:.4f}) "
            f"for maximum demand and profitability." if dishes else "No dishes found."
        ),
    }
