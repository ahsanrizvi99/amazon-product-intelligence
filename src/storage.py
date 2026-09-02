import json
import csv
from src.config import DATA_DIR, PROGRESS_FILE

def load_completed_keywords():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return []

def mark_keyword_done(keyword):
    completed = load_completed_keywords()
    completed.append(keyword)
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(completed, f, indent=2)

def append_products(new_products):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = DATA_DIR / "products_full.json"
    
    existing_products = []
    if output_file.exists():
        with open(output_file, encoding="utf-8") as f:
            existing_products = json.load(f)

    existing_products.extend(new_products)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing_products, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(new_products)} new products (total now: {len(existing_products)})")

def save_products_csv(products):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = DATA_DIR / "products_full.csv"

    csv_ready_products = []
    for product in products:
        product_copy = product.copy()
        product_copy["reviews"] = json.dumps(product["reviews"], ensure_ascii=False)
        product_copy["bullet_points"] = json.dumps(product["bullet_points"], ensure_ascii=False)
        product_copy["video_urls"] = json.dumps(product["video_urls"], ensure_ascii=False)
        csv_ready_products.append(product_copy)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = csv_ready_products[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_ready_products)

    print(f"Saved {len(products)} products to {output_file}")