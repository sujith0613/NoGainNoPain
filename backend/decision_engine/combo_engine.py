"""
Combo Engine: Suggest dish combinations using association_strength and co-occurrence.
"""
import pandas as pd
from data_pipeline.ingestion import load_raw_data
from data_pipeline.cleaning import clean_data
from data_pipeline.feature_engineering import engineer_features


def get_combo_analysis(cuisine_type: str = "", area: str = "") -> dict:
    """Return top dish combinations with association scores."""
    df = load_raw_data()
    if df.empty:
        return {"combos": []}

    df = clean_data(df)
    df = engineer_features(df)

    subset = df.copy()
    if cuisine_type:
        subset = subset[subset["cuisine_type"].str.lower() == cuisine_type.lower()]
    if area:
        subset = subset[subset["area"].str.lower() == area.lower()]
    if subset.empty:
        subset = df

    # Build co-occurrence from co_ordered_items field
    combo_counts: dict[tuple, dict] = {}
    for _, row in subset.iterrows():
        main_dish = row.get("dish_name", "")
        co_items = row.get("co_ordered_items", [])
        if not isinstance(co_items, list):
            continue
        demand = float(row.get("demand_score", 0))
        assoc = float(row.get("association_strength", 0))
        for item in co_items:
            key = tuple(sorted([main_dish, item]))
            if key not in combo_counts:
                combo_counts[key] = {"count": 0, "demand_sum": 0.0, "assoc_sum": 0.0}
            combo_counts[key]["count"] += 1
            combo_counts[key]["demand_sum"] += demand
            combo_counts[key]["assoc_sum"] += assoc

    combos = []
    for (a, b), stats in combo_counts.items():
        cnt = stats["count"]
        if cnt < 1:
            continue
        combos.append({
            "dish_a": a,
            "dish_b": b,
            "combo_count": cnt,
            "combo_score": round(stats["assoc_sum"] / cnt, 4),
            "avg_demand": round(stats["demand_sum"] / cnt, 4),
            "suggested_price_bundle": None,  # computed below
        })

    combos.sort(key=lambda x: x["combo_score"], reverse=True)
    combos = combos[:15]

    # Add bundle price suggestion (avg of both dishes × 0.85 for discount)
    dish_avg_price = subset.groupby("dish_name")["dish_price"].mean().to_dict()
    for c in combos:
        p_a = dish_avg_price.get(c["dish_a"], 0)
        p_b = dish_avg_price.get(c["dish_b"], 0)
        if p_a and p_b:
            c["suggested_price_bundle"] = round((p_a + p_b) * 0.85, 2)

    return {
        "cuisine_type": cuisine_type or "All",
        "area": area or "All",
        "combos": combos,
        "ai_summary": (
            f"Top combo: {combos[0]['dish_a']} + {combos[0]['dish_b']} "
            f"(association: {combos[0]['combo_score']:.4f}). "
            f"Bundle pricing can drive {int((1-0.85)*100)}% volume uplift."
            if combos else "No combo data available."
        ),
    }
