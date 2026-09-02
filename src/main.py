import json
from playwright.sync_api import sync_playwright
from utils import log_request, polite_delay

from src.config import SEARCH_KEYWORDS, DATA_DIR
from src.storage import load_completed_keywords, mark_keyword_done, append_products, save_products_csv
from src.scraper import build_search_url, get_products_from_page, get_product_details, get_reviews

def collect_all_products(keyword, page):
    search_url = build_search_url(keyword)

    try:
        page.goto(search_url)
        page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=10000)
        log_request("search", search_url, "success")
    except Exception as error:
        print(f"ERROR loading search page for '{keyword}': {error}")
        log_request("search", search_url, "error", note=str(error))
        return []

    product_list = get_products_from_page(page)
    print(f"Found {len(product_list)} products for '{keyword}'\n")

    full_data = []

    for index, product in enumerate(product_list, start=1):
        asin = product["asin"]
        print(f"[{index}/{len(product_list)}] Visiting {asin}...")
        polite_delay()

        try:
            details = get_product_details(page, asin)
            reviews = get_reviews(page)
        except Exception as error:
            print(f"    ERROR — skipping this product: {error}")
            log_request("product", f"https://www.amazon.com/dp/{asin}", "error", note=str(error))
            continue

        product_url = f"https://www.amazon.com/dp/{asin}"
        if details["title"]:
            log_request("product", product_url, "success")
            print(f"    OK — {len(reviews)} reviews")
        else:
            log_request("product", product_url, "empty")
            print(f"    EMPTY — page did not load correctly")

        combined = {
            "search_keyword": keyword,
            **details,
            "rating": product["rating"],
            "reviews": reviews,
        }
        full_data.append(combined)

    return full_data

def collect_everything():
    completed = load_completed_keywords()
    remaining_keywords = [kw for kw in SEARCH_KEYWORDS if kw not in completed]

    print(f"{len(completed)} keywords already done, {len(remaining_keywords)} remaining\n")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        for keyword_index, keyword in enumerate(remaining_keywords, start=1):
            print(f"\n=== Keyword {keyword_index}/{len(remaining_keywords)}: '{keyword}' ===\n")
            products = collect_all_products(keyword, page)

            if len(products) == 0:
                print(f"    WARNING: 0 products found for '{keyword}' — will retry next run")
                continue

            append_products(products)
            mark_keyword_done(keyword)

        browser.close()

if __name__ == "__main__":
    collect_everything()

    with open(DATA_DIR / "products_full.json", encoding="utf-8") as f:
        all_data = json.load(f)

    print(f"\n\nTOTAL collected: {len(all_data)} products")
    save_products_csv(all_data)