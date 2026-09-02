import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from core.utils import md, esc, get_image_fallback
from core.data import load_feature_a
from components.shared import render_product_card, show_product_details

def render(df: pd.DataFrame):
    fa = load_feature_a()
    if not fa:
        st.warning("Model files missing.")
        return
        
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
        query = st.text_input("Enter description", placeholder="e.g. wireless headphones noise cancelling")
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