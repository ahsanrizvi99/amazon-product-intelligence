import re

def build_search_url(keyword):
    formatted_keyword = keyword.replace(" ", "+")
    return f"https://www.amazon.com/s?k={formatted_keyword}"

def get_products_from_page(page):
    products = []
    product_cards = page.query_selector_all('div[data-component-type="s-search-result"]')

    for card in product_cards:
        asin = card.get_attribute("data-asin")
        title_element = card.query_selector("h2 span")
        price_element = card.query_selector("span.a-price span.a-offscreen")
        rating_element = card.query_selector("span.a-icon-alt")

        products.append({
            "asin": asin,
            "title": title_element.inner_text() if title_element else "",
            "price": price_element.inner_text() if price_element else "",
            "rating": rating_element.inner_text() if rating_element else "",
        })

    return products

def get_product_details(page, asin):
    product_url = f"https://www.amazon.com/dp/{asin}"
    page.goto(product_url)

    try:
        page.wait_for_selector("#productTitle", timeout=10000)
    except Exception:
        pass

    title_element = page.query_selector("#productTitle")
    title = title_element.inner_text().strip() if title_element else ""

    price_element = page.query_selector("#apex-pricetopay-accessibility-label")
    if price_element:
        match = re.search(r"\$[\d,]+\.\d{2}", price_element.inner_text())
        price = match.group() if match else ""
    else:
        price = ""

    brand_element = page.query_selector("#bylineInfo")
    if brand_element:
        brand = brand_element.inner_text().strip().replace("Visit the ", "").replace(" Store", "")
    else:
        brand = ""

    image_element = page.query_selector("#landingImage")
    main_image_url = image_element.get_attribute("src") if image_element else ""

    bullet_elements = page.query_selector_all("#feature-bullets ul.a-unordered-list li span.a-list-item")
    bullet_points = [b.inner_text().strip() for b in bullet_elements if b.inner_text().strip()]

    review_count_element = page.query_selector('span[data-hook="total-review-count"]')
    if review_count_element:
        match = re.search(r"[\d,]+", review_count_element.inner_text())
        review_count = match.group().replace(",", "") if match else ""
    else:
        review_count = ""

    video_urls = list(dict.fromkeys(re.findall(r"https://[^\s\"'\\&]+?\.m3u8", page.content())))

    return {
        "asin": asin,
        "title": title,
        "price": price,
        "brand": brand,
        "main_image_url": main_image_url,
        "bullet_points": bullet_points,
        "review_count": review_count,
        "video_urls": video_urls,
    }

def get_reviews(page):
    reviews = []
    review_blocks = page.query_selector_all('div[data-hook="review"]')

    for block in review_blocks:
        name_element = block.query_selector("span.a-profile-name")
        rating_element = block.query_selector('i[data-hook="review-star-rating"] span.a-icon-alt')
        title_element = block.query_selector('[data-hook="reviewTitle"]')
        verified_element = block.query_selector('span[data-hook="avp-badge"]')
        paragraph_elements = block.query_selector_all('div[data-hook="reviewRichContentContainer"] p span')

        body = " ".join([p.inner_text().strip() for p in paragraph_elements if p.inner_text().strip()])

        reviews.append({
            "reviewer_name": name_element.inner_text() if name_element else "",
            "rating": rating_element.inner_text() if rating_element else "",
            "title": title_element.inner_text().strip() if title_element else "",
            "verified_purchase": bool(verified_element),
            "body": body,
        })

    return reviews