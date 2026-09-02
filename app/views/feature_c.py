import pandas as pd
import streamlit as st
from core.utils import md, esc, get_image_fallback
from core.data import load_feature_c
from components.shared import render_product_card, show_product_details

def render(df_all: pd.DataFrame):
    clusters = load_feature_c()
    if clusters.empty:
        st.warning("Cluster data missing.")
        return

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
        merged = pd.merge(members, df_all, on="asin", how="inner")

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
        selected_title = st.selectbox("Search product", df_all["title"].tolist(),
                                      key="c_search", label_visibility="collapsed")
        target_product = df_all[df_all["title"] == selected_title].iloc[0]
        cluster_row = clusters[clusters["asin"] == target_product["asin"]]

        if cluster_row.empty:
            st.info("This product is not assigned to a visual cluster.")
        else:
            cid = int(cluster_row.iloc[0]["cluster"])
            members_s = clusters[clusters["cluster"] == cid]
            merged_s = pd.merge(members_s, df_all, on="asin", how="inner")

            render_product_card(target_product,
                                extra_meta=f" &nbsp;·&nbsp; cluster {cid} · {len(merged_s)} similar-looking items")
            if st.button("View full details", key="details_c"):
                show_product_details(target_product["asin"])
            render_cluster_grid(merged_s, highlight_asin=target_product["asin"])

    st.caption("CLIP image embeddings clustered with KMeans (k=25), fitted without "
               "category labels. Adjusted Rand Index 0.79 against the withheld categories.")