# Amazon Marketplace Product Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python\&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit\&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)
![YSD](https://img.shields.io/badge/YSD%20Training%20Program-Batch%2005-6C63FF)

**YSD Training Program – Batch 05**

## 📌 What This Project Does

Amazon product data such as **prices, images, and customer reviews** is scattered across individual listings with no central place to analyze it.

This project builds:

1. **A data collection pipeline** — scrapes live Amazon listings and reviews for an assigned search keyword, since no pre-existing dataset is allowed.
2. **Four analytical features**, each developed through its own preprocessing → EDA → modeling → evaluation pipeline:

   * **A — Similar Product Recommendation**: rank products by similarity to a given product or search term.
   * **B — Review Sentiment**: classify reviews as positive / neutral / negative, with per-product and per-category summaries.
   * **C — Thumbnail Grouping**: cluster product images into visual groups without using the site's category labels.
   * **D — Price Tier Classification**: classify products into budget / mid-range / premium using non-price attributes.
3. **A single Streamlit application** that lets a non-technical user browse collected products and run all four features interactively.

## 📊 Current status

Collection pipeline in progress (`src/scraper/`).

- Search results page: working — extracts ASIN, title, price, and rating
  for each product on the first page of results.
- Product detail pages: working — visits each product's own page and
  extracts title and price (more reliable than the search-page snapshot).
- Reviews: working — extracts reviewer name, rating, title, verified
  purchase status, and full review text for each review on a product page.
- Full pipeline: search page → product pages → reviews are now combined
  into one record per product, saved to `data/raw/products_full.json`.
- Notebooks, features, and application: not started yet.

Every request is logged to `logs/scraping_log.csv` with a timestamp and
outcome (success / blocked / empty).

Known issues, documented in the Project Questions & Clarifications Log:
- Some reviews are in languages other than English.
- Amazon occasionally returns a bot-check page on the very first request
  of a fresh browser session; visiting the search page before any product
  page avoids this.

## 📁 Planned Structure

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

> Collection instructions will be added once the pipeline is complete.
