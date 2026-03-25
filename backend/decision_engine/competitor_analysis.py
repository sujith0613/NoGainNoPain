"""
Competitor Analysis Module:
- Identify competitors (same area + cuisine)
- Compute competitor aggregates
- Performance score + ranking
- Improvement recommendations
- Gap analysis
"""
import pandas as pd
import numpy as np
from data_pipeline.ingestion import load_raw_data
from data_pipeline.cleaning import clean_data
from data_pipeline.normalization import normalize_data
from data_pipeline.nlp_processing import enrich_nlp_features
from data_pipeline.feature_engineering import engineer_features
from data_pipeline.scoring import compute_scores


def _load_enriched() -> pd.DataFrame:
    df = load_raw_data()
    if df.empty:
        return df
    df = clean_data(df)
    df = normalize_data(df)
    df = enrich_nlp_features(df)
    df = engineer_features(df)
    df = compute_scores(df)
    return df


def get_competitor_analysis(restaurant_name: str = "", restaurant_id: str = "", area: str = "", cuisine_type: str = "") -> dict:
    """Identify competitors and compute comparison metrics."""
    df = _load_enriched()
    if df.empty:
        return {"error": "No data"}

    # Find the target restaurant
    if restaurant_id:
        target_rows = df[df["restaurant_id"] == restaurant_id]
    elif restaurant_name:
        target_rows = df[df["restaurant_name"].str.lower().str.contains(restaurant_name.lower(), na=False)]
    else:
        return {"error": "Provide restaurant_name or restaurant_id"}

    if target_rows.empty:
        return {"error": f"Restaurant '{restaurant_name or restaurant_id}' not found"}

    # Take first match as target
    target = target_rows.iloc[0]
    t_area = area or target["area"]
    t_cuisine = cuisine_type or target["cuisine_type"]

    # Target aggregated stats
    target_stats = target_rows.agg({
        "rating": "mean",
        "normalized_rating": "mean",
        "demand_score": "mean",
        "sentiment_score": "mean",
        "taste_score": "mean",
        "service_score": "mean",
        "price_sentiment": "mean",
        "dish_price": "mean",
        "demand_growth_rate": "mean",
        "review_growth_rate": "mean",
        "performance_score": "mean",
    }).to_dict()

    # Competitors: same area + cuisine, exclude target
    competitors_df = df[
        (df["area"].str.lower() == t_area.lower()) &
        (df["cuisine_type"].str.lower() == t_cuisine.lower()) &
        (~df["restaurant_id"].isin(target_rows["restaurant_id"].unique()))
    ]

    if competitors_df.empty:
        competitors_df = df[
            (df["cuisine_type"].str.lower() == t_cuisine.lower()) &
            (~df["restaurant_id"].isin(target_rows["restaurant_id"].unique()))
        ]

    competitor_stats = competitors_df.agg({
        "rating": "mean",
        "demand_score": "mean",
        "sentiment_score": "mean",
        "taste_score": "mean",
        "service_score": "mean",
        "dish_price": "mean",
        "demand_growth_rate": "mean",
        "performance_score": "mean",
    }).to_dict()

    # Top competitors by performance
    top_competitors = (
        competitors_df.groupby("restaurant_name")
        .agg(
            avg_rating=("rating", "mean"),
            avg_price=("dish_price", "mean"),
            demand_score=("demand_score", "mean"),
            sentiment_score=("sentiment_score", "mean"),
            performance_score=("performance_score", "mean"),
        )
        .reset_index()
        .sort_values("performance_score", ascending=False)
        .head(5)
    )

    return {
        "restaurant_name": str(target["restaurant_name"]),
        "restaurant_id": str(target["restaurant_id"]),
        "area": t_area,
        "cuisine_type": t_cuisine,
        "target_metrics": {k: round(float(v), 4) for k, v in target_stats.items()},
        "competitor_metrics": {k: round(float(v), 4) for k, v in competitor_stats.items()},
        "top_competitors": [
            {
                "name": r["restaurant_name"],
                "avg_rating": round(float(r["avg_rating"]), 2),
                "avg_price": round(float(r["avg_price"]), 2),
                "demand_score": round(float(r["demand_score"]), 4),
                "sentiment_score": round(float(r["sentiment_score"]), 4),
                "performance_score": round(float(r["performance_score"]), 4),
            }
            for _, r in top_competitors.iterrows()
        ],
        "competitor_count": competitors_df["restaurant_id"].nunique(),
    }


def get_performance_score(restaurant_name: str = "", restaurant_id: str = "") -> dict:
    """Compute performance score, ranking, and percentile for a restaurant."""
    df = _load_enriched()
    if df.empty:
        return {"error": "No data"}

    if restaurant_id:
        target_rows = df[df["restaurant_id"] == restaurant_id]
    else:
        target_rows = df[df["restaurant_name"].str.lower().str.contains(restaurant_name.lower(), na=False)]

    if target_rows.empty:
        return {"error": "Restaurant not found"}

    target = target_rows.iloc[0]
    t_area = target["area"]
    t_cuisine = target["cuisine_type"]
    t_perf = float(target_rows["performance_score"].mean())

    # Area+cuisine peers
    peers = df[
        (df["area"].str.lower() == t_area.lower()) &
        (df["cuisine_type"].str.lower() == t_cuisine.lower())
    ]
    if peers.empty:
        peers = df[df["cuisine_type"].str.lower() == t_cuisine.lower()]

    peer_perf = peers.groupby("restaurant_id")["performance_score"].mean().reset_index()
    peer_perf = peer_perf.sort_values("performance_score", ascending=False).reset_index(drop=True)
    total = len(peer_perf)
    rank_row = peer_perf[peer_perf["restaurant_id"] == target["restaurant_id"]]
    rank = int(rank_row.index[0]) + 1 if not rank_row.empty else total
    percentile = round((1 - rank / total) * 100, 1) if total > 0 else 0

    return {
        "restaurant_name": str(target["restaurant_name"]),
        "restaurant_id": str(target["restaurant_id"]),
        "area": t_area,
        "cuisine_type": t_cuisine,
        "performance_score": round(t_perf, 4),
        "rank_in_area": rank,
        "total_competitors": total,
        "percentile_rank": percentile,
        "breakdown": {
            "rating": round(float(target_rows["normalized_rating"].mean()), 4),
            "demand": round(float(target_rows["demand_score"].mean()), 4),
            "taste": round(float(target_rows["taste_score"].mean()), 4),
            "service": round(float(target_rows["service_score"].mean()), 4),
            "growth": round(float(target_rows["demand_growth_rate"].mean()), 4),
        },
    }


def get_improvement_recommendations(restaurant_name: str = "", restaurant_id: str = "") -> dict:
    """Generate actionable improvement recommendations for a restaurant."""
    df = _load_enriched()
    if df.empty:
        return {"recommendations": []}

    if restaurant_id:
        target_rows = df[df["restaurant_id"] == restaurant_id]
    else:
        target_rows = df[df["restaurant_name"].str.lower().str.contains(restaurant_name.lower(), na=False)]

    if target_rows.empty:
        return {"recommendations": []}

    target = target_rows.iloc[0]
    t_area = target["area"]
    t_cuisine = target["cuisine_type"]

    competitors_df = df[
        (df["area"].str.lower() == t_area.lower()) &
        (df["cuisine_type"].str.lower() == t_cuisine.lower()) &
        (~df["restaurant_id"].isin(target_rows["restaurant_id"].unique()))
    ]
    if competitors_df.empty:
        competitors_df = df[df["cuisine_type"].str.lower() == t_cuisine.lower()]

    target_avg = target_rows[["rating", "demand_score", "sentiment_score",
                               "taste_score", "service_score", "price_sentiment",
                               "dish_price", "demand_growth_rate"]].mean()
    comp_avg = competitors_df[["rating", "demand_score", "sentiment_score",
                                "taste_score", "service_score", "price_sentiment",
                                "dish_price"]].mean()

    recs = []
    priority = 1

    if target_avg["dish_price"] > comp_avg["dish_price"] * 1.1:
        recs.append({
            "priority": priority,
            "area": "Pricing",
            "insight": "You are overpriced vs competitors",
            "action": f"Consider reducing average price by 8-15% to improve demand. "
                      f"Your avg: ₹{target_avg['dish_price']:.0f}, Market avg: ₹{comp_avg['dish_price']:.0f}",
            "impact": "High",
        })
        priority += 1

    if target_avg["service_score"] < 0.5:
        recs.append({
            "priority": priority,
            "area": "Service Quality",
            "insight": "Service score is below acceptable threshold",
            "action": "Invest in staff training, reduce wait times, implement feedback system",
            "impact": "High",
        })
        priority += 1

    if target_avg["taste_score"] < comp_avg["taste_score"] - 0.05:
        recs.append({
            "priority": priority,
            "area": "Food Quality",
            "insight": "Taste score lags behind competitors",
            "action": "Review recipes, source fresher ingredients, hire experienced chef",
            "impact": "High",
        })
        priority += 1

    if target_avg["demand_growth_rate"] < 0:
        recs.append({
            "priority": priority,
            "area": "Demand Growth",
            "insight": "Declining customer demand trend detected",
            "action": "Launch promotions, introduce new menu items, boost online presence",
            "impact": "Medium",
        })
        priority += 1

    if target_avg["rating"] < comp_avg["rating"] - 0.3:
        recs.append({
            "priority": priority,
            "area": "Overall Rating",
            "insight": f"Rating ({target_avg['rating']:.1f}) is below area average ({comp_avg['rating']:.1f})",
            "action": "Actively request reviews, resolve negative feedback, improve consistency",
            "impact": "Medium",
        })
        priority += 1

    if target_avg["demand_score"] < comp_avg["demand_score"] - 0.1:
        recs.append({
            "priority": priority,
            "area": "Menu Expansion",
            "insight": "Demand is lower than competitors",
            "action": "Add trending dishes from competitor menus, introduce combo offers",
            "impact": "Medium",
        })
        priority += 1

    # Peak hour suggestion
    recs.append({
        "priority": priority,
        "area": "Peak Hour Strategy",
        "insight": "Maximize revenue during lunch (12–14) and dinner (19–22) hours",
        "action": "Launch happy hour deals, pre-booking offers, peak-time staffing",
        "impact": "Low",
    })

    return {
        "restaurant_name": str(target["restaurant_name"]),
        "restaurant_id": str(target["restaurant_id"]),
        "recommendations": recs,
        "ai_summary": (
            f"Top priority: {recs[0]['area']} — {recs[0]['action']}" if recs else "No recommendations."
        ),
    }


def get_gap_analysis(restaurant_name: str = "", restaurant_id: str = "") -> dict:
    """Identify missing dishes and weak sentiment areas vs competitors."""
    df = _load_enriched()
    if df.empty:
        return {"gaps": []}

    if restaurant_id:
        target_rows = df[df["restaurant_id"] == restaurant_id]
    else:
        target_rows = df[df["restaurant_name"].str.lower().str.contains(restaurant_name.lower(), na=False)]

    if target_rows.empty:
        return {"gaps": []}

    target = target_rows.iloc[0]
    t_cuisine = target["cuisine_type"]
    t_area = target["area"]

    my_dishes = set(target_rows["dish_name"].str.lower().unique())

    # Competitor popular dishes
    competitors_df = df[
        (df["area"].str.lower() == t_area.lower()) &
        (df["cuisine_type"].str.lower() == t_cuisine.lower()) &
        (~df["restaurant_id"].isin(target_rows["restaurant_id"].unique()))
    ]
    if competitors_df.empty:
        competitors_df = df[df["cuisine_type"].str.lower() == t_cuisine.lower()]

    popular_competitor_dishes = (
        competitors_df[~competitors_df["dish_name"].str.lower().isin(my_dishes)]
        .groupby("dish_name")
        .agg(
            avg_demand=("demand_score", "mean"),
            avg_sentiment=("sentiment_score", "mean"),
            avg_price=("dish_price", "mean"),
            count=("restaurant_id", "count"),
        )
        .reset_index()
        .sort_values("avg_demand", ascending=False)
        .head(10)
    )

    # Weak sentiment areas
    weak_aspects = []
    for aspect in ["taste_score", "service_score", "price_sentiment"]:
        if aspect in target_rows.columns:
            my_val = float(target_rows[aspect].mean())
            comp_val = float(competitors_df[aspect].mean()) if aspect in competitors_df.columns else 0.5
            if my_val < comp_val - 0.05:
                label = aspect.replace("_score", "").replace("_sentiment", "")
                weak_aspects.append({
                    "aspect": label,
                    "my_score": round(my_val, 4),
                    "competitor_avg": round(comp_val, 4),
                    "gap": round(comp_val - my_val, 4),
                })

    return {
        "restaurant_name": str(target["restaurant_name"]),
        "restaurant_id": str(target["restaurant_id"]),
        "missing_dishes": [
            {
                "dish_name": row["dish_name"],
                "competitor_avg_demand": round(float(row["avg_demand"]), 4),
                "competitor_avg_price": round(float(row["avg_price"]), 2),
                "offered_by_n_competitors": int(row["count"]),
            }
            for _, row in popular_competitor_dishes.iterrows()
        ],
        "weak_sentiment_areas": weak_aspects,
        "total_my_dishes": len(my_dishes),
        "ai_summary": (
            f"You are missing {len(popular_competitor_dishes)} popular dishes "
            f"that competitors offer. Top gap: {popular_competitor_dishes.iloc[0]['dish_name']}. "
            f"Weak areas: {', '.join([a['aspect'] for a in weak_aspects]) or 'None'}."
            if not popular_competitor_dishes.empty else "Gap analysis complete."
        ),
    }
