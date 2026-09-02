import pandas as pd
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data" / "raw"
PROGRESS_FILE = DATA_DIR / "completed_keywords.json"
KEYWORDS_FILE = ROOT_DIR / "data" / "search_keywords.xlsx"

# Load Search Parameters from Excel
try:
    df = pd.read_excel(KEYWORDS_FILE)
    SEARCH_KEYWORDS = df["Search Keywords"].dropna().tolist()
except FileNotFoundError:
    print(f"Error: {KEYWORDS_FILE} not found.")
    SEARCH_KEYWORDS = []
except KeyError:
    print("Error: 'Search Keywords' column not found in the Excel file.")
    SEARCH_KEYWORDS = []
except Exception as e:
    print(f"Unexpected error loading keywords: {e}")
    SEARCH_KEYWORDS = []