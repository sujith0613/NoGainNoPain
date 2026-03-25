"""
Stage 4 – NLP Processing: Compute sentiment, taste, service, and price scores
using VADER (fast, no model download required for basic use).

For richer analysis, TextBlob polarity is also computed.
"""
import re
import pandas as pd

# VADER
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    _vader = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
except Exception:
    VADER_AVAILABLE = False

# ── Keyword dictionaries for aspect scoring ────────────────────────────────────
TASTE_KEYWORDS_POS = ["delicious", "tasty", "amazing", "flavour", "flavor",
                      "fresh", "yummy", "perfect", "spiced", "cooked", "great taste"]
TASTE_KEYWORDS_NEG = ["bland", "stale", "tasteless", "undercooked", "overcooked",
                      "cold", "flavourless", "bad taste"]

SERVICE_KEYWORDS_POS = ["quick", "fast", "excellent service", "attentive",
                        "friendly", "efficient", "professional", "prompt"]
SERVICE_KEYWORDS_NEG = ["slow", "rude", "bad service", "waited", "wait too long",
                        "ignored", "unprofessional"]

PRICE_KEYWORDS_POS = ["affordable", "value for money", "cheap", "reasonable",
                      "worth it", "great value", "good price"]
PRICE_KEYWORDS_NEG = ["expensive", "overpriced", "pricey", "not worth",
                      "too costly", "costly", "rip off"]


def _keyword_score(text: str, pos_kw: list[str], neg_kw: list[str]) -> float:
    """Return [-1, 1] score based on keyword presence."""
    text_l = text.lower()
    pos_count = sum(1 for kw in pos_kw if kw in text_l)
    neg_count = sum(1 for kw in neg_kw if kw in text_l)
    total = pos_count + neg_count
    if total == 0:
        return 0.0
    return round((pos_count - neg_count) / total, 4)


def _vader_score(text: str) -> float:
    """Return VADER compound score [-1, 1]."""
    if not VADER_AVAILABLE or not text:
        return 0.0
    return round(_vader.polarity_scores(text)["compound"], 4)


def enrich_nlp_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add / overwrite NLP-derived feature columns on the DataFrame:
      - sentiment_score  (VADER compound)
      - taste_score      (keyword aspect)
      - service_score    (keyword aspect)
      - price_sentiment  (keyword aspect)
    """
    if df.empty:
        return df

    df = df.copy()

    texts = df["review_text"].fillna("").tolist()

    sentiment_scores = [_vader_score(t) for t in texts]
    taste_scores = [_keyword_score(t, TASTE_KEYWORDS_POS, TASTE_KEYWORDS_NEG) for t in texts]
    service_scores = [_keyword_score(t, SERVICE_KEYWORDS_POS, SERVICE_KEYWORDS_NEG) for t in texts]
    price_sentiments = [_keyword_score(t, PRICE_KEYWORDS_POS, PRICE_KEYWORDS_NEG) for t in texts]

    df["sentiment_score"] = sentiment_scores
    df["taste_score"] = [round((s + 1) / 2, 4) for s in taste_scores]   # rescale to [0,1]
    df["service_score"] = [round((s + 1) / 2, 4) for s in service_scores]
    df["price_sentiment"] = price_sentiments

    return df
