import streamlit as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
DATA_FILE = ROOT / "data" / "cleaned" / "products_cleaned.json"
MODEL_DIR = ROOT / "models"

def init_page():
    st.set_page_config(
        page_title="Product Intelligence",
        page_icon="🛍️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )