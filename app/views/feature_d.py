import pandas as pd
import streamlit as st
from core.utils import md, esc
from core.data import load_feature_d
from components.shared import render_product_card, show_product_details

def render(df: pd.DataFrame):
    fd = load_feature_d()
    if not fd:
        st.warning("Model file missing.")
        return

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
            rev_insight = "High volume usually indicates a mass-market budget item." if p_rev > med_reviews else "Lower volume often aligns with niche or premium items."
            md(f"""
            <div style="background:#f0f4f9; border-radius:12px; padding:1rem;">
                <div style="font-weight:700;">Review volume</div>
                <div style="font-size:0.9rem; color:var(--muted);">This product: <b>{int(p_rev):,}</b></div>
                <div style="font-size:0.9rem; color:var(--muted);">Category median: <b>{int(med_reviews):,}</b></div>
                <div style="margin-top:0.5rem; font-size:0.85rem; color:{'#16866a' if delta_rev > 0 else '#b64b55'};">
                    {abs(delta_rev):.0f}% {'above' if delta_rev > 0 else 'below'} median
                </div>
                <div style="margin-top:0.4rem; font-size:0.75rem; color:var(--ink); font-weight:600;">
                    💡 {rev_insight}
                </div>
            </div>
            """)
        with col_b:
            delta_len = ((p_len - med_len) / med_len * 100) if med_len > 0 else 0
            len_insight = "Longer titles often indicate premium items detailing specific features." if p_len > med_len else "Shorter titles are common for generic or budget products."
            md(f"""
            <div style="background:#f0f4f9; border-radius:12px; padding:1rem;">
                <div style="font-weight:700;">Title length</div>
                <div style="font-size:0.9rem; color:var(--muted);">This product: <b>{p_len} chars</b></div>
                <div style="font-size:0.9rem; color:var(--muted);">Category median: <b>{med_len:.0f} chars</b></div>
                <div style="margin-top:0.5rem; font-size:0.85rem; color:{'#16866a' if delta_len > 0 else '#b64b55'};">
                    {abs(delta_len):.0f}% {'above' if delta_len > 0 else 'below'} median
                </div>
                <div style="margin-top:0.4rem; font-size:0.75rem; color:var(--ink); font-weight:600;">
                    💡 {len_insight}
                </div>
            </div>
            """)
        md(f'<div style="margin-top:0.9rem; font-size:0.85rem; color:var(--muted);">'
           f'Classified as <b>{pred.upper()}</b> using title, brand, bullet points, '
           f'rating and review count — completely ignoring the actual price tag.</div>')

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

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        md('<div class="panel-head" style="text-align:left;">Test the Model (Interactive)</div>')
        md('<div style="color:var(--muted); font-size:0.85rem; margin-bottom:0.8rem;">'
           'Modify the product details below. See if adding premium features (like a known brand or longer descriptions) '
           'changes the model\'s price tier prediction without looking at the price.</div>')
        
        with st.form("price_tier_test"):
            t_col1, t_col2 = st.columns(2)
            with t_col1:
                test_title = st.text_input("Product Title", value=product["title"])
                test_brand = st.text_input("Brand Name", value=str(product.get("brand", "")) if pd.notna(product.get("brand")) else "")
            with t_col2:
                test_reviews = st.number_input("Review Count", value=int(p_rev), min_value=0)
                test_rating = st.number_input("Star Rating", value=float(input_data["rating"].iloc[0]), min_value=1.0, max_value=5.0)
            
            test_bullets = st.text_area("Bullet Points (Combine all text)", value=" ".join(map(str, bp)))
            
            if st.form_submit_button("Predict Custom Tier", type="primary"):
                test_text_features = f"{test_title} {test_brand} {test_bullets}"
                
                test_df = pd.DataFrame([{
                    "text_features": test_text_features,
                    "search_keyword": product["search_keyword"],
                    "title_length": len(test_title),
                    "bullet_count": len(test_bullets.split('.')) if test_bullets else 0,
                    "has_brand": 1 if test_brand.strip() else 0,
                    "rating": test_rating,
                    "review_count": test_reviews,
                }])
                
                # Get prediction and probabilities
                custom_pred = fd.predict(test_df)[0]
                custom_proba = fd.predict_proba(test_df)[0]
                custom_classes = list(fd.classes_)
                custom_conf = dict(zip(custom_classes, custom_proba))
                
                tag_color = {"budget": "green", "mid-range": "orange", "premium": "blue"}.get(custom_pred, "blue")
                
                # Generate progress bars for the confidence scores
                bar_rows = ""
                bar_colors = {"budget": "#16866a", "mid-range": "#e5a83a", "premium": "#2e78b7"}
                tier_order = ["budget", "mid-range", "premium"]
                
                for cls in tier_order:
                    if cls in custom_conf:
                        pct = custom_conf[cls] * 100
                        bar_rows += f"""
                        <div style="margin-top:0.6rem; text-align:left;">
                            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--muted); text-transform:uppercase;">
                                <span>{cls}</span><span>{pct:.0f}%</span>
                            </div>
                            <div style="background:var(--line); border-radius:999px; height:8px; overflow:hidden;">
                                <div style="width:{pct}%; background:{bar_colors.get(cls, '#5aa9e6')}; height:100%;"></div>
                            </div>
                        </div>
                        """

                # Render the results, the probability bars, and the extracted numerical features
                md(f'<div style="margin-top:1rem; padding:1.2rem; background:var(--surface); border:1px solid var(--line-strong); border-radius:12px; text-align:center;">'
                   f'<div style="font-size:0.8rem; font-weight:800; color:var(--muted); text-transform:uppercase; margin-bottom:0.4rem;">Model Predicts</div>'
                   f'<span class="tag-pill tag-{tag_color}" style="font-size:1.2rem; padding:8px 18px; margin-bottom:0.8rem; display:inline-block;">{custom_pred.upper()}</span>'
                   
                   f'<div style="margin-top:0.5rem; border-top:1px solid var(--line); padding-top:0.8rem;">'
                   f'<div style="font-size:0.75rem; font-weight:700; color:var(--muted); margin-bottom:0.5rem; text-align:left;">CONFIDENCE SCORES:</div>'
                   f'{bar_rows}'
                   f'</div>'
                   
                   f'<div style="margin-top:1.2rem; padding-top:0.8rem; border-top:1px solid var(--line); font-size:0.75rem; color:var(--muted);">'
                   f'<b>Features extracted & passed to model:</b><br>'
                   f'Title Length: {test_df["title_length"][0]} chars &nbsp;·&nbsp; '
                   f'Est. Bullets: {test_df["bullet_count"][0]} &nbsp;·&nbsp; '
                   f'Brand Listed: {"Yes" if test_df["has_brand"][0] else "No"}'
                   f'</div>'
                   f'</div>')

    st.caption("Random Forest on non-price attributes. Test macro-F1 0.429 against a "
               "0.171 baseline — separates budget from premium reasonably; "
               "mid-range is hard to identify from text alone.")