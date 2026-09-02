import re
import pandas as pd
import streamlit as st
from core.utils import md, esc, get_image_fallback, get_amazon_url, star_sentiment
from core.data import load_products

def render_topbar(main_text, span_text, tag_text):
    md(f"""
    <div class="topbar animate-in">
        <div class="mark">{main_text}<span>{span_text}</span></div>
        <div class="tag">{tag_text}</div>
    </div>
    """)

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

@st.dialog("Product Details")
def show_product_details(asin):
    df_all = load_products()
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