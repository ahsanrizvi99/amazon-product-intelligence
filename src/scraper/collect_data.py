from playwright.sync_api import sync_playwright
import json
from pathlib import Path

SEARCH_URL = "https://www.amazon.com/s?k=usb+c+hub"
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"


def get_products_from_page(page):
    products = []

    product_cards = page.query_selector_all('div[data-component-type="s-search-result"]')

    for card in product_cards:
        asin = card.get_attribute("data-asin")

        title_element = card.query_selector("h2 span")
        title = title_element.inner_text() if title_element else ""

        price_element = card.query_selector("span.a-price span.a-offscreen")
        price = price_element.inner_text() if price_element else ""

        rating_element = card.query_selector("span.a-icon-alt")
        rating = rating_element.inner_text() if rating_element else ""

        products.append({
            "asin": asin,
            "title": title,
            "price": price,
            "rating": rating,
        })

    return products

def save_products(products):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = DATA_DIR / "products_search_page.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(products)} products to {output_file}")

def open_search_page():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(SEARCH_URL)
        page.wait_for_timeout(5000)

        products = get_products_from_page(page)

        print(f"Found {len(products)} products")
        for product in products:
            print(product)
        save_products(products)
        browser.close()


if __name__ == "__main__":
    open_search_page()