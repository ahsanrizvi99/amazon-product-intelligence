import re
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from core.utils import md, esc, star_sentiment
from core.data import load_feature_b
from components.shared import render_product_card, show_product_details

def render(df: pd.DataFrame):
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

    st.divider()
    with st.container(border=True):
        md('<div class="panel-head" style="text-align:left;">Try it yourself</div>')
        md('<div style="color:var(--muted); font-size:0.85rem; margin-bottom:0.8rem;">'
           'Write a review and see how the trained text classifier reads it — '
           'this works even with no star rating attached.</div>')
        user_review = st.text_area(
            "Your review",
            placeholder="e.g. Battery life is disappointing and it stopped charging after two weeks.",
            label_visibility="collapsed",
            height=100,
        )
        if st.button("Analyze sentiment", type="primary"):
            if not user_review.strip():
                st.warning("Write a review first.")
            else:
                fb = load_feature_b()
                if fb is None:
                    st.error("Sentiment model file not found — expected models/feature_b_sentiment_model.joblib.")
                else:
                    pipeline = fb
                    pred_label = pipeline.predict([user_review])[0]
                    proba = pipeline.predict_proba([user_review])[0]
                    classes = list(pipeline.classes_)
                    conf = dict(zip(classes, proba))
                    top_conf = conf[pred_label] * 100

                    tag_css = {"positive": "green", "neutral": "orange", "negative": "red"}.get(pred_label, "blue")
                    md(f'<div style="margin-top:0.9rem;">'
                       f'<span class="tag-pill tag-{tag_css}" style="font-size:0.9rem; padding:6px 14px;">'
                       f'{pred_label.upper()}</span>'
                       f'<span style="color:var(--muted); font-size:0.82rem; margin-left:0.6rem;">'
                       f'{top_conf:.0f}% confidence</span></div>')

                    bar_rows = ""
                    colors = {"positive": "#16866a", "neutral": "#e5a83a", "negative": "#b64b55"}
                    for cls in classes:
                        pct = conf[cls] * 100
                        bar_rows += f"""
                        <div style="margin-top:0.6rem;">
                            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:var(--muted);">
                                <span>{cls.capitalize()}</span><span>{pct:.0f}%</span>
                            </div>
                            <div style="background:var(--line); border-radius:999px; height:8px; overflow:hidden;">
                                <div style="width:{pct}%; background:{colors.get(cls, '#5aa9e6')}; height:100%;"></div>
                            </div>
                        </div>
                        """
                    md(f'<div style="margin-top:0.9rem;">{bar_rows}</div>')

                    tfidf_b = pipeline.steps[0][1]
                    words = set(re.findall(r"[a-zA-Z']+", user_review.lower()))
                    vocab = tfidf_b.vocabulary_
                    
                    matched = sorted(
                        [(w, tfidf_b.idf_[vocab[w]]) for w in words if w in vocab],
                        key=lambda x: x[1],
                        reverse=True,
                    )[:8]

                    if matched:
                        chip_html = "".join(
                            f'<span class="tag-pill tag-blue" style="margin-top:6px; display:inline-block;">'
                            f'{esc(w)} <span style="opacity:0.7; font-weight:normal; margin-left:4px;">{score:.2f}</span>'
                            f'</span>'
                            for w, score in matched
                        )
                        md(f'<div style="margin-top:1rem; font-size:0.78rem; color:var(--muted);">'
                           f'Words the model weighted most heavily (IDF score):</div>'
                           f'<div style="margin-top:4px; padding-bottom:1rem;">{chip_html}</div>')
                    else:
                        md('<div style="padding-bottom:1rem; margin-top:1rem;">'
                           '<span style="color:var(--muted); font-size:0.8rem;">'
                           'None of these words were in the model\'s trained vocabulary — '
                           'it\'s relying on rarer or unseen terms.</span></div>')