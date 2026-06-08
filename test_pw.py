from playwright.sync_api import sync_playwright
import time
import re

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page.goto("https://www.musinsa.com/products/5573822", wait_until="networkidle")
        
        # Scroll to load lazy images
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
        
        html = page.content()
        urls = re.findall(r'https://image\.msscdn\.net/[^\x22\x27\s\?]+', html)
        jpgs = [u for u in set(urls) if u.endswith('.jpg')]
        print(f"Found {len(jpgs)} jpg images.")
        for j in list(set(jpgs))[:10]:
            print(j)
        browser.close()

if __name__ == '__main__':
    run()
