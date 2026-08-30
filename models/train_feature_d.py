import json
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score

ROOT = Path(__file__).resolve().parent.parent

with open(ROOT / "data" / "cleaned" / "products_cleaned.json", encoding="utf-8") as f:
    df = pd.DataFrame(json.load(f))

print(f"Loaded {len(df)} products")

# Use only products with a genuine (non-imputed) price to define tiers
real = df[~df["price_was_imputed"]].copy().reset_index(drop=True)
print(f"Using {len(real)} products with real prices")

# Assign price tiers by within-category quantiles
q33 = real.groupby("search_keyword")["price"].transform(lambda s: s.quantile(0.333))
q67 = real.groupby("search_keyword")["price"].transform(lambda s: s.quantile(0.667))

real["price_tier"] = np.where(
    real["price"] <= q33, "budget",
    np.where(real["price"] <= q67, "mid-range", "premium")
)

print("\nTier distribution:")
print(real["price_tier"].value_counts())

# Build features - deliberately excludes price and anything derived from it
real["bullet_text"] = real["bullet_points"].apply(
    lambda b: " ".join(b) if isinstance(b, list) else "")
real["text_features"] = (real["title"].fillna("") + " " +
                         real["brand"].fillna("") + " " +
                         real["bullet_text"])
real["title_length"] = real["title"].str.len()
real["bullet_count"] = real["bullet_points"].apply(
    lambda b: len(b) if isinstance(b, list) else 0)
real["has_brand"] = (real["brand"].fillna("") != "").astype(int)
real["rating"] = real["rating"].fillna(real["rating"].median())
real["review_count"] = real["review_count"].fillna(real["review_count"].median())

num_cols = ["title_length", "bullet_count", "has_brand", "rating", "review_count"]
feature_cols = ["text_features", "search_keyword"] + num_cols

X = real[feature_cols]
y = real["price_tier"]

X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

print(f"\nTrain: {len(X_tr)}  Test: {len(X_te)}")

pipe = Pipeline([
    ("prep", ColumnTransformer([
        ("text", TfidfVectorizer(stop_words="english", max_features=3000,
                                 ngram_range=(1, 2), min_df=2, sublinear_tf=True),
         "text_features"),
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["search_keyword"]),
        ("num", StandardScaler(), num_cols),
    ])),
    ("clf", RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                   random_state=42, n_jobs=-1)),
])

pipe.fit(X_tr, y_tr)
pred = pipe.predict(X_te)

print(f"\nTest macro-F1: {f1_score(y_te, pred, average='macro'):.3f}")
print(classification_report(y_te, pred, digits=3))

out = ROOT / "models" / "feature_d_price_tier_pipeline.joblib"
joblib.dump(pipe, out)
print(f"Saved to {out}")