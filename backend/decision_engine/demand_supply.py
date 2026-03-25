"""
Demand-Supply Analyzer: Identify high-demand, low-supply cuisine/dish opportunities.
"""
import pandas as pd
from data_pipeline.ingestion import load_raw_data
from data_pipeline.cleaning import clean_data
from data_pipeline.normalization import normalize_data
from data_pipeline.feature_engineering import engineer_features
from data_pipeline.scoring import compute_scores


def get_demand_gap(city: str = "", area: str = "") -> dict:
    """
    Return cuisine/dish combinations with high demand_score but low supply_count.
    """
    filters = {}
    if city:
        filters["city"] = city

    df = load_raw_data(filters)
    if df.empty:
        return {"gaps": []}

    df = clean_data(df)
    df = normalize_data(df)
    df = engineer_features(df)
    df = compute_scores(df)

    subset = df.copy()
    if area:
        subset = subset[subset["area"].str.lower() == area.lower()]
    if subset.empty:
        subset = df

    agg = (
        subset.groupby(["area", "cuisine_type", "dish_name"])
        .agg(
            demand_score=("demand_score", "mean"),
            supply_count=("supply_count", "mean"),
            opportunity_score=("opportunity_score", "mean"),
            avg_price=("dish_price", "mean"),
            sentiment_score=("sentiment_score", "mean"),
        )
        .reset_index()
    )

    # Gap = high demand, low supply
    demand_thresh = agg["demand_score"].quantile(0.65)
    supply_thresh = agg["supply_count"].quantile(0.35)
    gaps = agg[
        (agg["demand_score"] >= demand_thresh) &
        (agg["supply_count"] <= supply_thresh)
    ].sort_values("opportunity_score", ascending=False).head(20)

    result = []
    for _, row in gaps.iterrows():
        result.append({
            "area": row["area"],
            "cuisine_type": row["cuisine_type"],
            "dish_name": row["dish_name"],
            "demand_score": round(float(row["demand_score"]), 4),
            "supply_count": int(row["supply_count"]),
            "opportunity_score": round(float(row["opportunity_score"]), 6),
            "avg_price": round(float(row["avg_price"]), 2),
            "sentiment_score": round(float(row["sentiment_score"]), 4),
        })

    return {
        "city": city or "All",
        "area": area or "All",
        "gaps": result,
        "ai_summary": (
            f"Found {len(result)} high-demand, low-supply opportunities. "
            f"Top gap: {result[0]['dish_name']} ({result[0]['cuisine_type']}) in {result[0]['area']}."
            if result else "No significant demand gaps found."
        ),
    }
