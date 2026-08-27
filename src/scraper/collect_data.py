from playwright.sync_api import sync_playwright
import json, csv, re
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

def get_product_details(page, asin):
    product_url = f"https://www.amazon.com/dp/{asin}"
    page.goto(product_url)
    page.wait_for_timeout(5000)

    title_element = page.query_selector("#productTitle")
    title = title_element.inner_text().strip() if title_element else ""

    price_element = page.query_selector("#apex-pricetopay-accessibility-label")
    if price_element:
        price_text = price_element.inner_text()
        match = re.search(r"\$[\d,]+\.\d{2}", price_text)
        price = match.group() if match else ""
    else:
        price = ""

    return {
        "asin": asin,
        "title": title,
        "price": price,
    }

def get_reviews(page):
    reviews = []

    review_blocks = page.query_selector_all('div[data-hook="review"]')

    for block in review_blocks:
        name_element = block.query_selector("span.a-profile-name")
        name = name_element.inner_text() if name_element else ""

        rating_element = block.query_selector('i[data-hook="review-star-rating"] span.a-icon-alt')
        rating = rating_element.inner_text() if rating_element else ""

        title_element = block.query_selector('[data-hook="reviewTitle"]')
        title = title_element.inner_text().strip() if title_element else ""

        verified_element = block.query_selector('span[data-hook="avp-badge"]')
        verified = True if verified_element else False

        paragraph_elements = block.query_selector_all('div[data-hook="reviewRichContentContainer"] p span')
        paragraphs = [p.inner_text().strip() for p in paragraph_elements if p.inner_text().strip()]
        body = " ".join(paragraphs)

        reviews.append({
            "reviewer_name": name,
            "rating": rating,
            "title": title,
            "verified_purchase": verified,
            "body": body,
        })

    return reviews

def save_products(products):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = DATA_DIR / "products_search_page.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(products, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(products)} products to {output_file}")

def save_products_csv(products):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_file = DATA_DIR / "products_search_page.csv"

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = products[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(products)

    print(f"Saved {len(products)} products to {output_file}")

def open_search_page():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(SEARCH_URL)
        page.wait_for_timeout(5000)
        page.screenshot(path="debug_screenshot.png")

        products = get_products_from_page(page)

        print(f"Found {len(products)} products")
        for product in products:
            print(product)
        save_products(products)
        save_products_csv(products)
        browser.close()


if __name__ == "__main__":
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(SEARCH_URL)
        page.wait_for_timeout(5000)

        details = get_product_details(page, "B0BR3M8XHK")
        print(details)

        reviews = get_reviews(page)
        print(f"\nFound {len(reviews)} reviews")
        for review in reviews:
            print(review)

        browser.close()