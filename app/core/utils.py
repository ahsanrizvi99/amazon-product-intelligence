import re
import html as html_lib
import pandas as pd
import streamlit as st

def md(html_str: str):
    cleaned = "\n".join(line.strip() for line in html_str.strip().splitlines())
    st.markdown(cleaned, unsafe_allow_html=True)

def esc(text) -> str:
    return html_lib.escape(str(text)) if pd.notna(text) else ""

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