# Amazon Marketplace Product Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)
![YSD](https://img.shields.io/badge/YSD%20Training%20Program-Batch%2005-6C63FF)

**YSD Training Program – Batch 05**

## 📌 What This Project Does

Amazon product data such as **prices, images, and customer reviews** is scattered across individual listings with no central place to analyze it.

This project builds:

1. **A data collection pipeline** — scrapes live Amazon listings and reviews across 28 assigned search keywords, since no pre-existing dataset is allowed.
2. **Four analytical features**, each developed through its own preprocessing → EDA → modeling → evaluation pipeline:
   * **A — Similar Product Recommendation**: rank products by similarity to a given product or search term.
   * **B — Review Sentiment**: classify reviews as positive / neutral / negative, with per-product and per-category summaries.
   * **C — Thumbnail Grouping**: cluster product images into visual groups without using the site's category labels.
   * **D — Price Tier Classification**: classify products into budget / mid-range / premium using non-price attributes.
3. **A single Streamlit application** that lets a non-technical user browse collected products and run all four features interactively.

## 📊 Current Status

**Part A (Data Collection): Complete.**
- Full pipeline working end-to-end: search results → product detail pages → reviews, combined into one record per product.
- 1028 products collected across all 28 assigned keywords, with title, brand, price, rating, review count, bullet points, main image URL, video URLs, and full reviews (reviewer name, rating, title, verified purchase status, body text).
- Every request logged to `logs/scraping_log.csv` with a timestamp and outcome (success / blocked / empty).
- Saved to `data/raw/products_full.json` and `data/raw/products_full.csv`.

**Part B (Analysis & Model Development): In progress.**
- Data cleaning notebook complete (`notebooks/01-data-cleaning.ipynb`): deduplication (23 repeated ASINs removed), type conversion for price/rating/review count, brand formatting fixes, category-based price imputation for missing values, and translation of non-English reviews to English (97.5% success rate) with originals preserved.
- Cleaned dataset saved to `data/cleaned/products_cleaned.json` and `.csv` (1005 products).
- Feature notebooks (A–D): not started yet.

**Part C (Application): Not started yet.**

Known issues and design decisions, documented in the Project Questions & Clarifications Log:
- Some reviews are in languages other than English; translated during preprocessing rather than at scrape time.
- Amazon occasionally returns a bot-check page on the very first request of a fresh browser session; visiting the search page before any product page avoids this.
- ~15% of products have no listed price and ~1% have no listed rating (products with no active discount or no reviews yet); handled via per-category imputation and explicit missing-value flags.

## 📁 Project Structure

```text
src/scraper/    Collection pipeline (fetching, parsing, logging)
data/raw/       Collected data + raw HTML evidence (not committed — see .gitignore)
data/cleaned/   Cleaned dataset used for modeling
notebooks/      One preprocessing → modeling notebook per feature (A–D)
app/            Streamlit application
docs/           Project Questions & Clarifications Log
logs/           Request/response log (success, blocked, empty)
```

## ⚙️ Constraints This Project Follows

* Public pages only — no login bypass, no CAPTCHA solving.
* Modest request rates with logging of every attempt's outcome.
* No personal data beyond reviewer names already public on the listing.
* Every question or assumption is recorded in the Questions & Clarifications Log before proceeding, per the project brief.

## 🚀 Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1      # Windows PowerShell
pip install -r requirements.txt
```

> Notebook and application setup instructions will be added as those stages are completed.
