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


# ──────────────────────────────────────────────────────────────
# Page configuration
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Product Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ──────────────────────────────────────────────────────────────
# Custom CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');

:root {
    --bg: #eef7ff;
    --surface: rgba(255,255,255,.88);
    --line: #d7e9f7;
    --line-strong: #b9d8ef;
    --ink: #102a43;
    --muted: #58738c;
    --blue: #5aa9e6;
    --blue-dark: #2e78b7;
    --blue-softer: #f3faff;
    --success: #188b6a;
    --danger: #b94a52;
    --shadow-sm: 0 8px 24px rgba(40,109,158,.08);
    --shadow-md: 0 16px 40px rgba(40,109,158,.12);
    --shadow-lg: 0 26px 70px rgba(40,109,158,.16);
}

html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', Arial, sans-serif;
    color: var(--ink);
}

.stApp {
    background:
        radial-gradient(circle at 10% 0%, rgba(121,213,232,.20), transparent 28%),
        radial-gradient(circle at 92% 4%, rgba(90,169,230,.18), transparent 30%),
        linear-gradient(180deg, #f5fbff 0%, var(--bg) 36%, #edf6fd 100%);
}

.block-container {
    max-width: 1500px;
    padding: 2.1rem 3.2rem 4rem;
}

::selection {
    background: #bfe7ff;
    color: var(--ink);
}


/* ── top chrome ───────────────────────────────────────────── */

.topbar {
    position: relative;
    overflow: hidden;
    background: linear-gradient(
        115deg,
        #eaf7ff 0%,
        #cfeaff 46%,
        #bfe5f7 100%
    );
    border: 1px solid rgba(255,255,255,.82);
    box-shadow: var(--shadow-lg);
    border-radius: 28px 28px 18px 18px;
    margin: 0 0 .8rem 0;
    padding: 1.35rem 1.7rem 1.25rem;
    display: flex;
    align-items: baseline;
    gap: 1rem;
    isolation: isolate;
    animation: riseIn .6s ease both;
}

.topbar::before,
.topbar::after {
    content: "";
    position: absolute;
    border-radius: 999px;
    filter: blur(1px);
    opacity: .65;
    z-index: -1;
}

.topbar::before {
    width: 230px;
    height: 230px;
    right: -70px;
    top: -120px;
    background: rgba(255,255,255,.72);
}

.topbar::after {
    width: 170px;
    height: 170px;
    left: 44%;
    bottom: -115px;
    background: rgba(121,213,232,.30);
}

.topbar .mark {
    color: #123a57;
    font-family: 'Manrope', sans-serif;
    font-size: 1.42rem;
    font-weight: 800;
    letter-spacing: -.045em;
}

.topbar .mark span {
    color: var(--blue-dark);
}

.topbar .tag {
    color: #55758f;
    font-size: .82rem;
    font-weight: 600;
    border-left: 1px solid #b4d3e8;
    padding-left: 1rem;
}

.subbar {
    background: rgba(255,255,255,.72);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(185,216,239,.8);
    box-shadow: var(--shadow-sm);
    border-radius: 14px;
    margin: 0 0 1.5rem 0;
    padding: .7rem 1rem;
    color: #54728a;
    font-size: .79rem;
    letter-spacing: .02em;
    animation: riseIn .7s .05s ease both;
}

.subbar b {
    color: var(--blue-dark);
    font-weight: 800;
}


/* ── cards ────────────────────────────────────────────────── */

.card,
.verdict,
.tile,
.stat {
    background: var(--surface);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(185,216,239,.82);
    box-shadow: var(--shadow-sm);
}

.card {
    border-radius: 22px;
    padding: 1.5rem 1.7rem;
    margin-bottom: 1rem;
    transition: transform .25s ease, box-shadow .25s ease;
    animation: riseIn .55s ease both;
}

.card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.ptitle {
    font-family: 'Manrope', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    color: var(--ink);
    line-height: 1.28;
    margin-bottom: .45rem;
    letter-spacing: -.028em;
}

.brandline {
    color: #3476a8;
    font-size: .9rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.price {
    color: #1d6fa9;
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -.035em;
}

.price .cents {
    font-size: .85rem;
    vertical-align: super;
}

.est {
    color: #698399;
    font-size: .68rem;
    font-style: italic;
    font-weight: 600;
    display: block;
}

.meta {
    color: var(--muted);
    font-size: .82rem;
    line-height: 1.9;
}

.meta a {
    color: var(--blue-dark) !important;
    font-weight: 700;
    text-decoration: none;
}

.stars {
    color: var(--blue);
    letter-spacing: .08em;
}


/* ── stat strip ───────────────────────────────────────────── */

.stat {
    border-radius: 14px;
    padding: .75rem .9rem;
    text-align: center;
}

.statlbl {
    font-size: .62rem;
    letter-spacing: .13em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 800;
    margin-bottom: .35rem;
}

.statval {
    font-family: 'Manrope', sans-serif;
    font-size: 1.45rem;
    font-weight: 800;
    color: var(--ink);
    line-height: 1;
}


/* ── catalogue tiles ──────────────────────────────────────── */

.tile {
    border-radius: 18px;
    padding: .9rem;
    height: 100%;
    transition: transform .22s ease, box-shadow .22s ease;
}

.tile:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
}

.tiletitle {
    font-size: .8rem;
    font-weight: 600;
    line-height: 1.35;
    color: var(--ink);
    margin: .6rem 0 .45rem;
    min-height: 3.2em;
}

.tileprice {
    font-family: 'Manrope', sans-serif;
    font-size: 1.05rem;
    font-weight: 800;
    color: #1d6fa9;
}

.tilerating {
    font-size: .7rem;
    color: var(--blue);
    margin-left: .4rem;
    letter-spacing: .05em;
}

.tilecat {
    font-size: .68rem;
    color: var(--muted);
    margin-top: .3rem;
}


/* ── result rows ──────────────────────────────────────────── */

.rowtitle {
    font-size: .93rem;
    font-weight: 700;
    color: var(--ink);
    line-height: 1.4;
}

.rowmeta {
    color: var(--muted);
    font-size: .78rem;
    margin-top: .25rem;
}

.reason {
    display: inline-block;
    background: var(--blue-softer);
    border: 1px solid var(--line-strong);
    border-radius: 999px;
    padding: .18rem .58rem;
    margin-right: .35rem;
    font-size: .7rem;
    color: #3f6782;
    font-weight: 700;
}


/* ── verdict ──────────────────────────────────────────────── */

.verdict {
    border-radius: 19px;
    padding: 1.25rem 1.45rem;
    position: relative;
    overflow: hidden;
    transition: transform .25s ease, box-shadow .25s ease;
}

.verdict:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
}

.verdict::after {
    content: "";
    position: absolute;
    inset: auto -50px -70px auto;
    width: 140px;
    height: 140px;
    border-radius: 50%;
    background: rgba(121,213,232,.12);
}

.verdict .lbl {
    font-size: .66rem;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: #6c8496;
    margin-bottom: .3rem;
    font-weight: 800;
}

.verdict .tier {
    font-family: 'Manrope', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--ink);
    letter-spacing: -.035em;
    line-height: 1;
}

.verdict .band {
    color: #658094;
    font-size: .79rem;
    margin-top: .7rem;
}

.agree {
    color: var(--success);
    font-weight: 800;
    font-size: .84rem;
}

.disagree {
    color: var(--danger);
    font-weight: 800;
    font-size: .84rem;
}


/* ── sentiment pills ─────────────────────────────────────── */

.pill {
    display: inline-block;
    border-radius: 999px;
    padding: .32rem .82rem;
    font-size: .76rem;
    font-weight: 800;
    margin-right: .4rem;
    margin-bottom: .35rem;
}

.pos {
    background: #e6f8f1;
    color: #15785f;
    border: 1px solid #a6dfcd;
}

.neu {
    background: #fff7df;
    color: #8e6517;
    border: 1px solid #e7cf8f;
}

.neg {
    background: #ffeded;
    color: #a94b54;
    border: 1px solid #e8b4b9;
}

.panel {
    background: rgba(255,255,255,.62);
    border: 1px solid rgba(185,216,239,.7);
    border-radius: 17px;
    padding: 1.05rem 1.2rem;
    height: 100%;
}

.panelhead {
    font-size: .68rem;
    letter-spacing: .13em;
    text-transform: uppercase;
    color: var(--muted);
    font-weight: 800;
    margin-bottom: .7rem;
}


/* ── tabs ────────────────────────────────────────────────── */

.stTabs [data-baseweb="tab-list"] {
    gap: .4rem;
    border-bottom: 1px solid var(--line);
    margin-bottom: 1.05rem;
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border-radius: 12px 12px 0 0;
    padding: .72rem 1.15rem;
    font-size: .86rem;
    font-weight: 700;
    color: #6a8294;
    transition: all .2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    background: rgba(255,255,255,.72);
    color: var(--blue-dark);
}

.stTabs [aria-selected="true"] {
    color: var(--blue-dark) !important;
    border-bottom: 3px solid var(--blue);
    background: rgba(255,255,255,.48);
}


/* ── sidebar ─────────────────────────────────────────────── */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #eef8ff 0%,
        #e8f4fc 100%
    );
    border-right: 1px solid #cfe2f1;
    box-shadow: 8px 0 30px rgba(42,105,146,.07);
}

section[data-testid="stSidebar"] h2 {
    font-family: 'Manrope', sans-serif;
    font-size: .76rem;
    letter-spacing: .13em;
    text-transform: uppercase;
    color: #4c718c;
    font-weight: 800;
}

section[data-testid="stSidebar"]
[data-testid="stWidgetLabel"] p {
    color: #486b83;
    font-weight: 700;
}


/* ── inputs ──────────────────────────────────────────────── */

.stTextInput input,
.stSelectbox [data-baseweb="select"] > div,
.stNumberInput input {
    border-radius: 13px !important;
    border: 1px solid #bfd9eb !important;
    background: rgba(255,255,255,.82) !important;
    color: var(--ink) !important;
    transition: all .2s ease;
}

.stTextInput input:focus,
.stSelectbox [data-baseweb="select"] > div:focus-within {
    border-color: #76b8e7 !important;
    box-shadow: 0 0 0 3px rgba(90,169,230,.14) !important;
}

[data-testid="stRadio"] label {
    font-weight: 700;
    color: #53728a;
}

[data-testid="stExpander"] {
    border: 1px solid var(--line);
    border-radius: 15px;
    background: rgba(255,255,255,.62);
}

hr {
    border-color: var(--line);
}

.stImage img {
    border-radius: 16px;
    box-shadow: 0 10px 26px rgba(38,100,140,.10);
    border: 1px solid #d8ebf7;
    transition: transform .28s ease, box-shadow .28s ease;
}

.stImage img:hover {
    transform: scale(1.015);
    box-shadow: 0 17px 34px rgba(38,100,140,.15);
}


/* ── footer ──────────────────────────────────────────────── */

.foot {
    background: linear-gradient(
        135deg,
        #d9efff 0%,
        #cbe9f8 100%
    );
    color: #58758a;
    border: 1px solid #c2ddeb;
    border-radius: 20px;
    margin: 3rem 0 0;
    padding: 1.45rem 1.4rem;
    font-size: .76rem;
    text-align: center;
    line-height: 1.9;
    box-shadow: var(--shadow-sm);
}

.foot b {
    color: #2d668f;
}

.foot .accent {
    color: var(--blue-dark);
}

#MainMenu,
footer,
header {
    visibility: hidden;
}


/* ── animation ───────────────────────────────────────────── */

@keyframes riseIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}


/* ── responsive ─────────────────────────────────────────── */

@media (max-width: 900px) {
    .block-container {
        padding: 1rem 1rem 3rem;
    }

    .topbar {
        border-radius: 20px;
        padding: 1.1rem 1.15rem;
    }

    .topbar .tag {
        display: none;
    }
}
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# Loaders
# ──────────────────────────────────────────────────────────────
@st.cache_data
def load_products():
    with open(DATA_FILE, encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))


@st.cache_resource
def load_feature_a():
    with open(MODEL_DIR / "feature_a_tfidf.pkl", "rb") as f:
        return pickle.load(f)


@st.cache_data
def load_feature_c():
    return pd.read_csv(MODEL_DIR / "feature_c_clusters.csv")


@st.cache_resource
def load_feature_d():
    return joblib.load(
        MODEL_DIR / "feature_d_price_tier_pipeline.joblib"
    )


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────
def stars(rating):
    if pd.isna(rating):
        return ""

    full = int(rating)
    half = 1 if rating - full >= 0.5 else 0

    return (
        "★" * full
        + ("⯪" if half else "")
        + "☆" * (5 - full - half)
    )


def price_html(value, imputed=False):
    if pd.isna(value):
        return '<span class="price">Price unavailable</span>'

    whole, cents = f"{value:.2f}".split(".")

    est = (
        '<span class="est">estimated</span>'
        if imputed
        else ""
    )

    return (
        f'<span class="price">${whole}'
        f'<span class="cents">{cents}</span>'
        f'</span>{est}'
    )


def star_sentiment(review):
    import re

    m = re.search(
        r"([\d.]+)\s*out of 5",
        str(review.get("rating", ""))
    )

    if not m:
        return "unknown"

    value = float(m.group(1))

    if value >= 4:
        return "positive"
    elif value == 3:
        return "neutral"
    else:
        return "negative"


# ──────────────────────────────────────────────────────────────
# Load dataset
# ──────────────────────────────────────────────────────────────
df = load_products()


# ──────────────────────────────────────────────────────────────
# Header
# ──────────────────────────────────────────────────────────────
st.markdown(
    '<div class="topbar">'
    '<div class="mark">product<span>intelligence</span></div>'
    '<div class="tag">Amazon marketplace analysis</div>'
    '</div>'
    '<div class="subbar">'
    f'<b>{len(df):,}</b> products &nbsp;·&nbsp; '
    f'<b>{df["search_keyword"].nunique()}</b> categories &nbsp;·&nbsp; '
    f'<b>{sum(len(r) for r in df["reviews"]):,}</b> reviews collected'
    '</div>',
    unsafe_allow_html=True,
)


# ──────────────────────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────────────────────
st.sidebar.markdown("## View")

view = st.sidebar.radio(
    "Mode",
    ["Catalogue", "Single product"],
    label_visibility="collapsed"
)

st.sidebar.markdown("## Filter")

category = st.sidebar.selectbox(
    "Category",
    [
        "All categories"
    ] + sorted(df["search_keyword"].unique().tolist())
)

filtered = (
    df
    if category == "All categories"
    else df[df["search_keyword"] == category]
)


# ──────────────────────────────────────────────────────────────
# Sidebar sorting
# ──────────────────────────────────────────────────────────────
sort_by = st.sidebar.selectbox(
    "Sort by",
    [
        "Relevance",
        "Price: low to high",
        "Price: high to low",
        "Highest rated",
        "Most reviewed"
    ]
)

if sort_by == "Price: low to high":
    filtered = filtered.sort_values(
        "price",
        na_position="last"
    )

elif sort_by == "Price: high to low":
    filtered = filtered.sort_values(
        "price",
        ascending=False,
        na_position="last"
    )

elif sort_by == "Highest rated":
    filtered = filtered.sort_values(
        "rating",
        ascending=False,
        na_position="last"
    )

elif sort_by == "Most reviewed":
    filtered = filtered.sort_values(
        "review_count",
        ascending=False,
        na_position="last"
    )


st.sidebar.caption(
    f"{len(filtered)} matching products"
)


# ──────────────────────────────────────────────────────────────
# Stop if sidebar filters return nothing
# ──────────────────────────────────────────────────────────────
if len(filtered) == 0:
    st.warning(
        "No products match those filters. "
        "Try a broader search."
    )
    st.stop()


# ──────────────────────────────────────────────────────────────
# CATALOGUE VIEW
# ──────────────────────────────────────────────────────────────
if view == "Catalogue":

    # ──────────────────────────────────────────────────────────
    # Working search bar moved from sidebar to top
    # ──────────────────────────────────────────────────────────
    search = st.text_input(
        "Search products",
        placeholder="Search 1,005 products…",
        label_visibility="collapsed"
    )

    if search:
        filtered = filtered[
            filtered["title"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    # ──────────────────────────────────────────────────────────
    # Pagination
    # ──────────────────────────────────────────────────────────
    per_page = 24

    pages = max(
        1,
        -(-len(filtered) // per_page)
    )

    page = (
        st.sidebar.number_input(
            "Page",
            min_value=1,
            max_value=pages,
            value=1
        )
        if pages > 1
        else 1
    )

    page_items = filtered.iloc[
        (page - 1) * per_page:
        page * per_page
    ]


    # ──────────────────────────────────────────────────────────
    # Meta information
    # ──────────────────────────────────────────────────────────
    category_text = (
        ""
        if category == "All categories"
        else f" in {category}"
    )

    page_text = (
        f" · page {page} of {pages}"
        if pages > 1
        else ""
    )

    st.markdown(
        f'<div class="rowmeta" style="margin-bottom:1rem">'
        f'{len(filtered)} products'
        f'{category_text}'
        f'{page_text}'
        f'</div>',
        unsafe_allow_html=True
    )


    # ──────────────────────────────────────────────────────────
    # Product grid
    # ──────────────────────────────────────────────────────────
    if len(page_items) == 0:

        st.info(
            "No products match your search. "
            "Try a broader search."
        )

    else:

        for start in range(
            0,
            len(page_items),
            4
        ):

            cols = st.columns(
                4,
                gap="medium"
            )

            for col, (_, p) in zip(
                cols,
                page_items.iloc[start:start + 4].iterrows()
            ):

                with col:

                    if p["main_image_url"]:
                        st.image(
                            p["main_image_url"],
                            use_container_width=True
                        )

                    title = str(p["title"])

                    display_title = (
                        title[:58] + "…"
                        if len(title) > 58
                        else title
                    )

                    price = (
                        f"${p['price']:.0f}"
                        if pd.notna(p["price"])
                        else "Price unavailable"
                    )

                    st.markdown(
                        f'<div class="tiletitle">'
                        f'{display_title}'
                        f'</div>'
                        f'<div class="tileprice">'
                        f'{price}'
                        f'<span class="tilerating">'
                        f'{stars(p["rating"])}'
                        f'</span>'
                        f'</div>'
                        f'<div class="tilecat">'
                        f'{p["search_keyword"]}'
                        f'</div>',
                        unsafe_allow_html=True
                    )

            st.markdown(
                "<div style='height:1.4rem'></div>",
                unsafe_allow_html=True
            )


    # ──────────────────────────────────────────────────────────
    # Footer
    # ──────────────────────────────────────────────────────────
    st.markdown(
        '<div class="foot">'
        'Built by <b>Ahsan Rizvi</b> '
        '&nbsp;<span class="accent">·</span>&nbsp; '
        'YSD Training Program, Batch 05<br>'
        'Data collected from public Amazon listings with '
        'a purpose-built Playwright pipeline. '
        'Not affiliated with Amazon.'
        '</div>',
        unsafe_allow_html=True
    )

    st.stop()


# ──────────────────────────────────────────────────────────────
# SINGLE PRODUCT VIEW
# ──────────────────────────────────────────────────────────────
selected_title = st.sidebar.selectbox(
    "Product",
    filtered["title"].tolist(),
    format_func=lambda t:
        t[:60] + ("…" if len(t) > 60 else "")
)

product = filtered[
    filtered["title"] == selected_title
].iloc[0]


# ──────────────────────────────────────────────────────────────
# Product header
# ──────────────────────────────────────────────────────────────
img_col, info_col = st.columns(
    [1, 2],
    gap="large"
)


with img_col:

    if product["main_image_url"]:
        st.image(
            product["main_image_url"],
            use_container_width=True
        )


with info_col:

    st.markdown(
        f'<div class="ptitle">'
        f'{product["title"]}'
        f'</div>'
        f'<div class="brandline">'
        f'{product["brand"] or "Brand not listed"}'
        f' &nbsp;·&nbsp; '
        f'{product["search_keyword"]}'
        f'</div>',
        unsafe_allow_html=True
    )


    s1, s2, s3 = st.columns(
        3,
        gap="small"
    )


    with s1:

        st.markdown(
            f'<div class="stat">'
            f'<div class="statlbl">Price</div>'
            f'{price_html(product["price"], product["price_was_imputed"])}'
            f'</div>',
            unsafe_allow_html=True
        )


    with s2:

        rv = (
            f'{product["rating"]}'
            if pd.notna(product["rating"])
            else "—"
        )

        st.markdown(
            f'<div class="stat">'
            f'<div class="statlbl">Rating</div>'
            f'<div class="statval">{rv}</div>'
            f'<div class="stars" '
            f'style="font-size:.72rem">'
            f'{stars(product["rating"])}'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )


    with s3:

        rc = (
            f'{int(product["review_count"]):,}'
            if pd.notna(product["review_count"])
            else "—"
        )

        st.markdown(
            f'<div class="stat">'
            f'<div class="statlbl">Ratings</div>'
            f'<div class="statval">{rc}</div>'
            f'</div>',
            unsafe_allow_html=True
        )


    st.markdown(
        f'<div class="meta" style="margin-top:.9rem">'
        f'ASIN {product["asin"]}'
        f' &nbsp;·&nbsp; '
        f'<a href="https://www.amazon.com/dp/'
        f'{product["asin"]}">'
        f'View on Amazon ›'
        f'</a>'
        f'</div>',
        unsafe_allow_html=True
    )


# ──────────────────────────────────────────────────────────────
# Product details
# ──────────────────────────────────────────────────────────────
bullets = [
    b
    for b in (product["bullet_points"] or [])
    if b and b.strip()
]

if bullets:

    with st.expander(
        f"Product details ({len(bullets)} points)"
    ):

        for b in bullets:
            st.markdown(f"- {b}")


st.markdown(
    "<div style='height:1rem'></div>",
    unsafe_allow_html=True
)


# ──────────────────────────────────────────────────────────────
# Feature tabs
# ──────────────────────────────────────────────────────────────
tab_a, tab_b, tab_c, tab_d = st.tabs([
    "Similar products",
    "Review sentiment",
    "Visual grouping",
    "Price tier"
])


# ══════════════════════════════════════════════════════════════
# FEATURE A — SIMILAR PRODUCT RECOMMENDATION
# ══════════════════════════════════════════════════════════════
with tab_a:

    fa = load_feature_a()

    tfidf = fa["vectorizer"]
    matrix = fa["matrix"]
    asins = fa["asins"]


    mode = st.radio(
        "Find products by",
        ["This product", "Description"],
        horizontal=True,
        label_visibility="collapsed"
    )


    # ──────────────────────────────────────────────────────────
    # This product
    # ──────────────────────────────────────────────────────────
    if mode == "This product":

        if product["asin"] not in asins:

            st.info(
                "This product isn't in the similarity index."
            )

        else:

            idx = asins.index(product["asin"])

            cat_map = dict(
                zip(
                    df["asin"],
                    df["search_keyword"]
                )
            )

            same_cat = [
                i
                for i, a in enumerate(asins)
                if (
                    cat_map.get(a)
                    == product["search_keyword"]
                    and i != idx
                )
            ]


            if not same_cat:

                st.info(
                    "No other products in this category "
                    "to compare against."
                )

            else:

                scores = cosine_similarity(
                    matrix[idx],
                    matrix[same_cat]
                )[0]

                ranked = sorted(
                    zip(same_cat, scores),
                    key=lambda x: (-x[1], x[0])
                )[:5]


                for i, score in ranked:

                    r = df[
                        df["asin"] == asins[i]
                    ].iloc[0]

                    c1, c2 = st.columns(
                        [1, 6],
                        gap="medium"
                    )


                    with c1:

                        if r["main_image_url"]:
                            st.image(
                                r["main_image_url"],
                                width=76
                            )


                    with c2:

                        tags = []


                        if (
                            r["brand"]
                            and r["brand"] == product["brand"]
                        ):

                            tags.append(
                                f'same brand · {r["brand"]}'
                            )


                        if (
                            pd.notna(r["price"])
                            and pd.notna(product["price"])
                        ):

                            diff = (
                                abs(
                                    r["price"]
                                    - product["price"]
                                )
                                / max(
                                    product["price"],
                                    .01
                                )
                            )

                            tags.append(
                                "similar price"
                                if diff <= .20
                                else (
                                    "lower price"
                                    if r["price"]
                                    < product["price"]
                                    else "higher price"
                                )
                            )


                        tag_html = "".join(
                            f'<span class="reason">{t}</span>'
                            for t in tags
                        )


                        st.markdown(
                            f'<div class="rowtitle">'
                            f'{r["title"][:95]}'
                            f'</div>'
                            f'<div class="rowmeta">'
                            f'${r["price"]:.2f}'
                            f' &nbsp;·&nbsp; '
                            f'match {score:.2f}'
                            f'</div>'
                            f'<div style="margin-top:.4rem">'
                            f'{tag_html}'
                            f'</div>',
                            unsafe_allow_html=True
                        )


                    st.markdown(
                        "<div style='height:.7rem'></div>",
                        unsafe_allow_html=True
                    )


    # ──────────────────────────────────────────────────────────
    # Description search
    # ──────────────────────────────────────────────────────────
    else:

        query = st.text_input(
            "Describe what you're looking for",
            placeholder=(
                "insulated steel water bottle "
                "that keeps drinks cold"
            )
        )


        if query:

            qv = tfidf.transform([query])

            scores = cosine_similarity(
                qv,
                matrix
            )[0]

            top = np.argsort(-scores)[:5]


            if scores[top[0]] < .05:

                st.info(
                    "Nothing in the catalogue closely "
                    "matches that description."
                )


            for i in top:

                r = df[
                    df["asin"] == asins[i]
                ].iloc[0]

                c1, c2 = st.columns(
                    [1, 6],
                    gap="medium"
                )


                with c1:

                    if r["main_image_url"]:
                        st.image(
                            r["main_image_url"],
                            width=76
                        )


                with c2:

                    st.markdown(
                        f'<div class="rowtitle">'
                        f'{r["title"][:95]}'
                        f'</div>'
                        f'<div class="rowmeta">'
                        f'{r["search_keyword"]}'
                        f' &nbsp;·&nbsp; '
                        f'${r["price"]:.2f}'
                        f' &nbsp;·&nbsp; '
                        f'match {scores[i]:.2f}'
                        f'</div>',
                        unsafe_allow_html=True
                    )


                st.markdown(
                    "<div style='height:.7rem'></div>",
                    unsafe_allow_html=True
                )


    st.caption(
        "TF-IDF cosine similarity within the same category. "
        "Precision@5 of 0.85 on 28 manually judged queries."
    )


# ══════════════════════════════════════════════════════════════
# FEATURE B — REVIEW SENTIMENT
# ══════════════════════════════════════════════════════════════
with tab_b:

    reviews = product["reviews"]


    if not reviews:

        st.info(
            "No reviews were collected for this product."
        )

    else:

        sentiments = [
            star_sentiment(r)
            for r in reviews
        ]

        counts = pd.Series(
            sentiments
        ).value_counts()

        total = len(sentiments)

        pos = counts.get("positive", 0)
        neu = counts.get("neutral", 0)
        neg = counts.get("negative", 0)


        cat_sent = [
            star_sentiment(r)
            for _, p in df[
                df["search_keyword"]
                == product["search_keyword"]
            ].iterrows()
            for r in p["reviews"]
        ]


        cs = (
            pd.Series(cat_sent)
            .value_counts(normalize=True)
            .mul(100)
        )


        left, right = st.columns(
            [1.3, 1],
            gap="medium"
        )


        with left:

            st.markdown(
                f'<div class="panel">'
                f'<div class="panelhead">'
                f'This product · {total} reviews'
                f'</div>'
                f'<span class="pill pos">'
                f'{pos} positive · '
                f'{pos / total * 100:.0f}%'
                f'</span>'
                f'<span class="pill neu">'
                f'{neu} neutral · '
                f'{neu / total * 100:.0f}%'
                f'</span>'
                f'<span class="pill neg">'
                f'{neg} negative · '
                f'{neg / total * 100:.0f}%'
                f'</span>'
                f'</div>',
                unsafe_allow_html=True
            )


        with right:

            st.markdown(
                f'<div class="panel">'
                f'<div class="panelhead">'
                f'{product["search_keyword"]} · '
                f'{len(cat_sent):,} reviews'
                f'</div>'
                f'<span class="pill pos">'
                f'{cs.get("positive", 0):.0f}% positive'
                f'</span>'
                f'<span class="pill neu">'
                f'{cs.get("neutral", 0):.0f}% neutral'
                f'</span>'
                f'<span class="pill neg">'
                f'{cs.get("negative", 0):.0f}% negative'
                f'</span>'
                f'</div>',
                unsafe_allow_html=True
            )


        st.markdown(
            "<div style='height:1.2rem'></div>",
            unsafe_allow_html=True
        )


        show = st.selectbox(
            "Show",
            [
                "All reviews",
                "Positive only",
                "Neutral only",
                "Negative only"
            ]
        )


        want = {
            "All reviews": None,
            "Positive only": "positive",
            "Neutral only": "neutral",
            "Negative only": "negative"
        }[show]


        shown = 0


        for r, s in zip(
            reviews,
            sentiments
        ):

            if want and s != want:
                continue

            shown += 1


            with st.expander(
                f'{r.get("title", "Review")[:75]} · {s}'
            ):

                st.caption(
                    f'{r.get("reviewer_name", "Anonymous")}'
                    f' · {r.get("rating", "")}'
                    + (
                        " · verified purchase"
                        if r.get("verified_purchase")
                        else ""
                    )
                )

                st.write(
                    r.get("body_en")
                    or r.get("body")
                    or ""
                )


        if shown == 0:

            st.info(
                f"No {want} reviews for this product."
            )


    st.caption(
        "Sentiment from star ratings, which reached "
        "macro-F1 0.887 against 180 manually labelled "
        "reviews — ahead of the trained text classifier (0.577)."
    )


# ══════════════════════════════════════════════════════════════
# FEATURE C — THUMBNAIL GROUPING
# ══════════════════════════════════════════════════════════════
with tab_c:

    clusters = load_feature_c()

    row = clusters[
        clusters["asin"] == product["asin"]
    ]


    if row.empty:

        st.info(
            "No image was available for this product, "
            "so it isn't grouped."
        )

    else:

        cid = int(
            row.iloc[0]["cluster"]
        )

        members = clusters[
            clusters["cluster"] == cid
        ]

        dominant = (
            members["category"]
            .value_counts()
        )

        purity = (
            dominant.iloc[0]
            / len(members)
            * 100
        )


        note = ""


        if purity < 70:

            others = ", ".join(
                dominant.index[1:4]
            )

            note = (
                f'<div class="rowmeta" '
                f'style="margin-top:.5rem">'
                f'This group mixes categories — '
                f'it also contains {others}. '
                f'Products that photograph similarly '
                f'cluster together even when they do '
                f'different jobs.'
                f'</div>'
            )


        st.markdown(
            f'<div class="verdict" '
            f'style="margin-bottom:1.2rem">'
            f'<div class="lbl">'
            f'Visual group {cid}'
            f'</div>'
            f'<div class="tier" '
            f'style="font-size:1.5rem">'
            f'{dominant.index[0]} '
            f'<span style="font-size:.9rem;'
            f'font-weight:600;'
            f'color:#658094">'
            f'{purity:.0f}% of {len(members)} products'
            f'</span>'
            f'</div>'
            f'{note}'
            f'</div>',
            unsafe_allow_html=True
        )


        sample = members.sample(
            min(8, len(members)),
            random_state=42
        )


        for start in range(
            0,
            len(sample),
            4
        ):

            cols = st.columns(
                4,
                gap="medium"
            )


            for col, (_, m) in zip(
                cols,
                sample.iloc[start:start + 4].iterrows()
            ):

                p = df[
                    df["asin"] == m["asin"]
                ]


                if p.empty:
                    continue


                p = p.iloc[0]


                with col:

                    if p["main_image_url"]:

                        st.image(
                            p["main_image_url"],
                            use_container_width=True
                        )


                    st.markdown(
                        f'<div class="tilecat">'
                        f'{m["category"]}'
                        f'</div>',
                        unsafe_allow_html=True
                    )


            st.markdown(
                "<div style='height:1rem'></div>",
                unsafe_allow_html=True
            )


    st.caption(
        "CLIP image embeddings clustered with KMeans "
        "(k=25), fitted without category labels. "
        "Adjusted Rand Index 0.79 against the withheld categories."
    )


# ══════════════════════════════════════════════════════════════
# FEATURE D — PRICE TIER CLASSIFICATION
# ══════════════════════════════════════════════════════════════
with tab_d:

    fd = load_feature_d()


    row_in = pd.DataFrame([{
        "text_features":
            f"{product['title']} "
            f"{product['brand']} "
            + " ".join(
                product["bullet_points"] or []
            ),

        "search_keyword":
            product["search_keyword"],

        "title_length":
            len(product["title"]),

        "bullet_count":
            len(
                product["bullet_points"] or []
            ),

        "has_brand":
            1 if product["brand"] else 0,

        "rating":
            (
                product["rating"]
                if pd.notna(product["rating"])
                else df["rating"].median()
            ),

        "review_count":
            (
                product["review_count"]
                if pd.notna(product["review_count"])
                else df["review_count"].median()
            ),
    }])


    pred = fd.predict(row_in)[0]


    cat_prices = df[
        df["search_keyword"]
        == product["search_keyword"]
    ]["price"]


    q33, q67 = cat_prices.quantile(
        [.333, .667]
    )


    actual = (
        "budget"
        if product["price"] <= q33
        else (
            "mid-range"
            if product["price"] <= q67
            else "premium"
        )
    )


    v1, v2 = st.columns(
        2,
        gap="medium"
    )


    with v1:

        st.markdown(
            f'<div class="verdict">'
            f'<div class="lbl">'
            f'Predicted from description'
            f'</div>'
            f'<div class="tier">'
            f'{pred}'
            f'</div>'
            f'<div class="band">'
            f'Using title, brand, bullet points, '
            f'rating and review count — never the price.'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )


    with v2:

        verdict = (
            '<span class="agree">'
            'Matches the price-based tier'
            '</span>'
            if pred == actual
            else
            '<span class="disagree">'
            'Differs from the price-based tier'
            '</span>'
        )


        st.markdown(
            f'<div class="verdict">'
            f'<div class="lbl">'
            f'Actual, from price'
            f'</div>'
            f'<div class="tier">'
            f'{actual}'
            f'</div>'
            f'<div class="band">'
            f'{verdict}<br>'
            f'In {product["search_keyword"]}: '
            f'budget up to ${q33:.2f}, '
            f'mid-range up to ${q67:.2f}.'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )


    st.caption(
        "Random Forest on non-price attributes. "
        "Test macro-F1 0.429 against a 0.171 baseline — "
        "it separates budget from premium reasonably, "
        "but mid-range products are hard to identify from text alone."
    )


# ──────────────────────────────────────────────────────────────
# Footer
# ──────────────────────────────────────────────────────────────
st.markdown(
    '<div class="foot">'
    'Built by <b>Ahsan Rizvi</b> '
    '&nbsp;<span class="accent">·</span>&nbsp; '
    'YSD Training Program, Batch 05<br>'
    'Data collected from public Amazon listings with '
    'a purpose-built Playwright pipeline. '
    'Not affiliated with Amazon.'
    '</div>',
    unsafe_allow_html=True
)