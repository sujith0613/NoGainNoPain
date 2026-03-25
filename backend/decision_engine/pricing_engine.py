"""
Pricing Engine: Determine optimal price range for a cuisine in an area
using price_elasticity_score and competitor benchmarking.
"""
import pandas as pd
from data_pipeline.ingestion import load_raw_data
from data_pipeline.cleaning import clean_data
from data_pipeline.feature_engineering import engineer_features


def get_pricing_analysis(area: str, cuisine_type: str) -> dict:
    """Return optimal pricing range and price intelligence for a cuisine in an area."""
    df = load_raw_data()
    if df.empty:
        return {"error": "No data"}

    df = clean_data(df)
    df = engineer_features(df)

    subset = df[(df["area"].str.lower() == area.lower()) &
                (df["cuisine_type"].str.lower() == cuisine_type.lower())]
    if subset.empty:
        subset = df[df["cuisine_type"].str.lower() == cuisine_type.lower()]

    if subset.empty:
        return {"area": area, "cuisine_type": cuisine_type, "dishes": []}

    dish_pricing = (
        subset.groupby("dish_name")
        .agg(
            avg_price=("dish_price", "mean"),
            min_price=("dish_price", "min"),
            max_price=("dish_price", "max"),
            demand_score=("demand_score", "mean"),
            price_elasticity=("price_elasticity_score", "mean"),
            price_deviation=("price_deviation", "mean"),
            avg_competitor_price=("avg_price_area", "mean"),
        )
        .reset_index()
    )

    dishes = []
    for _, row in dish_pricing.iterrows():
        elasticity = float(row["price_elasticity"])
        avg = float(row["avg_price"])
        demand = float(row["demand_score"])
        deviation = float(row["price_deviation"])

        # Optimal price: reduce if overpriced & elastic; increase if underpriced & inelastic
        if deviation > 0.1 and elasticity < 0:
            suggested = avg * 0.9
            pricing_action = "Reduce price — you're overpriced vs area average"
        elif deviation < -0.1:
            suggested = avg * 1.1
            pricing_action = "Increase price — gap exists vs competitors"
        else:
            suggested = avg
            pricing_action = "Price is optimal — maintain current pricing"

        dishes.append({
            "dish_name": row["dish_name"],
            "avg_price": round(avg, 2),
            "min_price": round(float(row["min_price"]), 2),
            "max_price": round(float(row["max_price"]), 2),
            "optimal_price": round(suggested, 2),
            "competitor_avg_price": round(float(row["avg_competitor_price"]), 2),
            "price_deviation": round(deviation, 4),
            "price_elasticity_score": round(elasticity, 4),
            "demand_score": round(demand, 4),
            "pricing_action": pricing_action,
        })

    overall_avg = round(subset["dish_price"].mean(), 2)
    return {
        "area": area,
        "cuisine_type": cuisine_type,
        "overall_avg_price": overall_avg,
        "dishes": sorted(dishes, key=lambda x: x["demand_score"], reverse=True),
        "ai_summary": (
            f"In {area}, the average {cuisine_type} meal costs ₹{overall_avg}. "
            f"Focus on high-demand items and review pricing of dishes with high price deviation."
        ),
    }
