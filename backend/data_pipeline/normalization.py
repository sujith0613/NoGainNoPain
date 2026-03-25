"""
Stage 3 – Normalization: Scale and normalize features to [0,1] or [-1,1] ranges.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def normalize_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize key numeric columns using Min-Max scaling and compute
    normalized_rating from raw rating.

    Args:
        df: Cleaned DataFrame
    Returns:
        DataFrame with normalized columns added
    """
    if df.empty:
        return df

    df = df.copy()

    # Normalize rating → [0, 1]
    if "rating" in df.columns:
        df["normalized_rating"] = ((df["rating"] - 1) / 4).clip(0.0, 1.0).round(4)

    # Normalize dish_price within area (relative pricing)
    if "dish_price" in df.columns and "area" in df.columns:
        df["price_norm"] = df.groupby("area")["dish_price"].transform(
            lambda x: ((x - x.min()) / (x.max() - x.min() + 1e-9)).round(4)
        )

    # Min-Max scale demand & supply scores to [0, 1]
    scaler_cols = ["demand_score", "supply_count", "area_demand_score", "area_competition_score"]
    scaler = MinMaxScaler()
    available = [c for c in scaler_cols if c in df.columns and df[c].notna().any()]
    if available:
        scaled = scaler.fit_transform(df[available].fillna(0))
        for i, col in enumerate(available):
            df[f"{col}_norm"] = np.round(scaled[:, i], 4)

    # Normalize review_count to log-scale [0, 1]
    if "review_count" in df.columns:
        max_log = np.log1p(df["review_count"].max())
        df["review_count_norm"] = (np.log1p(df["review_count"]) / (max_log + 1e-9)).round(4)

    return df
