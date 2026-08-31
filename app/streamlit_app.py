import json
import pickle
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration & Paths ---
ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "cleaned" / "products_cleaned.json"
MODEL_DIR = ROOT / "models"

st.set_page_config(page_title="Product Intelligence", layout="wide")

# --- Loaders ---
@st.cache_data
def load_products():
    try:
        with open(DATA_FILE, encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    except FileNotFoundError:
        return pd.DataFrame(columns=["asin", "title", "brand", "price", "rating", "review_count", "main_image_url", "search_keyword", "reviews", "bullet_points"])

@st.cache_resource
def load_feature_a():
    try:
        with open(MODEL_DIR / "feature_a_tfidf.pkl", "rb") as f:
            return pickle.load(f)
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

# --- Helpers ---
def star_sentiment(review):
    import re
    m = re.search(r"([\d.]+)\s*out of 5", str(review.get("rating", "")))
    if not m: return "unknown"
    v = float(m.group(1))
    return "positive" if v >= 4 else ("neutral" if v == 3 else "negative")

# --- Main Application ---
df = load_products()

if df.empty:
    st.error("Dataset not found. Ensure products_cleaned.json exists.")
    st.stop()

# Sidebar Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Select View", [
    "Dataset Explorer", 
    "Feature A: Similarity", 
    "Feature B: Sentiment", 
    "Feature C: Visual Groups", 
    "Feature D: Price Tier"
])

# Global Keyword Filter (Applies to all views)
st.sidebar.markdown("---")
st.sidebar.subheader("Global Filters")
keyword_list = ["All"] + sorted(df["search_keyword"].dropna().unique().tolist())
selected_keyword = st.sidebar.selectbox("Search Keyword", keyword_list)

if selected_keyword != "All":
    df = df[df["search_keyword"] == selected_keyword]

if app_mode == "Dataset Explorer":
    st.header("Dataset Explorer")
    st.metric("Total Products", len(df))
    st.dataframe(df.drop(columns=["reviews", "bullet_points"], errors="ignore"), use_container_width=True)

elif app_mode == "Feature A: Similarity":
    st.header("Feature A: Similar Product Recommendation")
    fa = load_feature_a()
    
    if not fa:
        st.warning("Model files for Feature A missing.")
    else:
        tfidf, matrix, asins = fa["vectorizer"], fa["matrix"], fa["asins"]
        search_mode = st.radio("Search by:", ["Existing Product", "Text Description"])
        
        if search_mode == "Existing Product":
            selected_title = st.selectbox("Select a product", df["title"].tolist())
            product = df[df["title"] == selected_title].iloc[0]
            
            if product["asin"] in asins:
                idx = asins.index(product["asin"])
                scores = cosine_similarity(matrix[idx], matrix)[0]
                top_indices = np.argsort(-scores)[1:6] # Skip self
                
                st.subheader("Top 5 Similar Products")
                for i in top_indices:
                    match_asin = asins[i]
                    match_row = df[df["asin"] == match_asin]
                    if not match_row.empty:
                        m = match_row.iloc[0]
                        st.write(f"**{m['title']}** (Score: {scores[i]:.2f}) - ${m['price']}")
            else:
                st.info("Product not in similarity index.")
                
        else:
            query = st.text_input("Enter description:")
            if query:
                qv = tfidf.transform([query])
                scores = cosine_similarity(qv, matrix)[0]
                top_indices = np.argsort(-scores)[:5]
                
                st.subheader("Top 5 Matches")
                for i in top_indices:
                    match_asin = asins[i]
                    match_row = df[df["asin"] == match_asin]
                    if not match_row.empty:
                        m = match_row.iloc[0]
                        st.write(f"**{m['title']}** (Score: {scores[i]:.2f}) - ${m['price']}")

elif app_mode == "Feature B: Sentiment":
    st.header("Feature B: Review Sentiment Analysis")
    selected_title = st.selectbox("Select a product to analyze", df["title"].tolist())
    product = df[df["title"] == selected_title].iloc[0]
    reviews = product.get("reviews", [])
    
    if not reviews:
        st.info("No reviews available for this product.")
    else:
        sentiments = [star_sentiment(r) for r in reviews]
        pos, neu, neg = sentiments.count("positive"), sentiments.count("neutral"), sentiments.count("negative")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Positive", pos)
        col2.metric("Neutral", neu)
        col3.metric("Negative", neg)
        
        st.subheader("Raw Reviews")
        for r, s in zip(reviews, sentiments):
            with st.expander(f"{r.get('title', 'Review')} - [Sentiment: {s.upper()}]"):
                st.write(r.get("body_en") or r.get("body") or "No text")

elif app_mode == "Feature C: Visual Groups":
    st.header("Feature C: Thumbnail Grouping")
    clusters = load_feature_c()
    
    if clusters.empty:
        st.warning("Cluster data missing.")
    else:
        cluster_ids = sorted(clusters["cluster"].unique().tolist())
        selected_cluster = st.selectbox("Select Cluster Group", cluster_ids)
        
        members = clusters[clusters["cluster"] == selected_cluster]
        st.write(f"**Total members in group {selected_cluster}:** {len(members)}")
        
        merged = pd.merge(members, df, on="asin", how="inner")
        cols = st.columns(4)
        for idx, row in merged.iterrows():
            with cols[idx % 4]:
                if pd.notna(row.get("main_image_url")):
                    st.image(row["main_image_url"], width=150)
                st.caption(row["title"][:50] + "...")

elif app_mode == "Feature D: Price Tier":
    st.header("Feature D: Price Tier Classification")
    fd = load_feature_d()
    
    if not fd:
        st.warning("Model file for Feature D missing.")
    else:
        selected_title = st.selectbox("Select a product to classify", df["title"].tolist())
        product = df[df["title"] == selected_title].iloc[0]
        
        # Prepare inference payload
        input_data = pd.DataFrame([{
            "text_features": f"{product['title']} {product['brand']} " + " ".join(product.get("bullet_points", [])),
            "search_keyword": product["search_keyword"],
            "title_length": len(product["title"]),
            "bullet_count": len(product.get("bullet_points", [])),
            "has_brand": 1 if product["brand"] else 0,
            "rating": product["rating"] if pd.notna(product["rating"]) else df["rating"].median(),
            "review_count": product["review_count"] if pd.notna(product["review_count"]) else df["review_count"].median(),
        }])
        
        prediction = fd.predict(input_data)[0]
        
        # Calculate actual for comparison
        cat_prices = df[df["search_keyword"] == product["search_keyword"]]["price"]
        q33, q67 = cat_prices.quantile([0.333, 0.667])
        actual = "budget" if product["price"] <= q33 else ("mid-range" if product["price"] <= q67 else "premium")
        
        col1, col2 = st.columns(2)
        col1.metric("Predicted Tier (Text-Based)", prediction.upper())
        col2.metric("Actual Tier (Price-Based)", actual.upper())
        
        st.write(f"Actual Price: ${product['price']}")