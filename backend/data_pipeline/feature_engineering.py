"""
Stage 5 – Feature Engineering: Compute all derived features from cleaned data.
This module handles demand/supply, pricing intelligence, trend, time, combo,
and location features.
"""
import pandas as pd
import numpy as np
from itertools import combinations


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all derived feature columns to the DataFrame using group aggregations.
    Works on a per-record basis using group stats.
    """
    if df.empty:
        return df
    df = df.copy()

    # ── Demand & Supply ────────────────────────────────────────────────────────
    # supply_count: how many restaurants in same area+cuisine serve this dish
    area_cuisine_supply = (
        df.groupby(["area", "cuisine_type", "dish_name"])["restaurant_id"]
        .nunique()
        .reset_index()
        .rename(columns={"restaurant_id": "supply_count_derived"})
    )
    df = df.merge(area_cuisine_supply, on=["area", "cuisine_type", "dish_name"], how="left")
    df["supply_count"] = df["supply_count_derived"].fillna(1).astype(int)
    df.drop(columns=["supply_count_derived"], inplace=True)

    # dish_mentions: count of records for this dish in area
    dish_mentions_map = (
        df.groupby(["area", "dish_name"])
        .size()
        .reset_index()
        .rename(columns={0: "dish_mentions_derived"})
    )
    df = df.merge(dish_mentions_map, on=["area", "dish_name"], how="left")
    df["dish_mentions"] = df["dish_mentions_derived"].fillna(1).astype(int)
    df.drop(columns=["dish_mentions_derived"], inplace=True)

    # dish_frequency: dish_mentions / total records in area
    area_total = df.groupby("area").size().reset_index().rename(columns={0: "area_total"})
    df = df.merge(area_total, on="area", how="left")
    df["dish_frequency"] = (df["dish_mentions"] / df["area_total"]).round(4)
    df.drop(columns=["area_total"], inplace=True)

    # demand_score (weighted composite)
    df["demand_score"] = (
        0.4 * df["normalized_rating"].clip(0, 1) +
        0.3 * (df["dish_mentions"] / df["dish_mentions"].max()).clip(0, 1) +
        0.3 * df["sentiment_score"].clip(-1, 1).apply(lambda x: max(x, 0))
    ).round(4)

    # ── Pricing Intelligence ───────────────────────────────────────────────────
    if "avg_price_area" in df.columns:
        df.drop(columns=["avg_price_area"], inplace=True)
    area_avg_price = (
        df.groupby(["area", "cuisine_type"])["dish_price"]
        .mean()
        .reset_index()
        .rename(columns={"dish_price": "avg_price_area"})
    )
    df = df.merge(area_avg_price, on=["area", "cuisine_type"], how="left")
    df["avg_price_area"] = df["avg_price_area"].round(2)
    df["price_deviation"] = ((df["dish_price"] - df["avg_price_area"]) / (df["avg_price_area"] + 1e-9)).round(4)

    # price_elasticity_score: negative of demand_score × price_deviation (higher price → lower demand)
    df["price_elasticity_score"] = (-df["price_deviation"] * df["demand_score"]).round(4)

    # ── Location Intelligence ──────────────────────────────────────────────────
    if "area_demand_score" in df.columns:
        df.drop(columns=["area_demand_score"], inplace=True)
    area_demand = (
        df.groupby("area")["demand_score"]
        .mean()
        .reset_index()
        .rename(columns={"demand_score": "area_demand_score"})
    )
    df = df.merge(area_demand, on="area", how="left")
    df["area_demand_score"] = df["area_demand_score"].round(4)

    area_competition = (
        df.groupby("area")["restaurant_id"]
        .nunique()
        .reset_index()
        .rename(columns={"restaurant_id": "area_restaurant_count"})
    )
    df = df.merge(area_competition, on="area", how="left")
    max_rest = df["area_restaurant_count"].max()
    df["area_competition_score"] = (df["area_restaurant_count"] / (max_rest + 1e-9)).round(4)

    if "area_popularity_rank" in df.columns:
        df.drop(columns=["area_popularity_rank"], inplace=True)
    area_rank = (
        df.groupby("area")["area_demand_score"]
        .first()
        .rank(ascending=False, method="min")
        .reset_index()
        .rename(columns={"area_demand_score": "area_popularity_rank"})
    )
    df = df.merge(area_rank, on="area", how="left")
    df["area_popularity_rank"] = df["area_popularity_rank"].fillna(99).astype(int)

    # ── Peak Hour ──────────────────────────────────────────────────────────────
    if "hour_of_day" not in df.columns and "timestamp" in df.columns:
        df["hour_of_day"] = pd.to_datetime(df["timestamp"]).dt.hour

    def _peak(h):
        if pd.isna(h):
            return 0.3
        if 12 <= h <= 14:
            return 1.0
        if 19 <= h <= 22:
            return 0.9
        if 8 <= h <= 10:
            return 0.5
        return 0.3

    df["peak_hour_score"] = df["hour_of_day"].apply(_peak)
    df["daily_demand"] = (df["demand_score"] * df["peak_hour_score"] * 1.0).round(4)

    # ── Combo Score ────────────────────────────────────────────────────────────
    # Simple association score based on dish co-occurrence in same restaurant
    from typing import Dict
    restaurant_dishes = df.groupby("restaurant_id")["dish_name"].apply(list)
    co_occur: Dict[tuple, int] = {}
    for dishes in restaurant_dishes:
        unique = list(set(dishes))
        for a, b in combinations(unique, 2):
            key = tuple(sorted([a, b]))
            co_occur[key] = co_occur.get(key, 0) + 1

    max_co = max(co_occur.values(), default=1)
    
    # Precompute best co-occurrence for each dish
    best_co_for_dish = {}
    for (a, b), cnt in co_occur.items():
        best_co_for_dish[a] = max(best_co_for_dish.get(a, 0), cnt)
        best_co_for_dish[b] = max(best_co_for_dish.get(b, 0), cnt)
        
    df["combo_score"] = df["dish_name"].map(lambda d: round(best_co_for_dish.get(d, 0) / (max_co + 1e-9), 4))
    df["association_strength"] = (df["combo_score"] * 0.9).round(4)

    # Clean up helper col
    if "area_restaurant_count" in df.columns:
        df.drop(columns=["area_restaurant_count"], inplace=True)

    return df

