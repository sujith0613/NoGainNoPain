"""
Stage 6 – Scoring: Compute Opportunity Score, Risk Score, Profitability Score.
"""
import pandas as pd
import numpy as np


def compute_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute the three master scores used throughout the decision engine:

    opportunity_score = (demand_score × sentiment_score × demand_growth_rate) / supply_count
    risk_score        = 0.4×competition + 0.3×negative_sentiment + 0.3×|price_elasticity|
    profitability_score = avg_price × demand_score × sentiment_score
    """
    if df.empty:
        return df
    df = df.copy()

    # Safe versions of required columns
    demand = df.get("demand_score", pd.Series(0, index=df.index)).fillna(0).clip(0, 1)
    sentiment = df.get("sentiment_score", pd.Series(0, index=df.index)).fillna(0)
    growth = df.get("demand_growth_rate", pd.Series(0.1, index=df.index)).fillna(0.1)
    supply = df.get("supply_count", pd.Series(1, index=df.index)).fillna(1).clip(lower=1)
    competition = df.get("area_competition_score", pd.Series(0.5, index=df.index)).fillna(0.5).clip(0, 1)
    elasticity = df.get("price_elasticity_score", pd.Series(0, index=df.index)).fillna(0)
    avg_price = df.get("avg_price_area", df.get("dish_price", pd.Series(200, index=df.index))).fillna(200)

    # Opportunity Score: higher is more attractive
    df["opportunity_score"] = (
        (demand * sentiment.clip(lower=0) * growth.clip(lower=0.01)) / supply
    ).round(6)

    # Risk Score: higher is more risky
    negative_sentiment_ratio = sentiment.apply(lambda x: max(-x, 0))
    df["risk_score"] = (
        0.4 * competition +
        0.3 * negative_sentiment_ratio +
        0.3 * elasticity.abs()
    ).clip(0, 1).round(4)

    # Profitability Score
    df["profitability_score"] = (
        avg_price * demand * sentiment.clip(lower=0)
    ).round(4)

    # Performance Score (used in competitor module) — weighted composite
    rating_n = df.get("normalized_rating", pd.Series(0.5, index=df.index)).fillna(0.5)
    taste = df.get("taste_score", pd.Series(0.5, index=df.index)).fillna(0.5)
    service = df.get("service_score", pd.Series(0.5, index=df.index)).fillna(0.5)
    review_cnt_norm = df.get("review_count_norm", pd.Series(0.5, index=df.index)).fillna(0.5)

    df["performance_score"] = (
        0.3 * rating_n.clip(0, 1) +
        0.2 * demand.clip(0, 1) +
        0.2 * taste.clip(0, 1) +
        0.15 * service.clip(0, 1) +
        0.15 * growth.clip(-1, 1).apply(lambda x: (x + 1) / 2)
    ).clip(0, 1).round(4)

    return df
