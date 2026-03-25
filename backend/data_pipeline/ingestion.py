"""
Stage 1 – Ingestion: Load raw records from MongoDB into a Pandas DataFrame.
"""
import pandas as pd
from typing import Optional
from pymongo import MongoClient
from config import MONGODB_URL, DATABASE_NAME, COLLECTION_NAME


def load_raw_data(filters: Optional[dict] = None) -> pd.DataFrame:
    """
    Fetch documents from MongoDB and return as a DataFrame.

    Args:
        filters: Optional pymongo query filter dict.
    Returns:
        Raw DataFrame with all stored fields.
    """
    client = MongoClient(MONGODB_URL)
    db = client[DATABASE_NAME]
    col = db[COLLECTION_NAME]
    query = filters or {}
    docs = list(col.find(query, {"_id": 0}))
    client.close()
    if not docs:
        return pd.DataFrame()
    return pd.DataFrame(docs)
