import json
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        # headless=False lets you see the browser open. Change to True once it works.
        browser = p.chromium.launch(headless=False) 
        page = browser.new_page()

        # Define what happens when a network response is received
        def handle_response(response):
            if "sync-get-free4talk-groups" in response.url and response.status == 200:
                try:
                    data = response.json()
                    print(f"Success! Intercepted data.")
                    
                    # Dump the intercepted JSON response to a local file
                    with open("free4talk_data.json", "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4)
                        print("Data saved to free4talk_data.json")
                except Exception as e:
                    print(f"Failed to parse JSON: {e}")

        # Attach the listener to the page
        page.on("response", handle_response)
        
        # Navigate to the target site
        print("Navigating to site and waiting for background sync...")
        page.goto("https://www.free4talk.com/")
        
        # Keep the browser open for 15 seconds to ensure we catch a polling cycle
        page.wait_for_timeout(15000) 
        
        browser.close()

if __name__ == "__main__":
    run()