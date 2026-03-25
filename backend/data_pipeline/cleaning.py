"""
Stage 2 – Cleaning: Remove nulls, fix types, deduplicate.
"""
import pandas as pd
import numpy as np


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean a raw DataFrame:
    - Drop rows with missing critical fields
    - Coerce numeric types
    - Clip values to valid ranges
    - Remove exact duplicates
    """
    if df.empty:
        return df

    critical_fields = ["restaurant_id", "restaurant_name", "area", "city", "cuisine_type", "dish_name"]
    df = df.dropna(subset=critical_fields)

    # Numeric coercion
    numeric_cols = [
        "dish_price", "rating", "review_count", "sentiment_score",
        "taste_score", "price_sentiment", "service_score", "demand_score",
        "supply_count", "avg_price_area", "price_deviation", "price_elasticity_score",
        "review_growth_rate", "demand_growth_rate", "opportunity_score",
        "risk_score", "profitability_score", "latitude", "longitude",
        "area_demand_score", "area_competition_score",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Clip to valid ranges
    if "rating" in df.columns:
        df["rating"] = df["rating"].clip(1.0, 5.0)
    if "normalized_rating" in df.columns:
        df["normalized_rating"] = df["normalized_rating"].clip(0.0, 1.0)
    if "sentiment_score" in df.columns:
        df["sentiment_score"] = df["sentiment_score"].clip(-1.0, 1.0)
    if "dish_price" in df.columns:
        df["dish_price"] = df["dish_price"].clip(1, 10000)

    # Fill remaining numerics with median
    df[numeric_cols] = df[numeric_cols].apply(lambda c: c.fillna(c.median()) if c.name in df.columns else c)

    # Boolean flags
    if "is_veg" in df.columns:
        df["is_veg"] = df["is_veg"].fillna(False).astype(bool)
    if "weekend_flag" in df.columns:
        df["weekend_flag"] = df["weekend_flag"].fillna(False).astype(bool)
    if "new_dish_flag" in df.columns:
        df["new_dish_flag"] = df["new_dish_flag"].fillna(False).astype(bool)

    # String cleanup
    str_cols = ["restaurant_name", "area", "city", "cuisine_type", "dish_name", "review_text"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].fillna("").str.strip()

    # Drop exact duplicates using critical fields to avoid unhashable lists
    df = df.drop_duplicates(subset=critical_fields)
    df = df.reset_index(drop=True)

    return df
