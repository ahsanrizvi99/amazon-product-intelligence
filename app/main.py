import streamlit as st
from core import config, styles, data
from core.utils import md
from components.shared import render_topbar
from views import overview, feature_a, feature_b, feature_c, feature_d

# Initialize page config and CSS
config.init_page()
styles.inject_css()

# Load primary dataset
df_all = data.load_products()

if df_all.empty:
    st.error("Dataset not found. Ensure products_cleaned.json exists.")
    st.stop()

# Application Routing Navigation
app_mode = st.radio(
    "Navigation",
    ["Overview", "Feature A: Similarity", "Feature B: Sentiment",
     "Feature C: Visual Groups", "Feature D: Price Tier"],
    horizontal=True,
    label_visibility="collapsed",
    key="nav_radio",
)

# Route-specific Topbar Mapping
topbar_map = {
    "Overview": ("product", "intelligence", "Amazon marketplace analysis"),
    "Feature A: Similarity": ("feature", "A", "Similar Product Recommendation"),
    "Feature B: Sentiment": ("feature", "B", "Review Sentiment Analysis"),
    "Feature C: Visual Groups": ("feature", "C", "Thumbnail Grouping"),
    "Feature D: Price Tier": ("feature", "D", "Price Tier Classification"),
}
render_topbar(*topbar_map[app_mode])

# Global Data Filtering (Applicable to A, B, and D)
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

# Route Execution
if app_mode == "Overview":
    overview.render(df)
elif app_mode == "Feature A: Similarity":
    feature_a.render(df)
elif app_mode == "Feature B: Sentiment":
    feature_b.render(df)
elif app_mode == "Feature C: Visual Groups":
    # Feature C usually processes df_all directly internally for clustering matches
    feature_c.render(df_all)
elif app_mode == "Feature D: Price Tier":
    feature_d.render(df)

# Global Footer
md("""
<div style="text-align:center; padding:3rem 0 1rem 0; color:var(--muted); font-size:0.8rem; font-weight:600;">
    Amazon Product Intelligence · Built by Ahsan Rizvi (30219) · YSD Training Program Batch 05
</div>
""")