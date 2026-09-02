import json
import pickle
import joblib
import pandas as pd
import streamlit as st
from core.config import DATA_FILE, MODEL_DIR

@st.cache_data
def load_products():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    except FileNotFoundError:
        return pd.DataFrame(columns=["asin", "title", "brand", "price", "rating",
                                     "review_count", "main_image_url",
                                     "search_keyword", "reviews", "bullet_points"])

@st.cache_resource
def load_feature_a():
    try:
        with open(MODEL_DIR / "feature_a_tfidf.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None

@st.cache_resource
def load_feature_b():
    try:
        return joblib.load(MODEL_DIR / "feature_b_sentiment_model.joblib")
    except FileNotFoundError:
        return None

@st.cache_data
def load_feature_c():
    try:
        return pd.read_csv(MODEL_DIR / "feature_c_clusters.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["asin", "cluster", "category"])

@st.cache_resource
def load_feature_d():
    try:
        return joblib.load(MODEL_DIR / "feature_d_price_tier_pipeline.joblib")
    except FileNotFoundError:
        return None