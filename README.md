# 🛒 Amazon Marketplace Product Intelligence Platform

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python\&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit\&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-ML%20Pipelines-F7931E?logo=scikitlearn\&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Scraper-2EAD33?logo=playwright\&logoColor=white)
![Status](https://img.shields.io/badge/Status-In%20Development-orange)

An end-to-end marketplace intelligence platform that collects Amazon product and review data, processes the data into a modeling-ready dataset, and provides four independent machine-learning-driven analytical features through a Streamlit application.

## 📌 Overview

The platform combines web scraping, data preprocessing, machine learning, computer vision, natural language processing, and interactive visualization into a single workflow.

The system consists of four major stages:

1. **Data Collection**
   A Playwright-based scraper collects product and review information from Amazon using 28 predefined search keywords.

2. **Data Preparation**
   Raw data is cleaned, deduplicated, imputed, language-processed, and transformed into a dataset suitable for downstream analysis.

3. **Machine Learning Features**

   * **Feature A — Similar Product Recommendation:** Finds related products using TF-IDF, sentence embeddings, and hybrid retrieval.
   * **Feature B — Review Sentiment Analysis:** Classifies review sentiment and produces product-level and category-level summaries.
   * **Feature C — Visual Product Grouping:** Groups visually similar product thumbnails using CLIP embeddings and clustering.
   * **Feature D — Price Tier Classification:** Predicts budget, mid-range, or premium product tiers using non-price product attributes.

4. **Streamlit Application**
   A unified dashboard allows users to browse products and interact with all four analytical features.

---
# 👨‍💻 Author

**Ahsan Rizvi**

---

## 🏗️ System Architecture

```text
Amazon Search & Product Pages
            │
            │ Playwright scraper
            │ Polite rate limiting
            ▼
      Raw JSON / CSV Data
   1,028 products · 11K+ reviews
            │
            │ Cleaning
            │ Deduplication
            │ Price imputation
            │ Language detection + translation
            ▼
     Cleaned Dataset
  products_cleaned.json / CSV
            │
            ├───────────────┬──────────────────┬──────────────────┐
            ▼               ▼                  ▼                  ▼
      Feature A          Feature B          Feature C          Feature D
   Recommendation       Sentiment          Visual Groups      Price Tier
            │               │                  │                  │
      TF-IDF +           TF-IDF +          CLIP ViT-B/32      TF-IDF +
      Embeddings        Logistic Regression    + KMeans       Random Forest
            │               │                  │                  │
            └───────────────┴──────────────────┴──────────────────┘
                                    │
                                    ▼
                         Streamlit Application
                         app/streamlit_app.py
```

---

## 📊 Dataset

The current pipeline produced the following dataset:

| Metric                  |                                       Value |
| ----------------------- | ------------------------------------------: |
| Search keywords         |                                          28 |
| Raw products collected  |                                       1,028 |
| Products after cleaning |                                       1,005 |
| Flattened reviews       |                                      11,288 |
| Prices imputed          |                                 149 / 1,005 |
| Images downloaded       |                               1,004 / 1,005 |
| Language processing     | Non-English reviews detected and translated |

The 28 search keywords cover categories including electronics, kitchen, fashion, and lifestyle.

### Scraping Logs

Scraping requests are logged in:

```text
logs/scraping_log.csv
```

The log records timestamps, outcomes, and errors to help monitor scraping activity and diagnose pipeline issues.

---

# 🔍 Feature A — Similar Product Recommendation

This feature recommends products that are similar to a selected product or user-provided text query.

The system uses a combined product representation containing:

* Product title
* Brand
* Bullet points

Three retrieval approaches were evaluated:

| Method                                   | Precision@5 |
| ---------------------------------------- | ----------: |
| **Hybrid: TF-IDF + Sentence Embeddings** |   **0.864** |
| TF-IDF                                   |       0.850 |
| Sentence Embeddings (`all-MiniLM-L6-v2`) |       0.821 |

Evaluation was performed on 28 queries using human judgment.

### Production Model

Although the hybrid approach achieved the highest measured precision, **TF-IDF was selected for production** because it achieved comparable performance with lower computational overhead during inference.

The application also supports free-text similarity queries against the TF-IDF index.

---

# 💬 Feature B — Review Sentiment Analysis

This feature analyzes customer reviews and categorizes them as:

* Positive
* Neutral
* Negative

Reviews were initially assigned weak labels using star ratings. A manually labeled set of 180 reviews was then used as a gold-standard benchmark.

### Model Comparison

| Model                                                     |  Accuracy |  Macro-F1 |
| --------------------------------------------------------- | --------: | --------: |
| **Star-rating baseline**                                  | **0.889** | **0.887** |
| Transformer (`cardiffnlp/twitter-roberta-base-sentiment`) |     0.678 |     0.623 |
| TF-IDF + Logistic Regression                              |     0.633 |     0.577 |
| VADER                                                     |     0.533 |     0.456 |

### Production Strategy

The star-rating heuristic performed best on the manually labeled benchmark and is therefore used for the dashboard's primary sentiment visualizations.

The TF-IDF + Logistic Regression model is retained as an additional model for scoring future review text that does not have a star rating.

---

# 🖼️ Feature C — Visual Product Grouping

This feature identifies visually similar products independently of their textual categories.

Product thumbnails are converted into **CLIP ViT-B/32 embeddings**, which are then clustered using multiple clustering algorithms.

### Clustering Comparison

| Method                   | Clusters | Silhouette Score | Result                   |
| ------------------------ | -------: | ---------------: | ------------------------ |
| **KMeans**               |   **25** |            0.174 | **Selected**             |
| Agglomerative Clustering |       25 |            0.164 | Comparable               |
| DBSCAN                   |       19 |        **0.373** | Poor assignment coverage |

DBSCAN achieved the highest silhouette score but failed to assign 853 of the 1,004 products to clusters.

KMeans was therefore selected because it produced complete assignments across the dataset while maintaining useful visual groupings.

The selected clustering configuration achieved:

* **ARI:** 0.79
* **NMI:** 0.87

These results indicate strong alignment with the original search categories while also revealing cross-category visual relationships.

---

# 🏷️ Feature D — Price Tier Classification

This feature predicts whether a product belongs to a:

* **Budget**
* **Mid-range**
* **Premium**

tier.

## Label Generation

Price tiers are generated using **category-specific price terciles**.

Importantly, the actual product price is **not used as a model input**.

The classifier instead uses:

* Product title
* Brand
* Bullet points
* Category
* Rating
* Review count

This makes the task a prediction problem based on product presentation and metadata rather than direct price lookup.

### Model Comparison

| Model                  | 5-Fold CV Macro-F1 | Test Accuracy | Test Macro-F1 |
| ---------------------- | -----------------: | ------------: | ------------: |
| **Random Forest**      |          **0.509** |     **0.421** |     **0.406** |
| Gradient Boosting      |              0.498 |             — |             — |
| Logistic Regression    |              0.482 |             — |             — |
| Most-Frequent Baseline |                  — |         0.346 |         0.171 |

Random Forest performed best among the evaluated models.

The results indicate that non-price textual and metadata features contain some information about a product's price positioning, although the classification task remains challenging.

---

# 💻 Streamlit Application

The Streamlit application brings all four features together in an interactive dashboard.

### Overview

Provides:

* Product catalog browsing
* Product filtering
* Product-level information

### Feature A — Similarity

Provides:

* Similar product recommendations
* Similarity scores
* Free-text product search

### Feature B — Sentiment

Provides:

* Product-level sentiment summaries
* Review-level sentiment filtering
* Sentiment visualizations

### Feature C — Visual Groups

Provides:

* Visual cluster browsing
* Thumbnail-based product grouping

### Feature D — Price Tier

Provides:

* Real-time price-tier prediction
* Prediction confidence information

---

# 🚀 Installation & Usage

## Prerequisites

* Python **3.10+**
* Git
* A compatible browser environment for Playwright

## 1. Clone the Repository

```bash
git clone https://github.com/ahsanrizvi99/amazon-product-intelligence.git
cd amazon-product-intelligence
```

## 2. Create a Virtual Environment

### Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the Application

```bash
streamlit run app/streamlit_app.py
```

The Streamlit interface will then be available locally through the URL provided by Streamlit.

---

# 📁 Repository Structure

```text
amazon-product-intelligence/
│
├── src/
│   └── scraper/             # Playwright-based data collection
│
├── data/
│   ├── raw/                 # Raw scraped data
│   └── cleaned/             # Cleaned and processed datasets
│
├── notebooks/               # Data cleaning and feature development
│
├── models/                  # Saved model artifacts and evaluation results
│
├── product_images/          # Downloaded product thumbnails
│
├── app/
│   └── streamlit_app.py     # Streamlit application
│
├── screenshots/             # Screenshots for documentation
│
├── logs/
│   └── scraping_log.csv     # Scraping activity and error logs
│
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

# ⚙️ System Constraints

The scraper and data pipeline operate under the following constraints:

* Data extraction is limited to publicly accessible pages.
* No CAPTCHA bypassing is used.
* No authenticated sessions are used.
* Scraping requests use randomized polite delays to reduce the likelihood of rate limiting.
* No personally identifiable information is intentionally stored beyond publicly displayed reviewer names.

---

# 📈 Key Results

The project combines four different machine-learning tasks with distinct evaluation strategies:

| Feature         | Selected Approach     | Main Result                                |
| --------------- | --------------------- | ------------------------------------------ |
| Similarity      | TF-IDF                | Precision@5 = **0.850**                    |
| Sentiment       | Star-rating heuristic | Accuracy = **0.889**, Macro-F1 = **0.887** |
| Visual grouping | CLIP + KMeans         | ARI = **0.79**, NMI = **0.87**             |
| Price tier      | Random Forest         | Test Macro-F1 = **0.406**                  |

The system therefore demonstrates an end-to-end workflow from web data collection through preprocessing, model evaluation, and interactive deployment.

---

# 📜 License

This project is released under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** license.

Under this license, you may:

* **Share** — copy and redistribute the material in any medium or format.
* **Adapt** — remix, transform, and build upon the material.

Subject to:

* **Attribution:** Appropriate credit must be given to the original author, along with a link to the repository and an indication of any changes.
* **NonCommercial:** The material may not be used for commercial purposes without explicit permission.

---

# 📚 Citation

If you use this project in research or another project, please cite:

```text
Rizvi, A. (2026).
Amazon Marketplace Product Intelligence Platform.
GitHub Repository.
```
