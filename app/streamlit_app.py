import json
import pickle
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import re

from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

# ============================================================
# CONFIGURATION & PATHS
# ============================================================
ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "cleaned" / "products_cleaned.json"
MODEL_DIR = ROOT / "models"

st.set_page_config(
    page_title="Product Intelligence",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CUSTOM CSS (Baby Blue Theme + Animations)
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

    :root {
        --bg: #f4f9fd;
        --surface: rgba(255,255,255,.72);
        --line: #dcebf5;
        --line-strong: #b9d8ef;
        --ink: #102a43;
        --muted: #58738c;
        --blue: #5aa9e6;
        --blue-dark: #2e78b7;
        --blue-soft: #f3faff;
        --green: #16866a;
        --yellow: #996f18;
        --red: #b64b55;
        --shadow-sm: 0 8px 24px rgba(40,109,158,.08);
        --shadow-md: 0 16px 40px rgba(40,109,158,.12);
        --shadow-lg: 0 26px 70px rgba(40,109,158,.16);
    }

    html, body, [class*="css"], .stApp {
        font-family: "DM Sans", Arial, sans-serif;
        color: var(--ink);
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(121,213,232,.20), transparent 28%),
            radial-gradient(circle at 92% 4%, rgba(90,169,230,.18), transparent 30%),
            linear-gradient(180deg, #f5fbff 0%, var(--bg) 36%, #edf6fd 100%);
    }

    .block-container { max-width: 1500px; padding: 2.1rem 3.2rem 4rem; }

    /* Animations */
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(15px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in { animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; opacity: 0; }
    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }

    /* ── top chrome / page headers ────────────────────────────── */
    .topbar {
        position: relative; overflow: hidden;
        background: linear-gradient(115deg, #eaf7ff 0%, #cfeaff 46%, #bfe5f7 100%);
        border: 1px solid rgba(255,255,255,.82);
        box-shadow: var(--shadow-lg);
        border-radius: 28px 28px 18px 18px;
        margin: 0 0 1rem 0; padding: 1.35rem 1.7rem 1.25rem;
        display: flex; align-items: baseline; gap: 1rem;
        isolation: isolate; 
        animation: fadeUp .6s ease both;
    }
    .topbar::before, .topbar::after {
        content: ""; position: absolute; border-radius: 999px; filter: blur(1px); opacity: .65; z-index: -1;
    }
    .topbar::before { width: 230px; height: 230px; right: -70px; top: -120px; background: rgba(255,255,255,.72); }
    .topbar::after  { width: 170px; height: 170px; left: 44%; bottom: -115px; background: rgba(121,213,232,.30); }
    .topbar .mark {
        color: #123a57; font-family: 'Manrope', sans-serif; font-size: 1.6rem; font-weight: 800; letter-spacing: -.045em;
    }
    .topbar .mark span { color: var(--blue-dark); }
    .topbar .tag {
        color: #55758f; font-size: .85rem; font-weight: 600; border-left: 1px solid #b4d3e8; padding-left: 1rem;
    }

    /* Top Navigation (Styled Radio) */
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        background: rgba(255,255,255,.72); backdrop-filter: blur(14px);
        border: 1px solid rgba(185,216,239,.8); box-shadow: var(--shadow-sm);
        border-radius: 14px; padding: 5px;
        display: flex; flex-wrap: wrap; gap: 5px !important; justify-content: center;
        margin-bottom: 1rem;
    }
    div[data-testid="stRadio"] label {
        border-radius: 10px; padding: 6px 14px; transition: all 0.2s ease;
        font-size: 0.85rem; font-weight: 600; cursor: pointer; color: #53728a;
    }
    div[data-testid="stRadio"] label:hover { background: var(--blue-soft); }
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: var(--blue); color: white;
    }
    div[data-testid="stRadio"] label > div:first-child { display: none; }

    /* ── boxes & cards ──────────────────────── */
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
    .stat { 
        background: var(--surface); backdrop-filter: blur(14px);
        border: 1px solid rgba(185,216,239,.82); box-shadow: var(--shadow-sm);
        border-radius: 14px; padding: 1.25rem .9rem; text-align: center; 
    }
    .stat-lbl { font-size: .65rem; letter-spacing: .13em; text-transform: uppercase; color: var(--muted); font-weight: 800; margin-bottom: .35rem; }
    .stat-val { font-family: 'Manrope', sans-serif; font-size: 1.8rem; font-weight: 800; color: var(--ink); line-height: 1; }

    /* Unified Product Row (Pure HTML) */
    .product-row {
        display: flex; align-items: center; gap: 1.5rem;
        background: var(--surface); backdrop-filter: blur(14px);
        border: 1px solid rgba(185,216,239,.82); box-shadow: var(--shadow-sm);
        border-radius: 22px; padding: 1.2rem 1.5rem; margin-bottom: 0.8rem;
        transition: transform .25s ease, box-shadow .25s ease;
    }
    .product-row:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
    .product-row img {
        width: 100px; height: 100px; object-fit: contain; border-radius: 12px;
        -webkit-box-reflect: below 4px linear-gradient(transparent, transparent, rgba(0,0,0,0.15));
    }
    .product-row-info { flex: 1; }
    .product-row-title { font-family: "Manrope", sans-serif; font-size: 1.2rem; font-weight: 800; color: var(--ink); margin-bottom: 0.3rem; line-height: 1.28; letter-spacing: -.028em; }
    .product-row-meta { font-size: 0.85rem; color: var(--muted); margin-bottom: 0.2rem;}
    .product-row-price { font-weight: 800; color: #1d6fa9; font-size: 1.2rem; }
    
    /* Cluster Grid (Feature C) */
    .cluster-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1.5rem; padding: 1rem 0; }
    .cluster-card {
        background: var(--surface); backdrop-filter: blur(14px);
        border: 1px solid rgba(185,216,239,.82); border-radius: 18px; padding: 1rem;
        text-align: center; box-shadow: var(--shadow-sm); transition: transform .22s ease;
    }
    .cluster-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-md); }
    .cluster-card img { width: 100%; height: 150px; object-fit: contain; margin-bottom: 1rem; border-radius: 8px; }
    .cluster-title { font-size: 0.8rem; font-weight: 600; color: var(--ink); line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 2.7em;}

    /* Verdict Cards (Feature D) */
    .verdict-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1rem; }
    .verdict {
        background: var(--surface); backdrop-filter: blur(14px);
        border: 1px solid rgba(185,216,239,.82); box-shadow: var(--shadow-sm);
        border-radius: 19px; padding: 1.5rem 1.7rem; position: relative; overflow: hidden;
        transition: transform .25s ease;
    }
    .verdict:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
    .verdict::after {
        content: ""; position: absolute; inset: auto -50px -70px auto;
        width: 140px; height: 140px; border-radius: 50%; background: rgba(121,213,232,.12);
    }
    .verdict .lbl { font-size: .66rem; letter-spacing: .14em; text-transform: uppercase; color: #6c8496; margin-bottom: .3rem; font-weight: 800; }
    .verdict .tier { font-family: 'Manrope', sans-serif; font-size: 2.2rem; font-weight: 800; color: var(--ink); letter-spacing: -.035em; line-height: 1; }
    .verdict .band { color: #658094; font-size: .85rem; margin-top: .8rem; font-weight: 600; }

    /* Sentiment Pills */
    .pill { display: inline-block; border-radius: 999px; padding: .32rem .82rem; font-size: .76rem; font-weight: 800; margin-right: .4rem; margin-bottom: .35rem; }
    .pos { background: #e6f8f1; color: #15785f; border: 1px solid #a6dfcd; }
    .neu { background: #fff7df; color: #8e6517; border: 1px solid #e7cf8f; }
    .neg { background: #ffeded; color: #a94b54; border: 1px solid #e8b4b9; }

    /* Interactive Panel Frame */
    .interactive-panel {
        background: rgba(255,255,255,.6); border: 1px dashed var(--line-strong);
        border-radius: 16px; padding: 1.5rem; margin: 1rem 0; box-shadow: inset 0 2px 10px rgba(0,0,0,0.02);
    }

    /* Custom DataFrame */
    div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 18px; overflow: hidden; box-shadow: var(--shadow-sm); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# HELPER FUNCTIONS
# ============================================================
def render_topbar(main_text, span_text, tag_text):
    st.markdown(f"""
    <div class="topbar">
        <div class="mark">{main_text}<span>{span_text}</span></div>
        <div class="tag">{tag_text}</div>
    </div>
    """, unsafe_allow_html=True)

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

def star_sentiment(review):
    # Robustly extracts the leading float from rating strings (e.g. "4.5 out of 5 stars")
    rating_str = str(review.get("rating", ""))
    m = re.search(r"([\d.]+)", rating_str)
    if not m: return "unknown"
    val = float(m.group(1))
    return "positive" if val >= 4 else "neutral" if val >= 3 else "negative"

def get_image_fallback(url):
    return url if pd.notna(url) and str(url).strip() else "https://via.placeholder.com/150?text=No+Image"


# ============================================================
# LOAD DATA & UI LAYOUT LOGIC
# ============================================================
df = load_products()

if df.empty:
    st.error("Dataset not found. Ensure products_cleaned.json exists.")
    st.stop()

# 1. NAVIGATION
app_mode = st.radio(
    "Navigation",
    ["Overview", "Feature A: Similarity", "Feature B: Sentiment", "Feature C: Visual Groups", "Feature D: Price Tier"],
    horizontal=True,
    label_visibility="collapsed",
)

# 2. TOPBAR HEADER
if app_mode == "Overview":
    render_topbar("product", "intelligence", "Amazon marketplace analysis")
elif app_mode == "Feature A: Similarity":
    render_topbar("feature", "A", "Similar Product Recommendation")
elif app_mode == "Feature B: Sentiment":
    render_topbar("feature", "B", "Review Sentiment Analysis")
elif app_mode == "Feature C: Visual Groups":
    render_topbar("feature", "C", "Thumbnail Grouping")
elif app_mode == "Feature D: Price Tier":
    render_topbar("feature", "D", "Price Tier Classification")

# 3. GLOBAL CATEGORY FILTER (Hidden on Overview and Feature C)
if app_mode in ["Feature A: Similarity", "Feature B: Sentiment", "Feature D: Price Tier"]:
    c1, c2 = st.columns([1, 4])
    with c1:
        keyword_list = ["All"] + sorted(df["search_keyword"].dropna().unique().tolist())
        selected_keyword = st.selectbox("Category Filter", keyword_list)
    if selected_keyword != "All":
        df = df[df["search_keyword"] == selected_keyword]

if df.empty:
    st.warning("No products found for the selected category.")
    st.stop()


# ============================================================
# VIEWS
# ============================================================

if app_mode == "Overview":
    st.markdown(
        f"""
        <div class="stat-grid animate-in delay-1">
            <div class="stat">
                <div class="stat-lbl">Total Products</div>
                <div class="stat-val">{len(df):,}</div>
            </div>
            <div class="stat">
                <div class="stat-lbl">Categories</div>
                <div class="stat-val">{df["search_keyword"].nunique():,}</div>
            </div>
            <div class="stat">
                <div class="stat-lbl">Avg Price</div>
                <div class="stat-val">${df["price"].mean():.2f}</div>
            </div>
            <div class="stat">
                <div class="stat-lbl">Avg Rating</div>
                <div class="stat-val">{df["rating"].mean():.2f}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="animate-in delay-2">', unsafe_allow_html=True)
    st.dataframe(
        df.drop(columns=["reviews", "bullet_points"], errors="ignore"),
        column_config={"main_image_url": st.column_config.ImageColumn("Thumbnail")},
        use_container_width=True, height=550,
    )
    st.markdown('</div>', unsafe_allow_html=True)

elif app_mode == "Feature A: Similarity":
    fa = load_feature_a()
    if not fa:
        st.warning("Model files missing.")
    else:
        tfidf, matrix, asins = fa["vectorizer"], fa["matrix"], fa["asins"]
        mode = st.radio("Search by", ["Target Product", "Text Description"], horizontal=True)

        if mode == "Target Product":
            selected_title = st.selectbox("Select product", df["title"].tolist(), label_visibility="collapsed")
            product = df[df["title"] == selected_title].iloc[0]
            
            st.markdown(f"""
                <div class="product-row animate-in delay-1">
                    <img src="{get_image_fallback(product['main_image_url'])}" onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=No+Image';">
                    <div class="product-row-info">
                        <div class="product-row-meta">TARGET PRODUCT &nbsp;·&nbsp; {product['search_keyword']}</div>
                        <div class="product-row-title">{product['title']}</div>
                        <div class="product-row-price">${product['price']:.2f}</div>
                    </div>
                </div>
                <div style="font-family:'Manrope'; font-size:1.1rem; font-weight:800; color:var(--ink); margin:1.5rem 0 0.5rem 0;">Top Matches</div>
            """, unsafe_allow_html=True)

            if product["asin"] in asins:
                idx = asins.index(product["asin"])
                scores = cosine_similarity(matrix[idx], matrix)[0]
                top = np.argsort(-scores)[1:6]
                
                html_matches = ""
                for i, match_idx in enumerate(top):
                    r = df[df["asin"] == asins[match_idx]]
                    if not r.empty:
                        m = r.iloc[0]
                        html_matches += f"""
                        <div class="product-row animate-in" style="animation-delay: {0.1 * (i+2)}s; padding: 1rem 1.7rem;">
                            <img src="{get_image_fallback(m['main_image_url'])}" onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=No+Image';" style="width:80px; height:80px;">
                            <div class="product-row-info">
                                <div class="product-row-title" style="font-size:1.1rem;">{m['title']}</div>
                                <div class="product-row-meta">Match Score: <strong style="color:var(--blue-dark)">{scores[match_idx]:.2f}</strong> &nbsp;|&nbsp; <span class="product-row-price" style="font-size:1.1rem;">${m['price']:.2f}</span></div>
                            </div>
                        </div>
                        """
                st.markdown(html_matches, unsafe_allow_html=True)
            else:
                st.info("Product not in index.")
        else:
            query = st.text_input("Enter description", placeholder="e.g. 'wireless headphones noise cancelling'")
            if query:
                qv = tfidf.transform([query])
                scores = cosine_similarity(qv, matrix)[0]
                top = np.argsort(-scores)[:5]
                html_matches = ""
                for i, match_idx in enumerate(top):
                    r = df[df["asin"] == asins[match_idx]]
                    if not r.empty:
                        m = r.iloc[0]
                        html_matches += f"""
                        <div class="product-row animate-in" style="animation-delay: {0.1 * i}s; padding: 1rem 1.7rem;">
                            <img src="{get_image_fallback(m['main_image_url'])}" onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=No+Image';" style="width:80px; height:80px;">
                            <div class="product-row-info">
                                <div class="product-row-title" style="font-size:1.1rem;">{m['title']}</div>
                                <div class="product-row-meta">Match Score: <strong style="color:var(--blue-dark)">{scores[match_idx]:.2f}</strong> &nbsp;|&nbsp; <span class="product-row-price" style="font-size:1.1rem;">${m['price']:.2f}</span></div>
                            </div>
                        </div>
                        """
                st.markdown(html_matches, unsafe_allow_html=True)

elif app_mode == "Feature B: Sentiment":
    selected_title = st.selectbox("Select product", df["title"].tolist(), label_visibility="collapsed")
    product = df[df["title"] == selected_title].iloc[0]
    
    st.markdown(f"""
        <div class="product-row animate-in delay-1">
            <img src="{get_image_fallback(product['main_image_url'])}" onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=No+Image';">
            <div class="product-row-info">
                <div class="product-row-meta">TARGET PRODUCT</div>
                <div class="product-row-title">{product['title']}</div>
                <div class="product-row-meta">Total Scraped Reviews: {int(product['review_count']) if pd.notna(product['review_count']) else 0}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    reviews = product.get("reviews", [])
    if not reviews:
        st.info("No scraped reviews available.")
    else:
        sentiments = [star_sentiment(r) for r in reviews]
        pos, neu, neg = sentiments.count("positive"), sentiments.count("neutral"), sentiments.count("negative")
        
        st.markdown(f"""
            <div class="stat-grid animate-in delay-2">
                <div class="stat"><div class="stat-lbl">Positive</div><div class="stat-val" style="color:var(--green)">{pos}</div></div>
                <div class="stat"><div class="stat-lbl">Neutral</div><div class="stat-val" style="color:var(--yellow)">{neu}</div></div>
                <div class="stat"><div class="stat-lbl">Negative</div><div class="stat-val" style="color:var(--red)">{neg}</div></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="animate-in delay-3">', unsafe_allow_html=True)
        for r, s in zip(reviews, sentiments):
            css = "pos" if s == "positive" else "neu" if s == "neutral" else "neg"
            with st.expander(r.get("title", "Review")[:75]):
                st.markdown(f'<span class="pill {css}">{s.upper()}</span>', unsafe_allow_html=True)
                st.write(r.get("body_en") or r.get("body") or "")
        st.markdown('</div>', unsafe_allow_html=True)

elif app_mode == "Feature C: Visual Groups":
    clusters = load_feature_c()
    if clusters.empty:
        st.warning("Cluster data missing.")
    else:
        # Search by product to find its cluster
        st.markdown("<div style='font-family:Manrope; font-weight:700; color:var(--ink); margin-bottom:0.3rem;'>Search product to find visual cluster:</div>", unsafe_allow_html=True)
        selected_title = st.selectbox("Search product", df["title"].tolist(), label_visibility="collapsed")
        
        target_product = df[df["title"] == selected_title].iloc[0]
        cluster_row = clusters[clusters["asin"] == target_product["asin"]]
        
        if cluster_row.empty:
            st.info("This product is not assigned to a visual cluster.")
        else:
            selected_cluster = int(cluster_row.iloc[0]["cluster"])
            members = clusters[clusters["cluster"] == selected_cluster]
            merged = pd.merge(members, df, on="asin", how="inner")
            
            st.markdown(f"""
                <div class="product-row animate-in" style="margin-top: 1rem;">
                    <img src="{get_image_fallback(target_product['main_image_url'])}" onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=No+Image';">
                    <div class="product-row-info">
                        <div class="product-row-meta">BELONGS TO CLUSTER {selected_cluster}</div>
                        <div class="product-row-title">{target_product['title']}</div>
                        <div class="product-row-meta">Showing {len(merged)} visually similar items in this cluster below:</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            html_cards = []
            for idx, row in merged.iterrows():
                img = get_image_fallback(row.get("main_image_url"))
                title = str(row.get("title", ""))
                html_cards.append(f"""
                    <div class="cluster-card animate-in" style="animation-delay: {min(idx * 0.05, 1.0)}s">
                        <img src="{img}" onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=No+Image';">
                        <div class="cluster-title">{title}</div>
                    </div>
                """)
            st.markdown(f'<div class="cluster-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)

elif app_mode == "Feature D: Price Tier":
    fd = load_feature_d()
    if not fd:
        st.warning("Model file missing.")
    else:
        selected_title = st.selectbox("Select product", df["title"].tolist(), label_visibility="collapsed")
        product = df[df["title"] == selected_title].iloc[0]
        
        st.markdown(f"""
            <div class="product-row animate-in delay-1">
                <img src="{get_image_fallback(product['main_image_url'])}" onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=No+Image';">
                <div class="product-row-info">
                    <div class="product-row-meta">BASELINE PRODUCT</div>
                    <div class="product-row-title">{product['title']}</div>
                    <div class="product-row-price">Actual Price: ${product['price']:.2f}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Interactive Manipulation Panel
        st.markdown('<div class="interactive-panel animate-in delay-2">', unsafe_allow_html=True)
        st.markdown("<div style='font-family:Manrope; font-weight:800; font-size:1.1rem; color:var(--ink); margin-bottom:1rem;'>Manipulate Attributes for Prediction</div>", unsafe_allow_html=True)
        
        sc1, sc2, sc3 = st.columns(3)
        sim_rating = sc1.slider("Simulate Rating", 1.0, 5.0, float(product["rating"] if pd.notna(product["rating"]) else 4.0), 0.1)
        sim_reviews = sc2.number_input("Simulate Review Count", 0, 500000, int(product["review_count"] if pd.notna(product["review_count"]) else 100))
        sim_brand = sc3.selectbox("Has Brand Name?", ["Yes", "No"], index=0 if product["brand"] else 1)
        sim_title = st.text_area("Simulate Title", product["title"])
        st.markdown('</div>', unsafe_allow_html=True)

        bp = product.get("bullet_points", [])
        if not isinstance(bp, list): bp = []
        text_features = f"{sim_title} {'BrandName' if sim_brand == 'Yes' else ''} " + " ".join(map(str, bp))
        
        input_data = pd.DataFrame([{
            "text_features": text_features,
            "search_keyword": product["search_keyword"],
            "title_length": len(sim_title),
            "bullet_count": len(bp),
            "has_brand": 1 if sim_brand == "Yes" else 0,
            "rating": sim_rating,
            "review_count": sim_reviews,
        }])
        
        pred = fd.predict(input_data)[0]
        
        cat_prices = df[df["search_keyword"] == product["search_keyword"]]["price"]
        q33, q67 = cat_prices.quantile([0.333, 0.667])
        actual = "budget" if product["price"] <= q33 else "mid-range" if product["price"] <= q67 else "premium"
        
        match_color = "var(--green)" if pred == actual else "var(--red)"
        match_icon = "Matches Actual Price Tier" if pred == actual else "Differs From Actual Tier"
        
        st.markdown(f"""
            <div class="verdict-grid animate-in delay-3">
                <div class="verdict">
                    <div class="lbl">Predicted Tier (From Text & Simulated Attributes)</div>
                    <div class="tier">{pred.upper()}</div>
                    <div class="band">Prediction dynamically updates as you change the inputs.</div>
                </div>
                <div class="verdict">
                    <div class="lbl">Actual Tier (From Baseline Price)</div>
                    <div class="tier">{actual.upper()}</div>
                    <div class="band" style="color:{match_color};">{match_icon}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("""
    <div style="text-align:center; padding:3rem 0 1rem 0; color:var(--muted); font-size:0.8rem; font-weight:600;">
        Product Intelligence · Built by Ahsan Rizvi · YSD Training Program Batch 05
    </div>
""", unsafe_allow_html=True)