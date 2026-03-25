"""
Sentiment Engine: Aspect-based sentiment insights for taste, service, price.
"""
import pandas as pd
from data_pipeline.ingestion import load_raw_data
from data_pipeline.cleaning import clean_data
from data_pipeline.nlp_processing import enrich_nlp_features


def get_sentiment_analysis(area: str = "", cuisine_type: str = "") -> dict:
    """Return aspect-level sentiment breakdown."""
    df = load_raw_data()
    if df.empty:
        return {"overall": {}, "aspects": {}}

    df = clean_data(df)
    df = enrich_nlp_features(df)

    subset = df.copy()
    if area:
        subset = subset[subset["area"].str.lower() == area.lower()]
    if cuisine_type:
        subset = subset[subset["cuisine_type"].str.lower() == cuisine_type.lower()]
    if subset.empty:
        subset = df

    def _bucket(score: float) -> str:
        if score >= 0.5:
            return "positive"
        if score >= 0.2:
            return "neutral"
        return "negative"

    overall_sentiment = float(subset["sentiment_score"].mean())
    taste_avg = float(subset["taste_score"].mean())
    service_avg = float(subset["service_score"].mean())
    price_avg = float(subset["price_sentiment"].mean())

    # Distribution
    sentiment_dist = subset["sentiment_score"].apply(
        lambda s: "positive" if s > 0.1 else ("negative" if s < -0.1 else "neutral")
    ).value_counts().to_dict()

    # Cuisine breakdown
    cuisine_sentiment = (
        subset.groupby("cuisine_type")
        .agg(
            sentiment=("sentiment_score", "mean"),
            taste=("taste_score", "mean"),
            service=("service_score", "mean"),
        )
        .reset_index()
        .sort_values("sentiment", ascending=False)
    )

    return {
        "area": area or "All",
        "cuisine_type": cuisine_type or "All",
        "overall_sentiment": round(overall_sentiment, 4),
        "overall_label": _bucket(overall_sentiment),
        "aspects": {
            "taste": {"score": round(taste_avg, 4), "label": _bucket(taste_avg)},
            "service": {"score": round(service_avg, 4), "label": _bucket(service_avg)},
            "price": {"score": round(price_avg, 4), "label": _bucket(price_avg + 0.5)},
        },
        "sentiment_distribution": {
            "positive": int(sentiment_dist.get("positive", 0)),
            "neutral": int(sentiment_dist.get("neutral", 0)),
            "negative": int(sentiment_dist.get("negative", 0)),
        },
        "by_cuisine": [
            {
                "cuisine_type": r["cuisine_type"],
                "sentiment": round(float(r["sentiment"]), 4),
                "taste": round(float(r["taste"]), 4),
                "service": round(float(r["service"]), 4),
            }
            for _, r in cuisine_sentiment.head(10).iterrows()
        ],
        "ai_summary": (
            f"Overall sentiment is {_bucket(overall_sentiment)} ({overall_sentiment:.3f}). "
            f"Taste scores well at {taste_avg:.3f} while service at {service_avg:.3f} "
            f"{'needs attention' if service_avg < 0.5 else 'is strong'}."
        ),
    }
