import pandas as pd
import streamlit as st
from core.utils import md, esc, get_image_fallback
from components.shared import show_product_details

def render(df: pd.DataFrame):
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

    if st.session_state.get("_last_search") != search_q:
        st.session_state["overview_page"] = 0
        st.session_state["_last_search"] = search_q

    PAGE_SIZE = 20
    N_COLS = 5
    total = len(view_df)
    total_pages = max(1, -(-total // PAGE_SIZE))
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