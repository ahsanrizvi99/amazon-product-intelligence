import json
import pickle
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "cleaned" / "products_cleaned.json"
MODEL_DIR = ROOT / "models"

st.set_page_config(page_title="Amazon Product Intelligence", layout="wide")


@st.cache_data
def load_products():
    with open(DATA_FILE, encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))


@st.cache_resource
def load_feature_a():
    with open(MODEL_DIR / "feature_a_tfidf.pkl", "rb") as f:
        return pickle.load(f)


@st.cache_resource
def load_feature_b():
    return joblib.load(MODEL_DIR / "feature_b_sentiment_model.joblib")


@st.cache_data
def load_feature_c():
    clusters = pd.read_csv(MODEL_DIR / "feature_c_clusters.csv")
    return clusters


@st.cache_resource
def load_feature_d():
    return joblib.load(MODEL_DIR / "feature_d_price_tier_pipeline.joblib")


df = load_products()

st.title("Amazon Marketplace Product Intelligence")
st.caption(f"{len(df)} products across {df['search_keyword'].nunique()} categories")

# ---------------------------------------------------------------
# Sidebar: product selection
# ---------------------------------------------------------------
st.sidebar.header("Browse products")

category = st.sidebar.selectbox(
    "Category", ["All"] + sorted(df["search_keyword"].unique().tolist()))

filtered = df if category == "All" else df[df["search_keyword"] == category]

search = st.sidebar.text_input("Filter by title")
if search:
    filtered = filtered[filtered["title"].str.contains(search, case=False, na=False)]

st.sidebar.write(f"{len(filtered)} products")

if len(filtered) == 0:
    st.warning("No products match that filter.")
    st.stop()

selected_title = st.sidebar.selectbox(
    "Select a product",
    filtered["title"].tolist(),
    format_func=lambda t: t[:70] + ("..." if len(t) > 70 else ""))

product = filtered[filtered["title"] == selected_title].iloc[0]

# ---------------------------------------------------------------
# Product detail
# ---------------------------------------------------------------
col1, col2 = st.columns([1, 2])

with col1:
    if product["main_image_url"]:
        st.image(product["main_image_url"], width=250)

with col2:
    st.subheader(product["title"])
    st.write(f"**Brand:** {product['brand'] or 'Unknown'}")
    st.write(f"**Category:** {product['search_keyword']}")
    price_note = " *(estimated)*" if product["price_was_imputed"] else ""
    st.write(f"**Price:** ${product['price']:.2f}{price_note}")
    if pd.notna(product["rating"]):
        st.write(f"**Rating:** {product['rating']} / 5 "
                 f"({int(product['review_count']) if pd.notna(product['review_count']) else '?'} ratings)")
    st.write(f"**ASIN:** {product['asin']}")
    st.write(f"[View on Amazon](https://www.amazon.com/dp/{product['asin']})")

if product["bullet_points"]:
    with st.expander("Product details"):
        for b in product["bullet_points"]:
            st.write(f"- {b}")

st.divider()

# ---------------------------------------------------------------
# Features
# ---------------------------------------------------------------
tab_a, tab_b, tab_c, tab_d = st.tabs([
    "A · Similar Products",
    "B · Review Sentiment",
    "C · Visual Groups",
    "D · Price Tier",
])

# ---- Feature A ----
with tab_a:
    st.subheader("Similar Product Recommendation")
    st.caption("TF-IDF cosine similarity, restricted to the same category.")

    fa = load_feature_a()
    tfidf, matrix, asins = fa["vectorizer"], fa["matrix"], fa["asins"]

    mode = st.radio("Search by", ["This product", "Free text"], horizontal=True)

    if mode == "This product":
        if product["asin"] not in asins:
            st.warning("This product is not in the similarity index.")
        else:
            idx = asins.index(product["asin"])
            same_cat = [i for i, a in enumerate(asins)
                        if df.loc[df["asin"] == a, "search_keyword"].iloc[0] == product["search_keyword"]
                        and i != idx]
            scores = cosine_similarity(matrix[idx], matrix[same_cat])[0]
            ranked = sorted(zip(same_cat, scores), key=lambda x: (-x[1], x[0]))[:5]

            for i, score in ranked:
                r = df[df["asin"] == asins[i]].iloc[0]
                c1, c2 = st.columns([1, 4])
                with c1:
                    if r["main_image_url"]:
                        st.image(r["main_image_url"], width=90)
                with c2:
                    st.write(f"**{r['title'][:90]}**")
                    reason = []
                    if r["brand"] and r["brand"] == product["brand"]:
                        reason.append(f"same brand ({r['brand']})")
                    diff = abs(r["price"] - product["price"]) / max(product["price"], 0.01)
                    reason.append("similar price" if diff <= 0.20
                                  else ("cheaper" if r["price"] < product["price"] else "pricier"))
                    st.caption(f"${r['price']:.2f} · similarity {score:.3f} · {'; '.join(reason)}")
    else:
        query = st.text_input("Describe what you're looking for",
                              "wireless bluetooth earbuds with noise cancelling")
        if query:
            qv = tfidf.transform([query])
            scores = cosine_similarity(qv, matrix)[0]
            top = np.argsort(-scores)[:5]
            for i in top:
                r = df[df["asin"] == asins[i]].iloc[0]
                c1, c2 = st.columns([1, 4])
                with c1:
                    if r["main_image_url"]:
                        st.image(r["main_image_url"], width=90)
                with c2:
                    st.write(f"**{r['title'][:90]}**")
                    st.caption(f"{r['search_keyword']} · ${r['price']:.2f} · similarity {scores[i]:.3f}")

# ---- Feature B ----
with tab_b:
    st.subheader("Review Sentiment")
    st.caption("Star-derived labels (macro-F1 0.887 vs manual labels). "
               "Text classifier available for comparison.")

    reviews = product["reviews"]
    if not reviews:
        st.info("No reviews collected for this product.")
    else:
        def star_sentiment(r):
            import re
            m = re.search(r"([\d.]+)\s*out of 5", str(r.get("rating", "")))
            if not m:
                return "unknown"
            v = float(m.group(1))
            return "positive" if v >= 4 else ("neutral" if v == 3 else "negative")

        sentiments = [star_sentiment(r) for r in reviews]
        counts = pd.Series(sentiments).value_counts()

        c1, c2, c3 = st.columns(3)
        c1.metric("Positive", counts.get("positive", 0))
        c2.metric("Neutral", counts.get("neutral", 0))
        c3.metric("Negative", counts.get("negative", 0))

        st.bar_chart(counts)

        show = st.selectbox("Show reviews", ["all", "positive", "neutral", "negative"])
        for r, s in zip(reviews, sentiments):
            if show != "all" and s != show:
                continue
            with st.expander(f"[{s}] {r.get('title', '')[:70]}"):
                st.write(f"**{r.get('reviewer_name', 'Anonymous')}** · {r.get('rating', '')}")
                st.write(r.get("body_en", r.get("body", "")))

    st.divider()
    st.write("**Category summary**")
    cat_reviews = []
    for _, p in df[df["search_keyword"] == product["search_keyword"]].iterrows():
        for r in p["reviews"]:
            cat_reviews.append(star_sentiment(r))
    if cat_reviews:
        st.bar_chart(pd.Series(cat_reviews).value_counts())

# ---- Feature C ----
with tab_c:
    st.subheader("Visual Grouping")
    st.caption("CLIP image embeddings + KMeans (k=25). ARI 0.79 against withheld categories.")

    clusters = load_feature_c()
    row = clusters[clusters["asin"] == product["asin"]]

    if row.empty:
        st.warning("No image cluster for this product.")
    else:
        cid = int(row.iloc[0]["cluster"])
        members = clusters[clusters["cluster"] == cid]
        dominant = members["category"].value_counts()
        purity = dominant.iloc[0] / len(members) * 100

        st.write(f"**Cluster {cid}** — {len(members)} products · "
                 f"dominant category: {dominant.index[0]} ({purity:.0f}%)")

        sample = members.sample(min(8, len(members)), random_state=42)
        cols = st.columns(4)
        for i, (_, m) in enumerate(sample.iterrows()):
            p = df[df["asin"] == m["asin"]]
            if p.empty:
                continue
            p = p.iloc[0]
            with cols[i % 4]:
                if p["main_image_url"]:
                    st.image(p["main_image_url"], width=140)
                st.caption(m["category"])

# ---- Feature D ----
with tab_d:
    st.subheader("Price Tier Classification")
    st.caption("Random Forest on non-price attributes. "
               "Test macro-F1 0.406 vs 0.171 baseline — indicative only.")

    fd = load_feature_d()
    row_in = pd.DataFrame([{
        "text_features": f"{product['title']} {product['brand']} " +
                         " ".join(product["bullet_points"] or []),
        "search_keyword": product["search_keyword"],
        "title_length": len(product["title"]),
        "bullet_count": len(product["bullet_points"] or []),
        "has_brand": 1 if product["brand"] else 0,
        "rating": product["rating"] if pd.notna(product["rating"]) else df["rating"].median(),
        "review_count": product["review_count"] if pd.notna(product["review_count"])
                        else df["review_count"].median(),
    }])

    pred = fd.predict(row_in)[0]
    st.metric("Predicted tier", pred)

    cat_prices = df[df["search_keyword"] == product["search_keyword"]]["price"]
    q33, q67 = cat_prices.quantile([0.333, 0.667])
    actual = "budget" if product["price"] <= q33 else ("mid-range" if product["price"] <= q67 else "premium")
    st.write(f"Actual tier (from price): **{actual}**")
    st.caption(f"Category thresholds — budget ≤ ${q33:.2f}, mid-range ≤ ${q67:.2f}")

    if pred == actual:
        st.success("Prediction matches the price-derived tier.")
    else:
        st.warning("Prediction differs from the price-derived tier.")