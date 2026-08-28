from playwright.sync_api import sync_playwright
import json, csv, re
from pathlib import Path
from utils import log_request, polite_delay

SEARCH_KEYWORDS = [
    "wireless earbuds",
    "gaming mouse",
    "USB-C hub",
    "mechanical keyboard",
    "smartwatch",
    "phone case",
    "portable charger",
    "webcam HD",
    "desk lamp LED",
    "air purifier",
    "instant pot",
    "electric toothbrush",
    "budget laptop",
    "bluetooth speaker",
    "kitchen knife set",
    "DSLR camera",
    "coffee maker",
    "gaming chair",
    "backpack",
    "monitor 27 inch",
    "water bottle",
    "t-shirt",
    "notebook journal",
    "sneakers",
    "candle",
    "sunglasses",
    "phone stand",
    "yamaha acoustic guitar",
]

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
PROGRESS_FILE = DATA_DIR / "completed_keywords.json"


def build_search_url(keyword):
    formatted_keyword = keyword.replace(" ", "+")
    return f"https://www.amazon.com/s?k={formatted_keyword}"


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


def collect_all_products(keyword, page):
    search_url = build_search_url(keyword)

    try:
        page.goto(search_url)
        page.wait_for_timeout(5000)
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
            "asin": asin,
            "title": details["title"],
            "price": details["price"],
            "rating": product["rating"],
            "reviews": reviews,
        }
        full_data.append(combined)

    return full_data


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

    if output_file.exists():
        with open(output_file, encoding="utf-8") as f:
            existing_products = json.load(f)
    else:
        existing_products = []

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
        csv_ready_products.append(product_copy)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = csv_ready_products[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(csv_ready_products)

    print(f"Saved {len(products)} products to {output_file}")


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