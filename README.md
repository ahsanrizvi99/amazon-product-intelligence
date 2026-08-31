# Amazon Marketplace Product Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python\&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit\&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)
![YSD](https://img.shields.io/badge/YSD%20Training%20Program-Batch%2005-6C63FF)

**YSD Training Program – Batch 05**

## 📌 What This Project Does

An Amazon Marketplace Product Intelligence Platform that automatically collects product and customer review data and provides analytical insights through a single Streamlit application.

The project includes:

1. **Data Collection Pipeline** — collects fresh Amazon product and review data across 28 assigned search keywords.
2. **Data Preparation & Analysis** — cleans, analyzes, and prepares the collected data for modeling.
3. **Four Analytical Features**

   * **A — Similar Product Recommendation:** recommends relevant products based on similarity.
   * **B — Review Sentiment:** classifies reviews as positive, neutral, or negative and provides summaries.
   * **C — Thumbnail Grouping:** groups product images based on visual similarity.
   * **D — Price Tier Classification:** classifies products into budget, mid-range, or premium using product attributes.
4. **Streamlit Application** — provides product browsing, product details, and access to all four analytical features.

## 📊 Current Status

### Part A — Data Collection 

* Collected **1,028 products** across 28 assigned keywords.
* Collected product information, images, videos, and customer reviews.
* Implemented request logging and raw data storage.

### Part B — Analysis & Model Development 

* Completed data cleaning and preprocessing.
* Developed and evaluated all four analytical features.
* Final approaches selected based on their evaluation results.
* Detailed methodology and evaluation are documented in the respective notebooks.

### Part C — Application 

* Streamlit application implemented.
* All four analytical features integrated.
* Product browsing and product detail views implemented.
* UI updated and improved.

## 📁 Project Structure

```text
src/scraper/    Data collection pipeline
data/raw/       Raw collected data
data/cleaned/   Cleaned dataset
notebooks/      Analysis and model development
app/            Streamlit application
docs/           Project documentation
logs/           Scraping logs
```

## ⚙️ Constraints

* Publicly accessible pages only.
* No login or CAPTCHA bypassing.
* Modest request rates.
* No personal data beyond publicly displayed reviewer names.
* All project questions and clarifications are documented.

## 🚀 Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app/app.py
```

## 🔗 Project Resources

* **Redmine Task #639881:** https://redmine.bjitgroup.com/redmine/issues/639881
* **GitHub Repository:** https://github.com/ahsanrizvi99/amazon-product-intelligence
* **Questions & Clarifications Log:** https://docs.google.com/spreadsheets/d/1LAtvyeIXl7Z8YFuDk5qBSWRmln5VghG0RbLc5PFR2iY/edit?gid=420372137#gid=420372137
