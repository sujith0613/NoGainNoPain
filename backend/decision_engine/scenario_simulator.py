"""
Scenario Simulator: Simulate adding a new restaurant in an area and
predict the market impact (opportunity score change, competition impact).
"""
import pandas as pd
import numpy as np
from data_pipeline.ingestion import load_raw_data
from data_pipeline.cleaning import clean_data
from data_pipeline.feature_engineering import engineer_features
from data_pipeline.scoring import compute_scores


def simulate_scenario(area: str, cuisine_type: str, budget: float) -> dict:
    """
    Simulate adding a new restaurant and predict key metric changes.
    Returns before/after comparison for opportunity score, competition, and profitability.
    """
    df = load_raw_data()
    if df.empty:
        return {"error": "No data"}

    df = clean_data(df)
    df = engineer_features(df)
    df = compute_scores(df)

    # Before state: stats for this area+cuisine
    subset = df[
        (df["area"].str.lower() == area.lower()) &
        (df["cuisine_type"].str.lower() == cuisine_type.lower())
    ]
    if subset.empty:
        subset = df[df["area"].str.lower() == area.lower()]

    before = {
        "supply_count": int(subset["supply_count"].mean()) if not subset.empty else 0,
        "opportunity_score": round(float(subset["opportunity_score"].mean()), 6) if not subset.empty else 0,
        "competition_density": round(float(subset["area_competition_score"].mean()), 4) if not subset.empty else 0,
        "avg_demand": round(float(subset["demand_score"].mean()), 4) if not subset.empty else 0,
        "avg_sentiment": round(float(subset["sentiment_score"].mean()), 4) if not subset.empty else 0,
    }

    # Simulate adding 1 more restaurant → increases supply_count → reduces opportunity_score
    new_supply = before["supply_count"] + 1
    sim_opportunity = round(
        before["opportunity_score"] * before["supply_count"] / max(new_supply, 1), 6
    )
    sim_competition = round(min(before["competition_density"] * 1.05, 1.0), 4)

    # Budget-based viability
    estimated_revenue_monthly = round(
        before["avg_demand"] * 50000 * max(before["avg_sentiment"], 0.1), 2
    )
    roi_months = round(budget / max(estimated_revenue_monthly, 1), 1)

    after = {
        "supply_count": new_supply,
        "opportunity_score": sim_opportunity,
        "competition_density": sim_competition,
        "avg_demand": before["avg_demand"],
        "avg_sentiment": before["avg_sentiment"],
    }

    viable = roi_months <= 24 and sim_opportunity > 0.001

    return {
        "area": area,
        "cuisine_type": cuisine_type,
        "budget": budget,
        "before": before,
        "after": after,
        "delta": {
            "opportunity_score_change": round(sim_opportunity - before["opportunity_score"], 6),
            "competition_impact": round(sim_competition - before["competition_density"], 4),
        },
        "estimated_monthly_revenue": estimated_revenue_monthly,
        "roi_months": roi_months,
        "viability": "Viable" if viable else "High Risk",
        "ai_summary": (
            f"Adding a new {cuisine_type} restaurant in {area} will "
            f"{'reduce' if sim_opportunity < before['opportunity_score'] else 'maintain'} "
            f"the opportunity score from {before['opportunity_score']:.4f} to {sim_opportunity:.4f}. "
            f"Estimated ROI in {roi_months} months. Verdict: {'✅ Viable' if viable else '⚠️ High Risk'}."
        ),
    }
