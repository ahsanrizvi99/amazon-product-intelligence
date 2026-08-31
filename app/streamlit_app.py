import json
import pickle
import joblib
import re
import html as html_lib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

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



def md(html_str: str):
    cleaned = "\n".join(line.strip() for line in html_str.strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)


def esc(text) -> str:
    return html_lib.escape(str(text)) if pd.notna(text) else ""


# ============================================================
# GLOBAL STYLE
# ============================================================
md("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --bg: #f4f9fd;
    --surface: rgba(255,255,255,.85);
    --surface-solid: #ffffff;
    --line: #dcebf5;
    --line-strong: #b9d8ef;
    --ink: #102a43;
    --muted: #58738c;
    --blue: #5aa9e6;
    --blue-dark: #2e78b7;
    --blue-soft: #eaf5fd;
    --green: #16866a;
    --yellow: #996f18;
    --orange: #e5732f;
    --red: #b64b55;
    --shadow-sm: 0 8px 24px rgba(40,109,158,.08);
    --shadow-md: 0 16px 40px rgba(40,109,158,.12);
    --shadow-lg: 0 26px 70px rgba(40,109,158,.16);
}
html, body, [class*="css"], .stApp { font-family: "DM Sans", Arial, sans-serif; color: var(--ink); }
.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(121,213,232,.20), transparent 28%),
        radial-gradient(circle at 92% 4%, rgba(90,169,230,.18), transparent 30%),
        linear-gradient(180deg, #f5fbff 0%, var(--bg) 36%, #edf6fd 100%);
}
.block-container { max-width: 1500px; padding: 2.1rem 3.2rem 4rem; }

@keyframes fadeUp { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
.animate-in { animation: fadeUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

.topbar {
    position: relative; overflow: hidden;
    background: linear-gradient(115deg, #eaf7ff 0%, #cfeaff 46%, #bfe5f7 100%);
    border: 1px solid rgba(255,255,255,.82);
    box-shadow: var(--shadow-lg); border-radius: 28px 28px 18px 18px;
    margin: 0 0 1.5rem 0; padding: 1.35rem 1.7rem 1.25rem;
    display: flex; align-items: baseline; gap: 1rem;
}
.topbar .mark { color: #123a57; font-family: 'Manrope', sans-serif; font-size: 1.6rem; font-weight: 800; letter-spacing: -.045em; }
.topbar .mark span { color: var(--blue-dark); }
.topbar .tag { color: #55758f; font-size: .85rem; font-weight: 600; border-left: 1px solid #b4d3e8; padding-left: 1rem; }

div[data-testid="stRadio"] > div[role="radiogroup"] {
    background: rgba(255,255,255,.72); border: 1px solid rgba(185,216,239,.8);
    box-shadow: var(--shadow-sm); border-radius: 14px; padding: 5px;
    display: flex; flex-wrap: wrap; gap: 5px !important; justify-content: center;
    margin-bottom: 1rem;
}
div[data-testid="stRadio"] label { border-radius: 10px; padding: 6px 14px; font-size: 0.85rem; font-weight: 600; color: #53728a; }
div[data-testid="stRadio"] label:hover { background: var(--blue-soft); }

.stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat {
    background: var(--surface); border: 1px solid rgba(185,216,239,.82);
    box-shadow: var(--shadow-sm); border-radius: 14px; padding: 1.25rem .9rem; text-align: center;
}
.stat-lbl { font-size: .65rem; letter-spacing: .13em; text-transform: uppercase; color: var(--muted); font-weight: 800; margin-bottom: .35rem; }
.stat-val { font-family: 'Manrope', sans-serif; font-size: 1.8rem; font-weight: 800; color: var(--ink); line-height: 1; }

.product-row {
    display: flex; align-items: center; gap: 1.5rem; background: var(--surface);
    border: 1px solid rgba(185,216,239,.82); box-shadow: var(--shadow-sm);
    border-radius: 22px; padding: 1.2rem 1.5rem; margin-bottom: 1rem;
}
.product-row img { width: 100px; height: 100px; object-fit: contain; border-radius: 12px; }
.product-row-title { font-family: "Manrope", sans-serif; font-size: 1.2rem; font-weight: 800; color: var(--ink); margin-bottom: 0.3rem; line-height: 1.28; }
.product-row-meta { font-size: 0.85rem; color: var(--muted); margin-bottom: 0.2rem; }
.product-row-price { font-weight: 800; color: #1d6fa9; font-size: 1.2rem; }

.carousel-container { display: flex; overflow-x: auto; gap: 1rem; padding: 0.5rem 0.5rem 1.5rem 0.5rem; }
.carousel-container::-webkit-scrollbar { height: 8px; }
.carousel-container::-webkit-scrollbar-thumb { background: var(--line-strong); border-radius: 999px; }
.carousel-card {
    min-width: 220px; max-width: 220px; flex-shrink: 0; background: var(--surface-solid);
    border-radius: 16px; padding: 1.1rem; box-shadow: var(--shadow-sm); border: 1px solid var(--line);
}
.carousel-card img { width: 100%; height: 130px; object-fit: contain; margin-bottom: 0.8rem; border-radius: 8px; background: #fafcfe; }
.carousel-title { font-size: 0.83rem; font-weight: 700; height: 2.4em; overflow: hidden; margin-bottom: 0.4rem; line-height: 1.2; }
.carousel-price { font-size: 1.15rem; font-weight: 800; color: #1d6fa9; margin-bottom: 0.35rem; }
.carousel-sim { font-size: 0.7rem; color: var(--muted); margin-bottom: 3px; }
.sim-track { width: 100%; background: var(--line); border-radius: 999px; height: 6px; margin-bottom: 0.7rem; overflow: hidden; }
.sim-fill { background: var(--blue-dark); height: 100%; border-radius: 999px; }

.tag-pill { display: inline-block; padding: 3px 8px; border-radius: 6px; font-size: 0.68rem; font-weight: 700; margin: 2px 3px 0 0; }
.tag-green { background: #e8f7f1; color: var(--green); border: 1px solid #b8e5d6; }
.tag-orange { background: #fff4ec; color: var(--orange); border: 1px solid #fedbc5; }
.tag-blue { background: #eaf5fd; color: var(--blue-dark); border: 1px solid #b9d8ef; }

.cluster-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap: 1.2rem; padding: 0.5rem 0; }
.cluster-card { background: var(--surface-solid); border: 1px solid var(--line); border-radius: 16px; padding: 0.9rem; text-align: center; box-shadow: var(--shadow-sm); }
.cluster-card img { width: 100%; height: 130px; object-fit: contain; margin-bottom: 0.8rem; border-radius: 8px; background: #fafcfe; }
.cluster-title { font-size: 0.78rem; font-weight: 600; color: var(--ink); line-height: 1.32; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; min-height: 2.6em; }
.target-glow { border: 2px solid var(--blue-dark); box-shadow: 0 0 15px rgba(46,120,183,0.3); }

.pill { display: inline-block; border-radius: 999px; padding: .32rem .82rem; font-size: .76rem; font-weight: 800; margin-right: .4rem; margin-bottom: .35rem; }
.pos { background: #e6f8f1; color: #15785f; border: 1px solid #a6dfcd; }
.neu { background: #fff7df; color: #8e6517; border: 1px solid #e7cf8f; }
.neg { background: #ffeded; color: #a94b54; border: 1px solid #e8b4b9; }

.panel-head { font-family: 'Manrope'; font-size: 0.95rem; font-weight: 800; color: var(--ink); text-align: center; margin-bottom: 0.6rem; }

[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 18px !important;
    box-shadow: var(--shadow-sm);
    background: var(--surface-solid);
}

div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 18px; overflow: hidden; box-shadow: var(--shadow-sm); }

/* ============================================================
   CLICKABLE PRODUCT GRID (Overview)
   ============================================================ */
.product-tile-inner {
    background: var(--surface-solid);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 0.9rem 0.9rem 0.7rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: -0.6rem;
    transition: transform .28s cubic-bezier(.16,1,.3,1), box-shadow .28s ease, border-color .28s ease;
}
.product-tile-inner:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-md);
    border-color: var(--line-strong);
}
.product-tile-inner img { width: 100%; height: 118px; object-fit: contain; border-radius: 10px; background: #fafcfe; margin-bottom: .6rem; }
.pt-cat { font-size: .62rem; font-weight: 800; letter-spacing: .07em; color: var(--muted); text-transform: uppercase; margin-bottom: .3rem; }
.pt-title { font-size: .85rem; font-weight: 700; line-height: 1.3; height: 2.6em; overflow: hidden; margin-bottom: .5rem; color: var(--ink); }
.pt-bottom { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: .3rem; }
.pt-price { font-weight: 800; color: #1d6fa9; font-size: 1.02rem; }
.pt-rating { font-size: .72rem; color: var(--muted); }

/* Every st.button in this app is a "view details" / quick-action
   trigger, so it's safe to theme all buttons the same premium way. */
.stButton > button {
    border-radius: 999px !important;
    border: 1px solid var(--line-strong) !important;
    background: var(--surface-solid) !important;
    color: var(--blue-dark) !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    padding: 0.45rem 1rem !important;
    transition: all .2s cubic-bezier(.16,1,.3,1) !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover {
    background: var(--blue-dark) !important;
    color: #fff !important;
    border-color: var(--blue-dark) !important;
    transform: translateY(-2px);
    box-shadow: var(--shadow-md) !important;
}
.stLinkButton > a {
    border-radius: 999px !important;
    font-weight: 700 !important;
    transition: all .2s cubic-bezier(.16,1,.3,1) !important;
}

/* ============================================================
   PRODUCT DETAIL MODAL — smooth, premium entrance
   Streamlit doesn't publish stable class/testid names for
   st.dialog's internal DOM, so these selectors target the ones
   commonly used in recent releases. If your installed version
   renders the dialog without this animation, it still opens and
   closes correctly — it just skips the extra motion.
   ============================================================ */
div[data-testid="stDialog"] { animation: piOverlayFade .22s ease-out; }
div[data-testid="stDialog"] [role="dialog"],
div[data-testid="stDialog"] > div > div {
    animation: piDialogPop .38s cubic-bezier(0.16, 1, 0.3, 1);
    border-radius: 26px !important;
    box-shadow: var(--shadow-lg) !important;
}
@keyframes piOverlayFade { from { opacity: 0; } to { opacity: 1; } }
@keyframes piDialogPop {
    from { opacity: 0; transform: scale(.93) translateY(18px); }
    to   { opacity: 1; transform: scale(1) translateY(0); }
}
</style>
""")


# ============================================================
# HELPERS
# ============================================================
def render_topbar(main_text, span_text, tag_text):
    md(f"""
    <div class="topbar animate-in">
        <div class="mark">{main_text}<span>{span_text}</span></div>
        <div class="tag">{tag_text}</div>
    </div>
    """)


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
    m = re.search(r"([\d.]+)", str(review.get("rating", "")))
    if not m:
        return "unknown"
    val = round(float(m.group(1)))
    return "positive" if val >= 4 else ("neutral" if val == 3 else "negative")


def get_image_fallback(url):
    return url if pd.notna(url) and str(url).strip() else \
        "https://dummyimage.com/200x200/eef7ff/102a43&text=No+Image"


def get_amazon_url(asin):
    return f"https://www.amazon.com/dp/{asin}"


def render_product_card(product, extra_meta=""):
    md(f"""
    <div class="product-row animate-in">
        <img src="{get_image_fallback(product['main_image_url'])}"
             onerror="this.onerror=null;this.src='https://dummyimage.com/200x200/eef7ff/102a43&text=No+Image';">
        <div>
            <div class="product-row-meta">{esc(product['search_keyword']).upper()}{extra_meta}</div>
            <div class="product-row-title">{esc(product['title'])}</div>
            <div class="product-row-price">${product['price']:.2f}</div>
        </div>
    </div>
    """)


# ============================================================
# PRODUCT DETAIL POPUP
# Triggered from anywhere in the app by calling
# show_product_details(asin) inside an `if st.button(...):` block.
# ============================================================
@st.dialog("Product Details")
def show_product_details(asin):
    match = df_all[df_all["asin"] == asin]
    if match.empty:
        st.error("Product not found.")
        return
    product = match.iloc[0]

    brand_html = ""
    if pd.notna(product.get("brand")) and str(product.get("brand")).strip():
        brand_html = f" &nbsp;·&nbsp; {esc(product['brand'])}"

    col_img, col_info = st.columns([1, 1.4])

    with col_img:
        md(f"""
        <img src="{get_image_fallback(product['main_image_url'])}"
             onerror="this.onerror=null;this.src='https://dummyimage.com/200x200/eef7ff/102a43&text=No+Image';"
             style="width:100%; max-height:280px; object-fit:contain; border-radius:16px; background:#fafcfe;">
        """)
        st.link_button("View on Amazon ↗", get_amazon_url(asin), use_container_width=True)

    with col_info:
        rating_txt = f"⭐ {product['rating']:.1f}" if pd.notna(product["rating"]) else "No rating yet"
        count = int(product["review_count"]) if pd.notna(product["review_count"]) else 0
        md(f"""
        <div class="pt-cat">{esc(product['search_keyword'])}{brand_html}</div>
        <div class="product-row-title" style="font-size:1.32rem; margin:0.35rem 0 0.6rem;">{esc(product['title'])}</div>
        <div style="display:flex; align-items:baseline; gap:0.9rem; margin-bottom:0.9rem;">
            <span class="product-row-price" style="font-size:1.55rem;">${product['price']:.2f}</span>
            <span style="color:var(--muted); font-size:0.85rem;">{rating_txt} &nbsp;·&nbsp; {count:,} ratings</span>
        </div>
        """)

        bp = product.get("bullet_points", [])
        if not isinstance(bp, list):
            bp = []
        if bp:
            md('<div class="panel-head" style="text-align:left; margin-bottom:0.4rem;">Highlights</div>')
            items = "".join(f"<li>{esc(b)}</li>" for b in bp[:6])
            md(f"<ul style='margin:0 0 0.2rem 1.1rem; padding:0; color:var(--ink); "
               f"font-size:0.87rem; line-height:1.55;'>{items}</ul>")

    st.divider()

    reviews = product.get("reviews", [])
    if not isinstance(reviews, list):
        reviews = []

    if reviews:
        sentiments = [star_sentiment(r) for r in reviews]
        pos, neu, neg = sentiments.count("positive"), sentiments.count("neutral"), sentiments.count("negative")

        md('<div class="panel-head" style="text-align:left;">Customer sentiment</div>')
        md(f"""
        <div style="margin-bottom:0.9rem;">
            <span class="pill pos">{pos} positive</span>
            <span class="pill neu">{neu} neutral</span>
            <span class="pill neg">{neg} negative</span>
        </div>
        """)

        for r, s in list(zip(reviews, sentiments))[:3]:
            try:
                star_val = round(float(re.search(r"([\d.]+)", str(r.get("rating", "0"))).group(1)))
            except Exception:
                star_val = 0
            css = {"positive": "green", "neutral": "orange", "negative": "red"}.get(s, "blue")
            with st.expander(f"{'⭐' * star_val} — {r.get('title', 'Review')[:60]}"):
                md(f'<span class="tag-pill tag-{css}">{s.upper()}</span>')
                st.write(r.get("body_en") or r.get("body") or "No text provided.")

        if len(reviews) > 3:
            st.caption(f"+ {len(reviews) - 3} more review(s) in the full sentiment view →")
    else:
        st.info("No scraped reviews available for this product.")

    st.divider()
    md('<div class="panel-head" style="text-align:left;">Explore this product further</div>')

    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("🔍 Similar", key="qa_a", use_container_width=True):
            st.session_state["nav_radio"] = "Feature A: Similarity"
            st.session_state["category_filter"] = "All"
            st.session_state["a_mode"] = "Target Product"
            st.session_state["sel_a"] = product["title"]
            st.rerun()
    with qa2:
        if st.button("💬 Sentiment", key="qa_b", use_container_width=True):
            st.session_state["nav_radio"] = "Feature B: Sentiment"
            st.session_state["category_filter"] = "All"
            st.session_state["sel_b"] = product["title"]
            st.rerun()
    with qa3:
        if st.button("🖼️ Visual group", key="qa_c", use_container_width=True):
            st.session_state["nav_radio"] = "Feature C: Visual Groups"
            st.session_state["c_search"] = product["title"]
            st.rerun()
    with qa4:
        if st.button("🏷️ Price tier", key="qa_d", use_container_width=True):
            st.session_state["nav_radio"] = "Feature D: Price Tier"
            st.session_state["category_filter"] = "All"
            st.session_state["sel_d"] = product["title"]
            st.rerun()


# ============================================================
# LOAD DATA
# ============================================================
df_all = load_products()

if df_all.empty:
    st.error("Dataset not found. Ensure products_cleaned.json exists.")
    st.stop()

app_mode = st.radio(
    "Navigation",
    ["Overview", "Feature A: Similarity", "Feature B: Sentiment",
     "Feature C: Visual Groups", "Feature D: Price Tier"],
    horizontal=True,
    label_visibility="collapsed",
    key="nav_radio",
)

topbar_map = {
    "Overview": ("product", "intelligence", "Amazon marketplace analysis"),
    "Feature A: Similarity": ("feature", "A", "Similar Product Recommendation"),
    "Feature B: Sentiment": ("feature", "B", "Review Sentiment Analysis"),
    "Feature C: Visual Groups": ("feature", "C", "Thumbnail Grouping"),
    "Feature D: Price Tier": ("feature", "D", "Price Tier Classification"),
}
render_topbar(*topbar_map[app_mode])

df = df_all.copy()

if app_mode in ["Feature A: Similarity", "Feature B: Sentiment", "Feature D: Price Tier"]:
    c1, _ = st.columns([1, 4])
    with c1:
        keyword_list = ["All"] + sorted(df["search_keyword"].dropna().unique().tolist())
        selected_keyword = st.selectbox("Category Filter", keyword_list,
                                         label_visibility="collapsed", key="category_filter")
    if selected_keyword != "All":
        df = df[df["search_keyword"] == selected_keyword]

if df.empty:
    st.warning("No products found for the selected category.")
    st.stop()

# ============================================================
# OVERVIEW — clickable product grid
# ============================================================
if app_mode == "Overview":
    md(f"""
    <div class="stat-grid animate-in">
        <div class="stat"><div class="stat-lbl">Total Products</div><div class="stat-val">{len(df):,}</div></div>
        <div class="stat"><div class="stat-lbl">Categories</div><div class="stat-val">{df["search_keyword"].nunique():,}</div></div>
        <div class="stat"><div class="stat-lbl">Avg Price</div><div class="stat-val">${df["price"].mean():.2f}</div></div>
        <div class="stat"><div class="stat-lbl">Avg Rating</div><div class="stat-val">⭐ {df["rating"].mean():.2f}</div></div>
    </div>
    """)

    search_col, _ = st.columns([2, 3])
    with search_col:
        search_q = st.text_input(
            "Search products",
            placeholder="🔍 Search by title or brand…",
            label_visibility="collapsed",
            key="overview_search",
        )

    view_df = df
    if search_q:
        q = search_q.strip().lower()
        mask = (
            view_df["title"].str.lower().str.contains(q, na=False)
            | view_df["brand"].astype(str).str.lower().str.contains(q, na=False)
        )
        view_df = view_df[mask]

    # Reset to page 1 whenever the search term changes
    if st.session_state.get("_last_search") != search_q:
        st.session_state["overview_page"] = 0
        st.session_state["_last_search"] = search_q

    PAGE_SIZE = 20
    N_COLS = 5
    total = len(view_df)
    total_pages = max(1, -(-total // PAGE_SIZE))  # ceil division
    page = max(0, min(st.session_state.get("overview_page", 0), total_pages - 1))
    start = page * PAGE_SIZE
    page_df = view_df.iloc[start:start + PAGE_SIZE]

    if page_df.empty:
        st.info("No products match your search.")
    else:
        for row_start in range(0, len(page_df), N_COLS):
            row_products = page_df.iloc[row_start:row_start + N_COLS]
            cols = st.columns(N_COLS)
            for col, (_, product) in zip(cols, row_products.iterrows()):
                with col:
                    rating_txt = f"⭐ {product['rating']:.1f}" if pd.notna(product["rating"]) else "No rating"
                    md(f"""
                    <div class="product-tile-inner animate-in">
                        <img src="{get_image_fallback(product['main_image_url'])}"
                             onerror="this.onerror=null;this.src='https://dummyimage.com/200x200/eef7ff/102a43&text=No+Image';">
                        <div class="pt-cat">{esc(product['search_keyword'])}</div>
                        <div class="pt-title">{esc(product['title'])}</div>
                        <div class="pt-bottom">
                            <span class="pt-price">${product['price']:.2f}</span>
                            <span class="pt-rating">{rating_txt}</span>
                        </div>
                    </div>
                    """)
                    if st.button("View details →", key=f"tile_{product['asin']}", use_container_width=True):
                        show_product_details(product["asin"])

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    nav_l, nav_mid, nav_r = st.columns([1, 2, 1])
    with nav_l:
        if st.button("← Previous", disabled=page <= 0, key="prev_page"):
            st.session_state["overview_page"] = page - 1
            st.rerun()
    with nav_mid:
        md(f"""
        <div style="text-align:center; color:var(--muted); font-size:0.85rem; padding-top:0.55rem;">
            Page {page + 1} of {total_pages} &nbsp;·&nbsp; {total:,} products
        </div>
        """)
    with nav_r:
        if st.button("Next →", disabled=page >= total_pages - 1, key="next_page"):
            st.session_state["overview_page"] = page + 1
            st.rerun()

# ============================================================
# FEATURE A — SIMILARITY
# ============================================================
elif app_mode == "Feature A: Similarity":
    fa = load_feature_a()
    if not fa:
        st.warning("Model files missing.")
    else:
        tfidf, matrix, asins = fa["vectorizer"], fa["matrix"], fa["asins"]
        mode = st.radio("Search by", ["Target Product", "Text Description"],
                         horizontal=True, key="a_mode")

        def render_carousel(cards):
            body = "".join(cards)
            md(f'<div class="carousel-container animate-in">{body}</div>')

        if mode == "Target Product":
            selected_title = st.selectbox("Select product", df["title"].tolist(),
                                          label_visibility="collapsed", key="sel_a")
            product = df[df["title"] == selected_title].iloc[0]
            render_product_card(product, extra_meta=" &nbsp;·&nbsp; TARGET PRODUCT")
            if st.button("View full details", key="details_a"):
                show_product_details(product["asin"])
            st.markdown("**Similar products**")

            if product["asin"] not in asins:
                st.info("Product not in similarity index.")
            else:
                idx = asins.index(product["asin"])
                cat_map = dict(zip(df["asin"], df["search_keyword"]))
                same_cat = [i for i, a in enumerate(asins)
                            if cat_map.get(a) == product["search_keyword"] and i != idx]

                if not same_cat:
                    st.info("No other products in this category to compare against.")
                else:
                    scores = cosine_similarity(matrix[idx], matrix[same_cat])[0]
                    ranked = sorted(zip(same_cat, scores), key=lambda x: (-x[1], x[0]))[:10]

                    cards = []
                    for i, score in ranked:
                        r = df[df["asin"] == asins[i]]
                        if r.empty:
                            continue
                        m = r.iloc[0]
                        tags = ""
                        if pd.notna(m["brand"]) and pd.notna(product["brand"]) and m["brand"] == product["brand"]:
                            tags += '<span class="tag-pill tag-green">Same brand</span>'
                        if pd.notna(m["price"]) and pd.notna(product["price"]):
                            if m["price"] < product["price"] * 0.9:
                                tags += '<span class="tag-pill tag-orange">Lower price</span>'
                            elif m["price"] > product["price"] * 1.1:
                                tags += '<span class="tag-pill tag-blue">Higher price</span>'
                        pct = round(score * 100)
                        cards.append(f"""
                        <div class="carousel-card">
                            <img src="{get_image_fallback(m['main_image_url'])}"
                                 onerror="this.onerror=null;this.src='https://dummyimage.com/200x200/eef7ff/102a43&text=No+Image';">
                            <div class="carousel-title">{esc(m['title'])}</div>
                            <div class="carousel-price">${m['price']:.2f}</div>
                            <div class="carousel-sim">Similarity: {pct}%</div>
                            <div class="sim-track"><div class="sim-fill" style="width:{pct}%"></div></div>
                            <div>{tags}</div>
                        </div>
                        """)
                    render_carousel(cards)

        else:
            query = st.text_input("Enter description",
                                  placeholder="e.g. wireless headphones noise cancelling")
            if query:
                qv = tfidf.transform([query])
                scores = cosine_similarity(qv, matrix)[0]
                top = np.argsort(-scores)[:10]
                if scores[top[0]] < 0.05:
                    st.info("Nothing in the catalogue closely matches that description.")

                cards = []
                for i in top:
                    r = df[df["asin"] == asins[i]]
                    if r.empty:
                        continue
                    m = r.iloc[0]
                    pct = round(scores[i] * 100)
                    cards.append(f"""
                    <div class="carousel-card">
                        <img src="{get_image_fallback(m['main_image_url'])}"
                             onerror="this.onerror=null;this.src='https://dummyimage.com/200x200/eef7ff/102a43&text=No+Image';">
                        <div class="carousel-title">{esc(m['title'])}</div>
                        <div class="carousel-price">${m['price']:.2f}</div>
                        <div class="carousel-sim">{esc(m['search_keyword'])} &nbsp;·&nbsp; match {pct}%</div>
                        <div class="sim-track"><div class="sim-fill" style="width:{pct}%"></div></div>
                    </div>
                    """)
                render_carousel(cards)

        st.caption("TF-IDF cosine similarity within the same category. "
                   "Precision@5 of 0.85 on 28 manually judged queries.")

# ============================================================
# FEATURE B — SENTIMENT
# ============================================================
elif app_mode == "Feature B: Sentiment":
    selected_title = st.selectbox("Select product", df["title"].tolist(),
                                  label_visibility="collapsed", key="sel_b")
    product = df[df["title"] == selected_title].iloc[0]
    count = int(product["review_count"]) if pd.notna(product["review_count"]) else 0
    render_product_card(product, extra_meta=f" &nbsp;·&nbsp; {count:,} ratings")
    if st.button("View full details", key="details_b"):
        show_product_details(product["asin"])

    reviews = product.get("reviews", [])
    if not reviews:
        st.info("No scraped reviews available for this product.")
    else:
        sentiments = [star_sentiment(r) for r in reviews]
        pos, neu, neg = sentiments.count("positive"), sentiments.count("neutral"), sentiments.count("negative")

        cat_sent = [star_sentiment(r)
                    for _, p in df[df["search_keyword"] == product["search_keyword"]].iterrows()
                    for r in p.get("reviews", [])]
        c_pos, c_neu, c_neg = cat_sent.count("positive"), cat_sent.count("neutral"), cat_sent.count("negative")
        colors = ["#16866a", "#996f18", "#b64b55"]

        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                md('<div class="panel-head">This product</div>')
                fig1 = go.Figure(data=[go.Pie(labels=["Positive", "Neutral", "Negative"],
                                              values=[pos, neu, neg], hole=.6,
                                              marker_colors=colors)])
                fig1.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=220,
                                   paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig1, use_container_width=True)
        with col2:
            with st.container(border=True):
                md(f'<div class="panel-head">Category average · {esc(product["search_keyword"])}</div>')
                fig2 = go.Figure(data=[go.Pie(labels=["Positive", "Neutral", "Negative"],
                                              values=[c_pos, c_neu, c_neg], hole=.6,
                                              marker_colors=colors)])
                fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=220,
                                   paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

        filter_opt = st.radio(
            "Filter reviews",
            [f"All ({len(reviews)})", f"Positive ({pos})", f"Neutral ({neu})", f"Negative ({neg})"],
            horizontal=True)
        filter_key = filter_opt.split(" ")[0].lower()

        shown = 0
        for r, s in zip(reviews, sentiments):
            if filter_key != "all" and s != filter_key:
                continue
            shown += 1
            try:
                star_val = round(float(re.search(r"([\d.]+)", str(r.get("rating", "0"))).group(1)))
            except Exception:
                star_val = 0
            css = {"positive": "green", "neutral": "orange", "negative": "red"}.get(s, "blue")
            with st.expander(f"{'⭐' * star_val} — {r.get('title', 'Review')[:60]}"):
                md(f'<span class="tag-pill tag-{css}">{s.upper()}</span>')
                st.write(r.get("body_en") or r.get("body") or "No text provided.")
        if shown == 0:
            st.info("No reviews match this filter.")

    st.caption("Sentiment from star ratings, which reached macro-F1 0.887 against "
               "180 manually labelled reviews — ahead of the trained text classifier (0.577).")

# ============================================================
# FEATURE C — VISUAL GROUPS
# ============================================================
elif app_mode == "Feature C: Visual Groups":
    clusters = load_feature_c()
    if clusters.empty:
        st.warning("Cluster data missing.")
    else:
        def render_cluster_grid(rows, highlight_asin=None):
            cards = []
            for _, row in rows.iterrows():
                glow = "target-glow" if row["asin"] == highlight_asin else ""
                cards.append(f"""
                <div class="cluster-card {glow}">
                    <img src="{get_image_fallback(row.get('main_image_url'))}"
                         onerror="this.onerror=null;this.src='https://dummyimage.com/200x200/eef7ff/102a43&text=No+Image';">
                    <div class="cluster-title">{esc(row.get('title', ''))}</div>
                    <div style="font-size:0.65rem;color:var(--muted);margin-top:4px;">{esc(row['search_keyword'])}</div>
                </div>
                """)
            md(f'<div class="cluster-grid animate-in">{"".join(cards)}</div>')

        tab1, tab2 = st.tabs(["Browse by cluster", "Search by product"])

        with tab1:
            cluster_ids = sorted(clusters["cluster"].unique().tolist())
            selected_cluster = st.selectbox("Select visual cluster", cluster_ids)
            members = clusters[clusters["cluster"] == selected_cluster]
            merged = pd.merge(members, df, on="asin", how="inner")

            dominant_cat = merged["search_keyword"].value_counts().index[0]
            purity = (merged["search_keyword"] == dominant_cat).mean() * 100

            with st.container(border=True):
                md(f"""
                <div class="panel-head" style="text-align:left;">Cluster {selected_cluster}</div>
                <div style="color:var(--muted);font-size:0.9rem;">
                    {len(merged)} products &nbsp;·&nbsp; dominant: {esc(dominant_cat)} &nbsp;·&nbsp; purity {purity:.0f}%
                </div>
                """)
            st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
            render_cluster_grid(merged)

        with tab2:
            st.markdown("Search a product to see which visual cluster it belongs to:")
            selected_title = st.selectbox("Search product", df["title"].tolist(),
                                          key="c_search", label_visibility="collapsed")
            target_product = df[df["title"] == selected_title].iloc[0]
            cluster_row = clusters[clusters["asin"] == target_product["asin"]]

            if cluster_row.empty:
                st.info("This product is not assigned to a visual cluster.")
            else:
                cid = int(cluster_row.iloc[0]["cluster"])
                members_s = clusters[clusters["cluster"] == cid]
                merged_s = pd.merge(members_s, df, on="asin", how="inner")

                render_product_card(target_product,
                                    extra_meta=f" &nbsp;·&nbsp; cluster {cid} · {len(merged_s)} similar-looking items")
                if st.button("View full details", key="details_c"):
                    show_product_details(target_product["asin"])
                render_cluster_grid(merged_s, highlight_asin=target_product["asin"])

    st.caption("CLIP image embeddings clustered with KMeans (k=25), fitted without "
               "category labels. Adjusted Rand Index 0.79 against the withheld categories.")

# ============================================================
# FEATURE D — PRICE TIER
# ============================================================
elif app_mode == "Feature D: Price Tier":
    fd = load_feature_d()
    if not fd:
        st.warning("Model file missing.")
    else:
        selected_title = st.selectbox("Select product", df["title"].tolist(),
                                      label_visibility="collapsed", key="sel_d")
        product = df[df["title"] == selected_title].iloc[0]
        render_product_card(product)
        if st.button("View full details", key="details_d"):
            show_product_details(product["asin"])

        bp = product.get("bullet_points", [])
        if not isinstance(bp, list):
            bp = []
        text_features = f"{product['title']} {product['brand']} " + " ".join(map(str, bp))

        input_data = pd.DataFrame([{
            "text_features": text_features,
            "search_keyword": product["search_keyword"],
            "title_length": len(product["title"]),
            "bullet_count": len(bp),
            "has_brand": 1 if product["brand"] else 0,
            "rating": product["rating"] if pd.notna(product["rating"]) else df["rating"].median(),
            "review_count": product["review_count"] if pd.notna(product["review_count"])
                           else df["review_count"].median(),
        }])
        pred = fd.predict(input_data)[0]

        cat_prices = df[df["search_keyword"] == product["search_keyword"]]["price"].dropna()
        q33, q67 = cat_prices.quantile([0.333, 0.667])
        actual = "budget" if product["price"] <= q33 else \
                 "mid-range" if product["price"] <= q67 else "premium"
        percentile = (cat_prices <= product["price"]).mean() * 100
        marker_pos = min(max(percentile, 2), 98)

        with st.container(border=True):
            md(f'<div class="panel-head" style="text-align:left;">'
               f'Where this price sits in {esc(product["search_keyword"])}</div>')
            md(f"""
            <div style="position:relative; width:100%; margin: 1.6rem 0 0.4rem 0;">
                <div style="position:absolute; left:{marker_pos}%; top:-24px; transform:translateX(-50%); white-space:nowrap;">
                    <span style="font-size:0.75rem; font-weight:800; color:var(--ink);">${product['price']:.2f}</span>
                </div>
                <div style="display:flex; width:100%; height:16px; border-radius:999px; overflow:hidden; box-shadow: inset 0 1px 3px rgba(0,0,0,0.08);">
                    <div style="width:33.33%; background:#5aa9e6;"></div>
                    <div style="width:33.34%; background:#f2b84b;"></div>
                    <div style="width:33.33%; background:#16866a;"></div>
                </div>
                <div style="position:absolute; left:{marker_pos}%; top:16px; transform:translateX(-50%);">
                    <div style="width:0;height:0;border-left:7px solid transparent;border-right:7px solid transparent;border-top:9px solid #102a43;"></div>
                </div>
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:1.6rem; font-size:0.72rem; color:var(--muted); font-weight:700;">
                <span>BUDGET<br><span style="font-weight:400">≤ ${q33:.2f}</span></span>
                <span style="text-align:center">MID-RANGE<br><span style="font-weight:400">≤ ${q67:.2f}</span></span>
                <span style="text-align:right">PREMIUM<br><span style="font-weight:400">&gt; ${q67:.2f}</span></span>
            </div>
            <div style="text-align:center; margin-top:0.9rem; font-size:0.8rem; color:var(--muted);">
                Cheaper than <b>{percentile:.0f}%</b> of {esc(product["search_keyword"])} products
            </div>
            """)

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        med_reviews = df[df["search_keyword"] == product["search_keyword"]]["review_count"].median()
        med_len = df[df["search_keyword"] == product["search_keyword"]]["title"].str.len().median()
        p_rev = input_data["review_count"].iloc[0]
        p_len = input_data["title_length"].iloc[0]

        with st.container(border=True):
            md('<div class="panel-head" style="text-align:left;">Model reasoning</div>')
            col_a, col_b = st.columns(2)
            with col_a:
                delta_rev = ((p_rev - med_reviews) / med_reviews * 100) if med_reviews > 0 else 0
                md(f"""
                <div style="background:#f0f4f9; border-radius:12px; padding:1rem;">
                    <div style="font-weight:700;">Review volume</div>
                    <div style="font-size:0.9rem; color:var(--muted);">This product: <b>{int(p_rev):,}</b></div>
                    <div style="font-size:0.9rem; color:var(--muted);">Category median: <b>{int(med_reviews):,}</b></div>
                    <div style="margin-top:0.5rem; font-size:0.85rem; color:{'#16866a' if delta_rev > 0 else '#b64b55'};">
                        {abs(delta_rev):.0f}% {'above' if delta_rev > 0 else 'below'} median
                    </div>
                </div>
                """)
            with col_b:
                delta_len = ((p_len - med_len) / med_len * 100) if med_len > 0 else 0
                md(f"""
                <div style="background:#f0f4f9; border-radius:12px; padding:1rem;">
                    <div style="font-weight:700;">Title length</div>
                    <div style="font-size:0.9rem; color:var(--muted);">This product: <b>{p_len} chars</b></div>
                    <div style="font-size:0.9rem; color:var(--muted);">Category median: <b>{med_len:.0f} chars</b></div>
                    <div style="margin-top:0.5rem; font-size:0.85rem; color:{'#16866a' if delta_len > 0 else '#b64b55'};">
                        {abs(delta_len):.0f}% {'above' if delta_len > 0 else 'below'} median
                    </div>
                </div>
                """)
            md(f'<div style="margin-top:0.9rem; font-size:0.85rem; color:var(--muted);">'
               f'Classified as <b>{pred.upper()}</b> using title, brand, bullet points, '
               f'rating and review count — never the price.</div>')

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        match = pred == actual
        bg = "#e8f7f1" if match else "#fff4ec"
        border = "#16866a" if match else "#e5732f"
        txt = "#16866a" if match else "#996f18"
        msg = "Model agrees with market pricing" if match else "Model detects features of a different tier"

        md(f"""
        <div class="animate-in" style="background:{bg}; border:1px solid {border}; border-radius:16px;
             padding:1.5rem; display:flex; justify-content:space-between; align-items:center; box-shadow: var(--shadow-sm);">
            <div>
                <div style="font-size:0.8rem; font-weight:800; color:{txt}; text-transform:uppercase; letter-spacing:0.1em;">Final verdict</div>
                <div style="font-family:Manrope; font-size:1.3rem; font-weight:800; color:var(--ink); margin-top:0.3rem;">{msg}</div>
            </div>
            <div style="text-align:right; background:white; padding:0.8rem 1.2rem; border-radius:12px; box-shadow:0 4px 12px rgba(0,0,0,0.05);">
                <div style="font-size:0.7rem; color:var(--muted); font-weight:700;">PREDICTED</div>
                <div style="font-family:Manrope; font-size:1.4rem; font-weight:800; color:var(--blue-dark);">{pred.upper()}</div>
                <div style="font-size:0.7rem; color:var(--muted); font-weight:700; margin-top:0.4rem;">ACTUAL</div>
                <div style="font-family:Manrope; font-size:1.4rem; font-weight:800; color:var(--ink);">{actual.upper()}</div>
            </div>
        </div>
        """)

        st.caption("Random Forest on non-price attributes. Test macro-F1 0.429 against a "
                   "0.171 baseline — separates budget from premium reasonably; "
                   "mid-range is hard to identify from text alone.")

# ============================================================
# FOOTER
# ============================================================
md("""
<div style="text-align:center; padding:3rem 0 1rem 0; color:var(--muted); font-size:0.8rem; font-weight:600;">
    Amazon Product Intelligence · Built by Ahsan Rizvi (30219) · YSD Training Program Batch 05
</div>
""")