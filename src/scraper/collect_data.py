from playwright.sync_api import sync_playwright

SEARCH_URL = "https://www.amazon.com/s?k=usb+c+hub"

def open_search_page():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(SEARCH_URL)
        page.wait_for_timeout(5000)
        print(page.title())
        browser.close()

if __name__ == "__main__":
    open_search_page()