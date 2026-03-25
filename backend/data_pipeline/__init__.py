"""
Data pipeline package initialization.
Exports the full pipeline runner and individual stage functions.
"""
from .ingestion import load_raw_data
from .cleaning import clean_data
from .normalization import normalize_data
from .nlp_processing import enrich_nlp_features
from .feature_engineering import engineer_features
from .scoring import compute_scores

__all__ = [
    "load_raw_data",
    "clean_data",
    "normalize_data",
    "enrich_nlp_features",
    "engineer_features",
    "compute_scores",
]
