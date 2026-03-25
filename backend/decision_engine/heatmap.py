"""
Heatmap Data: Return aggregated lat/lng demand and competition scores
for map visualization.
"""
import pandas as pd
from data_pipeline.ingestion import load_raw_data
from data_pipeline.cleaning import clean_data
from data_pipeline.feature_engineering import engineer_features
from data_pipeline.scoring import compute_scores


def get_heatmap_data(city: str = "") -> dict:
    """Return per-area heatmap data points with demand/competition metrics."""
    filters = {}
    if city:
        filters["city"] = city

    df = load_raw_data(filters)
    if df.empty:
        return {"points": []}

    df = clean_data(df)
    df = engineer_features(df)
    df = compute_scores(df)

    area_agg = (
        df.groupby(["area", "city"])
        .agg(
            latitude=("latitude", "mean"),
            longitude=("longitude", "mean"),
            demand_score=("demand_score", "mean"),
            opportunity_score=("opportunity_score", "mean"),
            competition_score=("area_competition_score", "mean"),
            avg_rating=("rating", "mean"),
            restaurant_count=("restaurant_id", "nunique"),
            avg_price=("dish_price", "mean"),
        )
        .reset_index()
    )

    points = []
    for _, row in area_agg.iterrows():
        points.append({
            "area": row["area"],
            "city": row["city"],
            "latitude": round(float(row["latitude"]), 6),
            "longitude": round(float(row["longitude"]), 6),
            "demand_score": round(float(row["demand_score"]), 4),
            "opportunity_score": round(float(row["opportunity_score"]), 6),
            "competition_score": round(float(row["competition_score"]), 4),
            "avg_rating": round(float(row["avg_rating"]), 2),
            "restaurant_count": int(row["restaurant_count"]),
            "avg_price": round(float(row["avg_price"]), 2),
            "intensity": round(float(row["demand_score"]) * 100, 1),  # for heatmap
        })

    return {
        "city": city or "All",
        "total_areas": len(points),
        "points": sorted(points, key=lambda x: x["demand_score"], reverse=True),
    }
